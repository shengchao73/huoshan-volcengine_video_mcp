# MCP 配置指南

## 配置文件位置

根据您使用的 MCP 客户端,配置文件位置可能不同:

### Claude Desktop (推荐)

**Windows**:
```
%APPDATA%\Claude\claude_desktop_config.json
```
通常是: `C:\Users\你的用户名\AppData\Roaming\Claude\claude_desktop_config.json`

**macOS**:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux**:
```
~/.config/Claude/claude_desktop_config.json
```

### Cherry Studio

配置文件通常在应用设置中直接编辑,或位于:
```
应用数据目录/config/mcp_servers.json
```

## 配置内容

将以下内容添加到您的 MCP 配置文件中:

```json
{
  "mcpServers": {
    "huoshan_video": {
      "command": "python",
      "args": [
        "-m",
        "src.server"
      ],
      "cwd": "E:\\CherryStudioDaTa\\Agent\\论文\\huoshan_mcp",
      "env": {
        "VOLCES_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## 配置说明

### 1. 服务器名称
```json
"huoshan_video": {
```
- 服务器的唯一标识符
- **注意**: 使用下划线 `_` 而不是连字符 `-`
- 可以自定义,但建议使用有意义的名称

### 2. 命令
```json
"command": "python",
```
- Python 解释器命令
- 如果使用虚拟环境,可以指定完整路径:
  - Windows: `"C:\\path\\to\\venv\\Scripts\\python.exe"`
  - macOS/Linux: `"/path/to/venv/bin/python"`

### 3. 参数
```json
"args": [
  "-m",
  "src.server"
],
```
- `-m src.server`: 以模块方式运行服务器
- 不要修改此参数

### 4. 工作目录
```json
"cwd": "E:\\CherryStudioDaTa\\Agent\\论文\\huoshan_mcp",
```
- **重要**: 必须修改为您的实际项目路径
- Windows 路径使用双反斜杠 `\\` 或单正斜杠 `/`
- 示例:
  - `"E:\\Projects\\huoshan_mcp"`
  - `"E:/Projects/huoshan_mcp"`
  - `"C:\\Users\\YourName\\Documents\\huoshan_mcp"`

### 5. 环境变量
```json
"env": {
  "VOLCES_API_KEY": "your_api_key_here"
}
```
- **必须**: 将 `your_api_key_here` 替换为您的实际 API Key
- 获取 API Key: [火山引擎控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey)

## 完整配置示例

### 示例 1: Windows 系统

```json
{
  "mcpServers": {
    "huoshan_video": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "C:\\Users\\John\\Projects\\huoshan_mcp",
      "env": {
        "VOLCES_API_KEY": "sk-abc123def456..."
      }
    }
  }
}
```

### 示例 2: macOS/Linux 系统

```json
{
  "mcpServers": {
    "huoshan_video": {
      "command": "python3",
      "args": ["-m", "src.server"],
      "cwd": "/Users/john/projects/huoshan_mcp",
      "env": {
        "VOLCES_API_KEY": "sk-abc123def456..."
      }
    }
  }
}
```

### 示例 3: 使用虚拟环境 (Windows)

```json
{
  "mcpServers": {
    "huoshan_video": {
      "command": "C:\\Users\\John\\Projects\\huoshan_mcp\\venv\\Scripts\\python.exe",
      "args": ["-m", "src.server"],
      "cwd": "C:\\Users\\John\\Projects\\huoshan_mcp",
      "env": {
        "VOLCES_API_KEY": "sk-abc123def456..."
      }
    }
  }
}
```

### 示例 4: 使用虚拟环境 (macOS/Linux)

```json
{
  "mcpServers": {
    "huoshan_video": {
      "command": "/Users/john/projects/huoshan_mcp/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/Users/john/projects/huoshan_mcp",
      "env": {
        "VOLCES_API_KEY": "sk-abc123def456..."
      }
    }
  }
}
```

## 配置步骤

### 步骤 1: 找到配置文件

1. 打开您的 MCP 客户端 (如 Claude Desktop)
2. 找到配置文件位置 (见上方"配置文件位置"部分)
3. 如果文件不存在,创建一个新的 JSON 文件

### 步骤 2: 编辑配置

1. 用文本编辑器打开配置文件
2. 如果文件为空,添加基本结构:
   ```json
   {
     "mcpServers": {}
   }
   ```
3. 在 `mcpServers` 对象中添加 `huoshan_video` 配置

### 步骤 3: 修改路径和 API Key

1. 将 `cwd` 修改为您的实际项目路径
2. 将 `VOLCES_API_KEY` 替换为您的实际 API Key
3. 如果使用虚拟环境,修改 `command` 为虚拟环境的 Python 路径

### 步骤 4: 验证配置

1. 保存配置文件
2. 重启 MCP 客户端
3. 检查服务器是否成功加载
4. 尝试调用工具测试

## 验证配置

### 方法 1: 手动测试

在命令行中运行:

```bash
cd E:\CherryStudioDaTa\Agent\论文\huoshan_mcp
python -m src.server
```

如果看到类似以下输出,说明服务器正常:
```
MCP Huoshan Video server running on stdio
```

### 方法 2: JSON 格式验证

使用 Python 验证 JSON 格式:

```bash
python -m json.tool claude_desktop_config.json
```

如果没有错误输出,说明 JSON 格式正确。

## 常见问题

### Q1: "无效输入,请检查 JSON 格式"

**原因**: JSON 格式错误

**解决方法**:
1. 检查是否有多余的逗号
2. 检查引号是否配对
3. 检查括号是否配对
4. 使用 JSON 验证工具检查格式

### Q2: "找不到模块 src.server"

**原因**: `cwd` 路径不正确

**解决方法**:
1. 确认 `cwd` 指向项目根目录
2. 确认项目根目录下有 `src` 文件夹
3. 使用绝对路径而不是相对路径

### Q3: "API key is required"

**原因**: API Key 未设置或格式错误

**解决方法**:
1. 确认 `VOLCES_API_KEY` 已设置
2. 确认 API Key 格式正确 (通常以 `sk-` 开头)
3. 确认 API Key 有效且未过期

### Q4: 服务器无法启动

**原因**: Python 环境或依赖问题

**解决方法**:
1. 确认 Python 版本 >= 3.8
2. 确认已安装所有依赖: `pip install -r requirements.txt`
3. 尝试手动运行服务器测试

### Q5: 路径包含中文或特殊字符

**原因**: 某些系统可能不支持路径中的非 ASCII 字符

**解决方法**:
1. 尽量使用英文路径
2. 如果必须使用中文路径,确保使用 UTF-8 编码
3. 在 Windows 上使用双反斜杠转义

## 多服务器配置

如果您有多个 MCP 服务器,配置如下:

```json
{
  "mcpServers": {
    "huoshan_video": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "E:\\Projects\\huoshan_mcp",
      "env": {
        "VOLCES_API_KEY": "sk-abc123..."
      }
    },
    "another_server": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "E:\\Projects\\another_mcp"
    }
  }
}
```

## 安全建议

1. **不要分享配置文件**: 配置文件包含 API Key,请勿上传到公开仓库
2. **使用环境变量**: 考虑使用系统环境变量而不是直接在配置中写入 API Key
3. **定期更换 API Key**: 定期更换 API Key 以提高安全性
4. **限制权限**: 确保配置文件只有您的用户账户可以读取

## 获取帮助

如果遇到配置问题:

1. 检查本文档的"常见问题"部分
2. 查看 README.md 中的详细说明
3. 确认 Python 环境和依赖正确安装
4. 尝试手动运行服务器进行调试
