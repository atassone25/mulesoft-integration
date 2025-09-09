import os
import json
import aiohttp
from typing import Dict, Any, Optional, Tuple
from teams_agent.utils import extract_cnpj
from teams_agent.a2a_fixtures import DISAMBIGUATION_TEXT, FINAL_HISTORY_TEXT


A2A_ENDPOINT = os.getenv("A2A_ENDPOINT", "https://agentforce.example.com/a2a/jsonrpc")
A2A_AUTH_TOKEN = os.getenv("A2A_AUTH_TOKEN", "MOCK_TOKEN")
A2A_MODE = os.getenv("A2A_MODE", "mock").lower()

def a2a_message_send_payload(
    skill: str,
    input_obj: Dict[str, Any],
    accept: Tuple[str, ...] = ("text/plain", "application/json"),
    user_text: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": "req-001",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {"kind": "text", "text": user_text or "Solicitar histórico de cliente"},
                    {
                        "kind": "data",
                        "data": {"skill": skill, "input": input_obj},
                        "metadata": {"mimeType": "application/json"},
                    },
                ],
            },
            "configuration": {"acceptedOutputModes": list(accept), "historyLength": 0},
        },
    }

class A2ABackend:
    async def message_send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class HttpBackend(A2ABackend):
    def __init__(self, endpoint: str, token: str):
        self.endpoint = endpoint
        self.token = token

    async def message_send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

# --- Fixtures for mock mode are imported from teams_agent.a2a_fixtures ---

class MockBackend(A2ABackend):
    async def message_send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        parts = payload.get("params", {}).get("message", {}).get("parts", [])
        input_obj = {}
        text_part = ""
        for p in parts:
            if p.get("kind") == "data":
                input_obj = p.get("data", {}).get("input", {}) or {}
            if p.get("kind") == "text":
                text_part = p.get("text") or text_part

        cnpj_from_text = extract_cnpj(text_part) if text_part else None
        cnpj = input_obj.get("cnpj") or input_obj.get("client_id") or cnpj_from_text

        text_out = DISAMBIGUATION_TEXT
        if (cnpj and "12.345.678/0001-90" in str(cnpj)) or ("NIMBUS EDITORA" in json.dumps(input_obj).upper()):
            text_out = FINAL_HISTORY_TEXT

        return {
            "jsonrpc": "2.0",
            "id": payload.get("id", "req-001"),
            "result": {
                "message": {"role": "assistant", "parts": [{"kind": "text", "text": text_out}]}
            },
        }

def _build_backend() -> A2ABackend:
    if A2A_MODE == "http":
        return HttpBackend(A2A_ENDPOINT, A2A_AUTH_TOKEN)
    return MockBackend()

class A2AClient:
    def __init__(self, backend: Optional[A2ABackend] = None):
        self.backend = backend or _build_backend()

    async def get_client_history(
        self,
        client_id: Optional[str] = None,
        cnpj: Optional[str] = None,
        since: Optional[str] = None,
        user_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        input_obj: Dict[str, Any] = {}
        if client_id:
            input_obj["client_id"] = client_id
        if cnpj:
            input_obj["cnpj"] = cnpj
        if since:
            input_obj["since"] = since

        payload = a2a_message_send_payload(
            skill="get_client_history",
            input_obj=input_obj,
            accept=("text/plain", "application/json"),
            user_text=user_text or "Obter histórico do cliente",
        )
        return await self.backend.message_send(payload)
