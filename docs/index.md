---
layout: default
title: Home
nav_order: 1
---

# Mineres-Compilador

Documentacao oficial do projeto, com foco em organizacao comercial, clareza tecnica e evolucao incremental.

<p>
  <img src="https://img.shields.io/badge/status-em%20evolucao-1f6feb" alt="status" />
  <img src="https://img.shields.io/badge/fase-aplicacao%20e%20CLI-0a7f5a" alt="fase" />
  <img src="https://img.shields.io/badge/progresso-65%25-f59e0b" alt="progresso" />
</p>

---

## Visao Geral

<table>
  <tr>
    <td><strong>Objetivo</strong></td>
    <td>Construir um compilador da linguagem Mineres com arquitetura limpa e padrao profissional.</td>
  </tr>
  <tr>
    <td><strong>Etapa Atual</strong></td>
    <td>Implementacao da camada de aplicacao e CLI.</td>
  </tr>
  <tr>
    <td><strong>Proxima Etapa</strong></td>
    <td>Criar CLI funcional com servico de analise lexica e suporte a saida JSON/texto.</td>
  </tr>
</table>

---

## Painel de Progresso

### Progresso Global

<progress value="65" max="100">65%</progress>

**65% concluido**

### Progresso por Fase

| Fase | Progresso | Status |
|---|---:|---|
| Fundacao | 90% | Quase completa |
| Nucleo Lexico | 85% | Quase completa |
| Aplicacao e CLI | 0% | Nao iniciado |
| Qualidade e Governanca | 20% | Em andamento |
| Release Inicial | 0% | Nao iniciado |

---

## Mapa Rapido

| Documento | Finalidade |
|---|---|
| [Estado Atual](status.md) | O que foi feito, o que falta e riscos |
| [Arquitetura Alvo](architecture.md) | Estrutura por camadas e principios de projeto |
| [Roadmap de Entrega](roadmap.md) | Plano por fases com checklists |
| [Documentacao Temporaria](temporary-updates.md) | Registro de mudancas pequenas e incrementais |
| [ADR 0001](decisions/ADR-0001-estrutura-inicial.md) | Decisao da estrutura inicial |

---

## Snapshot do Projeto

### Ja concluido

- Estrutura base de pastas para crescimento organizado.
- Modelo de token imutavel em `mineires_token.py`.
- Catalogo de token types e mapas lexicos em `tokentype.py`.
- Automato (AFD) implementado e validado em `src/mineres_compilador/automato.py`.
- Lexer implementado com rastreamento de linha/coluna em `src/mineres_compilador/lexer.py`.
- Validacoes locais de automato e lexer realizadas durante a implementacao.
- Documentacao tecnica e tutoriais criados em docs.

### Em aberto

- Definir contrato final de erro lexico (excecao vs token de erro).
- Garantir emissao de token `EOF` consistente.
- Criar `application/lexical_analysis_service.py`.
- Criar CLI (`main.py`) com suporte a `--input`, `--output`, `--format`.
- Configurar lint, format, type checking e CI/CD.

---

## Como usar esta documentacao

1. Comece por [Estado Atual](status.md) para entender a situacao real.
2. Leia [Arquitetura Alvo](architecture.md) para alinhar decisoes tecnicas.
3. Execute o [Roadmap de Entrega](roadmap.md) fase por fase.
4. Registre novas decisoes em docs/decisions usando o formato ADR.

---

## Atualizacao de Progresso

Ao final de cada entrega:

1. Atualize a porcentagem global nesta pagina.
2. Ajuste a tabela de progresso por fase.
3. Marque os itens concluidos em roadmap.md.
4. Atualize status.md com fatos tecnicos e riscos.
5. Registre mudancas pequenas em temporary-updates.md.
6. Quando a mudanca for consolidada, promova para status.md, architecture.md, roadmap.md ou ADR.
