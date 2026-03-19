# Arquitetura Alvo

## Objetivo

Organizar o compilador com separacao clara de responsabilidades, seguindo principios da Zen of Python:

- Explicito e melhor que implicito.
- Simples e melhor que complexo.
- Estruturas claras e previsiveis para manutencao.

## Camadas propostas

### Domain (nucleo lexico)

Responsavel por regras da linguagem e estruturas centrais.

Componentes esperados:

- `token.py` (modelo de token)
- `tokentype.py` (enum e mapas)
- `automato.py` (AFD e transicoes)
- `lexer.py` (analise lexico)

### Application

Orquestra casos de uso da analise, sem acoplamento com IO de baixo nivel.

Componentes esperados:

- `application/services/lexical_analysis_service.py`
- Contratos de entrada e saida da analise

### Interface (CLI)

Camada de entrada para usuario final e automacao.

Componentes esperados:

- `main.py` ou `cli.py`
- parse de argumentos
- escolha de formato de saida (texto/json)

### Infrastructure

Implementacoes de IO e utilitarios tecnicos.

Componentes esperados:

- leitura de arquivo
- escrita de relatorio de tokens
- logging/configuracao

## Principios de projeto

- Modulos pequenos e coesos.
- Dependencia apontando para dentro (interface -> application -> domain).
- Erros com mensagens claras e contexto de linha/coluna.
- Testabilidade por design (funcoes puras quando possivel).

## Estado atual vs alvo

| Item | Estado atual | Estado alvo |
|---|---|---|
| Domain | Parcial | Completo |
| Application | Estrutura vazia | Casos de uso implementados |
| Interface | Nao iniciado | CLI funcional |
| Infrastructure | Nao iniciado | IO/log/config isolados |
| Testes | Nao iniciado | Unitario + Integracao |
