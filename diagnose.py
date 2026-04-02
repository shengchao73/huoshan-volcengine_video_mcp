#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置诊断脚本
用于检查 MCP 服务器配置是否正确
"""
import os
import sys
import json
from pathlib import Path

# 设置控制台编码
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def check_python_version():
    """检查 Python 版本"""
    print("[检查] Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"[OK] Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[FAIL] Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("       需要 Python 3.8 或更高版本")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n[检查] 依赖包...")
    required_packages = ["mcp", "httpx", "dotenv"]
    missing = []

    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[FAIL] {package} 未安装")
            missing.append(package)

    if missing:
        print(f"\n请运行: pip install -r requirements.txt")
        return False
    return True


def check_project_structure():
    """检查项目结构"""
    print("\n[检查] 项目结构...")
    required_files = [
        "src/__init__.py",
        "src/server.py",
        "src/volces_client.py",
        "src/models.py",
        "requirements.txt",
        ".env.example"
    ]

    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"[OK] {file}")
        else:
            print(f"[FAIL] {file} 不存在")
            all_exist = False

    return all_exist


def check_env_file():
    """检查环境变量配置"""
    print("\n[检查] 环境变量配置...")

    env_file = Path(".env")
    if not env_file.exists():
        print("[WARN] .env 文件不存在")
        print("       请复制 .env.example 为 .env 并填入 API Key")
        return False

    print("[OK] .env 文件存在")

    # 检查 API Key
    api_key = os.getenv("VOLCES_API_KEY")
    if not api_key:
        # 尝试从 .env 文件读取
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("VOLCES_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break
        except Exception as e:
            print(f"[FAIL] 读取 .env 文件失败: {e}")
            return False

    if not api_key or api_key == "your_api_key_here":
        print("[FAIL] VOLCES_API_KEY 未设置或使用默认值")
        print("       请在 .env 文件中设置您的 API Key")
        return False

    print(f"[OK] VOLCES_API_KEY 已设置 (长度: {len(api_key)})")
    return True


def check_mcp_config():
    """检查 MCP 配置文件"""
    print("\n[检查] MCP 配置示例...")

    config_file = Path("mcp-config-example.json")
    if not config_file.exists():
        print("[FAIL] mcp-config-example.json 不存在")
        return False

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        print("[OK] JSON 格式正确")

        # 检查配置结构
        if "mcpServers" not in config:
            print("[FAIL] 缺少 mcpServers 字段")
            return False

        if "huoshan_video" not in config["mcpServers"]:
            print("[FAIL] 缺少 huoshan_video 服务器配置")
            return False

        server_config = config["mcpServers"]["huoshan_video"]

        # 检查必需字段
        required_fields = ["command", "args", "cwd", "env"]
        for field in required_fields:
            if field in server_config:
                print(f"[OK] {field} 字段存在")
            else:
                print(f"[FAIL] 缺少 {field} 字段")
                return False

        # 检查 cwd 路径
        cwd = server_config["cwd"]
        current_dir = str(Path.cwd())
        if cwd != current_dir:
            print(f"[WARN] 配置中的 cwd 与当前目录不匹配")
            print(f"       配置: {cwd}")
            print(f"       当前: {current_dir}")
            print(f"       请更新配置文件中的 cwd 路径")

        return True

    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON 格式错误: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] 检查配置文件失败: {e}")
        return False


def test_import():
    """测试导入模块"""
    print("\n[检查] 测试导入模块...")

    try:
        from src import server
        print("[OK] 成功导入 src.server")
        return True
    except Exception as e:
        print(f"[FAIL] 导入失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("火山引擎视频生成 MCP 服务器 - 配置诊断")
    print("=" * 60)

    results = []

    # 运行所有检查
    results.append(("Python 版本", check_python_version()))
    results.append(("依赖包", check_dependencies()))
    results.append(("项目结构", check_project_structure()))
    results.append(("环境变量", check_env_file()))
    results.append(("MCP 配置", check_mcp_config()))
    results.append(("模块导入", test_import()))

    # 总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"{name}: {status}")

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        print("\n[成功] 所有检查通过!服务器配置正确。")
        print("\n下一步:")
        print("1. 确保在 .env 文件中设置了正确的 API Key")
        print("2. 将 mcp-config-example.json 的内容添加到您的 MCP 客户端配置中")
        print("3. 修改配置中的 cwd 路径为您的实际项目路径")
        print("4. 重启 MCP 客户端")
        return 0
    else:
        print("\n[警告] 发现问题,请根据上述提示修复。")
        print("\n常见解决方法:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 创建 .env 文件: cp .env.example .env")
        print("3. 在 .env 中设置 API Key")
        print("4. 确保所有文件完整")
        return 1


if __name__ == "__main__":
    sys.exit(main())
