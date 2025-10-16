# Team Agent A2A

Refactored agentic system for contextualized offer generation using the Agent-to-Agent (A2A) protocol.

## Architecture

```
Data AI Agent (A2A Server)          Product Search Agent (A2A Server)
    Port: 10001                            Port: 10002
    │                                      │
    └────────────── A2A Protocol ──────────┘
                      │
                Orchestrator
              (ADK Web Interface)
```

## Components

### A2A Servers

1. **Data AI Agent** (`data_ai_agent/`)
   - Searches B2B products and offers from Vertex AI Search datastore
   - Port: 10001
   - Endpoint: `http://localhost:10001`

2. **Product Search Agent** (`product_search_agent/`)
   - Searches and verifies products in Salesforce using buscar_produto
   - Port: 10002
   - Endpoint: `http://localhost:10002`

### Orchestrator

- **Location**: Original `teams_agent/` project (external to this directory)
- **Interface**: ADK Web UI at `http://localhost:8000`
- **Communication**: Connects to A2A servers via A2A protocol

## Quick Start

See `HOWTO.md` for detailed manual commands.

### Run in 3 Terminals

**Terminal 1 - Data AI Agent:**
```bash
cd team_agent_a2a && source ../.venv/bin/activate
python -m data_ai_agent.a2a_server
```

**Terminal 2 - Product Search Agent:**
```bash
cd team_agent_a2a && source ../.venv/bin/activate
python -m product_search_agent.a2a_server
```

**Terminal 3 - Orchestrator:**
```bash
cd team_agent_a2a && source ../.venv/bin/activate
adk run web orchestrator
```

Then open browser to: `http://localhost:8000`

## Environment Configuration

Environment variables are loaded from the parent `mulesoft-integration/.env` file.

Key variables:
- `GOOGLE_CLOUD_PROJECT` - Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION` - Google Cloud region (e.g., us-central1)
- `GOOGLE_GENAI_USE_VERTEXAI` - Set to `TRUE` to use Vertex AI
- `ADK_MODEL` - Model name (e.g., gemini-2.5-flash)
- `AGENT_ENGINE_ID` - Vertex AI Search engine ID

## Project Structure

```
team_agent_a2a/
├── data_ai_agent/
│   ├── __init__.py
│   ├── agent.py              # ADK agent configuration
│   ├── agent_executor.py     # A2A request executor
│   ├── a2a_server.py         # A2A server with Starlette
│   ├── config.py             # Environment setup
│   └── tools.py              # vertex_search tool
├── product_search_agent/
│   ├── __init__.py
│   ├── agent.py              # ADK agent configuration
│   ├── agent_executor.py     # A2A request executor
│   ├── a2a_server.py         # A2A server with Starlette
│   ├── config.py             # Environment setup
│   └── tools.py              # buscar_produto tool
├── shared/
│   ├── status_manager.py     # A2A status updates
│   └── utils.py              # Common utilities
├── logs/                     # Server logs
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Key Features

- **A2A Protocol**: Full implementation of Agent-to-Agent streaming protocol
- **Vertex AI Integration**: Direct integration with Vertex AI Search
- **Salesforce Integration**: Product search and verification via Salesforce API
- **Streaming Responses**: Real-time event streaming from agents
- **Modular Architecture**: Clean separation between servers and orchestrator

## Management

### Stop Servers

```bash
lsof -ti:10001 | xargs kill -9  # Data AI Agent
lsof -ti:10002 | xargs kill -9  # Product Search Agent
```

### Clean Up

```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## References

- [A2A Protocol Documentation](https://a2a-protocol.org/latest/)
- [A2A Python SDK](https://github.com/a2aproject/a2a-python)
- [Google ADK Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder)

## Notes

- Both A2A servers must be running before starting the orchestrator
- The orchestrator discovers agents via their agent card endpoints
- All agents use Vertex AI models configured via environment variables
- Logs are written to the `logs/` directory for debugging

