# Datastore Test Agent

A simple ADK agent for testing Vertex AI Search connectivity to the ma014-datastore-oferta_b2b datastore.

## Overview

This agent is designed to test the connection to the Vertex AI Search datastore:
- **Datastore ID**: `projects/205867137421/locations/us/collections/default_collection/dataStores/ma014-datastore-oferta_b2b`
- **Purpose**: Test connectivity and search functionality
- **Tools**: Vertex AI Search (`search_b2b_offers`)

## Features

- ✅ Simple agent with single Vertex AI Search tool
- ✅ Google Cloud Trace enabled for observability
- ✅ Same environment variables as teams_agent
- ✅ Local testing capabilities
- ✅ Deployment to Agent Engine

## Files

- `agent.py` - Main agent implementation with Vertex AI Search tool
- `deploy.py` - Deployment script for Agent Engine
- `test_local.py` - Local testing script
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Usage

### 1. Local Testing (Optional)

Test the agent locally before deployment:

```bash
cd /home/emmanueltassone/globo/mulesoft-integration
python datastore_agent/test_local.py
```

### 2. Deploy to Agent Engine

Deploy the agent to Google Cloud Agent Engine:

```bash
cd /home/emmanueltassone/globo/mulesoft-integration
python datastore_agent/deploy.py
```

The deployment will:
- Initialize Vertex AI
- Create ADK App with Cloud Trace enabled
- Deploy to Agent Engine
- Run initial connectivity test

### 3. Test Queries

Once deployed, you can test with queries like:
- "Search for B2B offers in the datastore"
- "What products are available?"
- "Find information about business services"
- "Search for pricing information"

## Configuration

The agent uses the same environment variables as the teams_agent:

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Optional
MODEL=gemini-2.0-flash
ADK_ENV=dev
USE_VERTEX_MEMORY=FALSE

# A2A and Salesforce configs (available but not used by this agent)
SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO=...
SALESFORCE_A2A_AGENT_BUSCAR_PRODUTO=...
# ... etc
```

## Monitoring

- **Cloud Trace**: Enabled automatically for observability
- **Logs**: Available in Google Cloud Logging
- **Agent Engine Console**: Monitor via Vertex AI console

## Architecture

```
Datastore Agent
├── Vertex AI Search Tool
│   └── ma014-datastore-oferta_b2b
├── Google Cloud Trace
└── Agent Engine Runtime
```

## Differences from teams_agent

- **Simplified**: Single tool instead of multi-agent system
- **Focused**: Only datastore connectivity testing
- **No Sub-agents**: Direct tool integration
- **No Memory**: Disabled for simplicity
- **Same Environment**: Uses same env vars for consistency

## Troubleshooting

Common issues:

1. **Datastore not found**: Verify datastore ID and permissions
2. **Search fails**: Check Vertex AI Search API is enabled
3. **Deployment fails**: Verify project and location settings
4. **No results**: Datastore may be empty or query needs refinement

## Next Steps

After successful deployment and testing:

1. Verify datastore contains expected data
2. Test various search queries
3. Monitor performance in Cloud Trace
4. Integrate findings into larger system
5. Scale up to more complex use cases
