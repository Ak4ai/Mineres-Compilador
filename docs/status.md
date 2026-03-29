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
- `src/mineres_compilador/token.py` e `src/mineres_compilador/tokentype.py`
  - Modulos consolidados dentro do pacote principal para imports relativos estaveis.
  - `TokenType` e `ALL_WORD_TOKENS` usados diretamente pelo lexer do pacote.
- `src/mineres_compilador/lexer.py`
  - API implementada com `carregar_arquivo`, `carregar_string` e `analisar`.
  - Reconhecimento token a token com apoio do `Automato`.
  - Diferenciacao de `IDENTIFIER` para palavras reservadas via `ALL_WORD_TOKENS`.
  - Rastreamento de posicao (`line`, `column`) por token.
  - Fallback de erro lexico com `TokenType.ERROR` ao falhar reconhecimento.
- `testes_individuais/test_automato.py` e `testes_individuais/test_lexer.py`
  - Casos de validacao para automato e lexer passando localmente.
  - Testes com prints detalhados de debug para facilitar diagnostico.

### Configuracao de repositorio

- `.gitattributes` com `* text=auto` para normalizacao de quebras de linha.

## O que ainda falta

- Criar ponto de entrada de aplicacao (CLI/Main) no pacote principal.
- Definir contrato final de erro lexico para uso externo (ex.: excecao vs token de erro).
- Garantir e padronizar emissao de token `EOF` no fluxo final de tokenizacao.
- Expandir cobertura com testes de integracao orientados a CLI.
- Criar workflow de CI em `.github/workflows`.
- Completar README principal com guia de uso e contribuicao.

## Riscos atuais

- Sem CI, qualidade ainda depende de execucao manual local.
- Contrato de erro lexico e de `EOF` ainda pode divergir entre uso interno e CLI.
- Ausencia de CLI impede validacao ponta a ponta via linha de comando.

## Definicao de pronto da fase atual

- `mineires_token.py` e `tokentype.py` mantidos como fonte unica de verdade de contrato lexico.
- `automato.py` implementado e validado com testes manuais de carga e reconhecimento.
- `lexer.py` implementado e validado com `test_lexer.py`.
- Testes de automato e lexer executando com sucesso localmente.
- Documentacao minima de status estabelecida e sincronizada.
- Roadmap de implementacao definido e versionado.
