---
title: Estado Atual
nav_order: 2
---

# Estado Atual do Projeto

## O que foi feito

### Estrutura

- Criadas pastas de organizacao: `.github/workflows`, `configs`, `docs/decisions`, `scripts`, `src/mineres_compilador/application`.
- Projeto com layout inicial para evolucao em padrao comercial.

### Codigo ja implementado

- `mineires_token.py`
  - Classe `Token` com `@dataclass(slots=True, frozen=True)`.
  - Campos: `type`, `lexeme`, `line`, `column`.
  - Metodo `to_output_row()` para serializacao estavel em formato tabular.
- `tokentype.py`
  - `Enum TokenType` com tipos de token de controle, identificadores, literais, palavras reservadas, operadores e delimitadores.
  - Mapas lexicos: `KEYWORD_TOKENS`, `TYPE_TOKENS`, `BOOLEAN_TOKENS`, `WORD_OPERATOR_TOKENS`, `WORD_DELIMITER_TOKENS`, `ALL_WORD_TOKENS`.
- `src/mineres_compilador/automato.py`
  - Estruturas de estado e transicao implementadas (`EstadoTipo`, `Estado`, `Automato`).
  - Carregamento de AFD por arquivo (`carregar_do_arquivo`) com validacoes de integridade.
  - Reconhecimento greedy implementado (`reconhecer`) retornando `(aceito, token_type, comprimento)`.
  - Validado com casos: `certin`, `2`, `@@@`.

### Configuracao de repositorio

- `.gitattributes` com `* text=auto` para normalizacao de quebras de linha.

## O que ainda falta

- Implementar lexer no pacote principal.
- Criar ponto de entrada de aplicacao (CLI).
- Definir estrategia de tratamento de erro lexico.
- Criar testes unitarios e de integracao.
- Criar workflow de CI em `.github/workflows`.
- Completar README principal com guia de uso e contribuicao.

## Riscos atuais

- Ausencia de testes automatizados pode mascarar regressao.
- Sem CI, qualidade depende de execucao manual local.
- Contrato de entrada/saida ainda nao formalizado para uso externo.

## Definicao de pronto da fase atual

- `mineires_token.py` e `tokentype.py` mantidos como fonte unica de verdade de contrato lexico.
- `automato.py` implementado e validado com testes manuais de carga e reconhecimento.
- Documentacao minima de status estabelecida.
- Roadmap de implementacao definido e versionado.
