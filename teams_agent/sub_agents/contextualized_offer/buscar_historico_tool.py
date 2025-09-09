from google.adk.tools import FunctionTool
from teams_agent.a2a_client import A2AClient
from typing import Any, Dict


async def buscar_historico(query: str) -> str:
    text = (query or "").strip()
    if not text:
        return "Informe o nome do cliente ou CNPJ."

    client = A2AClient()
    resp = await client.get_client_history(user_text=text)

    result = resp.get("result", {})
    message = result.get("message")
    if message:
        parts = message.get("parts", [])
        text_out = next((p.get("text") for p in parts if p.get("kind") == "text"), "")
        return text_out or ""

    # Fallback: return raw JSON-RPC result stringified
    return str(resp)

# Expose the tool instance with a clear schema so the agent passes a string
buscar_historico_tool_instance = FunctionTool(func=buscar_historico)
