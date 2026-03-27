# OpenCode + OpenSage Integration Skills

Skills for integrating OpenCode with OpenSage's Neo4j memory system.

## Skills

- **opencode-opensage.md** - Complete integration guide
- **opensage-memory-api.md** - Memory API reference  
- **opensage-memory.md** - Basic memory usage
- **opensage-local-setup.md** - Original OpenSage setup

## Quick Start

### 1. Start Neo4j
```bash
brew services start neo4j
```

### 2. Start Memory API
```bash
cd opensage
source .venv/bin/activate
python opensage_api.py
```

### 3. Use in OpenCode
```bash
!curl "http://localhost:5555/remember?key=notes&value=My notes"
!curl "http://localhost:5555/recall?key=notes"
```

## Files

| File | Description |
|------|-------------|
| `opensage_api.py` | HTTP API for Neo4j memory |
| `opensage_mcp_server.py` | MCP server |
| `opensage_memory.py` | CLI memory tool |
| `config-*.toml` | Model configs |
