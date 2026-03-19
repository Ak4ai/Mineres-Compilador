---
title: Roadmap de Entrega
nav_order: 4
---

# Roadmap de Entrega

## Fase 1 - Fundacao (concluida parcialmente)

- [x] Criar estrutura base de pastas.
- [x] Definir modelo de token.
- [x] Definir catalogo de token types e mapas de palavras.
- [x] Iniciar documentacao tecnica.
- [ ] Completar README principal do repositorio.

## Fase 2 - Nucleo Lexico

- [ ] Implementar `automato.py` no pacote principal.
- [ ] Implementar `lexer.py` no pacote principal.
- [ ] Definir contrato de erro lexico.
- [ ] Implementar leitura de fonte por arquivo e por string.
- [ ] Garantir token `EOF` consistente.

## Fase 3 - Aplicacao e CLI

- [ ] Criar servico de analise lexico em `application`.
- [ ] Criar CLI com parametros (`--input`, `--output`, `--format`).
- [ ] Suportar saida humana e json.
- [ ] Definir codigos de retorno padrao para automacao.

## Fase 4 - Qualidade e Governanca

- [ ] Criar testes unitarios de tokenizacao.
- [ ] Criar testes de integracao com exemplos da linguagem.
- [ ] Configurar lint e format.
- [ ] Configurar type checking.
- [ ] Criar workflow de CI em `.github/workflows`.

## Fase 5 - Release inicial

- [ ] Gerar versao `v0.1.0`.
- [ ] Publicar changelog.
- [ ] Fechar checklist de pronto comercial.

## Criterios de conclusao de MVP

- Lexer processa casos principais sem erro.
- Saida de tokens reproduzivel.
- Cobertura minima de testes definida e atingida.
- CI obrigatorio para merge.
- Documentacao de uso e arquitetura atualizada.
