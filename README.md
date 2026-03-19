# Mineres-Compilador

Base organizada para evolucao de um compilador da linguagem Mineres, com foco em clareza, arquitetura limpa e padrao comercial.

## Status

- Fase atual: fundacao de estrutura e contratos lexicos.
- Progresso geral: 22%.
- Ultimo marco: criacao da central de documentacao em docs.

## Documentacao

- Home local da documentacao: [docs/index.md](docs/index.md)
- Home no GitHub (renderizada): [docs/README.md](docs/README.md)
- Estado atual: [docs/status.md](docs/status.md)
- Arquitetura alvo: [docs/architecture.md](docs/architecture.md)
- Roadmap: [docs/roadmap.md](docs/roadmap.md)
- Documentacao temporaria: [docs/temporary-updates.md](docs/temporary-updates.md)
- Decisoes tecnicas: [docs/decisions/ADR-0001-estrutura-inicial.md](docs/decisions/ADR-0001-estrutura-inicial.md)

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

## O que ja foi feito

- Estrutura base de pastas para crescimento organizado.
- Modelo de token imutavel em token.py.
- Catalogo de tipos de token e mapas de palavras em tokentype.py.
- Home visual para docs em docs/index.md.

## Proximos passos

- Implementar automato (AFD) no pacote principal.
- Implementar lexer no pacote principal.
- Criar camada de aplicacao e CLI.
- Adicionar testes automatizados e workflow de CI.

## Contribuicao

Fluxo recomendado para contribuicoes:

1. Atualizar codigo.
2. Se a mudanca for pequena, registrar em docs/temporary-updates.md.
3. Se a mudanca for final/consolidada, atualizar docs/status.md, docs/architecture.md e docs/roadmap.md.
4. Registrar decisoes relevantes em docs/decisions.
5. Abrir PR com descricao objetiva do impacto tecnico.

## Licenca

Definir licenca do projeto antes da primeira release publica.

