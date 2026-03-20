---
title: "Fase 1: Implemente automato.py"
parent: Tutorial - Implementar o Compilador Lexical
nav_order: 1
---

# Fase 1: Implemente `automato.py`

## 🎯 Objetivo

Implementar uma classe `Automato` que:
- Carrega definição de Autômato Finito Determinístico (AFD) de arquivo
- Gerencia estados e transições
- Reconhece tokens da linguagem Minerês

## 📖 Conceitos fundamentais

### O que é um AFD?

Um **Autômato Finito Determinístico** é um modelo matemático com:
- **Estados**: pontos no diagrama
- **Transições**: setas com caracteres (ex: 'a' passa do estado q0 → q1)
- **Estado inicial**: onde começamos (q0)
- **Estados finais**: onde aceitamos a entrada (ex: q_certin, q_2)
- **Entrada**: sequência de caracteres (ex: "certin", "123")

### Exemplo visual

```
         'c'
    q0 ------> q_c
                 |
               'e'
                 ↓
               q_ce
                 |
               'r'
                 ↓
              q_cer
              ... (continua)
                 |
               'n'
                 ↓
          q_certin (FINAL) → Aceita "certin" como CERTIN token
```

## 📝 Seu arquivo de entrada

Abra: `grafos/automato_simples.txt`

Este arquivo tem 2 seções:

### Seção [ESTADOS]
```
[ESTADOS]
q0 INICIAL
q_2 FINAL INTEGER_LITERAL
q_a FINAL IDENTIFIER
q_b INTERMEDIARIO
...
```

**Formato**: `nome tipo [token_type]`
- `nome`: identificador único (ex: q0, q_a, q_certin)
- `tipo`: um de INICIAL, INTERMEDIARIO, FINAL
- `token_type`: (opcional) qual TokenType quando estado é FINAL (ex: CERTIN, INTEGER_LITERAL)

### Seção [TRANSICOES]
```
[TRANSICOES]
q0 q_2 2
q0 q_a a
q_b q_bo o
...
```

**Formato**: `origem destino caractere`
- `origem`: estado atual
- `destino`: próximo estado
- `caractere`: qual caractere dispara a transição

## 💻 Estrutura de código

Comece criando o arquivo: `src/mineres_compilador/automato.py`

### Passo 1: Imports e Enums

```python
"""
Módulo de Automato - Gerencia o Autômato Finito Determinístico (AFD)
que reconhece tokens da linguagem Minerês.
"""

from enum import Enum
from typing import Dict, Tuple, Optional, Set
from dataclasses import dataclass
from pathlib import Path


class EstadoTipo(Enum):
    """Classifica o tipo de estado no AFD."""
    INICIAL = "INICIAL"
    INTERMEDIARIO = "INTERMEDIARIO"
    FINAL = "FINAL"


@dataclass(slots=True)
class Estado:
    """Representa um estado do AFD."""
    nome: str
    tipo: EstadoTipo
    token_type: Optional[str] = None  # TokenType quando estado é FINAL
```

**O que fazer**: Crie a classe `Estado` como um dataclass imutável que armazena informações sobre cada estado.

### Passo 2: Classe Automato - Estrutura básica

```python
class Automato:
    """
    Gerencia o Autômato Finito Determinístico para reconhecimento de tokens.
    
    Atributos:
    - estados: Dict mapeando nome_estado → Estado
    - transicoes: Dict mapeando (estado, char) → próximo_estado
    - estado_inicial: nome do estado inicial
    - estados_finais: Set de nomes de estados finais
    """
    
    def __init__(self):
        """Inicializa automato vazio."""
        self.estados: Dict[str, Estado] = {}
        self.transicoes: Dict[Tuple[str, str], str] = {}
        self.estado_inicial: Optional[str] = None
        self.estados_finais: Set[str] = set()
```

### Passo 3: Implementar `carregar_do_arquivo()`

Este método deve:
1. Ler arquivo em `caminho`
2. Separar em seções [ESTADOS] e [TRANSICOES]
3. Processar cada seção

```python
    def carregar_do_arquivo(self, caminho: str) -> None:
        """
        Carrega definição do AFD do arquivo.
        
        Args:
            caminho: Caminho ao arquivo automato_simples.txt
            
        Levanta:
            FileNotFoundError se arquivo não existir
        """
        path = Path(caminho)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        
        # TODO: Ler conteúdo do arquivo
        # TODO: Separar em seções por '[ESTADOS]' e '[TRANSICOES]'
        # TODO: Chamar _processar_estados() e _processar_transicoes()
```

**Dica**: Use `open(path, 'r', encoding='utf-8')` para ler. Separe por `string.split('[')` para encontrar seções.

### Passo 4: Implementar `_processar_estados()`

Processa cada linha da seção [ESTADOS]:

```python
    def _processar_estados(self, linhas_texto: str) -> None:
        """Processa seção [ESTADOS] do arquivo."""
        # TODO: Para cada linha
        #   - Ignorar comentários (começam com #) e linhas vazias
        #   - Fazer split em palavras
        #   - Extrair: nome, tipo, token_type (se houver)
        #   - Criar Estado e adicionar a self.estados
        #   - Se tipo == INICIAL, guarde em self.estado_inicial
        #   - Se tipo == FINAL, adicione a self.estados_finais
```

