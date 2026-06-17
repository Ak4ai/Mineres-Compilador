import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analisador_sintatico.interpretador import Interpretador


class TestInterpretador(unittest.TestCase):
    def test_print_fica_apenas_no_buffer_de_saida(self):
        codigo = [
            ("call", "print", 'lit:"oi"', "null"),
        ]

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            interpretador = Interpretador(codigo)
            self.assertTrue(interpretador.executar())

        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(interpretador.get_saida(), "oi")

    def test_literais_booleano_hex_octal_e_char(self):
        codigo = [
            ("att", "var:b1", "lit:eh", "null"),
            ("att", "var:b2", "lit:num_eh", "null"),
            ("att", "var:h", "lit:0x10", "null"),
            ("att", "var:o", "lit:010", "null"),
            ("att", "var:c", "lit:'A'", "null"),
        ]

        interpretador = Interpretador(codigo)
        self.assertTrue(interpretador.executar())
        self.assertEqual(interpretador.variaveis["b1"], 1)
        self.assertEqual(interpretador.variaveis["b2"], 0)
        self.assertEqual(interpretador.variaveis["h"], 16)
        self.assertEqual(interpretador.variaveis["o"], 8)
        self.assertEqual(interpretador.variaveis["c"], "A")

    def test_num_eh_segue_ramo_falso(self):
        codigo = [
            ("if", "lit:num_eh", "label1", "label2"),
            ("label", "label1", "null", "null"),
            ("call", "print", 'lit:"true"', "null"),
            ("jump", "label3", "null", "null"),
            ("label", "label2", "null", "null"),
            ("call", "print", 'lit:"false"', "null"),
            ("label", "label3", "null", "null"),
        ]

        interpretador = Interpretador(codigo)
        self.assertTrue(interpretador.executar())
        self.assertEqual(interpretador.get_saida(), "false")

    def test_operacao_invalida_retorna_erro_controlado(self):
        codigo = [
            ("add", "temp1", 'lit:"a"', "lit:1"),
        ]

        interpretador = Interpretador(codigo)
        self.assertFalse(interpretador.executar())
        self.assertIn("Erro na operação 'add'", interpretador.get_erros())

    def test_variavel_nao_declarada_nao_e_inicializada_por_uso(self):
        codigo = [
            ("call", "print", "var:x", "null"),
        ]

        interpretador = Interpretador(codigo)
        self.assertFalse(interpretador.executar())
        self.assertIn("Variável não declarada: 'x'", interpretador.get_erros())

    def test_operacao_com_variavel_nao_declarada_falha(self):
        codigo = [
            ("add", "temp1", "var:x", "lit:1"),
        ]

        interpretador = Interpretador(codigo)
        self.assertFalse(interpretador.executar())
        self.assertIn("Variável não declarada: 'x'", interpretador.get_erros())

    def test_temporario_nao_inicializado_falha(self):
        codigo = [
            ("call", "print", "temp1", "null"),
        ]

        interpretador = Interpretador(codigo)
        self.assertFalse(interpretador.executar())
        self.assertIn("Temporário não inicializado: 'temp1'", interpretador.get_erros())

    def test_divisao_por_zero_falha(self):
        codigo = [
            ("div", "temp1", "lit:10", "lit:0"),
        ]

        interpretador = Interpretador(codigo)
        self.assertFalse(interpretador.executar())
        self.assertIn("Divisão por zero", interpretador.get_erros())


if __name__ == "__main__":
    unittest.main(verbosity=2)
