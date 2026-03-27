"""Teste de unidade do Lexer"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mineres_compilador.lexer import Lexer
from src.mineres_compilador.tokentype import TokenType

ARQUIVO_EXEMPLO = (
    Path(__file__).resolve().parent.parent / "exemplos" / "programa_exemplo.mineires.txt"
)


def _novo_lexer() -> Lexer:
    lexer = Lexer()
    print("[DEBUG] Lexer criado")
    print(f"[DEBUG] arquivo_exemplo = {ARQUIVO_EXEMPLO}")
    print("[DEBUG]---------------------------------------------")
    return lexer


def _debug_tokens(nome_teste: str, entrada: str, tokens: list) -> None:
    print(f"[DEBUG] {nome_teste}")
    print(f"[DEBUG] entrada = {entrada!r}")
    print(f"[DEBUG] total_tokens = {len(tokens)}")
    for i, token in enumerate(tokens):
        print(
            f"[DEBUG] token[{i}] type={token.type.value}, "
            f"lexeme={token.lexeme!r}, line={token.line}, column={token.column}"
        )


def test_lexer_reconhece_string_simples():
    """Testa tokenização de string simples"""
    lexer = _novo_lexer()
    entrada = "certin"
    lexer.carregar_string(entrada)
    tokens = lexer.analisar()

    _debug_tokens("test_lexer_reconhece_string_simples", entrada, tokens)
    print("[DEBUG] esperado: 1 token CERTIN em L1:C1")

    assert len(tokens) == 1, f"Deve haver 1 token, recebeu {len(tokens)}"
    assert tokens[0].type == TokenType.CERTIN
    assert tokens[0].lexeme == "certin"
    assert tokens[0].line == 1
    assert tokens[0].column == 1
    print("test_lexer_reconhece_string_simples passou")


def test_lexer_rastreia_posicao():
    """Testa rastreamento correto de linha/coluna"""
    lexer = _novo_lexer()
    entrada = "certin eradin"
    lexer.carregar_string(entrada)
    tokens = lexer.analisar()

    _debug_tokens("test_lexer_rastreia_posicao", entrada, tokens)
    print("[DEBUG] esperado: token[0] em L1:C1 e token[1] em L1:C8")

    assert len(tokens) == 2
    assert tokens[0].line == 1 and tokens[0].column == 1
    assert tokens[1].line == 1 and tokens[1].column == 8
    print("test_lexer_rastreia_posicao passou")


def test_lexer_reconhece_multiplos_tokens():
    """Testa tokenização de múltiplos tokens"""
    lexer = _novo_lexer()
    entrada = "c_to_pensanu 2 uai"
    lexer.carregar_string(entrada)
    tokens = lexer.analisar()

    _debug_tokens("test_lexer_reconhece_multiplos_tokens", entrada, tokens)
    print("[DEBUG] esperado: C_TO_PENSANU, INTEGER_LITERAL, UAI")

    assert len(tokens) == 3
    assert tokens[0].type == TokenType.C_TO_PENSANU
    assert tokens[1].type == TokenType.INTEGER_LITERAL
    assert tokens[2].type == TokenType.UAI
    print("test_lexer_reconhece_multiplos_tokens passou")


def test_lexer_arquivo():
    """Testa carregamento de arquivo"""
    lexer = _novo_lexer()
    lexer.carregar_arquivo(str(ARQUIVO_EXEMPLO))
    tokens = lexer.analisar()

    _debug_tokens("test_lexer_arquivo", str(ARQUIVO_EXEMPLO), tokens)
    print("[DEBUG] esperado: pelo menos 1 token")

    # Deve reconhecer muitos tokens
    assert len(tokens) > 0, "Deve haver tokens"
    print(f"test_lexer_arquivo passou ({len(tokens)} tokens reconhecidos)")


if __name__ == "__main__":
    test_lexer_reconhece_string_simples()
    test_lexer_rastreia_posicao()
    test_lexer_reconhece_multiplos_tokens()
    test_lexer_arquivo()
    print("\nTodos os testes de Lexer passaram!")
