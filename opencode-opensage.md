# OpenCode + OpenSage Integration

Combine OpenCode's TUI with OpenSage's memory system.

## Quick Start

### 1. Start Neo4j (if not running)
```bash
brew services start neo4j
```

### 2. Start OpenSage Memory API
```bash
cd /Users/ghostgear/opensage
source .venv/bin/activate
python opensage_api.py &
```

### 3. Use in OpenCode
```bash
# Store memory
!curl "http://localhost:5555/remember?key=today&value=Working on auth API"

# Recall memory  
!curl "http://localhost:5555/recall?key=today"

# List all
!curl "http://localhost:5555/list"

# Search
!curl "http://localhost:5555/search?q=auth"
```

## Architecture

```
┌─────────────┐     HTTP      ┌─────────────┐
│  OpenCode   │ ───────────►  │ OpenSage    │
│  (Frontend) │               │ API Server  │
└─────────────┘               └──────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │   Neo4j     │
                              │  (Memory)   │
                              └─────────────┘
```

## OpenCode Models (Free)

OpenCode has built-in free models that work well:
- `opencode/mimo-v2-pro-free`
- `opencode/minimax-m2.5-free`
- `opencode/nemotron-3-super-free`
- `opencode/gpt-5-nano`

## OpenSage Models

OpenSage supports litellm-compatible models. Config files:
- `/Users/ghostgear/opensage/config-grok.toml` - Grok API
- `/Users/ghostgear/opensage/config-minimax.toml` - MiniMax via OpenRouter
- `/Users/ghostgear/opensage/config-opencode.toml` - OpenCode models

## Files Reference

| File | Description |
|------|-------------|
| `opensage_api.py` | HTTP API server for memory |
| `opensage_mcp_server.py` | MCP server (not currently used) |
| `opensage_memory.py` | CLI memory tool |
| `config-*.toml` | Model configurations |

## Neo4j Credentials

- URL: bolt://127.0.0.1:7687
- User: neo4j
- Password: callgraphn4j!
