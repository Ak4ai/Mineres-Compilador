---
title: "🚀 Comece aqui"
nav_order: 1
---

# 🚀 Comece aqui

Bem-vindo ao **Mineres Compilador**! 

Este guia vai te colocar no caminho para construir um compilador lexical da linguagem Minerês do zero.

## 📋 O que você vai aprender

Este projeto te ensina como:
- ✅ Construir um **Autômato Finito Determinístico (AFD)**
- ✅ Implementar um **Analisador Léxico (Lexer)**
- ✅ Criar uma **Interface de Linha de Comando (CLI)**
- ✅ Testar seu compilador com código real

**Tempo estimado**: 4-6 horas

## 🎯 O que é necessário

- Python 3.8+
- Editor de código (VS Code recomendado)
- Conhecimento básico de Python
- Curiosidade! 🧠

## 🏗️ Estrutura do projeto

```
Mineres-Compilador/
├── grafos/
│   └── automato_simples.txt        ← Definição do seu autômato
├── exemplos/
│   └── programa_exemplo.mineires.txt    ← Código de teste
├── src/
│   └── mineres_compilador/
│       ├── token.py                ← Modelo de token
│       ├── tokentype.py            ← Tipos de tokens
│       ├── automato.py             ← ❌ Você vai implementar
│       └── lexer.py                ← ❌ Você vai implementar
├── main.py                         ← ❌ Você vai implementar
└── docs/
    ├── tutorial/                   ← Guias de implementação
    │   ├── 01-automato.md
    │   ├── 02-lexer.md
    │   ├── 03-main.md
    │   └── 04-teste.md
    └── ...
```

## 📝 Seu roteiro de aprendizado

### Fase 1: Entender o contexto (15 min) 📚

1. Leia o [README.md](../README.md) para entender visão geral
2. Abra `grafos/automato_simples.txt` para ver o AFD (não precisa entender tudo)
3. Abra `exemplos/programa_exemplo.mineires.txt` para ver código Minerês de exemplo

### Fase 2: Implementar Automato (60-90 min) 🤖

1. Abra: [docs/tutorial/01-automato.md](tutorial/01-automato.md)
2. Crie arquivo: `src/mineres_compilador/automato.py`
3. Implemente classe `Automato` seguindo tutorial
4. Execute testes locais
5. Quando pronto, execute: `python test_automato.py`

**Resultado**: Um programa que reconhece tokens individuais ✅

### Fase 3: Implementar Lexer (60-90 min) 🔤

1. Abra: [docs/tutorial/02-lexer.md](tutorial/02-lexer.md)
2. Crie arquivo: `src/mineres_compilador/lexer.py`
3. Implemente classe `Lexer` seguindo tutorial
4. Execute: `python test_lexer.py`

**Resultado**: Um tokenizador que processa fluxos de entrada ✅

### Fase 4: Implementar CLI (30 min) 💻

1. Abra: [docs/tutorial/03-main.md](tutorial/03-main.md)
2. Crie arquivo: `main.py` na raiz
3. Implemente CLI seguindo tutorial
4. Teste com: `python main.py -s "certin"`

**Resultado**: Uma interface funcional para seu compilador ✅

### Fase 5: Validar tudo (30 min) ✅

1. Abra: [docs/tutorial/04-teste.md](tutorial/04-teste.md)
2. Execute todos os testes sugeridos
3. Verifique que `python main.py exemplos/programa_exemplo.mineires.txt` retorna ~38 tokens

**Resultado**: Compilador lexical completo e validado! 🎉

## 🚀 Comece agora

Você está pronto? Siga para [Fase 1: Automato](tutorial/01-automato.md)

## ❓ Precisa de ajuda?

- **Conceitos**: Leia o começo de cada arquivo tutorial para explicações
- **Erros**: Procure pelos TODOs nas seções de código
- **Debugging**: Use `print()` para ver valores das variáveis

## 📞 Dúvidas frequentes

### "Por onde começo se não sei Python?"

Comece com:
- [Python basics (EN)](https://docs.python.org/3/tutorial/)
- Classes e dataclasses
- Type hints
- Dicts e sets

### "Quanto tempo leva?"

- Automato: 60-90 min
- Lexer: 60-90 min
- Main: 30 min
- Testes: 30 min

**Total**: 4-6 horas dedicadas

### "E se eu me travar?"

1. Releia a seção do tutorial relevante
2. Procure pelos exemplos de código
3. Use `print()` para debug
4. Declare uma variável temporária para entender tipos

## 🎓 O que você aprenderá

Após completar este projeto, você entenderá:

```
Compilador = Fases sequenciais
│
├─ Análise Lexical (você vai implementar)
│  ├─ Automato (reconhece tokens)
│  └─ Lexer (tokeniza entrada)
│
├─ Análise Sintática (próximo nível)
│  ├─ Parser (valida sintaxe)
│  └─ AST (construir árvore)
│
├─ Análise Semântica (próximo nível)
│  ├─ Type checking
│  └─ Validação
│
└─ Geração de Código (próximo nível)
   ├─ Bytecode
   └─ Máquina virtual
```

Você está começando o primeiro passo! 🚀

## 💡 Dicas para sucesso

1. **Implemente incrementalmente**: Não tente tudo de uma vez
2. **Teste frequentemente**: Rode testes a cada seção concluída
3. **Use o debugger**: VS Code tem debugging excelente para Python
4. **Leia erros com atenção**: Eles dizem exatamente o que está errado
5. **Celebre vitórias pequenas**: Cada metade de fase é uma vitória!

## 🎉 Pronto?

Abra: [Fase 1: Automato](tutorial/01-automato.md) e comece! 

---

**Tempo estimado até primeira vitória**: 15 minutos
**Próxima milestone**: Ter `test_automato.py` passando ✅
