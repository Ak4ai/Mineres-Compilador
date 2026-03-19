---
layout: default
title: Home
nav_order: 1
---

# Mineres-Compilador

Documentacao oficial do projeto, com foco em organizacao comercial, clareza tecnica e evolucao incremental.

<p>
  <img src="https://img.shields.io/badge/status-em%20evolucao-1f6feb" alt="status" />
  <img src="https://img.shields.io/badge/fase-fundacao-0a7f5a" alt="fase" />
  <img src="https://img.shields.io/badge/progresso-22%25-f59e0b" alt="progresso" />
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
    <td>Fundacao de dominio e organizacao estrutural.</td>
  </tr>
  <tr>
    <td><strong>Proxima Etapa</strong></td>
    <td>Implementacao do nucleo lexico no pacote principal.</td>
  </tr>
</table>

---

## Painel de Progresso

### Progresso Global

<progress value="22" max="100">22%</progress>

**22% concluido**

### Progresso por Fase

| Fase | Progresso | Status |
|---|---:|---|
| Fundacao | 70% | Em andamento |
| Nucleo Lexico | 0% | Nao iniciado |
| Aplicacao e CLI | 0% | Nao iniciado |
| Qualidade e Governanca | 0% | Nao iniciado |
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
- Modelo de token definido em token.py.
- Catalogo de token types e mapas lexicos em tokentype.py.
- Documentacao tecnica inicial criada em docs.

### Em aberto

- Implementar automato (AFD) no pacote principal.
- Implementar lexer no pacote principal.
- Criar CLI de execucao com contratos de entrada e saida.
- Adicionar testes, CI e politicas de qualidade.

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
