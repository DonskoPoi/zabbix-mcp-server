# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中进行代码开发提供指导。

该项目的计划请参照development-plan.md

## 项目概述

**Zabbix MCP Server** 是一个模型上下文协议（MCP）服务器，使用 FastMCP 和 python-zabbix-utils 实现与 Zabbix 监控系统的集成。它通过 MCP 兼容工具提供对 Zabbix API 功能的完整访问。

- **许可证：** MIT
- **Python 版本：** ≥ 3.10
- **包管理器：** uv
- **版本：** 1.1.0

## 常用命令

### 安装与设置
```bash
uv sync                                      # 安装依赖并创建虚拟环境
cp config/.env.example .env                  # 复制环境变量模板
```

### 运行
```bash
uv run python scripts/start_server.py        # 带验证启动服务器（推荐）
uv run python src/zabbix_mcp_server.py       # 直接运行服务器
uv run zabbix-mcp                             # 通过入口点运行
```

### 测试
```bash
uv run python scripts/test_server.py          # 运行完整测试套件
```

### Docker
```bash
docker build -t zabbix-mcp-server .           # 构建 Docker 镜像
docker compose up -d                           # 使用 Docker Compose 运行（后台）
docker compose logs -f                         # 查看日志
```

## 代码架构

### 项目结构
```
zabbix-mcp-server/
├── src/
│   └── zabbix_mcp_server.py    # 主服务器，包含所有 MCP 工具（50+ 工具）
├── scripts/
│   ├── start_server.py          # 增强型启动脚本，带验证
│   └── test_server.py           # 完整测试套件
├── test_code/                   # 临时测试代码和演示脚本（非正式项目文件）
├── config/
│   ├── .env.example             # 环境变量模板
│   └── mcp.json                 # MCP 客户端配置示例
├── pyproject.toml               # 项目配置
└── requirements.txt             # 依赖项
```

**注意：** 所有临时测试代码、演示脚本和一次性实验脚本都应放入 `test_code/` 文件夹，不要放在 `scripts/` 文件夹中。

### 关键组件

**主服务器 (`src/zabbix_mcp_server.py`)：**
- 基于 FastMCP 框架构建
- 实现 50+ Zabbix API 方法作为 MCP 工具
- Zabbix 客户端延迟初始化（首次请求时创建）
- 支持基于令牌或用户名/密码的身份验证
- 只读模式，阻止创建/更新/删除操作
- 双传输支持：STDIO（Claude Desktop 默认）和 Streamable HTTP
- 完善的错误处理和响应格式化

**工具类别：**
- 主机管理：`host_get`、`host_create`、`host_update`、`host_delete`
- 主机组管理：`hostgroup_get`、`hostgroup_create`、`hostgroup_update`、`hostgroup_delete`
- 监控项管理：`item_get`、`item_create`、`item_update`、`item_delete`
- 触发器管理：`trigger_get`、`trigger_create`、`trigger_update`、`trigger_delete`
- 模板管理：`template_get`、`template_create`、`template_update`、`template_delete`
- 问题与事件管理：`problem_get`、`event_get`、`event_acknowledge`
- 数据检索：`history_get`、`trend_get`
- 用户管理：`user_get`、`user_create`、`user_update`、`user_delete`
- 代理管理：`proxy_get`、`proxy_create`、`proxy_update`、`proxy_delete`
- 维护管理：`maintenance_get`、`maintenance_create`、`maintenance_update`、`maintenance_delete`
- 其他：`graph_get`、`discoveryrule_get`、`itemprototype_get`、`configuration_export`、`configuration_import`、`apiinfo_version`

### 配置

**必需环境变量：**
- `ZABBIX_URL` - Zabbix 服务器 API 端点

**身份验证（选择一种）：**
- `ZABBIX_TOKEN` - API 令牌（推荐）
- 或 `ZABBIX_USER` + `ZABBIX_PASSWORD` - 用户名/密码

**可选：**
- `READ_ONLY` - 启用只读模式（true/1/yes）
- `VERIFY_SSL` - SSL 验证（默认：true）
- `ZABBIX_MCP_TRANSPORT` - `stdio`（默认）或 `streamable-http`
- `DEBUG` - 启用调试日志

## 开发指南
- 任何关于Zabbix API的操作方式，请优先调用api-rag查询定义与使用方法，如果未找到，请在网页上搜索相关定义

### 编码标准
- 遵循 PEP 8 Python 风格指南
- 为函数参数和返回值使用类型提示
- 为所有函数和类编写文档字符串
- 保持函数聚焦和单一用途
- 使用有意义的变量名

### 添加新工具
遵循的模式：
```python
@mcp.tool()
def example_get(param1: str, param2: Optional[int] = None) -> str:
    """从 Zabbix 获取示例数据

    Args:
        param1: 必需参数描述
        param2: 可选参数描述

    Returns:
        包含示例数据的 JSON 字符串
    """
    client = get_zabbix_client()
    params = {"param1": param1}

    if param2 is not None:
        params["param2"] = param2

    result = client.example.get(**params)
    return format_response(result)
```

### 重要模式
- 始终使用 `get_zabbix_client()` 获取 API 客户端
- 使用 `format_response()` 实现一致的 JSON 输出
- 对写入操作检查 `is_read_only()`
- 将 API 调用包装在 try/except 块中以进行适当的错误处理
