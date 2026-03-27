# Zabbix MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A comprehensive Model Context Protocol (MCP) server for Zabbix integration using FastMCP and python-zabbix-utils. This server provides complete access to Zabbix API functionality through MCP-compatible tools.

<a href="https://glama.ai/mcp/servers/@mpeirone/zabbix-mcp-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@mpeirone/zabbix-mcp-server/badge" alt="zabbix-mcp-server MCP server" />
</a>

## Features

### 🏠 Host Management
- `host_get` - Retrieve hosts with advanced filtering
- `host_create` - Create new hosts with interfaces and templates
- `host_update` - Update existing host configurations
- `host_delete` - Remove hosts from monitoring

### 👥 Host Group Management
- `hostgroup_get` - Retrieve host groups
- `hostgroup_create` - Create new host groups
- `hostgroup_update` - Modify existing host groups
- `hostgroup_delete` - Remove host groups

### 📊 Item Management
- `item_get` - Retrieve monitoring items with filtering
- `item_create` - Create new monitoring items
- `item_update` - Update existing items
- `item_delete` - Remove monitoring items

### ⚠️ Trigger Management
- `trigger_get` - Retrieve triggers and alerts
- `trigger_create` - Create new triggers
- `trigger_update` - Modify existing triggers
- `trigger_delete` - Remove triggers

### 📋 Template Management
- `template_get` - Retrieve monitoring templates
- `template_create` - Create new templates
- `template_update` - Update existing templates
- `template_delete` - Remove templates

### 🚨 Problem & Event Management
- `problem_get` - Retrieve current problems and issues
- `event_get` - Get historical events
- `event_acknowledge` - Acknowledge events and problems

### 📈 Data Retrieval
- `history_get` - Access historical monitoring data
- `trend_get` - Retrieve trend data and statistics

### 👤 User Management
- `user_get` - Retrieve user accounts
- `user_create` - Create new users
- `user_update` - Update user information
- `user_delete` - Remove user accounts

### 🔗 Proxy Management
- `proxy_get` - Retrieve Zabbix proxies with filtering
- `proxy_create` - Create new proxies
- `proxy_update` - Update existing proxies
- `proxy_delete` - Remove proxies

### 🔧 Maintenance Management
- `maintenance_get` - Retrieve maintenance periods
- `maintenance_create` - Schedule maintenance windows
- `maintenance_update` - Modify maintenance periods
- `maintenance_delete` - Remove maintenance schedules

### 📊 Additional Features
- `graph_get` - Retrieve graph configurations
- `discoveryrule_get` - Get discovery rules
- `itemprototype_get` - Retrieve item prototypes
- `configuration_export` - Export Zabbix configurations
- `configuration_import` - Import configurations
- `apiinfo_version` - Get API version information

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Access to a Zabbix server with API enabled

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mpeirone/zabbix-mcp-server.git
   cd zabbix-mcp-server
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   cp config/.env.example .env
   # Edit .env with your Zabbix server details
   ```

4. **Test the installation:**
   ```bash
   # Test read-only server
   uv run python scripts/test_server.py --readonly

   # Test writable server
   uv run python scripts/test_server.py --writable
   ```

## Architecture (v2.0.0+)

Version 2.0.0 introduces a fully separated dual-server architecture for maximum security:

```
zabbix-mcp-server/
├── zabbix-mcp-readonly  [22 read-only tools]
│   └── Tools: *_get, apiinfo_version, auto_map_preview, configuration_export
│
└── zabbix-mcp-writable  [41 writable tools]
    └── Tools: *_create, *_update, *_delete, event_acknowledge, auto_map_update, configuration_import
```

**Key Benefits:**
- 🔒 **Complete Separation**: No overlap between read and write tools
- 🛡️ **Security**: Read-only server can never perform modifications
- ✨ **Simplicity**: Each server has its own independent configuration
- 📊 **Visibility**: Easy to monitor and audit each server separately

## Configuration

### Shared Configuration (Both Servers)

```env
# Required: Zabbix server URL
ZABBIX_URL=https://zabbix.example.com

# Authentication Method 1: API Token (Recommended)
ZABBIX_TOKEN=<your_api_token>

# Authentication Method 2: Username/Password (alternative)
# ZABBIX_USER=<username>
# ZABBIX_PASSWORD=<password>

# SSL Configuration
VERIFY_SSL=true
DEBUG=false
```

### Read-Only Server Configuration

```env
# READONLY_TRANSPORT: stdio or streamable-http
READONLY_TRANSPORT=stdio

# HTTP Transport Settings (only for streamable-http)
READONLY_HOST=0.0.0.0
READONLY_PORT=9002
READONLY_STATELESS_HTTP=false
READONLY_MOUNTPATH="/"
READONLY_AUTH_TYPE=no-auth
```

### Writable Server Configuration

```env
# WRITABLE_TRANSPORT: stdio or streamable-http
WRITABLE_TRANSPORT=stdio

