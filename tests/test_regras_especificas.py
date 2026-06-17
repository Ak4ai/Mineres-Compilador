'''
Suite complementar de regras especificas do parser.

Este arquivo cobre cenarios pontuais de expressoes, controle,
case e erros sintaticos usando fontes em memoria.
'''

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analisador_lexico.lexer import Lexer
from analisador_sintatico.analisador_sintatico import Parser, ParserError, SemanticError
from main import _linhas_codigo_intermediario
from tokentype import TokenType


class TestRegrasEspecificas(unittest.TestCase):
    # Helpers de apoio para montar cenarios de teste em memoria.
    def _parse_string(self, fonte: str):
        lexer = Lexer()
        lexer.carregar_string(fonte)
        tokens = lexer.analisar(continuar_apos_erro=True)
        return tokens, lexer.errors

    def _assert_valido(self, fonte: str):
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")
        self.assertTrue(Parser(tokens).parse())

    def _assert_erro(self, fonte: str, trecho_msg: str = None):
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro léxico inesperado")

        with self.assertRaises(ParserError) as ctx:
            Parser(tokens).parse()

        if trecho_msg:
            self.assertIn(trecho_msg, str(ctx.exception))

    def _assert_erro_semantico(self, fonte: str, trecho_msg: str = None):
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        with self.assertRaises(SemanticError) as ctx:
            Parser(tokens).parse()

        if trecho_msg:
            self.assertIn(trecho_msg, str(ctx.exception))

    # Casos focados em expressoes e precedencia.
    def test_precedencia(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao 1 + 2 veiz 3 uai
cabo
""")

    def test_codigo_intermediario_simples(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru x uai
    x fica_assim_entao 1 + 2 veiz 3 uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro léxico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("mult", "temp1", "lit:2", "lit:3"),
                ("add", "temp2", "lit:1", "temp1"),
                ("att", "var:x", "temp2", "null"),
            ],
        )

    def test_codigo_intermediario_modulo(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru x uai
    x fica_assim_entao 5 % 2 uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("mod", "temp1", "lit:5", "lit:2"),
                ("att", "var:x", "temp1", "null"),
            ],
        )

    def test_codigo_intermediario_hex_octal_em_decimal(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru x uai
    x fica_assim_entao 0x10 + 010 uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("add", "temp1", "lit:16", "lit:8"),
                ("att", "var:x", "temp1", "null"),
            ],
        )

    def test_codigo_intermediario_diferencia_variavel_de_literal(self):
        fonte = """
bora_cumpade main()
simbora
    trem_discrita a, b uai
    a fica_assim_entao "teste" uai
    b fica_assim_entao a + a uai
    b fica_assim_entao a + "a" uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:a", 'lit:"teste"', "null"),
                ("add", "temp1", "var:a", "var:a"),
                ("att", "var:b", "temp1", "null"),
                ("add", "temp2", "var:a", 'lit:"a"'),
                ("att", "var:b", "temp2", "null"),
            ],
        )

    def test_codigo_intermediario_if_sem_else(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru x uai
    x fica_assim_entao 0 uai
    uai_se(x < 10)
        oia_proce_ve(x) uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:x", "lit:0", "null"),
                ("les", "temp1", "var:x", "lit:10"),
                ("if", "temp1", "label1", "label2"),
                ("label", "label1", "null", "null"),
                ("call", "print", "var:x", "null"),
                ("label", "label2", "null", "null"),
            ],
        )

    def test_codigo_intermediario_if_com_else(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru x, y uai
    x fica_assim_entao 1 uai
    y fica_assim_entao 2 uai
    uai_se(eh)
        oia_proce_ve(x) uai
    uai_senao
        oia_proce_ve(y) uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:x", "lit:1", "null"),
                ("att", "var:y", "lit:2", "null"),
                ("if", "lit:eh", "label1", "label2"),
                ("label", "label1", "null", "null"),
                ("call", "print", "var:x", "null"),
                ("jump", "label3", "null", "null"),
                ("label", "label2", "null", "null"),
                ("call", "print", "var:y", "null"),
                ("label", "label3", "null", "null"),
            ],
        )

    def test_codigo_intermediario_while(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru x uai
    x fica_assim_entao 0 uai
    enquanto_tiver_trem(x < 3)
        x fica_assim_entao x + 1 uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:x", "lit:0", "null"),
                ("label", "label1", "null", "null"),
                ("les", "temp1", "var:x", "lit:3"),
                ("if", "temp1", "label2", "label3"),
                ("label", "label2", "null", "null"),
                ("add", "temp2", "var:x", "lit:1"),
                ("att", "var:x", "temp2", "null"),
                ("jump", "label1", "null", "null"),
                ("label", "label3", "null", "null"),
            ],
        )

    def test_codigo_intermediario_while_com_para_o_trem(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru x uai
    x fica_assim_entao 0 uai
    enquanto_tiver_trem(x < 3)
        para_o_trem uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:x", "lit:0", "null"),
                ("label", "label1", "null", "null"),
                ("les", "temp1", "var:x", "lit:3"),
                ("if", "temp1", "label2", "label3"),
                ("label", "label2", "null", "null"),
                ("jump", "label3", "null", "null"),
                ("jump", "label1", "null", "null"),
                ("label", "label3", "null", "null"),
            ],
        )

    def test_codigo_intermediario_for_completo(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru i uai
    roda_esse_trem(i fica_assim_entao 0; i < 10; i fica_assim_entao i + 1)
        oia_proce_ve(i) uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:i", "lit:0", "null"),
                ("label", "label1", "null", "null"),
                ("les", "temp1", "var:i", "lit:10"),
                ("if", "temp1", "label2", "label3"),
                ("label", "label2", "null", "null"),
                ("call", "print", "var:i", "null"),
                ("add", "temp2", "var:i", "lit:1"),
                ("att", "var:i", "temp2", "null"),
                ("jump", "label1", "null", "null"),
                ("label", "label3", "null", "null"),
            ],
        )

    def test_codigo_intermediario_for_com_toca_o_trem(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru i uai
    roda_esse_trem(i fica_assim_entao 0; i < 10; i fica_assim_entao i + 1)
        toca_o_trem uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:i", "lit:0", "null"),
                ("label", "label1", "null", "null"),
                ("les", "temp1", "var:i", "lit:10"),
                ("if", "temp1", "label2", "label3"),
                ("label", "label2", "null", "null"),
                ("jump", "label4", "null", "null"),
                ("label", "label4", "null", "null"),
                ("add", "temp2", "var:i", "lit:1"),
                ("att", "var:i", "temp2", "null"),
                ("jump", "label1", "null", "null"),
                ("label", "label3", "null", "null"),
            ],
        )

    def test_codigo_intermediario_for_sem_condicao(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru i uai
    roda_esse_trem(i fica_assim_entao 0; ; i fica_assim_entao i + 1)
        oia_proce_ve(i) uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:i", "lit:0", "null"),
                ("label", "label1", "null", "null"),
                ("if", "lit:eh", "label2", "label3"),
                ("label", "label2", "null", "null"),
                ("call", "print", "var:i", "null"),
                ("add", "temp1", "var:i", "lit:1"),
                ("att", "var:i", "temp1", "null"),
                ("jump", "label1", "null", "null"),
                ("label", "label3", "null", "null"),
            ],
        )

    def test_string_literal_com_escape_newline_vira_quebra_real_no_token(self):
        fonte = """
bora_cumpade main()
simbora
    oia_proce_ve("a\\nb") uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        string_token = next(
            token for token in tokens if token.type == TokenType.STRING_LITERAL
        )
        self.assertEqual(string_token.lexeme, '"a\nb"')

    def test_codigo_intermediario_escapa_newline_ao_exibir_string(self):
        fonte = """
