"""Teste de unidade do Automato."""

import sys
from pathlib import Path

# Garante que o diretório Mineres-Compilador esteja no sys.path quando o teste
# for executado a partir da raiz do repositório.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.mineres_compilador.automato import Automato


# O arquivo do AFD fica em Mineres-Compilador/grafos/, não em testes_individuais/.
ARQUIVO_AUTOMATO = Path(__file__).resolve().parent.parent / "grafos" / "automato_simples.txt"


def _novo_automato() -> Automato:
    """Cria e carrega uma nova instância do AFD para cada teste."""
    afd = Automato()
    afd.carregar_do_arquivo(str(ARQUIVO_AUTOMATO))
    print("[DEBUG] Automato carregado")
    print(f"[DEBUG] arquivo = {ARQUIVO_AUTOMATO}")
    print(f"[DEBUG] estado_inicial = {afd.estado_inicial}")
    print(f"[DEBUG] total_estados = {len(afd.estados)}")
    print(f"[DEBUG] total_transicoes = {len(afd.transicoes)}")
    print(f"[DEBUG] total_estados_finais = {len(afd.estados_finais)}")
    print("[DEBUG]---------------------------------------------")
    return afd


def _debug_result(nome_teste: str, entrada: str, resultado: tuple[bool, str | None, int]) -> None:
    aceito, token_type, comprimento = resultado
    print(f"[DEBUG] {nome_teste}")
    print(f"[DEBUG] entrada = {entrada!r}")
    print(f"[DEBUG] saida.aceito = {aceito}")
    print(f"[DEBUG] saida.token_type = {token_type}")
    print(f"[DEBUG] saida.comprimento = {comprimento}")


def test_automato_reconhece_identifier_basico() -> None:
    """No nível do AFD, palavras reservadas ainda são IDENTIFIER."""
    afd = _novo_automato()

    resultado = afd.reconhecer("certin")
    _debug_result("test_automato_reconhece_identifier_basico", "certin", resultado)
    aceito, token_type, comprimento = resultado

    print("[DEBUG] esperado: aceito=True, token_type='IDENTIFIER', comprimento=6")

    assert aceito is True, "Deve aceitar 'certin'"
    assert token_type == "IDENTIFIER", f"Deve ser IDENTIFIER, recebeu {token_type}"
    assert comprimento == 6, f"Comprimento deve ser 6, recebeu {comprimento}"
    print("test_automato_reconhece_identifier_basico passou")


def test_automato_reconhece_integer_literal() -> None:
    """Valida literal inteiro aceito pelo AFD atual."""
    afd = _novo_automato()

    resultado = afd.reconhecer("2")
    _debug_result("test_automato_reconhece_integer_literal", "2", resultado)
    aceito, token_type, comprimento = resultado

    print("[DEBUG] esperado: aceito=True, token_type='INTEGER_LITERAL', comprimento=1")

    assert aceito is True, "Deve aceitar '2'"
    assert token_type == "INTEGER_LITERAL", f"Deve ser INTEGER_LITERAL, recebeu {token_type}"
    assert comprimento == 1, f"Comprimento deve ser 1, recebeu {comprimento}"
    print("test_automato_reconhece_integer_literal passou")


def test_automato_reconhece_palavras_reservadas_como_identifier() -> None:
    """Palavras reservadas são classificadas como IDENTIFIER no AFD."""
    afd = _novo_automato()

    palavras = ["c_to_pensanu", "simbora", "cabou", "uai", "eradin"]

    for palavra in palavras:
        resultado = afd.reconhecer(palavra)
        _debug_result("test_automato_reconhece_palavras_reservadas_como_identifier", palavra, resultado)
        aceito, token_type, comprimento = resultado
        print(
            f"[DEBUG] esperado para {palavra!r}: "
            f"aceito=True, token_type='IDENTIFIER', comprimento={len(palavra)}"
        )
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

    resultado = afd.reconhecer("certin@@")
    _debug_result("test_automato_aplica_maximo_prefixo_valido", "certin@@", resultado)
    aceito, token_type, comprimento = resultado

    print("[DEBUG] esperado: aceito=True, token_type='IDENTIFIER', comprimento=6")
    print("[DEBUG] observacao: deve consumir apenas o prefixo valido 'certin'")

    assert aceito is True, "Deve aceitar prefixo válido de 'certin@@'"
    assert token_type == "IDENTIFIER", f"Deve ser IDENTIFIER, recebeu {token_type}"
    assert comprimento == 6, f"Deve consumir apenas 'certin', recebeu {comprimento}"
    print("test_automato_aplica_maximo_prefixo_valido passou")


def test_automato_rejeita_inicio_invalido() -> None:
    """Se o primeiro caractere não possui transição, deve rejeitar."""
    afd = _novo_automato()

    resultado = afd.reconhecer("@@@")
    _debug_result("test_automato_rejeita_inicio_invalido", "@@@", resultado)
    aceito, token_type, comprimento = resultado

    print("[DEBUG] esperado: aceito=False, token_type=None, comprimento=0")

    assert aceito is False, "Deve rejeitar '@@@'"
    assert token_type is None, "Token type deve ser None em rejeição"
    assert comprimento == 0, "Comprimento deve ser 0 em rejeição"
    print("test_automato_rejeita_inicio_invalido passou")


def test_automato_rejeita_entrada_vazia() -> None:
    """Entrada vazia não pode formar token."""
    afd = _novo_automato()

    resultado = afd.reconhecer("")
    _debug_result("test_automato_rejeita_entrada_vazia", "", resultado)
    aceito, token_type, comprimento = resultado

    print("[DEBUG] esperado: aceito=False, token_type=None, comprimento=0")

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
