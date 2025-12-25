# MCP Agent Base

A framework for building MCP-based agents.

## Installation

```bash
uv pip install -e /path/to/mcp-agent-base
```

## Configuration

Create a symlink to your .env file:

```bash
mkdir -p ~/.config/mcp-agent-base
ln -sf /path/to/your/.env ~/.config/mcp-agent-base/.env
```

Required environment variables:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`
- `GITHUB_TOKEN` or `GITHUB_PERSONAL_ACCESS_TOKEN`
