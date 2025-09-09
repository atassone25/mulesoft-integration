"""Mock fixtures for A2A client responses.

This module centralizes hardcoded mock texts used by the MockBackend in
`teams_agent.a2a_client`. Keeping them here makes it easier to maintain
and reuse across tests.
"""

# Text shown when only a client name is provided and multiple matches are found.
DISAMBIGUATION_TEXT = """Encontrei vários clientes com o nome "ACME SCHOOLS". Por favor, escolha o cliente correto com base na razão social, cidade ou CNPJ:

1. NIMBUS EDITORA E PAPELARIA LTDA
   - Nome: ACME SCHOOLS
   - CNPJ: 12.345.678/0001-90
   - Localização: São Paulo
   - Atividade Econômica: Edição integrada à impressão de livros
2. FUNDACAO ALPHA EDUCACAO.
   - Nome: FUNDACAO ACME
   - CNPJ: 98.765.432/0001-10
   - Localização: São Paulo
   - Atividade Econômica: Ensino de idiomas
3. BETA E GAMA EDITORA LTDA
   - Nome: ACME SCHOOLS
   - CNPJ: 23.456.789/0001-01
   - Localização: São Paulo
   - Atividade Econômica: Edição integrada à impressão de livros
4. ACME SCHOOLS LIMITED
   - Nome: ESCOLAS ACME
   - CNPJ: 45.678.123/0019-45
   - Localização: Curitiba
   - Atividade Econômica: Ensino de idiomas
5. ACME SCHOOLS LIMITED
   - Nome: ESCOLAS ACME
   - CNPJ: 45.678.123/0003-21
   - Localização: São Paulo
   - Atividade Econômica: Outras atividades de ensino não especificadas anteriormente
6. FUNDACAO ALPHA EDUCACAO
   - Nome: ACME SCHOOLS
   - CNPJ: 56.789.012/0025-55
   - Localização: Curitiba
7. FUNDACAO ALPHA EDUCACAO - DIV.PBF
   - Nome: ACME SCHOOLS
   - CNPJ: 56.789.012/0028-10
   - Localização: São Paulo

Por favor, me informe qual cliente você deseja consultar.
"""

# Text shown when a unique client (by CNPJ or specific identifier) is identified.
FINAL_HISTORY_TEXT = """Aqui está o histórico de compras do cliente NIMBUS EDITORA E PAPELARIA LTDA (ACME SCHOOLS):

Oportunidade: ACME 2019
- Data de Fechamento: 2018-12-15
- Status: Fechada Ganha
- Nenhuma ordem de mercado foi registrada para esta oportunidade.

Oportunidade: ACME SHOW - KARAOKE 07/02
- Período de Exibição: 2021-03-07 até 2021-03-07
- Data de Fechamento: 2020-11-27
- Status: Fechada Ganha
   - Ordem de Mercado: MO-26180
      - Status Comercial: Em entrega
      - Linha: MOL-032024
         - Período: 2021-03-07 até 2021-03-07
         - Detalhe:
            - Programa: RSHW - REALITY SHOW BRASIL
            - Descrição: TV LINEAR on TV Canal 1 - Air | RSHW - REALITY SHOW BRASIL / SPOT view @ 508000

Oportunidade: ACME TALENT KIDS
- Período de Exibição: 2021-07-19 até 2021-08-06
- Data de Fechamento: 2021-06-14
- Status: Fechada Ganha
- Nenhuma ordem de mercado foi registrada para esta oportunidade.

Oportunidade: ACME TALENT KIDS (KIDS TV)
- Período de Exibição: 2021-08-01 até 2021-08-06
- Data de Fechamento: 2021-06-23
- Status: Fechada Ganha
- Nenhuma ordem de mercado foi registrada para esta oportunidade.

Oportunidade: ACME | CALD + MAVO 1 TRIMESTRE 22
- Período de Exibição: 2022-01-29 até 2022-02-05
- Data de Fechamento: 2021-12-10
- Status: Fechada Ganha
- Nenhuma ordem de mercado foi registrada para esta oportunidade.

Oportunidade: ACME_ COTA ELIMINAÇÃO SHOW_JANEIRO
- Período de Exibição: 2022-12-22 até 2023-01-31
- Data de Fechamento: 2022-12-22
- Status: Fechada Ganha
- Nenhuma ordem de mercado foi registrada para esta oportunidade.

Oportunidade: CONTEÚDO | ACME | MANHÃ SHOW | FEVEREIRO 23
- Período de Exibição: 2023-02-08 até 2023-02-09
- Data de Fechamento: 2022-12-21
- Status: Fechada Ganha
- Nenhuma ordem de mercado foi registrada para esta oportunidade.

Oportunidade: CONTEÚDO | ACME | 1º semestre 2024 | MAVO
- Período de Exibição: 2024-02-01 até 2024-02-10
- Data de Fechamento: 2023-11-15
- Status: Fechada Ganha
- Nenhuma ordem de mercado foi registrada para esta oportunidade.

Oportunidade: ACME :: AÇÃO ALTAS :: FEV/24
- Período de Exibição: 2024-02-24 até 2024-02-24
- Data de Fechamento: 2024-02-20
- Status: Fechada Ganha
- Nenhuma ordem de mercado foi registrada para esta oportunidade.
"""

__all__ = [
    "DISAMBIGUATION_TEXT",
    "FINAL_HISTORY_TEXT",
]
