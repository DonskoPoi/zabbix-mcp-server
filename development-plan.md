# Zabbix MCP Server 开发计划 v2.0

## 状态概览
=========

当前状态: 已完成基础 Zabbix MCP 核心工具集和自动拓扑功能（Map API + auto_map)。本计划聚焦于：Dify 集成、Dashboard 自动化、智能运维三大方向。

## 目录
1. [核心功能补充
2. [Dify 集成架构
3. [智能运维应用

---

## 第一阶段：核心功能补充 - 系统级 Dashboard 自动化
============================================

### 现状分析
- 已有：Map API (map_get/map_create/map_update/map_delete) ✓
- 已有：auto_map_preview/auto_map_update ✓
- 待实现：Dashboard API + 自动 Dashboard 生成

### P0: Dashboard 原生 API 包装
实现 Zabbix Dashboard API 原生包装，保持与其他资源一致的 CRUD 结构：
- `dashboard_get` - 获取 Dashboard 列表与详情
- `dashboard_create` - 创建新 Dashboard
- `dashboard_update` - 更新现有 Dashboard
- `dashboard_delete` - 删除 Dashboard

**关键设计要点：
- Dashboard 结构：`pages` (页) → `widgets` (组件)
- 支持 30+ 种 widget 类型：Map、Graph、Problems、Host availability 等
- 注意：Zabbix 6.0+ 使用新 Dashboard API（旧版 Screen API 不再优先）

### P1: 关键监控项预设与自动图表生成
为不同类型主机定义关键监控项（item）预设：

**Linux 服务器关键指标：
- CPU: `system.cpu.util[,idle]` / `system.cpu.load[percpu,avg1]`
- 内存: `vm.memory.size[available]` / `vm.memory.util`
- 磁盘: `vfs.fs.size[/,pfree]` / `vfs.fs.inode[/,pfree]`
- 网络: `net.if.in[eth0]` / `net.if.out[eth0]`

**Windows 服务器关键指标：
- CPU: `system.cpu.util[,idle]`
- 内存: `vm.memory.size[available]`
- 磁盘: `vfs.fs.size[C:,pfree]`
- 网络: `net.if.in[*]`

**网络设备关键指标：
- 接口流量/丢包/错误
- CPU 负载
- 内存使用率

### P2: 系统级 Dashboard 自动生成
新增高层 helper：
- `dashboard_create_system_overview` - 创建系统总览 Dashboard
  - 顶部：系统信息 + 问题概览
  - 中部：拓扑图（Map widget）
  - 底部：关键主机指标（Host card / Item value widget）

- `dashboard_create_host_detail` - 创建单主机详情 Dashboard
  - 主机状态概览
  - CPU/内存/磁盘/网络图表
  - 相关触发器

设计原则：
- Widget 坐标系统：x/y 从 0 开始，width 最大 36，height 以行为单位
- 优先使用 Zabbix 内置 widget，不做外部图表

---

## 第二阶段：Dify 集成架构
===================

### Dify 与 MCP 集成方案：
- Dify 通过 MCP 标准协议接入多个 MCP Server
- 接入两个核心 MCP：
  1. Zabbix MCP (当前项目) - Zabbix 操作
  2. RAG MCP (已有) - 知识库查询

### P0: MCP Server 传输层适配
- 确认 FastMCP 已支持 STDIO 和 streamable-http 两种传输
- Dify 推荐使用 streamable-http（便于网络连接）
- 配置：`ZABBIX_MCP_TRANSPORT=streamable-http`
- 注意：需要设置 `AUTH_TYPE=no-auth` （Dify 处理认证）

### P1: Dify 应用配置指南
创建 `docs/dify-integration.md`：
1. Dify 中配置 MCP Server 步骤
2. Zabbix MCP 工具列表与使用示例
3. RAG MCP 与 Zabbix MCP 协同调用示例

### P2: 示例工作流模板
提供可导入的 Dify 工作流模板：
- 「主机巡检工作流
- 「问题分析工作流
- 「拓扑更新工作流

---

## 第三阶段：智能运维应用
================

### P0: 定时巡检（Dify 定时任务）
巡检内容：
1. 所有主机可用性检查（agent.ping）
2. 触发器状态汇总
3. 关键指标阈值检查（CPU > 80%、磁盘 > 90%）

输出：
- 巡检报告（Markdown）
- 异常项高亮
- 历史趋势对比

### P1: 告警接收与分析
Zabbix → Dify 告警链路：
- 方式1: Zabbix 告警脚本调用 Dify API
- 方式2: Dify 定时拉取 Zabbix problem

分析流程：
1. 接收告警/拉取问题
2. 调用 RAG MCP 查询历史同类问题
3. 调用 Zabbix MCP 获取相关主机/监控项
4. 综合分析输出根因
5. 生成修复建议

### P2: 预测性告警（远期）
基于历史数据的预测：
- 趋势分析（trend.get）
- 异常检测
- 提前告警阈值

### P3: 自动修复（远期，安全敏感）
- 默认关闭，显式开启
- 带审批流程
- 完整审计日志
- 支持的操作：服务重启、磁盘清理、配置修正

---

## 项目结构更新
============

新增目录结构：
```
zabbix-mcp-server/
├── src/zabbix_mcp_server.py   # 主服务
├── test_code/                  # 临时测试脚本
├── scripts/                    # 正式脚本
├── docs/                       # 新增
│   ├── dify-integration.md   # Dify 集成文档
│   └── workflow-templates/      # Dify 工作流模板
└── ...
```

---

## 实现优先级
==========

Phase 1（核心补充）:
- Dashboard 原生 API → 预设关键指标 → 自动 Dashboard 生成

Phase 2（Dify 集成）:
- 传输层确认 → 集成文档 → 工作流模板

Phase 3（智能运维）:
- 定时巡检 → 告警分析 → 预测告警 → 自动修复

## 附录
====

重要参考：
- Zabbix Dashboard API 支持 30+ 种 widget：
  - Map, Graph, Problems, Host availability, Host card,
  - Item value, Gauge, Pie chart, System info 等
- 关键指标依据行业标准运维监控最佳实践定义
