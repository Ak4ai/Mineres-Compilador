# Documentacao do Mineres-Compilador

Esta pasta centraliza o estado do projeto, arquitetura, decisoes e plano de entrega.

## Progresso Geral

<progress value="65" max="100">65%</progress>

**65% concluido**

- Etapa atual: implementacao da camada de aplicacao e CLI.
- Proxima etapa: criar CLI funcional com servico de analise lexica.

## Mapa de Status

| Area | Status | Observacao |
|---|---|---|
| Estrutura de pastas | Concluido | Layout inicial comercial criado |
| Modelo de token | Concluido | `mineires_token.py` com dataclass imutavel |
| Catalogo de token types | Concluido | `tokentype.py` com enum e mapas |
| Automato (AFD) | Concluido | `automato.py` implementado e validado |
| Lexer | Concluido | `lexer.py` implementado com rastreamento de posicao |
| Testes unitarios | Em progresso | Automato e lexer cobertos; integracao CLI pendente |
| Documentacao tecnica | Em progresso | Docs criados; alguns arquivos com info desatualizada |
| CLI/entrada da aplicacao | Nao iniciado | `main.py` e service de analise ainda nao existem |
| Lint/format/typecheck | Nao iniciado | Sem configuracao de qualidade ainda |
| CI/CD | Nao iniciado | Workflow vazio |

## Leitura Rapida

- [Estado Atual](status.md)
- [Arquitetura Alvo](architecture.md)
- [Roadmap de Entrega](roadmap.md)
- [Documentacao Temporaria](temporary-updates.md)
- [ADR 0001 - Estrutura Inicial](decisions/ADR-0001-estrutura-inicial.md)

## Como Atualizar o Progresso

1. Atualize a porcentagem no elemento `<progress>` desta pagina.
2. Atualize os checklists em `status.md` e `roadmap.md`.
3. Para mudancas pequenas, registre em `temporary-updates.md`.
4. Para mudancas finais, atualize os documentos oficiais e ADR quando necessario.
5. Registre decisoes arquiteturais em `docs/decisions`.
