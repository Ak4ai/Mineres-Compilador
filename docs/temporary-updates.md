---
title: Documentacao Temporaria
nav_order: 6
---

# Documentacao Temporaria

Este espaco e usado para registrar mudancas pequenas, incrementais e de baixo impacto.

## Regra de uso

- Mudanca pequena: registrar aqui com data, escopo e impacto.
- Mudanca final/consolidada: mover para a documentacao oficial (status, arquitetura, roadmap ou ADR).

## Template de registro rapido

Copie e preencha o bloco abaixo para cada ajuste pequeno:

### YYYY-MM-DD - Titulo curto da mudanca

- Tipo: pequena
- Arquivos alterados: caminho/do/arquivo
- Resumo tecnico: o que mudou em 1 a 3 linhas
- Impacto: baixo/medio/alto
- Acao futura: manter aqui ou promover para doc oficial

---

## Entradas

### 2026-03-29 - Documentacao sincronizada com estado real do lexer

- Tipo: pequena
- Arquivos alterados: docs/status.md, docs/roadmap.md, docs/tutorial.md
- Resumo tecnico: status atualizado com `lexer.py` e testes do lexer concluidos; roadmap marcou itens de fase 2 e testes iniciais como feitos; tutorial ajustado para indicar Fase 3 (Main/CLI) e expansao de testes como proximos passos.
- Impacto: medio
- Acao futura: promover para documentacao oficial final apos conclusao da CLI e padronizacao de erro lexico/EOF.

### 2026-03-24 - Etapa 1 do nucleo lexico concluida e documentacao consolidada

- Tipo: pequena
- Arquivos alterados: src/mineres_compilador/automato.py, mineires_token.py, docs/status.md, docs/roadmap.md, README.md
- Resumo tecnico: conflito de import com modulo padrao `token` corrigido via renomeacao para `mineires_token.py`; automato implementado e validado com casos `certin`, `2` e `@@@`; status e roadmap atualizados removendo pendencia de automato.
- Impacto: medio
- Acao futura: promover para documentacao oficial quando lexer e CLI forem concluídos.

### 2026-03-19 - Padrao de atualizacao de documentacao definido

- Tipo: pequena
- Arquivos alterados: docs/temporary-updates.md, docs/index.md, docs/README.md, README.md
- Resumo tecnico: definido fluxo para registrar mudancas pequenas nesta pagina e promover mudancas finais para a documentacao oficial.
- Impacto: medio
- Acao futura: manter ativo e revisar a cada marco de release.
