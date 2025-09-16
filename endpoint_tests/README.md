# Endpoint Tests

This directory contains test scripts for the Salesforce A2A agent endpoints.

## Running Tests

### Individual Tests

- **Purchase History**: `poetry run python endpoint_tests/historico_test.py`
- **Product Search**: `poetry run python endpoint_tests/buscar_produto_test.py`
- **Opportunities**: `poetry run python endpoint_tests/oportunidades_test.py`

### Test Files

- `historico_test.py` - Tests purchase history and lost opportunities functionality
- `buscar_produto_test.py` - Tests product search functionality  
- `oportunidades_test.py` - Tests opportunity management functionality

## Environment Variables

All test files now read configuration from environment variables instead of hardcoded values:

- `SALESFORCE_A2A_AGENT_BUSCAR_HISTORICO` - URL for history search endpoint
- `SALESFORCE_A2A_AGENT_BUSCAR_PRODUTO` - URL for product search endpoint
- `SALESFORCE_A2A_AGENT_OPORTUNIDADES` - URL for opportunities endpoint
- `A2A_AUTH_USERNAME` - Authentication username
- `A2A_AUTH_PASSWORD` - Authentication password

## Security

The URLs and credentials are no longer hardcoded in the test files. Make sure your `.env` file is properly configured and never commit it to version control.
