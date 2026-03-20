---
title: "Fase 2: Implemente lexer.py"
parent: Tutorial - Implementar o Compilador Lexical
nav_order: 2
---

# Fase 2: Implemente `lexer.py`

## 🎯 Objetivo

Implementar uma classe `Lexer` que:
- Carrega código Minerês de arquivo ou string
- Usa o `Automato` para reconhecer tokens individuais
- Rastreia posição (linha/coluna) para cada token
- Retorna lista de `Token` objects

## 📖 Conceitos

### O que faz o Lexer?

```
Entrada (arquivo):          Processamento:                 Saída (tokens):
--------------              --------                       -----------
"certin"           ┐
"c_nao"            ├─→ Lexer (usa Automato) ──→   [(CERTIN, line=1, col=1),
"2 uai"            │                                (C_NAO, line=2, col=1),
                   │                                (INTEGER_LITERAL, line=3, col=1),
                   ┘                                (UAI, line=3, col=3)]
```

### Diferença Automato vs Lexer

- **Automato**: Reconhece UM token de cada vez (entrada arbitrária)
- **Lexer**: Tokeniza FLUXO de entrada, rastreando posição

## 💻 Estrutura esperada

Arquivo: `src/mineres_compilador/lexer.py`

### Passo 1: Imports

```python
"""
Módulo Lexer - Análise lexical de programas Minerês.

Responsabilidades:
- Ler arquivo/string de entrada
- Usar automato para reconhecer tokens
- Rastrear linha/coluna
- Tratar identificadores vs palavras-chave
"""

from typing import List, Optional, Generator
from pathlib import Path

from .automato import Automato
from .token import Token
from .tokentype import TokenType, ALL_WORD_TOKENS
```

### Passo 2: Classe Lexer - Estrutura

```python
class Lexer:
    """
    Analisador léxico para Minerês.
    
    Atributos:
    - automato: Automato carregado
    - input_str: Código a analisar
    - posicao: Índice atual na entrada
    - linha: Número da linha current
    - coluna: Número da coluna current
    - tokens: Lista de tokens reconhecidos
    """
    
    def __init__(self, caminho_automato: str = "grafos/automato_simples.txt"):
        """Inicializa lexer com automato."""
        self.automato = Automato()
        self.automato.carregar_do_arquivo(caminho_automato)
        
        self.input_str = ""
        self.posicao = 0
        self.linha = 1
        self.coluna = 1
        self.tokens: List[Token] = []
```

### Passo 3: Carregar entrada

```python
    def carregar_arquivo(self, caminho: str) -> None:
        """
        Carrega arquivo de entrada.
        
        Args:
            caminho: Caminho ao arquivo .mineires
            
        TODO:
        - Abrir arquivo
        - Ler conteúdo completo
        - Resetar posição/linha/coluna/tokens
        """
        # Exemplo:
        # path = Path(caminho)
        # with open(path, 'r', encoding='utf-8') as f:
        #     self.input_str = f.read()
        # Resetar estado
    
    def carregar_string(self, conteudo: str) -> None:
        """Carrega entrada a partir de string."""
        # TODO: Similar a carregar_arquivo, mas sem arquivo
        # self.input_str = conteudo
        # Resetar estado
```

### Passo 4: Método principal `analisar()`

Este método tokeniza entrada completa:

```python
    def analisar(self) -> List[Token]:
        """
        Realiza análise lexical completa.
        
        Algoritmo:
        1. Enquanto houver entrada (self.posicao < len(self.input_str)):
           a. Se caractere é whitespace (espaço, tab):
              - Pule (mas rastreie coluna)
           b. Se caractere é newline:
              - Increment linha, resete coluna
           c. Senão:
              - Reconheça um token via _reconhecer_proximo_token()
              - Adicione a self.tokens
        
        Returns:
            self.tokens (lista de tokens reconhecidos)
        """
        self.tokens = []
        
        # TODO: Implemente while loop acima
```

**Whitespace handling**:
```python
if self.input_str[self.posicao] == ' ':
    self.posicao += 1
    self.coluna += 1
    continue
```

### Passo 5: Reconhecer um token

O método mais importante:

