# Documentacao do Mineres-Compilador

Esta pasta centraliza o estado do projeto, arquitetura, decisoes e plano de entrega.

## Progresso Geral

<progress value="22" max="100">22%</progress>

**22% concluido**

- Etapa atual: fundacao de dominio e organizacao estrutural.
- Proxima etapa: implementar o nucleo lexico em `src/mineres_compilador`.

## Mapa de Status

| Area | Status | Observacao |
|---|---|---|
| Estrutura de pastas | Concluido | Layout inicial comercial criado |
| Modelo de token | Concluido | `token.py` com dataclass imutavel |
| Catalogo de token types | Concluido | `tokentype.py` com enum e mapas |
| Documentacao tecnica | Em progresso | Esta pasta foi iniciada |
| Lexer | Nao iniciado | Ainda nao existe modulo no pacote principal |
| Automato (AFD) | Nao iniciado | Ainda nao existe modulo no pacote principal |
| CLI/entrada da aplicacao | Nao iniciado | Sem ponto de entrada definido |
| Testes automatizados | Nao iniciado | Suite ainda nao criada |
| CI/CD | Nao iniciado | Workflow vazio |

## Leitura Rapida

- [Estado Atual](status.md)
- [Arquitetura Alvo](architecture.md)
- [Roadmap de Entrega](roadmap.md)
- [ADR 0001 - Estrutura Inicial](decisions/ADR-0001-estrutura-inicial.md)

## Como Atualizar o Progresso

1. Atualize a porcentagem no elemento `<progress>` desta pagina.
2. Atualize os checklists em `status.md` e `roadmap.md`.
3. Registre decisoes arquiteturais em `docs/decisions`.