bora_cumpade main()
simbora
    oia_proce_ve("a\\nb") uai
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [("call", "print", 'lit:"a\nb"', "null")],
        )
        self.assertEqual(
            _linhas_codigo_intermediario(parser.codigo),
            ['(call, print, lit:"a\\nb", null)'],
        )

    def test_codigo_intermediario_for_temporarios_em_ordem_visual(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru i, x, y uai
    x fica_assim_entao 0 uai
    y fica_assim_entao 0 uai
    roda_esse_trem(i fica_assim_entao 0; i < 10; i fica_assim_entao i + 1)
        simbora
            x fica_assim_entao x + 1 uai
            y fica_assim_entao y + x uai
        cabo
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:x", "lit:0", "null"),
                ("att", "var:y", "lit:0", "null"),
                ("att", "var:i", "lit:0", "null"),
                ("label", "label1", "null", "null"),
                ("les", "temp1", "var:i", "lit:10"),
                ("if", "temp1", "label2", "label3"),
                ("label", "label2", "null", "null"),
                ("add", "temp2", "var:x", "lit:1"),
                ("att", "var:x", "temp2", "null"),
                ("add", "temp3", "var:y", "var:x"),
                ("att", "var:y", "temp3", "null"),
                ("add", "temp4", "var:i", "lit:1"),
                ("att", "var:i", "temp4", "null"),
                ("jump", "label1", "null", "null"),
                ("label", "label3", "null", "null"),
            ],
        )

    def test_codigo_intermediario_case_com_default(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru x, y uai
    x fica_assim_entao 1 uai
    dependenu(x) simbora
        du_casu 1: y fica_assim_entao 10 uai
        du_casu 2: y fica_assim_entao 20 uai
        uai_so: y fica_assim_entao 30 uai
    cabo
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:x", "lit:1", "null"),
                ("eq", "temp1", "var:x", "lit:1"),
                ("if", "temp1", "label2", "label3"),
                ("label", "label2", "null", "null"),
                ("att", "var:y", "lit:10", "null"),
                ("jump", "label1", "null", "null"),
                ("label", "label3", "null", "null"),
                ("eq", "temp2", "var:x", "lit:2"),
                ("if", "temp2", "label4", "label5"),
                ("label", "label4", "null", "null"),
                ("att", "var:y", "lit:20", "null"),
                ("jump", "label1", "null", "null"),
                ("label", "label5", "null", "null"),
                ("att", "var:y", "lit:30", "null"),
                ("label", "label1", "null", "null"),
            ],
        )

    def test_codigo_intermediario_case_hex_octal_em_decimal(self):
        fonte = """
bora_cumpade main()
simbora
    trem_di_numeru x, y uai
    x fica_assim_entao 16 uai
    dependenu(x) simbora
        du_casu 0x10: y fica_assim_entao 1 uai
        du_casu 010: y fica_assim_entao 2 uai
    cabo
cabo
"""
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        parser = Parser(tokens)
        self.assertTrue(parser.parse())
        self.assertEqual(
            parser.codigo,
            [
                ("att", "var:x", "lit:16", "null"),
                ("eq", "temp1", "var:x", "lit:16"),
                ("if", "temp1", "label2", "label3"),
                ("label", "label2", "null", "null"),
                ("att", "var:y", "lit:1", "null"),
                ("jump", "label1", "null", "null"),
                ("label", "label3", "null", "null"),
                ("eq", "temp2", "var:x", "lit:8"),
                ("if", "temp2", "label4", "label5"),
                ("label", "label4", "null", "null"),
                ("att", "var:y", "lit:2", "null"),
                ("jump", "label1", "null", "null"),
                ("label", "label5", "null", "null"),
                ("label", "label1", "null", "null"),
            ],
        )

    def test_precedencia_parenteses(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao (1 + 2) veiz 3 uai
cabo
""")

    def test_associatividade(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao 1 - 2 - 3 uai
cabo
""")

    def test_unarios(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao - - + 5 uai
cabo
""")

    def test_parenteses_profundos(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao (((((((((1))))))))) uai
cabo
""")

    # Casos de operadores logicos.
    def test_logicos(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_discolhe a uai
    a fica_assim_entao eh quarque_um num_eh tamem eh uai
cabo
""")

    def test_not_encadeado(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_discolhe a uai
    a fica_assim_entao vam_marca vam_marca eh uai
cabo
""")

    # Casos de comandos de controle.
    def test_if_else(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    uai_se(eh)
        uai
    uai_senao
        uai
cabo
""")

    def test_if_aninhado(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    uai_se(eh)
        uai_se(num_eh)
            uai
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
    trem_di_numeru i uai
    roda_esse_trem(i fica_assim_entao 0; i < 10; i fica_assim_entao i + 1)
        para_o_trem uai
cabo
""")

    # Casos da estrutura dependenu/du_casu/uai_so.
    def test_case_completo(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru x uai
    x fica_assim_entao 1 uai
    dependenu(x) simbora
        du_casu 1: uai
        du_casu 2: uai
        uai_so: uai
    cabo
cabo
""")

    def test_case_aninhado(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru x, y uai
    x fica_assim_entao 1 uai
    y fica_assim_entao 2 uai
    dependenu(x) simbora
        du_casu 1:
            dependenu(y) simbora
                du_casu 2: uai
                uai_so: uai
            cabo
    cabo
cabo
""")

    def test_case_sem_default(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru x uai
    x fica_assim_entao 1 uai
    dependenu(x) simbora
        du_casu 1: uai
    cabo
cabo
""")

    def test_case_nao_aceita_identificador_como_caso(self):
        self._assert_erro("""
bora_cumpade main()
simbora
    trem_di_numeru x, y uai
    x fica_assim_entao 1 uai
    y fica_assim_entao 1 uai
    dependenu(x) simbora
        du_casu y: uai
    cabo
cabo
""", "fatorZinMenorAinda")

    # Casos de erro sintatico.
    def test_falta_delimitador(self):
        self._assert_erro("""
bora_cumpade main()
simbora
    trem_di_numeru x
cabo
""", "uai")

    def test_ponto_virgula_fora_do_for_invalido(self):
        self._assert_erro("""
bora_cumpade main()
simbora
    trem_di_numeru x;
cabo
""", "uai")

    def test_expr_invalida(self):
        self._assert_erro("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao 1 + uai
cabo
""", "fator")

    def test_parenteses_errado(self):
        self._assert_erro("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
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
    trem_di_numeru i uai
    roda_esse_trem(i 0 i < 10 i++)
        para_o_trem uai
cabo
""")

    # Casos de robustez com programas maiores.
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
        du_casu 1: uai
        uai_so: uai
    cabo
cabo
""")

    def test_recursao_profunda(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao (((((((((((((1))))))))))))) uai
cabo
""")

    def test_erro_semantico_variavel_nao_declarada(self):
        self._assert_erro_semantico("""
bora_cumpade main()
simbora
    a fica_assim_entao 1 uai
cabo
""", "nao declarada")

    def test_erro_semantico_condicao_nao_booleana(self):
        self._assert_erro_semantico("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao 1 uai
    uai_se(a)
        para_o_trem uai
cabo
""", "booleana")

    def test_escopo_permite_sombrear_variavel_em_bloco_interno(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao 1 uai
    simbora
        trem_di_numeru a uai
        a fica_assim_entao 2 uai
    cabo
    a fica_assim_entao a + 1 uai
cabo
""")

    def test_erro_semantico_variavel_fora_do_escopo(self):
        self._assert_erro_semantico("""
bora_cumpade main()
simbora
    simbora
        trem_di_numeru a uai
        a fica_assim_entao 1 uai
    cabo
    a fica_assim_entao 2 uai
cabo
""", "nao declarada")

    def test_erro_semantico_variavel_nao_inicializada(self):
        self._assert_erro_semantico("""
bora_cumpade main()
simbora
    trem_di_numeru a, b uai
    b fica_assim_entao a + 1 uai
cabo
""", "antes de receber valor")

    def test_erro_semantico_para_o_trem_fora_de_laco(self):
        self._assert_erro_semantico("""
bora_cumpade main()
simbora
    para_o_trem uai
cabo
""", "dentro de laco")

    def test_int_recebe_float_por_familia_numerica(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao 1.5 uai
cabo
""")

    def test_comparacao_entre_int_e_float_valida(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    trem_cum_virgula b uai
    trem_discolhe resultado uai
    a fica_assim_entao 1 uai
    b fica_assim_entao 1.5 uai
    resultado fica_assim_entao a < b uai
cabo
""")

    def test_atribuicao_entre_variaveis_numericas_valida(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    trem_cum_virgula b uai
    b fica_assim_entao 1.5 uai
    a fica_assim_entao b uai
cabo
""")

    def test_float_com_operacao_float_valido(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_cum_virgula a, b uai
    a fica_assim_entao 1.5 uai
    b fica_assim_entao a + 2.5 uai
cabo
""")

    # Casos de borda.
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
