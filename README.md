# OpenCode + OpenSage Integration

One command to start everything: `opensage-start`

## Quick Start

```bash
# One command to start all services
opensage-start

# Or manually:
./start_opencode_opensage.sh
```

This starts:
- Neo4j (graph database)
- Memory API (port 5555)
- Dynamic LLM Bridge (port 5557)

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
echo "opencode/gpt-5-nano" > ~/.opencode/current_model
```

### Method 2: Via opencode command (RECOMMENDED)
```bash
opencode --model opencode/gpt-5-nano --version
# or any opencode command with --model flag
```

Both OpenCode and OpenSage will use the new model automatically.

## Usage

### Memory
```bash
curl "http://localhost:5555/remember?key=notes&value=My notes"
curl "http://localhost:5555/recall?key=notes"
curl "http://localhost:5555/list"
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
| `start_opencode_opensage.sh` | One-command startup script |
| `opensage_api.py` | Memory API |
| `opencode_dynamic_bridge.py` | LLM bridge |
| `~/.opencode/bin/opencode` | Wrapper that updates model file when using `--model` |

See `opencode-opensage.md` for complete documentation.