**Exemplo de processamento**:
```
Entrada: "q_certin FINAL CERTIN"
Split: ['q_certin', 'FINAL', 'CERTIN']
Resultado: Estado(nome='q_certin', tipo=EstadoTipo.FINAL, token_type='CERTIN')
```

### Passo 5: Implementar `_processar_transicoes()`

Processa cada linha de [TRANSICOES]:

```python
    def _processar_transicoes(self, linhas_texto: str) -> None:
        """Processa seção [TRANSICOES] do arquivo."""
        # TODO: Para cada linha
        #   - Ignorar comentários e linhas vazias
        #   - Split: [origem, destino, caractere]
        #   - Adicione a self.transicoes: (origem, caractere) -> destino
```

**Exemplo**:
```
Entrada: "q0 q_a a"
Resultado: self.transicoes[('q0', 'a')] = 'q_a'
```

### Passo 6: Métodos auxiliares

Implemente estes helpers:

```python
    def obter_proximo_estado(self, estado_atual: str, char: str) -> Optional[str]:
        """
        Qual é o próximo estado dado entrada de caractere?
        
        Args:
            estado_atual: Nome do estado atual
            char: Caractere de entrada
            
        Returns:
            Nome do próximo estado ou None se sem transição
        """
        # TODO: Procure em self.transicoes[(estado_atual, char)]
        
    def eh_estado_final(self, estado: str) -> bool:
        """Este estado é aceição?"""
        # TODO: Verifique se estado está em self.estados_finais
        
    def obter_token_type(self, estado: str) -> Optional[str]:
        """Que tipo de token este estado final representa?"""
        # TODO: Retorne self.estados[estado].token_type
```

### Passo 7: Implementar `reconhecer()`

Este é o método principal:

```python
    def reconhecer(self, entrada: str) -> Tuple[bool, Optional[str], int]:
        """
        Reconhece string usando o AFD.
        
        Args:
            entrada: String a reconhecer (ex: "certin", "123")
            
        Returns:
            Tupla (aceito, token_type_nome, comprimento)
            - aceito: True se entrada foi aceita
            - token_type_nome: Nome do TokenType (ex: 'CERTIN', 'INTEGER_LITERAL')
            - comprimento: Quantos caracteres foram consumidos
            
        Algoritmo:
        1. Comece em estado_inicial
        2. Para cada caractere da entrada:
           a. Procure próximo estado: obter_proximo_estado()
           b. Se sem transição, para
           c. Se estado é final, lembre de: token_type + posição
        3. Retorne a última aceitação válida
        
        Exemplo com entrada "certin":
        - q0 + 'c' → q_c
        - q_c + 'e' → q_ce
        - ...
        - q_certin + (fim) → FINAL, lembre token_type='CERTIN', len=6
        - Retorna: (True, 'CERTIN', 6)
        """
        # TODO: Implemente algoritmo acima
```

## ✅ Checklist de implementação

- [ ] Enums `EstadoTipo` criado
- [ ] Dataclass `Estado` criado
- [ ] Classe `Automato` inicializa com atributos vazios
- [ ] `carregar_do_arquivo()` lê arquivo e separa seções
- [ ] `_processar_estados()` popula `self.estados` e `self.estados_finais`
- [ ] `_processar_transicoes()` popula `self.transicoes`
- [ ] `obter_proximo_estado()` retorna próximo ou None
- [ ] `eh_estado_final()` verifica se estado é final
- [ ] `obter_token_type()` retorna tipo de token
- [ ] `reconhecer()` implementa algoritmo e retorna aceição correta

## 🧪 Teste sua implementação

Crie um script temporário `test_automato.py` na raiz:

```python
from src.mineres_compilador.automato import Automato

# Teste
afd = Automato()
afd.carregar_do_arquivo("grafos/automato_simples.txt")

# Deve reconhecer "certin" como CERTIN
aceito, token_type, comprimento = afd.reconhecer("certin")
print(f"Entrada: 'certin' → Aceito: {aceito}, TokenType: {token_type}, Comprimento: {comprimento}")
assert aceito == True
assert token_type == "CERTIN"
assert comprimento == 6

# Deve reconhecer "2" como INTEGER_LITERAL
aceito, token_type, comprimento = afd.reconhecer("2")
print(f"Entrada: '2' → Aceito: {aceito}, TokenType: {token_type}, Comprimento: {comprimento}")
assert aceito == True
assert token_type == "INTEGER_LITERAL"
assert comprimento == 1

print("✅ Testes passaram!")
```

Execute: `python test_automato.py`

## 💡 Dicas importantes

1. **Caracteres especiais**: Em transições, espaço `_` representa espaço real
2. **Estados finais**: Quando reconhecimento termina em estado final, é aceição
3. **Reconhecimento greedy**: Le a maior sequência válida possível
4. **Comentários**: Linhas começando com `#` devem ser ignoradas

## 🆘 Se ficar travado

- Imprima `self.estados` e `self.transicoes` para debug
- Teste manualmente: `print(afd.transicoes.get(('q0', 'c')))`
- Leia o arquivo `grafos/automato_simples.txt` manualmente para entender formato

## 📚 Próximo passo

Quando terminar e testes passarem, avance para [Fase 2: Lexer.py](02-lexer.md)
