---
title: "Fase 4: Teste Completo"
parent: Tutorial - Implementar o Compilador Lexical
nav_order: 4
---

# Fase 4: Teste Completo

## 🎯 Objetivo

Validar que automato, lexer e main funcionam juntos corretamente.

## 🧪 Testes unitários

### Teste 1: Automato sozinho

Arquivo: `test_automato.py` (na raiz)

Observacao: no nivel do AFD, palavras reservadas ainda retornam `IDENTIFIER`.
O remapeamento para `CERTIN`, `C_TO_PENSANU`, etc. acontece no Lexer.

```python
"""Teste de unidade do Automato."""

from pathlib import Path

from src.mineres_compilador.automato import Automato


ARQUIVO_AUTOMATO = Path(__file__).resolve().parent / "grafos" / "automato_simples.txt"


def _novo_automato() -> Automato:
    """Cria e carrega uma nova instância do AFD para cada teste."""
    afd = Automato()
    afd.carregar_do_arquivo(str(ARQUIVO_AUTOMATO))
    return afd


def test_automato_reconhece_identifier_basico() -> None:
    """No nível do AFD, palavras reservadas ainda são IDENTIFIER."""
    afd = _novo_automato()

    aceito, token_type, comprimento = afd.reconhecer("certin")

    assert aceito is True, "Deve aceitar 'certin'"
    assert token_type == "IDENTIFIER", f"Deve ser IDENTIFIER, recebeu {token_type}"
    assert comprimento == 6, f"Comprimento deve ser 6, recebeu {comprimento}"
    print("test_automato_reconhece_identifier_basico passou")


def test_automato_reconhece_integer_literal() -> None:
    """Valida literal inteiro aceito pelo AFD atual."""
    afd = _novo_automato()

    aceito, token_type, comprimento = afd.reconhecer("2")

    assert aceito is True, "Deve aceitar '2'"
    assert token_type == "INTEGER_LITERAL", f"Deve ser INTEGER_LITERAL, recebeu {token_type}"
    assert comprimento == 1, f"Comprimento deve ser 1, recebeu {comprimento}"
    print("test_automato_reconhece_integer_literal passou")


def test_automato_reconhece_palavras_reservadas_como_identifier() -> None:
    """Palavras reservadas são classificadas como IDENTIFIER no AFD."""
    afd = _novo_automato()

    palavras = ["c_to_pensanu", "simbora", "cabou", "uai", "eradin"]

    for palavra in palavras:
        aceito, token_type, comprimento = afd.reconhecer(palavra)
        assert aceito is True, f"Deve aceitar '{palavra}'"
        assert token_type == "IDENTIFIER", (
            f"'{palavra}' deve ser IDENTIFIER no AFD, recebeu {token_type}"
        )
        assert comprimento == len(palavra), (
            f"'{palavra}' deve consumir {len(palavra)} caracteres, recebeu {comprimento}"
        )

    print("test_automato_reconhece_palavras_reservadas_como_identifier passou")


def test_automato_aplica_maximo_prefixo_valido() -> None:
    """Se houver sufixo inválido, o AFD devolve o último estado final válido."""
    afd = _novo_automato()

    aceito, token_type, comprimento = afd.reconhecer("certin@@")

    assert aceito is True, "Deve aceitar prefixo válido de 'certin@@'"
    assert token_type == "IDENTIFIER", f"Deve ser IDENTIFIER, recebeu {token_type}"
    assert comprimento == 6, f"Deve consumir apenas 'certin', recebeu {comprimento}"
    print("test_automato_aplica_maximo_prefixo_valido passou")


def test_automato_rejeita_inicio_invalido() -> None:
    """Se o primeiro caractere não possui transição, deve rejeitar."""
    afd = _novo_automato()

    aceito, token_type, comprimento = afd.reconhecer("@@@")

    assert aceito is False, "Deve rejeitar '@@@'"
    assert token_type is None, "Token type deve ser None em rejeição"
    assert comprimento == 0, "Comprimento deve ser 0 em rejeição"
    print("test_automato_rejeita_inicio_invalido passou")


def test_automato_rejeita_entrada_vazia() -> None:
    """Entrada vazia não pode formar token."""
    afd = _novo_automato()

    aceito, token_type, comprimento = afd.reconhecer("")

    assert aceito is False, "Deve rejeitar entrada vazia"
    assert token_type is None, "Token type deve ser None em rejeição"
    assert comprimento == 0, "Comprimento deve ser 0 em rejeição"
    print("test_automato_rejeita_entrada_vazia passou")


if __name__ == "__main__":
    test_automato_reconhece_identifier_basico()
    test_automato_reconhece_integer_literal()
    test_automato_reconhece_palavras_reservadas_como_identifier()
    test_automato_aplica_maximo_prefixo_valido()
    test_automato_rejeita_inicio_invalido()
    test_automato_rejeita_entrada_vazia()
    print("\nTodos os testes de Automato passaram!")
```