```python
    def _reconhecer_proximo_token(self) -> Optional[Token]:
        """
        Reconhece um token a partir da posição atual.
        
        Algoritmo:
        1. Guarde posição inicial (linha_inicio, coluna_inicio)
        2. Extraia substring restante: self.input_str[self.posicao:]
        3. Use self.automato.reconhecer() para tentar reconhecer
        4. Se aceito:
           a. Extraia lexeme (substring de comprimento reconhecido)
           b. Se token_type é 'IDENTIFIER':
              - Verifique se é palavra-chave em ALL_WORD_TOKENS
              - Se sim, mude token_type para a palavra-chave
           c. Senão, mappe token_type_nome para TokenType enum
        5. Se não aceito:
           - Considere caractere como erro (UNKNOWN)
        6. Atualize self.posicao
        7. Atualize linha/coluna (considerando newlines no token)
        8. Retorne Token(...) ou None se erro
        
        Exemplo com entrada "certin":
        - posicao=0, linha=1, coluna=1
        - automato.reconhecer("certin...") → (True, 'CERTIN', 6)
        - lexeme = "certin"
        - TokenType.CERTIN
        - posicao += 6
        - Retorna: Token(type=TokenType.CERTIN, lexeme="certin", line=1, column=1)
        """
        # TODO: Implemente algoritmo
```

**Pseudo-código**:
```python
linha_inicio = self.linha
coluna_inicio = self.coluna
restante = self.input_str[self.posicao:]

aceito, token_type_nome, comprimento = self.automato.reconhecer(restante)

if aceito and comprimento > 0:
    lexeme = restante[:comprimento]
    # Mapeie token_type_nome para TokenType enum
    # Verifique se é IDENTIFIER que pode ser palavra-chave
else:
    # Caractere não reconhecido
    lexeme = restante[0] if restante else ""
    token_type = TokenType.UNKNOWN

# Atualize posição
self.posicao += len(lexeme)

# Atualize linha/coluna
for char in lexeme:
    if char == '\n':
        self.linha += 1
        self.coluna = 1
    else:
        self.coluna += 1

return Token(type=token_type, lexeme=lexeme, line=linha_inicio, column=coluna_inicio)
```

### Passo 6: Gerador (opcional)

Para eficiência em arquivos grandes:

```python
    def gerar_tokens(self) -> Generator[Token, None, None]:
        """
        Gerador que produz tokens um a um.
        
        Uso:
        lexer.carregar_arquivo("programa.mineires")
        for token in lexer.gerar_tokens():
            print(token)
        """
        # TODO: Similar a analisar(), mas não armazena em lista
        # Em vez disso: yield token
```

## ⚠️ Detalhes importantes

### 1. Mapeamento de Identificador → Palavra-chave

```python
if token_type_nome == "IDENTIFIER":
    # Verificar se é palavra reservada
    token_mapeado = ALL_WORD_TOKENS.get(lexeme.lower())
    if token_mapeado:
        token_type = token_mapeado  # É palavra-chave
    else:
        token_type = TokenType.IDENTIFIER  # É identificador normal
```

### 2. Rastreamento de linha/coluna

```python
for char in lexeme:
    if char == '\n':
        self.linha += 1
        self.coluna = 1
    else:
        self.coluna += 1
```

### 3. TokenType enum lookup

```python
try:
    token_type = TokenType[token_type_nome]  # Ex: TokenType["CERTIN"]
except KeyError:
    token_type = TokenType.UNKNOWN
```

## ✅ Checklist

- [ ] Classe `Lexer` com inicialização
- [ ] `carregar_arquivo()` funciona
- [ ] `carregar_string()` funciona
- [ ] `analisar()` implementa loop principal
- [ ] `_reconhecer_proximo_token()` reconhece um token
- [ ] Whitespace/newline tratados corretamente
- [ ] Identificadores vs palavras-chave diferenciados
- [ ] TokenType mapeado de nome para enum
- [ ] Rastreamento de linha/coluna correto
- [ ] Retorna lista de Token objects

## 🧪 Teste

```python
from src.mineres_compilador.lexer import Lexer

lexer = Lexer()
lexer.carregar_string("certin")
tokens = lexer.analisar()

assert len(tokens) == 1
assert tokens[0].type.value == "CERTIN"
assert tokens[0].lexeme == "certin"
assert tokens[0].line == 1
assert tokens[0].column == 1

print("✅ Lexer funciona!")
```

Ou teste com arquivo:
```python
lexer.carregar_arquivo("exemplos/programa_exemplo.mineires.txt")
tokens = lexer.analisar()
print(f"Total de tokens: {len(tokens)}")
for token in tokens[:5]:
    print(f"  {token.type.value:20} {token.lexeme:15} L{token.line}:C{token.column}")
```

## 📚 Próximo passo

Quando lexer funcionar, avance para [Fase 3: Main.py](03-main.md)
