# Mulesoft Accenture

This project contains agents for handling Mulesoft and Accenture related tasks.

## Installation

```bash
poetry install
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

See the teams_agent directory for the main agent implementation and sub-agents.
