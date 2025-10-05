# SSL 诊断工具

一个基于 Python 的综合性工具，用于诊断与远程服务器的 SSL/TLS 连接问题。该工具帮助识别证书问题、SSL 配置问题和网络连接问题。

## 功能特点

- 🔍 **多种 SSL 测试方法**
  - 禁用 SSL 验证
  - 使用 Certifi 证书包
  - 系统默认证书
  - 宽松 SSL 设置

- 📊 **智能诊断分析**
  - 自动分析测试结果
  - 提供具体问题诊断
  - 给出解决方案建议

- 🛠️ **易于使用**
  - 简单的命令行界面
  - 自动环境配置
  - 详细的错误信息

## 系统要求

- Python 3.7 或更高版本
- Windows 操作系统（主要针对 Windows 环境测试）

## 快速开始

### 方法一：使用批处理文件（推荐）

1. 下载项目文件到同一目录：
   - `ssl_diagnostic_tool.py`
   - `run_ssl_tool.bat`

2. 双击运行 `run_ssl_tool.bat`

3. 批处理文件会自动：
   - 创建 Python 虚拟环境
   - 安装所需依赖
   - 启动 SSL 诊断工具

### 方法二：手动运行

1. 安装依赖：
```bash
pip install aiohttp certifi
```

2. 运行工具：
```bash
python ssl_diagnostic_tool.py
```

## 使用方法

1. 启动工具后，输入要测试的完整 URL（必须以 `http://` 或 `https://` 开头）

2. 工具将自动执行以下测试：
   - **测试 1**: 禁用 SSL 验证
   - **测试 2**: 使用 Certifi 证书
   - **测试 3**: 系统默认证书
   - **测试 4**: 宽松 SSL 设置

3. 查看诊断结果和建议解决方案

## 测试场景

### 常见问题诊断

- ✅ **所有测试成功**: SSL 配置正常
- ❌ **所有测试失败**: 网络连接问题或服务器不可用
- ⚠️ **SSL 证书验证问题**: 证书链不完整或根证书问题
- ⚠️ **主机名验证问题**: 证书与访问的主机名不匹配

### 典型解决方案

1. **证书问题**:
   ```python
   # 使用 certifi 证书
   ssl_context = ssl.create_default_context(cafile=certifi.where())
   ```

2. **临时解决方案**:
   ```python
   # 禁用 SSL 验证（不推荐生产环境）
   connector = aiohttp.TCPConnector(ssl=False)
   ```

3. **系统证书问题**:
   - 更新操作系统根证书
   - 重新安装系统证书库

## 项目结构

```
ssl-diagnostic-tool/
├── ssl_diagnostic_tool.py  # 主程序文件
├── run_ssl_tool.bat        # Windows 启动脚本
├── venv/                   # 虚拟环境目录（自动创建）
└── requirements.txt        # 依赖列表（自动创建）
```

## 依赖包

- `aiohttp` >= 3.8.0: 异步 HTTP 客户端
- `certifi` >= 2023.11.17: 最新的 CA 证书包

## 故障排除

### 常见问题

1. **Python 未找到**
   - 确保已安装 Python 3.7+
   - 将 Python 添加到系统 PATH

2. **虚拟环境创建失败**
   - 检查 Python 安装是否完整
   - 尝试手动运行: `python -m venv venv`

3. **依赖安装失败**
   - 检查网络连接
   - 尝试手动安装: `pip install aiohttp certifi`

4. **SSL 测试失败**
   - 检查目标网址是否正确
   - 验证网络连接和防火墙设置
   - 确认目标服务器是否可用

### 手动诊断

如果批处理文件无法运行，可以手动执行以下步骤：

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate.bat

# 3. 安装依赖
pip install aiohttp certifi

# 4. 运行工具
python ssl_diagnostic_tool.py
```

## 贡献

欢迎提交问题和改进建议！

## 免责声明

此工具仅用于诊断目的。在生产环境中使用 SSL 相关配置时，请遵循安全最佳实践。禁用 SSL 验证仅建议在测试环境中使用。
