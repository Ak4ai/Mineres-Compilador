import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analisador_lexico.lexer import Lexer
from analisador_sintatico.analisador_sintatico import Parser, ParserError


class TestRegrasEspecificas(unittest.TestCase):

    # =========================
    # HELPERS
    # =========================

    def _parse_string(self, fonte: str):
        lexer = Lexer()
        lexer.carregar_string(fonte)
        tokens = lexer.analisar(continuar_apos_erro=True)
        return tokens, lexer.errors

    def _assert_valido(self, fonte: str):
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro léxico inesperado")
        self.assertTrue(Parser(tokens).parse())

    def _assert_erro(self, fonte: str, trecho_msg: str = None):
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro léxico inesperado")

        with self.assertRaises(ParserError) as ctx:
            Parser(tokens).parse()

        if trecho_msg:
            self.assertIn(trecho_msg, str(ctx.exception))

    # =========================
    # EXPRESSÕES
    # =========================

    def test_precedencia(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    a fica_assim_entao 1 + 2 veiz 3 uai
cabo
""")

    def test_precedencia_parenteses(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    a fica_assim_entao (1 + 2) veiz 3 uai
cabo
""")

    def test_associatividade(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    a fica_assim_entao 1 - 2 - 3 uai
cabo
""")

    def test_unarios(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    a fica_assim_entao - - + 5 uai
cabo
""")

    def test_parenteses_profundos(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    a fica_assim_entao (((((((((1))))))))) uai
cabo
""")

    # =========================
    # LÓGICOS
    # =========================

    def test_logicos(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    a fica_assim_entao eh quarque_um num_eh tamem eh uai
cabo
""")

    def test_not_encadeado(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    a fica_assim_entao vam_marca vam_marca eh uai
cabo
""")

    # =========================
    # CONTROLE
    # =========================

    def test_if_else(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    uai_se(eh)
        para_o_trem uai
    uai_senao
        toca_o_trem uai
cabo
""")

    def test_if_aninhado(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    uai_se(eh)
        uai_se(num_eh)
            para_o_trem uai
cabo
""")

    def test_while(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    enquanto_tiver_trem(eh)
        para_o_trem uai
cabo
""")

    def test_for_completo(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    roda_esse_trem(i fica_assim_entao 0; i < 10; i fica_assim_entao i + 1)
        para_o_trem uai
cabo
""")

    # =========================
    # CASE
    # =========================

    def test_case_completo(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    dependenu(x) simbora
        du_casu 1: para_o_trem uai
        du_casu 2: toca_o_trem uai
        default: para_o_trem uai
    cabo
cabo
""")

    def test_case_aninhado(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    dependenu(x) simbora
        du_casu 1:
            dependenu(y) simbora
                du_casu 2: para_o_trem uai
                default: toca_o_trem uai
            cabo
    cabo
cabo
""")

    def test_case_sem_default(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    dependenu(x) simbora
        du_casu 1: para_o_trem uai
    cabo
cabo
""")

    # =========================
    # ERROS SINTÁTICOS
    # =========================

    def test_falta_delimitador(self):
        self._assert_erro("""
bora_cumpade main()
simbora
    trem_di_numeru x
cabo
""", "uai")

    def test_expr_invalida(self):
        self._assert_erro("""
bora_cumpade main()
simbora
    a fica_assim_entao 1 + uai
cabo
""", "fator")

    def test_parenteses_errado(self):
        self._assert_erro("""
bora_cumpade main()
simbora
    a fica_assim_entao (1 uai
cabo
""", "RIGHT_PAREN")

    def test_if_sem_parenteses(self):
        self._assert_erro("""
bora_cumpade main()
simbora
    uai_se eh
        para_o_trem uai
cabo
""")

    def test_for_errado(self):
        self._assert_erro("""
bora_cumpade main()
simbora
    roda_esse_trem(i 0 i < 10 i++)
        para_o_trem uai
cabo
""")

    # =========================
    # ROBUSTEZ
    # =========================

    def test_programa_grande(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a, b uai
    a fica_assim_entao 10 uai
    b fica_assim_entao 20 uai

    uai_se(a < b)
        enquanto_tiver_trem(eh)
            para_o_trem uai

    dependenu(a) simbora
        du_casu 1: para_o_trem uai
        default: toca_o_trem uai
    cabo
cabo
""")

    def test_recursao_profunda(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    a fica_assim_entao (((((((((((((1))))))))))))) uai
cabo
""")

    # =========================
    # EDGE CASES
    # =========================

    def test_vazio(self):
        self._assert_erro("", "BORA_CUMPADE")

    def test_sem_bloco(self):
        self._assert_erro("""
bora_cumpade main()
""", "SIMBORA")

    def test_lixo_antes(self):
        self._assert_erro("""
lixo
bora_cumpade main()
simbora
cabo
""", "BORA_CUMPADE")