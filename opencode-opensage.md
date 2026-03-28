# OpenCode + OpenSage Integration (opencodesage)

Complete integration: OpenCode (frontend) ↔ OpenSage (backend with Neo4j memory) in a portable folder.

## Architecture

```
┌─────────────┐     HTTP API      ┌──────────────────┐
│  OpenCode   │ ◄──────────────► │  OpenSage        │
│  (Frontend) │    Dynamic        │  (Backend)       │
│             │    Bridge         │                  │
│  - TUI      │    port 5557     │  - Neo4j Memory  │
│  - Models   │                  │  - Agents        │
└─────────────┘                  │  - Tools         │
                                 └──────────────────┘
                                         │
                                         ▼
                                 ┌──────────────────┐
                                 │  Neo4j           │
                                 │  (Graph DB)      │
                                 └──────────────────┘
```

## Quick Start

```bash
# One command to start all services
./start_opencodesage.sh

# This starts:
# - Neo4j (graph database)
# - Memory API (port 5555)
# - Dynamic LLM Bridge (port 5557)
```

## Default Model

**`opencode/minimax-m2.5-free`**

## Available Models

- `opencode/minimax-m2.5-free` (default)
- `opencode/mimo-v2-pro-free`
- `opencode/nemotron-3-super-free`
- `opencode/gpt-5-nano`

## Switch Model

### Method 1: Direct file edit
```bash
echo "opencode/gpt-5-nano" > .opencode/current_model
```

### Method 2: Via opencode command (RECOMMENDED)
```bash
bin/opencode --model opencode/gpt-5-nano --version
# or any opencode command with --model flag
```

Both OpenCode and OpenSage will use the new model automatically.

## Usage

### Memory API
```bash
curl "http://localhost:5555/remember?key=notes&value=My notes"
curl "http://localhost:5555/recall?key=notes"
curl "http://localhost:5555/list"
curl "http://localhost:5555/search?q=project"
```

### LLM Bridge
```bash
curl -X POST http://localhost:5557/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## Services

| Service | Port | URL |
|---------|------|-----|
| Neo4j | 7474 | http://localhost:7474 |
| Memory API | 5555 | http://localhost:5555 |
| LLM Bridge | 5557 | http://localhost:5557 |

## Files

| File | Description |
|------|-------------|
| `start_opencodesage.sh` | One-command startup script |
| `opensage_api.py` | Memory API |
| `opencode_dynamic_bridge.py` | LLM bridge |
| `bin/opencode` | Wrapper that updates model file when using `--model` |
| `.opencode/current_model` | Shared model file |
| `.env.example` | Template for environment variables |

## Environment Variables (optional)

Create a `.env` file (copy from `.env.example`) to set:
- `NEO4J_PASSWORD` (required)
- `NEO4J_URI` (default: bolt://127.0.0.1:7687)
- `NEO4J_USER` (default: neo4j)
- `OPENSAGE_API_PORT` (default: 5555)
- `OPENCODE_BRIDGE_PORT` (default: 5557)
- `OPENCODE_HOME` (default: ~/.opencode)
- `OPENCODE_CMD` (default: opencode on PATH)

## Design Highlights

- ✅ Model synchronization: Changing model via `bin/opencode --model` updates the shared file, which the LLM bridge reads automatically
- ✅ Persistent memory: Neo4j stores memories across sessions
- ✅ Portability: Everything self-contained in the `opencodesage` folder
- ✅ One-command startup: `start_opencodesage.sh` handles Neo4j, Memory API, and LLM Bridge
- ✅ Secure: Neo4j password required via environment (not hardcoded)

## Test Results

- Memory (Neo4j): ✓ PASS
- Docker Sandbox: ✓ PASS  
- OpenSage Agent: ✓ PASS
- Bash Tool: ✓ PASS
- Dynamic Sub-agents: ✓ PASS
- LLM Models (1655): ✓ PASS
- Web Search: ✓ PASS
- Agent Ensemble: ✓ PASS
- Neo4j Tools: ✓ PASS
- Coding Tasks: ✓ PASS

## See Also

- `opensage-memory-api.md` - Memory API reference