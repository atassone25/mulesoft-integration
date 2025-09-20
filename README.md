# Mulesoft Accenture - A2A Integration

This project contains agents for handling Mulesoft and Accenture related tasks, now upgraded to use the Agent-to-Agent (A2A) protocol for communication with Salesforce agents.

## Features

- **A2A Protocol Integration**: Communicates with Salesforce agents using the standardized A2A protocol
- **Multi-agent Architecture**: Coordinator agent with specialized sub-agents
- **Salesforce Integration**: Tools for client history, product search, and opportunity management
- **Memory Service Support**: Long-term memory capabilities with Vertex AI integration

## Installation

```bash
poetry install
```

## A2A Configuration

1. Copy the A2A configuration example:
```bash
cp a2a_config.example .env
```

2. Configure your A2A Salesforce agent URIs in `.env`:
```bash
SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO=https://your-salesforce-a2a-agent.com/buscar_historico
SALESFORCE_A2A_AGENT_BUSCAR_PRODUTO=https://your-salesforce-a2a-agent.com/buscar_produto
SALESFORCE_A2A_AGENT_OPORTUNIDADES=https://your-salesforce-a2a-agent.com/oportunidades
```

## Usage

### Basic Usage
```bash
poetry run adk web
```

### Debug Mode
```bash
poetry run adk web -v
```

### With Memory Service (Long-term Memory)
```bash
poetry run adk web -v --memory_service_uri="agentengine://4388410391198171136"
```

## Architecture

### Multi-Agent System
- **Orchestrator Agent**: Main coordinator that presents services and routes requests to specialized agents
- **Contextualized Offer Agent**: Generates personalized business offers requiring client name, strategy, and investment amount
- **Opportunity Agent**: Handles opportunity registration and management in Salesforce

### Available Services
1. **Service1**: General consultation and information services
2. **Register Opportunity**: Register new business opportunities in the system
3. **Contextualized Offer**: Generate personalized business offers based on client data and strategy

### Tools
- **A2A Salesforce Tools**: 
  - `buscar_produto`: Search and verify products via A2A protocol (used by Contextualized Offer Agent)
  - `oportunidades`: Manage opportunities via A2A protocol (used by Opportunity Agent)
- **Data and AI Tool**:
  - `data_and_ai`: Returns available Globo products (Globo Reporter, Jornal Nacional, Futebol)

## Migration from Legacy API

The project has been upgraded from direct Salesforce API calls to A2A protocol communication. The legacy API configuration is still documented in `a2a_config.example` for reference but is no longer used.

See the teams_agent directory for the main agent implementation and sub-agents.