Execute:
```bash
python test_automato.py
```

### Teste 2: Lexer sozinho

Arquivo: `test_lexer.py` (na raiz)

```python
"""Teste de unidade do Lexer"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mineres_compilador.lexer import Lexer
from mineres_compilador.tokentype import TokenType


def test_lexer_reconhece_string_simples():
    """Testa tokenização de string simples"""
    lexer = Lexer()
    lexer.carregar_string("certin")
    tokens = lexer.analisar()
    
    assert len(tokens) == 1, f"Deve haver 1 token, recebeu {len(tokens)}"
    assert tokens[0].type == TokenType.CERTIN
    assert tokens[0].lexeme == "certin"
    assert tokens[0].line == 1
    assert tokens[0].column == 1
    print("✅ test_lexer_reconhece_string_simples passou")


def test_lexer_rastreia_posicao():
    """Testa rastreamento correto de linha/coluna"""
    lexer = Lexer()
    lexer.carregar_string("certin eradin")
    tokens = lexer.analisar()
    
    assert len(tokens) == 2
    assert tokens[0].line == 1 and tokens[0].column == 1
    assert tokens[1].line == 1 and tokens[1].column == 8
    print("✅ test_lexer_rastreia_posicao passou")


def test_lexer_reconhece_multiplos_tokens():
    """Testa tokenização de múltiplos tokens"""
    lexer = Lexer()
    lexer.carregar_string("c_to_pensanu 2 uai")
    tokens = lexer.analisar()
    
    assert len(tokens) == 3
    assert tokens[0].type == TokenType.C_TO_PENSANU
    assert tokens[1].type == TokenType.INTEGER_LITERAL
    assert tokens[2].type == TokenType.UAI
    print("✅ test_lexer_reconhece_multiplos_tokens passou")


def test_lexer_arquivo():
    """Testa carregamento de arquivo"""
    lexer = Lexer()
    lexer.carregar_arquivo("exemplos/programa_exemplo.mineires.txt")
    tokens = lexer.analisar()
    
    # Deve reconhecer muitos tokens
    assert len(tokens) > 0, "Deve haver tokens"
    print(f"✅ test_lexer_arquivo passou ({len(tokens)} tokens reconhecidos)")


if __name__ == "__main__":
    test_lexer_reconhece_string_simples()
    test_lexer_rastreia_posicao()
    test_lexer_reconhece_multiplos_tokens()
    test_lexer_arquivo()
    print("\n✅ Todos os testes de Lexer passaram!")
```

Execute:
```bash
python test_lexer.py
```

## 🖥️ Teste de integração (CLI)

### Teste string simples

```bash
python main.py -s "certin"
```

**Saída esperada**:
```
Tokens reconhecidos:
------------------------------------------------------------
Tipo                    Lexema          Linha   Coluna
------------------------------------------------------------
CERTIN                  certin          1       1
------------------------------------------------------------
Total: 1 tokens reconhecidos
```

### Teste string múltipla

```bash
python main.py -s "c_to_pensanu 2 uai"
```

**Saída esperada**:
```
Tokens reconhecidos:
------------------------------------------------------------
Tipo                    Lexema          Linha   Coluna
------------------------------------------------------------
C_TO_PENSANU            c_to_pensanu    1       1
INTEGER_LITERAL         2               1       14
UAI                     uai             1       16
------------------------------------------------------------
Total: 3 tokens reconhecidos
```

### Teste arquivo completo

```bash
python main.py exemplos/programa_exemplo.mineires.txt
```

**Resultado esperado**: ~38 tokens

Você deve ver algo como:
```
Tokens reconhecidos:
------------------------------------------------------------
Tipo                    Lexema          Linha   Coluna
------------------------------------------------------------
BORA_CUMPADE            bora_cumpade    1       1
CABOU                   cabou           2       1
COMMENT_START           causo           3       1
CERTIN                  certin          4       1
C_NAO                   c_nao           5       1
...
```

