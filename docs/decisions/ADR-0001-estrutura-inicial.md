# ADR 0001 - Estrutura Inicial do Projeto

## Status

Aceito

## Contexto

O projeto precisava sair de um formato inicial de experimento para uma base mais proxima de padrao comercial, com organizacao previsivel e documentacao minima para evolucao incremental.

## Decisao

Adotar estrutura com separacao por responsabilidades e pasta de documentacao viva:

- `.github/workflows` para governanca de CI.
- `configs` para configuracoes do projeto.
- `docs` para status, arquitetura, roadmap e ADRs.
- `scripts` para automacoes locais.
- `src/mineres_compilador` como pacote principal.

Tambem foi definido que `token.py` e `tokentype.py` seriam o primeiro contrato estavel do nucleo lexico.

## Consequencias

Positivas:

- Base pronta para crescimento sem acoplamento desnecessario.
- Melhor rastreabilidade de decisoes e progresso.
- Facilita entrada de novos colaboradores.

Custos:

- Mais arquivos de manutencao desde o inicio.
- Exige disciplina para manter docs sincronizada com codigo.

## Proximos passos

- Implementar automato e lexer no pacote principal.
- Fechar contrato da CLI.
- Ativar CI e testes automatizados.
