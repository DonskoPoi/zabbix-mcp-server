# CHANGELOG

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范，版本号遵循 [语义化版本 (Semantic Versioning)](https://semver.org/lang/zh-CN/)。

## 版本说明
- 主版本号（MAJOR）：不兼容的 API 变更
- 次版本号（MINOR）：新增功能，向后兼容
- 修订号（PATCH）：向后兼容的问题修正

## [2.1.0] - 2026-03-27

### 新增
- **Media Type 管理功能**：添加原生 Media Type API 工具
  - `mediatype_get` - 获取 media types，支持完整参数过滤
  - `mediatype_create` - 创建新 media type，支持所有类型（Email、Script、SMS、Webhook）
  - `mediatype_update` - 更新现有 media type
  - `mediatype_delete` - 删除 media types
- **Action 管理功能**：添加原生 Action API 工具
  - `action_get` - 获取 actions，支持 selectFilter、selectOperations、selectRecoveryOperations、selectUpdateOperations
  - `action_create` - 创建新 action，支持完整参数配置
  - `action_update` - 更新现有 action
  - `action_delete` - 删除 actions
- **User Media 管理功能**：添加用户媒体关联工具
  - `usermedia_get` - 获取用户的媒体配置
  - `usermedia_add` - 为用户添加 media type
  - `usermedia_update` - 更新用户的所有媒体配置
  - `usermedia_remove` - 移除用户的 media type

### 修复
- **usermedia.py 参数名错误**：修复了用户媒体管理工具中的参数名问题
  - 将 `user_medias` 修正为正确的 `medias` 参数名
  - 此问题影响 `usermedia_add()`、`usermedia_update()` 和 `usermedia_remove()` 函数

## [2.0.0] - 2026-03-25

### 重大变更（BREAKING CHANGES）
- **完全分离的双 MCP 服务器架构**：
  - 移除了"完整"服务器（main.py 和 `zabbix-mcp` 入口点）
  - 只保留两个独立的服务器：
    - `zabbix-mcp-readonly` - 只读查询服务器
    - `zabbix-mcp-writable` - 写入操作服务器
  - 两个服务器拥有完全分离的配置（传输协议、地址、端口等）

### 新增
- **统一工具装饰器系统**：
  - 新增 `src/zabbix_mcp_server/core/tool_registry.py` - 全局工具注册表
  - `@readonly_tool()` 和 `@writable_tool()` 统一装饰器
  - `register_readonly_tools()` 和 `register_writable_tools()` 统一注册函数
  - 消除了所有工具模块中的重复装饰器和注册代码

- **分离的配置系统**：
  - `get_transport_config_readonly()` - 获取只读服务器配置
  - `get_transport_config_writable()` - 获取写入服务器配置
  - 支持独立配置每个服务器的传输协议、主机、端口等

- **更新的启动脚本**：
  - `--readonly/-r` - 仅启动只读服务器
  - `--writable/-w` - 仅启动写入服务器
  - `--all/-a` - 同时启动两个服务器（后台进程）

### 改进
- **代码架构优化**：
  - 移除所有工具模块中的 `_ToolInfo`、`_tools` 列表、`_register_tool()` 等重复代码
  - 移除 `validate_read_only()` 函数（写入服务器本身就允许写入）
  - 简化 `tools/__init__.py` - 只需导入工具模块触发注册

### 配置变更
- **新的 .env 配置结构**：
  ```env
  # 共用配置
  ZABBIX_URL=...
  ZABBIX_TOKEN=...
  VERIFY_SSL=...
  DEBUG=...

  # 只读服务器配置
  READONLY_TRANSPORT=stdio
  READONLY_HOST=0.0.0.0
  READONLY_PORT=9002
  ...

  # 写入服务器配置
  WRITABLE_TRANSPORT=stdio
  WRITABLE_HOST=0.0.0.0
  WRITABLE_PORT=9003
  ...
  ```

## [1.8.0] - 2026-03-25

### 改进
- **代码架构优化**：消除工具模块中的大量代码重复
  - 使用模块级注册表 + 装饰器模式重构所有 22 个工具模块
  - 每个工具函数现在只定义一次，消除了 6000+ 行重复代码
  - 通过 `@readonly_tool()` 和 `@writable_tool()` 装饰器标记工具类别
  - 简化了 `register_tools()`、`register_readonly_tools()`、`register_writable_tools()` 函数实现
  - 保持 100% 向后兼容性，公共 API 完全不变

### 技术改进
- 重构的工具模块：
  - `system.py`、`host.py`、`hostgroup.py`、`item.py`、`trigger.py`
  - `template.py`、`problem.py`、`event.py`、`history.py`、`trend.py`
  - `user.py`、`proxy.py`、`maintenance.py`、`graph.py`、`valuemap.py`
  - `discovery.py`、`itemprototype.py`、`configuration.py`、`macro.py`
  - `map.py`、`dashboard.py`

## [1.7.0] - 2026-03-25

### 新增
- **物理分离的双服务器架构**：
  - 新增 `zabbix-mcp-readonly` 只读服务器入口，仅包含查询工具（`*_get`），从源码级别保证无写入操作
  - 新增 `zabbix-mcp-writable` 写入服务器入口，仅包含修改工具（`*_create`/`*_update`/`*_delete`）
  - 两个服务器工具集合完全不相交，从根源避免 AI 误调用写入操作
  - 完全向后兼容：原有 `zabbix-mcp` 入口保持不变，仍包含所有工具

### 改进
- **streamable-http 默认配置更新**：
  - 默认监听地址从 `127.0.0.1` 改为 `0.0.0.0`，便于容器化部署和远程访问
  - 默认端口从 `8000` 改为 `9002`，避免与常见服务冲突
  - 保持环境变量可配置性，用户仍可通过 `.env` 自定义

## [1.6.0] - 2026-03-19

### 改进
- **代码架构重构**：将单一文件重构为模块化结构
  - 核心功能分离到 `core/` 模块（client、config、utils）
  - 工具按类别拆分到 `tools/` 模块（21+ 个独立工具文件）
  - 新增 `zabbix_mcp_server.main` 主模块
  - 新增 `zabbix_mcp_server.tools.register_all_tools()` 统一工具注册入口
- **向后兼容性**：保留原始 `src/zabbix_mcp_server.py` 作为薄包装层，并添加弃用警告

### 技术改进
- 新目录结构：
  ```
  src/zabbix_mcp_server/
  ├── __init__.py          # 包初始化
  ├── main.py              # 主模块
  ├── core/                # 核心功能
  │   ├── client.py
  │   ├── config.py
  │   └── utils.py
  └── tools/               # 工具模块
      ├── host.py
      ├── hostgroup.py
      ├── item.py
      ├── ... (20+ 个工具文件)
      └── __init__.py
  ```

## [1.5.0] - 2026-03-18

### 新增
- **自动 Dashboard 生成功能**：P2 阶段 - 系统级 Dashboard 自动生成
  - `dashboard_create_system_overview` - 创建系统总览 Dashboard
    - 顶部：系统信息 + 时钟 + 问题概览
    - 中部：拓扑图（可选）
    - 底部：关键主机卡片（支持按主机组筛选）
  - `dashboard_create_host_detail` - 创建单主机详情 Dashboard
    - 主机状态概览卡片
    - CPU/内存/磁盘/网络图表（自动查找匹配图表）
    - 该主机的问题和触发器列表

## [1.4.0] - 2026-03-18

### 新增
- **Dashboard 管理功能**：添加原生 Dashboard API 工具
  - `dashboard_get` - 获取 Dashboard，支持 selectUsers、selectUserGroups
  - `dashboard_create` - 创建新 Dashboard，支持完整参数配置
  - `dashboard_update` - 更新现有 Dashboard
  - `dashboard_delete` - 删除 Dashboard
- **值映射管理功能**：添加 Value Map API 工具
  - `valuemap_get` - 获取值映射，支持 selectMappings
  - `valuemap_create` - 创建新值映射
  - `valuemap_update` - 更新现有值映射
  - `valuemap_delete` - 删除值映射
- **图形管理功能**：添加完整 Graph API 工具
  - `graph_create` - 创建新图形，支持 gitems 配置
  - `graph_update` - 更新现有图形
  - `graph_delete` - 删除图形

### 改进
- 扩展 `item_create` 函数，添加 `interfaceid` 参数（Zabbix agent 监控项必需）
- 扩展 `item_update` 函数，添加 `valuemapid` 参数（用于应用值映射）
- 扩展 `valuemap_create` 函数，添加 `hostid` 参数（值映射必需关联主机/模板）
- 扩展 `dashboard_get` 函数，添加 `selectPages` 参数（用于获取仪表盘页面和 widget 配置）

## [1.3.0] - 2026-03-17

### 新增
- **地图管理功能**：添加原生 Map API 工具
  - `map_get` - 获取地图，支持 selectSelements、selectLinks、selectShapes、selectLines、selectUsers、selectUserGroups
  - `map_create` - 创建新地图，支持完整参数配置
  - `map_update` - 更新现有地图
  - `map_delete` - 删除地图s
- **AutoMap 自动拓扑功能**：基于主机标签自动构建拓扑图
  - `auto_map_preview` - 预览拓扑（只读，不修改 Zabbix）
  - `auto_map_update` - 执行自动拓扑更新
  - 支持可配置标签前缀（默认 "am."）
  - 内置简单 grid 布局（无外部依赖）
  - 可选 igraph 布局（circle、tree、drl、fr、kk、random、rt、large_graph）
  - 保留现有主机位置和非主机元素（图片、子图等）
  - 支持自定义图标配置
- 项目配置更新：
  - 添加可选依赖 `igraph`（用于高级布局算法）
  - 更新版本号至 1.3.0
  - 添加 Python 3.13

### 改进
- 整合 ZabbixAutomap 项目的核心功能，优化了原脚本的依赖过重、配置分离等问题
- 所有功能内置，无需外部 config.json 文件
- 支持预览模式，安全确认后再修改

## [1.2.0] - 2026-03-17

### 新增
- 扩展 `host_get` 函数，添加所有常见的 `select*` 参数支持（selectInterfaces、selectTags、selectInheritedTags、selectGroups、selectTemplates、selectMacros、selectInventory、selectParentTemplates、selectDiscoveries、selectDiscoveryRule、selectHttpTests、selectItems、selectTriggers、selectGraphs、selectApplications、selectScreens）
- 扩展 `host_create` 函数，添加完整的参数支持（name、templates、tags、macros、inventory_mode、inventory、status、tls_connect、tls_accept、tls_psk_identity、tls_psk、tls_issuer、tls_subject、monitored_by、proxyid、proxy_groupid）

## [1.1.0] - 2025-01-07

### 新增
- 添加代理管理功能（proxy_get、proxy_create、proxy_update、proxy_delete）
- 添加 VERIFY_SSL 配置选项，支持禁用 SSL 证书验证
- 添加 streamable-http 传输支持

### 修复
- 更新 zabbix_utils 到 2.0.3 版本，支持 Zabbix 7.4
- 修复 verify_ssl 配置问题
- 更新文档，说明 'output' 参数支持字符串或列表

## [1.0.0] - 2024-12-01

### 新增
- 初始版本发布
- 实现 50+ Zabbix API 方法作为 MCP 工具
- 主机管理（host_get、host_create、host_update、host_delete）
- 主机组管理（hostgroup_get、hostgroup_create、hostgroup_update、hostgroup_delete）
- 监控项管理（item_get、item_create、item_update、item_delete）
- 触发器管理（trigger_get、trigger_create、trigger_update、trigger_delete）
- 模板管理（template_get、template_create、template_update、template_delete）
- 问题与事件管理（problem_get、event_get、event_acknowledge）
- 数据检索（history_get、trend_get）
- 用户管理（user_get、user_create、user_update、user_delete）
- 维护管理（maintenance_get、maintenance_create、maintenance_update、maintenance_delete）
- 其他功能（graph_get、discoveryrule_get、itemprototype_get、configuration_export、configuration_import、apiinfo_version）
- 支持基于令牌或用户名/密码的身份验证
- 只读模式支持
- 双传输支持：STDIO 和 Streamable HTTP
