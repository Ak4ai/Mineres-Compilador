"""Teste de unidade do Lexer"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mineres_compilador.lexer import Lexer
from src.mineres_compilador.tokentype import TokenType


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
