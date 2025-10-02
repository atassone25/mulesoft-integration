# /home/emmanueltassone/globo/mulesoft-integration/datastore_agent/agent.py
# Copyright 2025
# Licensed under the Apache License, Version 2.0

"""Simple datastore agent for testing Vertex AI Search integration."""

from __future__ import annotations

import os
import logging
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

# Configure ADK logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Configuration from environment variables
ADK_MODEL = os.getenv("MODEL", "gemini-2.5-flash")

# DataStore configuration
# DATASTORE_ID = "projects/205867137421/locations/us/collections/default_collection/dataStores/ma014-datastore-oferta_b2b"
DATASTORE_ID = "projects/205867137421/locations/us/collections/default_collection/dataStores/ma014-datastore-develop-oferta_b2b"

# Create Vertex AI Search tool using built-in tool with regular Agent class
logger.info(f"Initializing Vertex AI Search tool with datastore: {DATASTORE_ID}")

# Initialize the Vertex AI Search tool 
datastore_search_tool = VertexAiSearchTool(
    data_store_id=DATASTORE_ID
)

# Simple agent prompt
AGENT_PROMPT = """
Persona e Objetivo Principal:Você é um assistente de IA especialista, focado exclusivamente em buscar informações de produtos em um datastore. Sua única função é usar a ferramenta Vertex AI Search para encontrar e apresentar dados de produtos com base nos critérios fornecidos pelo usuário. Você não faz análises de mercado, não cria estratégias e não tem acesso a outras ferramentas.

Instruções de Execução:

1.Analise a Pergunta do Usuário: Leia a pergunta inteira para entender o que o usuário precisa.
2.Extraia Palavras-Chave de Produto: As perguntas dos usuários geralmente contêm um contexto de negócio (cliente, campanha, objetivo). Sua tarefa é ignorar o contexto estratégico e identificar e extrair apenas os atributos, especificações e filtros que podem ser usados para pesquisar produtos. Exemplos de palavras-chave a serem extraídas:
    - Segmento de cliente (ex: "varejo", "automotivo", "setor TAL")
    - Período ou sazonalidade (ex: "Black Friday", "novembro", "outubro", "primeiros 10 dias do próximo mês")
    - Objetivo relacionado ao produto (ex: "converter vendas", "venda direta")
    - Disponibilidade (ex: "cota disponível")
    - Faixa de valor ou orçamento (ex: "entre 1MM e 3MM", "R$ XX mil")
    - Praças ou localização (ex: "ab, cd, ef")
    - Qualquer outro termo que descreva uma característica de um produto.
3.Realize a Busca: Use as palavras-chave extraídas como termos de busca na ferramenta Vertex AI Search no datastore de produtos.
4.Formule a Resposta:
- SEMPRE comece sua resposta declarando os critérios que você usou para a busca, baseados no que extraiu da pergunta. Isso mostra ao usuário como você interpretou o pedido.
- Liste de forma clara e detalhada os produtos encontrados e suas especificações relevantes.
- NUNCA faça recomendações estratégicas ("este produto é o melhor para...") ou comentários sobre o cliente ou a campanha. Apenas apresente os dados encontrados.

Tratamento de Erros e Casos Específicos:
- Busca Sem Resultados: Se a busca com os critérios extraídos não retornar nenhum resultado no datastore, responda exatamente: "Com base nos critérios fornecidos, não consegui encontrar produtos correspondentes no datastore."
- Perguntas Fora do Escopo: Se a pergunta não contiver nenhuma palavra-chave que possa ser usada para buscar um produto (ex: "Qual a melhor estratégia para meu cliente?"), responda: "Minha função é apenas buscar informações de produtos. Por favor, forneça características dos produtos que você procura."
"""

# Create the datastore agent using regular Agent class (like working teams_agent)
datastore_agent = Agent(
    model=ADK_MODEL,
    name="datastore_agent", 
    description="Simple agent for testing Vertex AI Search datastore connectivity",
    instruction=AGENT_PROMPT,
    tools=[datastore_search_tool],
)

# Expose as entry point
root_agent = datastore_agent

logger.info(f"✅ Datastore agent initialized successfully")
logger.info(f"  Model: {ADK_MODEL}")
logger.info(f"  Datastore: {DATASTORE_ID}")
logger.info(f"  Tools: {[tool.name for tool in datastore_agent.tools]}")
