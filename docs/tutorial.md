---
title: Tutorial - Implementar o Compilador Lexical
nav_order: 7
has_children: true
---

# Tutorial: Implemente o Compilador Lexical

Bem-vindo! Este é um tutorial **prático e progressivo** onde você aprende implementando.

> **Novo aqui?** Comece em [COMECE_AQUI.md](../COMECE_AQUI.md) — guia de orientação completo (15 min).

## 🎯 O que você vai construir

Um **compilador lexical funcional** para Minerês em 4 fases:

1. **Automato.py** (60-90 min) - Reconhecer tokens individuais
2. **Lexer.py** (60-90 min) - Tokenizar fluxos de entrada
3. **Main.py** (30 min) - Interface de linha de comando
4. **Testes** (30 min) - Validação completa

## 📈 Progresso

```
 0% ════════════════════════════════════ 100%
 │
 ├─ Fase 1: Automato ✅ → test_automato.py passa
 ├─ Fase 2: Lexer ✅ → test_lexer.py passa
 ├─ Fase 3: Main.py ✅ → CLI funcional
 └─ Fase 4: Testes ✅ → 38 tokens reconhecidos
```

## 📚 Fases do tutorial

### [Fase 1: Automato.py →](tutorial/01-automato.md)
- Entender AFD (Autômato Finito Determinístico)
- Carregar arquivo `grafos/automato_simples.txt`
- Implementar reconhecimento de tokens
- Resultado: Reconhecer entrada individual ✅

### [Fase 2: Lexer.py →](tutorial/02-lexer.md)
- Usar Automato para tokenizar fluxos
- Rastreamento linha/coluna
- Palavras-chave vs identificadores
- Resultado: Analisador léxico funcional ✅

### [Fase 3: Main.py →](tutorial/03-main.md)
- CLI para testar seu compilador
- Aceitar arquivo ou string
- Exibição formatada de tokens
- Resultado: `python main.py programa.txt` ✅

### [Fase 4: Testes →](tutorial/04-teste.md)
- Testes unitários
- Testes de integração
- Validação completa
- Resultado: 38 tokens de `exemplos/programa_exemplo.mineires.txt` ✅

## ⏱️ Tempo total

- **Leitura + Planejamento**: 15 min
- **Implementação**: 3-4 horas
- **Debugging + Testes**: 45 min
- **Total: 4-6 horas dedicadas**

## 🚀 Comece agora

**Opção 1 - Guiado completo** (recomendado para primeiro estudo):
→ [COMECE_AQUI.md](../COMECE_AQUI.md)

**Opção 2 - Direto ao código**:
→ [Fase 1: Automato.py](tutorial/01-automato.md)

## 📖 Recursos

- **[Arquitetura](../docs/architecture.md)** — Visão técnica do projeto
- **[Elementos](../%20Elementos%20da%20Linguagem%20em%20Minerês.csv)** — Vocabulário Minerês completo
- **[README](../README.md)** — Overview do projeto
