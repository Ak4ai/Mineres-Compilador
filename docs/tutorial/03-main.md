---
title: "Fase 3: Implemente main.py"
parent: Tutorial - Implementar o Compilador Lexical
nav_order: 3
---

# Fase 3: Implemente `main.py`

## 🎯 Objetivo

Criar uma interface CLI (Command Line Interface) para teste do lexer:

```bash
python main.py programa.mineires
python main.py -s "certin"
```

## 💻 Estrutura

Arquivo: `main.py` (na raiz do projeto)

### Passo 1: Setup de imports

```python
#!/usr/bin/env python3
"""
CLI principal para Mineres Compilador

Uso:
    python main.py <arquivo.mineires>
    python main.py -s "<codigo mineres>"
"""

import sys
from pathlib import Path

# Adicione diretório src ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mineres_compilador import Lexer
```

### Passo 2: Função main

```python
def main():
    """
    Ponto de entrada do programa.
    
    Lógica:
    1. Verifique argumentos (deve ter at least 1)
    2. Se arg[1] == '-s': analise string
    3. Senão: analise arquivo
    4. Crie lexer e tokenize
    5. Exiba tokens em formato tabular
    6. Se erro: imprima em stderr
    """
    
    if len(sys.argv) < 2:
        # TODO: Exiba mensagem de uso (help)
        print("Uso: python main.py <arquivo.mineires>")
        print("      python main.py -s '<codigo>'")
        sys.exit(1)
    
    # TODO: Crie Lexer
    # TODO: Se -s: carregar_string()
    # TODO: Senão: carregar_arquivo()
    # TODO: Chame analisar()
    # TODO: Print tokens em tabela
```

**Exemplo de saída esperada**:
```
Tokens reconhecidos:
------------------------------------------------------------
Tipo                    Lexema          Linha   Coluna
------------------------------------------------------------
CERTIN                  certin          1       1
C_NAO                   c_nao           2       1
INTEGER_LITERAL         2               3       1
UAI                     uai             3       3
------------------------------------------------------------
Total: 4 tokens reconhecidos
```

### Passo 3: Exibição de tokens

```python
    # Após tokenizar, exiba assim:
    print("Tokens reconhecidos:")
    print("-" * 60)
    print(f"{'Tipo':<20}\t{'Lexema':<15}\t{'Linha':<5}\t{'Coluna':<5}")
    print("-" * 60)
    
    for token in tokens:
        # TODO: Exiba cada token em formato tabular
        # token.type.value ← nome do tipo
        # token.lexeme ← string original
        # token.line, token.column ← posição
    
    print("-" * 60)
    print(f"Total: {len(tokens)} tokens reconhecidos")
```

### Passo 4: Tratamento de erros

```python
    try:
        # TODO: Código de tokenização
    except FileNotFoundError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erro durante análise: {e}", file=sys.stderr)
        sys.exit(1)
```

### Passo 5: Entry point

```python
if __name__ == "__main__":
    main()
```

## 📋 Template completo

```python
#!/usr/bin/env python3
"""
CLI principal para Mineres Compilador

Uso:
    python main.py <arquivo.mineires>
    python main.py -s "<codigo mineres>"
"""

import sys
from pathlib import Path

# Adicione diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mineres_compilador import Lexer


def main():
    """Função principal."""
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.mineires>")
        print("      python main.py -s '<codigo>'")
        sys.exit(1)
    
    lexer = Lexer(caminho_automato="grafos/automato_simples.txt")
    
    try:
        # Carregar entrada
        if sys.argv[1] == "-s":
            if len(sys.argv) < 3:
                print("Erro: especifique código após -s", file=sys.stderr)
                sys.exit(1)
            codigo = sys.argv[2]
            lexer.carregar_string(codigo)
        else:
            arquivo = sys.argv[1]
            lexer.carregar_arquivo(arquivo)
        
        # Tokenizar
        tokens = lexer.analisar()
        
        # Exibir
        print("Tokens reconhecidos:")
        print("-" * 60)
        print(f"{'Tipo':<20}\t{'Lexema':<15}\t{'Linha':<5}\t{'Coluna':<5}")
        print("-" * 60)
        
        for token in tokens:
            print(f"{token.type.value:<20}\t{token.lexeme:<15}\t{token.line}\t{token.column}")
        
        print("-" * 60)
        print(f"Total: {len(tokens)} tokens reconhecidos")
        
    except FileNotFoundError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erro durante análise: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## 🧪 Teste manual

```bash
# Teste 1: String simples
python main.py -s "certin"

# Saída esperada:
# Tokens reconhecidos:
# ------------------------------------------------------------
# Tipo                    Lexema          Linha   Coluna
# ------------------------------------------------------------
# CERTIN                  certin          1       1
# ------------------------------------------------------------
# Total: 1 tokens reconhecidos

# Teste 2: Arquivo
python main.py exemplos/programa_exemplo.mineires.txt

# Saída esperada: ~38 tokens (verifique em Fase 4)
```

## ✅ Checklist

- [ ] `#!/usr/bin/env python3` no início
- [ ] Imports corretos (sys, Path, Lexer)
- [ ] Diretório src adicionado ao sys.path
- [ ] Argumentos parseados corretamente (-s vs arquivo)
- [ ] Lexer criado com path correto ao automato
- [ ] carregar_string() ou carregar_arquivo() chamado
- [ ] analisar() chamado
- [ ] Tokens exibidos em formato tabular
- [ ] Tratamento de erros com mensagens úteis
- [ ] exit codes corretos (0 = sucesso, 1 = erro)

## 💡 Dicas

1. **Shebang**: `#!/usr/bin/env python3` permite executar como `./main.py`
2. **sys.path**: Adiciona diretório src para resolver imports
3. **stderr**: Use `file=sys.stderr` para mensagens de erro
4. **Formatação**: Use f-strings com larguras (ex: `{valor:<20}`)

## 📚 Próximo passo

Quando main.py funcionar, avance para [Fase 4: Teste](04-teste.md)