## ✅ Checklist de validação

### Automato
- [ ] Reconhece palavras-chave corretamente (certin, eradin, c_to_pensanu, etc)
- [ ] Reconhece números (INTEGER_LITERAL)
- [ ] Reconhece identificadores genéricos
- [ ] Retorna (True, tipo, comprimento) para aceição
- [ ] Retorna (False, None, 0) para rejeição

### Lexer
- [ ] Toda string vazia = 0 tokens
- [ ] String com 1 palavra = 1 token
- [ ] String com múltiplas palavras separadas por espaço = múltiplos tokens
- [ ] Rastreamento de linha começa em 1
- [ ] Rastreamento de coluna começa em 1
- [ ] Coluna incrementa com caracteres
- [ ] Coluna reseta em newline
- [ ] Identifica palavras-chave vs identificadores
- [ ] Carrega arquivo corretamente
- [ ] Carrega string corretamente

### Main.py
- [ ] `python main.py` sem argumentos mostra help
- [ ] `python main.py -s "texto"` funciona
- [ ] `python main.py arquivo.txt` funciona
- [ ] Exibe tokens em tabela formatada
- [ ] Exibe total de tokens
- [ ] Mostra mensagem de erro se arquivo não existe
- [ ] Exit code 0 em sucesso
- [ ] Exit code 1 em erro

## 📊 Resultado esperado final

Quando rodar `python main.py exemplos/programa_exemplo.mineires.txt`, você deve ver:

```
Tokens reconhecidos:
------------------------------------------------------------
Tipo                    Lexema          Linha   Coluna
------------------------------------------------------------
BORA_CUMPADE            bora_cumpade    1       1
CABOU                   cabou           2       1
COMMENT_START           causo           3       1
CERTIN                  certin          4       1
C_NAO                   c_nao           5       1
C_NAO_C_TO_PENSANU      c_nao_c_to_pensanu      6       1
C_TO_PENSANU            c_to_pensanu    7       1
DEPENDENU               dependenu       8       1
DU_CASU                 du_casu         9       1
ENQUANTO_TIVER_TREM     enquanto_tiver_trem     10      1
ERADIN                  eradin          11      1
FICA_ASSIM_ENTAO        fica_assim_entao        12      1
COMMENT_END             fim_do_causo    13      1
MEMA_COISA              mema_coisa      14      1
NEH_NADA                neh_nada        15      1
OIA_PROCE_VE            oia_proce_ve    16      1
PARA_O_TREM             para_o_trem     17      1
QUARQUE_UM              quarque_um      18      1
RODA_ESSE_TREM          roda_esse_trem  19      1
SIMBORA                 simbora         20      1
SOB                     sob             21      1
TA_BAO                  ta_bao          22      1
TAMEM                   tamem           23      1
TOCA_O_TREM             toca_o_trem     24      1
TREM_CUM_VIRGULA        trem_cum_virgula        25      1
TREM_DI_NUMERU          trem_di_numeru  26      1
TREM_DISCOLHE           trem_discolhe   27      1
TREM_DISCRITA           trem_discrita   28      1
TROSSO                  trosso          29      1
UAI                     uai             30      1
UM_O_OTO                um_o_oto        31      1
VAM_MARCA               vam_marca       32      1
VEIZ                    veiz            33      1
XOVE                    xove            34      1
IDENTIFIER              a               35      1
FICA_ASSIM_ENTAO        fica_assim_entao        35      3
INTEGER_LITERAL         2               35      20
UAI                     uai             35      22
------------------------------------------------------------
Total: 38 tokens reconhecidos
```

## 🎉 Sucesso!

Se você chegar aqui com tudo funcionando, você completou com sucesso:
- ✅ Implementou um Autômato Finito
- ✅ Implementou um Analisador Léxico
- ✅ Criou uma CLI funcional
- ✅ Tokenizou código Minerês corretamente

**Parabéns! Você aprendeu lexing na prática! 🚀**

## 📚 Próximas etapas

Agora você está pronto para:
- Implementar um **Parser** (análise sintática)
- Criar uma **Árvore de Sintaxe Abstrata (AST)**
- Implementar **análise semântica**
- Gerar **código de máquina virtual** ou **bytecode**