# HTTP Transport Settings (only for streamable-http)
WRITABLE_HOST=0.0.0.0
WRITABLE_PORT=9003
WRITABLE_STATELESS_HTTP=false
WRITABLE_MOUNTPATH="/"
WRITABLE_AUTH_TYPE=no-auth
```

## Usage

### Running the Servers

**Using the startup script (recommended):**

```bash
# Start only the read-only server
uv run python scripts/start_server.py --readonly

# Start only the writable server
uv run python scripts/start_server.py --writable

# Start both servers in background
uv run python scripts/start_server.py --all
```

**Direct execution:**

```bash
# Read-only server
uv run zabbix-mcp-readonly

# Writable server
uv run zabbix-mcp-writable
```

### Transport Options

Both servers support two transport methods:

#### STDIO Transport (Default)
Standard input/output transport for MCP clients like Claude Desktop:
```env
READONLY_TRANSPORT=stdio
WRITABLE_TRANSPORT=stdio
```

#### HTTP Transport
HTTP-based transport for web integrations:
```env
READONLY_TRANSPORT=streamable-http
READONLY_HOST=0.0.0.0
READONLY_PORT=9002
READONLY_AUTH_TYPE=no-auth

WRITABLE_TRANSPORT=streamable-http
WRITABLE_HOST=0.0.0.0
WRITABLE_PORT=9003
WRITABLE_AUTH_TYPE=no-auth
```

**Note:** When using `streamable-http` transport, `AUTH_TYPE` must be set to `no-auth`.

### MCP Client Configuration

Configure your MCP client (Claude Desktop, etc.) to use both servers:

```json
{
  "mcpServers": {
    "zabbix-readonly": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/zabbix-mcp-server", "zabbix-mcp-readonly"],
      "env": {
        "ZABBIX_URL": "https://zabbix.example.com",
        "ZABBIX_TOKEN": "your-token-here"
      }
    },
    "zabbix-writable": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/zabbix-mcp-server", "zabbix-mcp-writable"],
      "env": {
        "ZABBIX_URL": "https://zabbix.example.com",
        "ZABBIX_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Docker Support

### Using Docker Compose

```bash
cp config/.env.example .env
# Edit .env with your settings
docker compose up -d
```

### Building Docker Image

```bash
docker build -t zabbix-mcp-server .
```

## Development

### Project Structure

```
zabbix-mcp-server/
├── src/zabbix_mcp_server/
│   ├── __init__.py              # Package initialization (v2.0.0)
│   ├── main_readonly.py         # Read-only server
│   ├── main_writable.py         # Writable-only server
│   ├── core/                    # Core functionality
│   │   ├── client.py            # Zabbix client
│   │   ├── config.py            # Configuration (separated)
│   │   ├── utils.py             # Utilities
│   │   └── tool_registry.py     # Unified tool registry (NEW!)
│   └── tools/                   # Tool modules (22+)
│       ├── host.py
│       ├── hostgroup.py
│       ├── item.py
│       └── ...
├── scripts/
│   ├── start_server.py          # Enhanced startup (--readonly/--writable/--all)
│   └── test_server.py           # Test suite
├── config/
│   ├── .env.example             # v2.0.0 config template
│   └── mcp.json                 # MCP config example
├── pyproject.toml               # Project configuration (v2.0.0)
├── docker-compose.yml
├── CHANGELOG.md                 # Version history
└── README.md                    # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Running Tests

```bash
# Test read-only server
uv run python scripts/test_server.py --readonly

# Test writable server
uv run python scripts/test_server.py --writable
```

## Error Handling

- ✅ Authentication errors clearly reported
- 🔒 Write operations only available on writable server
- ✔️ Invalid parameters validated
- 🌐 Network and API errors properly formatted
- 📝 Detailed logging for troubleshooting

## Security Considerations

- 🔑 Use API tokens instead of username/password
- 🔒 Use the read-only server for monitoring/dashboard integrations
- 🛡️ Only use the writable server when modifications are actually needed
- 🔐 Secure your environment variables
- 🔄 Use HTTPS for Zabbix connections
- 🔄 Regularly rotate API tokens

## Troubleshooting

**Connection Failed:** Verify `ZABBIX_URL`, check credentials, ensure Zabbix API is enabled.

**Tool Not Found:** Run `uv sync`, verify Python 3.10+.

**Debug Mode:** Set `DEBUG=1` for detailed logging.

**Port Conflicts:** Change `READONLY_PORT` or `WRITABLE_PORT` in .env.

## Dependencies

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [python-zabbix-utils](https://github.com/zabbix/python-zabbix-utils) - Official Zabbix library

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Zabbix](https://www.zabbix.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)

## Support

- 📖 [Documentation](README.md)
- 🐛 [Issue Tracker](https://github.com/mpeirone/zabbix-mcp-server/issues)
- 💬 [Discussions](https://github.com/mpeirone/zabbix-mcp-server/discussions)

---

**Made with ❤️ for the Zabbix and MCP communities**

**Version 2.0.0 - Fully Separated Dual-Server Architecture**
