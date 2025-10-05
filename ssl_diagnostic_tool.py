import ssl
import aiohttp
import asyncio
import platform
import certifi
import sys

def get_user_input():
    """获取用户输入的测试网址"""
    print("=== SSL 连接诊断工具 ===")
    print(f"Windows 版本: {platform.platform()}")
    print(f"Python 版本: {sys.version}")
    print(f"OpenSSL 版本: {ssl.OPENSSL_VERSION}")
    
    # 获取测试网址，必须输入
    while True:
        test_url = input("\n请输入要测试的网址 (必须包含 http:// 或 https://): ").strip()
        
        if not test_url:
            print("❌ 网址不能为空，请重新输入")
            continue
            
        if not test_url.startswith(('http://', 'https://')):
            print("❌ 网址必须以 http:// 或 https:// 开头，请重新输入")
            continue
            
        break
    
    return test_url

async def test_ssl_connection(session, url, test_name):
    """测试SSL连接并返回结果"""
    try:
        async with session.get(url, timeout=10) as resp:
            status = resp.status
            return True, f"✅ {test_name}: 成功 (状态码: {status})"
    except asyncio.TimeoutError:
        return False, f"❌ {test_name}: 超时 (10秒)"
    except aiohttp.ClientConnectorCertificateError as e:
        return False, f"❌ {test_name}: 证书错误 - {e}"
    except aiohttp.ClientConnectorSSLError as e:
        return False, f"❌ {test_name}: SSL错误 - {e}"
    except aiohttp.ClientConnectionError as e:
        return False, f"❌ {test_name}: 连接错误 - {e}"
    except Exception as e:
        return False, f"❌ {test_name}: 失败 - {type(e).__name__}: {e}"

async def diagnose_ssl(test_url):
    """诊断SSL连接问题"""
    print(f"\n开始测试网址: {test_url}")
    results = {}
    
    # 1. 测试禁用 SSL 验证
    print("\n1. 测试禁用 SSL 验证...")
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            success, message = await test_ssl_connection(session, test_url, "禁用 SSL 验证")
            print(f"   {message}")
            results["禁用 SSL 验证"] = message
    except Exception as e:
        error_msg = f"配置失败 - {e}"
        print(f"   ❌ 禁用 SSL 验证: {error_msg}")
        results["禁用 SSL 验证"] = f"❌ {error_msg}"

    # 2. 测试使用 certifi 证书
    print("\n2. 测试使用 certifi 证书...")
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            success, message = await test_ssl_connection(session, test_url, "使用 certifi")
            print(f"   {message}")
            results["使用 certifi"] = message
    except Exception as e:
        error_msg = f"配置失败 - {e}"
        print(f"   ❌ 使用 certifi: {error_msg}")
        results["使用 certifi"] = f"❌ {error_msg}"

    # 3. 测试系统默认证书
    print("\n3. 测试系统默认证书...")
    try:
        async with aiohttp.ClientSession() as session:
            success, message = await test_ssl_connection(session, test_url, "系统默认证书")
            print(f"   {message}")
            results["系统默认证书"] = message
    except Exception as e:
        error_msg = f"配置失败 - {e}"
        print(f"   ❌ 系统默认证书: {error_msg}")
        results["系统默认证书"] = f"❌ {error_msg}"

    # 4. 测试自定义SSL上下文（宽松设置）
    print("\n4. 测试宽松SSL设置...")
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            success, message = await test_ssl_connection(session, test_url, "宽松SSL设置")
            print(f"   {message}")
            results["宽松SSL设置"] = message
    except Exception as e:
        error_msg = f"配置失败 - {e}"
        print(f"   ❌ 宽松SSL设置: {error_msg}")
        results["宽松SSL设置"] = f"❌ {error_msg}"
    
    return results

def print_summary(results):
    """根据测试结果打印智能诊断总结"""
    print("\n" + "="*50)
    print("智能诊断总结:")
    
    # 提取测试结果
    disable_ssl_success = "成功" in results.get("禁用 SSL 验证", "")
    certifi_success = "成功" in results.get("使用 certifi", "")
    system_success = "成功" in results.get("系统默认证书", "")
    relaxed_success = "成功" in results.get("宽松SSL设置", "")
    
    all_success = all([disable_ssl_success, certifi_success, system_success, relaxed_success])
    all_failed = all([not disable_ssl_success, not certifi_success, not system_success, not relaxed_success])
    
    if all_success:
        print("✅ 所有测试都成功 - SSL配置正常")
        print("   您的系统SSL配置正确，可以正常访问目标网站")
        
    elif all_failed:
        print("❌ 所有测试都失败 - 可能的问题:")
        print("   • 网络连接问题")
        print("   • 目标服务器不可用")
        print("   • 防火墙或代理阻止连接")
        print("   • 网址不正确")
        
    elif disable_ssl_success and not system_success:
        print("⚠️  SSL证书验证问题")
        print("   • 禁用SSL验证成功，但系统证书失败 - 存在证书验证问题")
        if certifi_success:
            print("   • certifi证书工作正常 - 建议更新系统证书库")
        else:
            print("   • certifi证书也失败 - 可能是证书链不完整或根证书问题")
            
    elif relaxed_success and not system_success:
        print("⚠️  主机名验证问题")
        print("   • 宽松设置成功但系统默认失败 - 可能存在主机名验证问题")
        print("   • 目标网站的证书可能不包含您访问的主机名")
        
    elif system_success and certifi_success:
        print("✅ 系统证书和certifi都正常 - SSL环境健康")
        if not disable_ssl_success:
            print("   • 禁用SSL验证失败可能是偶然的网络问题")
            
    elif system_success and not certifi_success:
        print("ℹ️  系统证书正常但certifi失败")
        print("   • certifi证书库可能需要更新")
        print("   • 运行 'pip install --upgrade certifi' 更新证书")
        
    elif certifi_success and not system_success:
        print("⚠️  系统证书库问题")
        print("   • certifi工作但系统证书失败 - 系统证书库可能损坏")
        print("   • 考虑更新操作系统或重新安装根证书")
        
    else:
        print("🔍 混合情况 - 详细分析:")
        if disable_ssl_success:
            print("   • 禁用SSL验证成功: 基本网络连接正常")
        if relaxed_success:
            print("   • 宽松SSL设置成功: SSL协议协商正常")
        if certifi_success:
            print("   • certifi成功: Python证书库正常")
        if system_success:
            print("   • 系统证书成功: 操作系统证书库正常")
    
    # 给出具体建议
    print("\n建议解决方案:")
    if not system_success and certifi_success:
        print("1. 在代码中使用 certifi 证书:")
        print("   ssl_context = ssl.create_default_context(cafile=certifi.where())")
        
    if disable_ssl_success and not system_success:
        print("1. 临时解决方案（不推荐生产环境）:")
        print("   connector = aiohttp.TCPConnector(ssl=False)")
        print("2. 长期解决方案: 更新系统根证书")
        
    if all_failed:
        print("1. 检查网络连接和防火墙设置")
        print("2. 验证目标网址是否正确可用")
        print("3. 尝试使用其他网络环境测试")
        
    if relaxed_success and not system_success:
        print("1. 检查目标网址与证书中的主机名是否匹配")
        print("2. 如果是内部服务器，可能需要将证书添加到信任库")

async def main():
    """主函数"""
    try:
        test_url = get_user_input()
        results = await diagnose_ssl(test_url)
        print_summary(results)
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n程序执行出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())