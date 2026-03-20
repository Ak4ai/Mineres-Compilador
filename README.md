# Mineres-Compilador

Base organizada para evolucao de um compilador da linguagem Mineres, com foco em clareza, arquitetura limpa e padrao comercial.

## Status

- Fase atual: **Implementação de análise lexical (tutorial)**.
- Progresso geral: 75%.
- Último marco: Tutoriais completos para aprendizado auto-guiado e testes funcionais.

## 🚀 Comece aqui

**Novo no projeto?** Leia: [COMECE_AQUI.md](COMECE_AQUI.md) (15 min leitura)

Isso te coloca no caminho para implementar o compilador lexical passo a passo.

## 📚 Documentação

### Tutoriais (para aprender implementando)
- **[COMECE_AQUI.md](COMECE_AQUI.md)** — Roteiro de aprendizado (~4-6 horas)
- **[Tutorial Completo](docs/tutorial.md)** — 4 fases de implementação:
  - [Fase 1: Automato.py](docs/tutorial/01-automato.md) - AFD e reconhecimento
  - [Fase 2: Lexer.py](docs/tutorial/02-lexer.md) - Tokenização
  - [Fase 3: Main.py](docs/tutorial/03-main.md) - CLI funcional
  - [Fase 4: Testes](docs/tutorial/04-teste.md) - Validação completa

### Documentação técnica
- Home: [docs/index.md](docs/index.md)
- Estado atual: [docs/status.md](docs/status.md)
- Arquitetura: [docs/architecture.md](docs/architecture.md)
- Roadmap: [docs/roadmap.md](docs/roadmap.md)
- Decisões técnicas: [docs/decisions/ADR-0001-estrutura-inicial.md](docs/decisions/ADR-0001-estrutura-inicial.md)

Se o GitHub Pages estiver habilitado com branch main e pasta /docs, a home publica sera:

- https://ak4ai.github.io/Mineres-Compilador/

## Estrutura do Repositorio

```
Mineres-Compilador/
	.github/workflows/          # CI/CD
	configs/                    # configuracoes de projeto
	docs/                       # documentacao viva (status, arquitetura, roadmap, ADR)
	scripts/                    # automacoes locais
	src/mineres_compilador/     # pacote principal da aplicacao
	token.py                    # contrato de token
	tokentype.py                # enum de tokens e mapas lexicos
```

## O que já foi feito

- ✅ Estrutura base de pastas para crescimento organizado
- ✅ Modelo de token imutável em token.py
- ✅ Catálogo de tipos de token e mapas lexicos em tokentype.py
- ✅ Ar quivos de recursos: `grafos/automato_simples.txt`, `exemplos/programa_exemplo.mineires.txt`
- ✅ Documentação técnica e tutoriais

## Próximos passos (para você implementar!)

Siga o tutorial em **[COMECE_AQUI.md](COMECE_AQUI.md)**:

1. **Implementar automato.py** - Reconhecer tokens individuais (60-90 min)
2. **Implementar lexer.py** - Tokenizar fluxos de entrada (60-90 min)
3. **Implementar main.py** - Interface CLI funcional (30 min)
4. **Testar** - Validar com testes (30 min)

**Total**: 4-6 horas dedicadas de aprendizado prático!

## Contribuicao

Fluxo recomendado para contribuicoes:

1. Atualizar codigo.
2. Se a mudanca for pequena, registrar em docs/temporary-updates.md.
3. Se a mudanca for final/consolidada, atualizar docs/status.md, docs/architecture.md e docs/roadmap.md.
4. Registrar decisoes relevantes em docs/decisions.
5. Abrir PR com descricao objetiva do impacto tecnico.

## Licenca

Definir licenca do projeto antes da primeira release publica.

