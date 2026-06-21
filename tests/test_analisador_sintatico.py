'''
Suite principal de testes do analisador sintatico.

Este arquivo valida o fluxo completo lexer -> parser usando os
arquivos de entrada do projeto (casos validos e erros esperados).
'''

import re
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
ENTRADAS_DIR = ROOT_DIR / "entradas"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analisador_lexico.lexer import Lexer
from analisador_sintatico.analisador_sintatico import Parser, ParserError, SemanticError


class TestAnalisadorSintatico(unittest.TestCase):
    PARSER_ERROR_PATTERN = re.compile(
        r"^Erro sintático: esperado .+, mas recebeu .+ na linha \d+, coluna \d+$"
    )

    def _analisar_arquivo(self, arquivo: Path):
        lexer = Lexer()
        lexer.carregar_arquivo(str(arquivo))
        tokens = lexer.analisar(continuar_apos_erro=True)
        return tokens, lexer.errors

    def test_casos_validos_passam_no_parser(self):
        pasta = ENTRADAS_DIR / "casos_validos"
        arquivos = sorted(p for p in pasta.iterdir() if p.is_file())
        self.assertGreater(len(arquivos), 0, "Nao ha arquivos em entradas/casos_validos")

        for arquivo in arquivos:
            with self.subTest(arquivo=arquivo.name):
                tokens, erros_lexicos = self._analisar_arquivo(arquivo)
                self.assertEqual(
                    erros_lexicos,
                    [],
                    f"Esperava zero erros lexicos em {arquivo.name}",
                )

                resultado = Parser(tokens).parse()
                self.assertTrue(resultado, f"Parser deveria retornar True em {arquivo.name}")

    def test_erros_lexicos_falham_no_lexer(self):
        pasta = ENTRADAS_DIR / "erros_lexicos"
        arquivos = sorted(p for p in pasta.iterdir() if p.is_file())
        self.assertGreater(len(arquivos), 0, "Nao ha arquivos em entradas/erros_lexicos")

        for arquivo in arquivos:
            with self.subTest(arquivo=arquivo.name):
                _, erros_lexicos = self._analisar_arquivo(arquivo)
                self.assertGreater(
                    len(erros_lexicos),
                    0,
                    f"Esperava ao menos um erro lexico em {arquivo.name}",
                )

    def test_erros_sintaticos_falham_no_parser(self):
        pasta = ENTRADAS_DIR / "erros_sintaticos"
        arquivos = sorted(p for p in pasta.iterdir() if p.is_file())
        self.assertGreater(len(arquivos), 0, "Nao ha arquivos em entradas/erros_sintaticos")

        for arquivo in arquivos:
            with self.subTest(arquivo=arquivo.name):
                tokens, erros_lexicos = self._analisar_arquivo(arquivo)
                self.assertEqual(
                    erros_lexicos,
                    [],
                    f"Arquivo de erro sintatico nao deveria falhar no lexer: {arquivo.name}",
                )

                with self.assertRaises(ParserError) as ctx:
                    Parser(tokens).parse()

                msg = str(ctx.exception)
                self.assertRegex(
                    msg,
                    self.PARSER_ERROR_PATTERN,
                    f"Formato de erro sintatico inesperado em {arquivo.name}: {msg}",
                )

    def test_erros_semanticos_falham_no_parser(self):
        pasta = ENTRADAS_DIR / "erros_semanticos"
        arquivos = sorted(p for p in pasta.iterdir() if p.is_file())
        self.assertGreater(len(arquivos), 0, "Nao ha arquivos em entradas/erros_semanticos")

        for arquivo in arquivos:
            with self.subTest(arquivo=arquivo.name):
                tokens, erros_lexicos = self._analisar_arquivo(arquivo)
                self.assertEqual(
                    erros_lexicos,
                    [],
                    f"Arquivo de erro semantico nao deveria falhar no lexer: {arquivo.name}",
                )

                with self.assertRaises(SemanticError):
                    Parser(tokens).parse()

    def test_formato_do_erro_sintatico(self):
        # Sem 'cabo' para forcar erro sintatico previsivel.
        fonte = "bora_cumpade main()\nsimbora\n    uai\n"

        lexer = Lexer()
        lexer.carregar_string(fonte)
        tokens = lexer.analisar(continuar_apos_erro=True)
        self.assertEqual(lexer.errors, [])

        with self.assertRaises(ParserError) as ctx:
            Parser(tokens).parse()

        self.assertRegex(str(ctx.exception), self.PARSER_ERROR_PATTERN)

    def assertParserErrorContains(self, arquivo: Path, expected_msg_part: str):
        tokens, erros_lexicos = self._analisar_arquivo(arquivo)
        self.assertEqual(erros_lexicos, [], f"Erro léxico inesperado em {arquivo.name}")

        with self.assertRaises(ParserError) as ctx:
            Parser(tokens).parse()

        msg = str(ctx.exception)
        self.assertIn(
            expected_msg_part,
            msg,
            (
                f"Esperava mensagem contendo '{expected_msg_part}' em "
                f"{arquivo.name}, mas veio: {msg}"
            ),
        )

    def test_case_default_sem_colon(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "sint_default_sem_colon.txt"
        self.assertParserErrorContains(arquivo, "COLON")

    def test_case_sem_casos(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "erro_case_sem_casos.txt"
        self.assertParserErrorContains(arquivo, "DU_CASU")

    def test_for_sem_ponto_virgula(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "erro_for_sem_ponto_virgula.txt"
        self.assertParserErrorContains(arquivo, "SEMICOLON")

    def test_if_sem_parenteses(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "erro_if_sem_parenteses.txt"
        self.assertParserErrorContains(arquivo, "LEFT_PAREN")

    def test_while_sem_expr(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "erro_while_sem_condicao.txt"
        self.assertParserErrorContains(arquivo, "fator")

    def test_declaracao_invalida(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "erro_virgula_sem_identificador.txt"
        self.assertParserErrorContains(arquivo, "IDENTIFIER")

    def test_expr_invalida(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "erro_operador_sem_operando.txt"
        self.assertParserErrorContains(arquivo, "fator")

    def test_io_lista_invalida(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "erro_io_virgula_final.txt"
        self.assertParserErrorContains(arquivo, "fator")

    def test_token_nao_suportado(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "erro_ta_bao.txt"
        self.assertParserErrorContains(arquivo, "CABO")

    def test_lixo_apos_programa(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "erro_lixo_apos_programa.txt"
        self.assertParserErrorContains(arquivo, "EOF")

    def test_case_dois_default(self):
        arquivo = ENTRADAS_DIR / "erros_sintaticos" / "erro_dois_default.txt"
        self.assertParserErrorContains(arquivo, "DU_CASU")

    # Helpers de apoio para montar cenarios de teste em memoria.

    def _parse_string(self, fonte: str):
        lexer = Lexer()
        lexer.carregar_string(fonte)
        tokens = lexer.analisar(continuar_apos_erro=True)
        return tokens, lexer.errors

    def _assert_valido(self, fonte: str):
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Não deveria haver erro léxico")
        resultado = Parser(tokens).parse()
        self.assertTrue(resultado)

    def _assert_erro_sintatico(self, fonte: str, expected_msg_part: str = None):
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro léxico inesperado")

        with self.assertRaises(ParserError) as ctx:
            Parser(tokens).parse()

        if expected_msg_part:
            self.assertIn(expected_msg_part, str(ctx.exception))

    def _assert_erro_semantico(self, fonte: str, expected_msg_part: str = None):
        tokens, erros = self._parse_string(fonte)
        self.assertEqual(erros, [], "Erro lexico inesperado")

        with self.assertRaises(SemanticError) as ctx:
            Parser(tokens).parse()

        if expected_msg_part:
            self.assertIn(expected_msg_part, str(ctx.exception))

    # Casos focados em expressoes e precedencia.

    def test_precedencia_operadores(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao 1 + 2 veiz 3 uai
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

    def test_parenteses_aninhados(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao (((((1))))) uai
cabo
""")

    def test_unarios_encadeados(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao - - + 5 uai
cabo
""")

    # Casos de operadores logicos.

    def test_operadores_logicos(self):
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

    def test_if_else_aninhado(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    uai_se(eh)
        uai_se(num_eh)
            uai
        uai_senao
            uai
cabo
""")

    def test_while_com_bloco(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    enquanto_tiver_trem(eh)
        simbora
            para_o_trem uai
        cabo
cabo
""")

    def test_for_completo_complexo(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru i uai
    roda_esse_trem(i fica_assim_entao 0; i < 10; i fica_assim_entao i + 1)
        simbora
            para_o_trem uai
        cabo
cabo
""")

    # Casos da estrutura dependenu/du_casu/default.

    def test_case_completo(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru x uai
    x fica_assim_entao 1 uai
    dependenu(x) simbora
        du_casu 1: uai
        du_casu 2: uai
        default: uai
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
                default: uai
            cabo
    cabo
cabo
""")

    # Casos de erro sintatico mais sutis.

    def test_falta_delimitador(self):
        self._assert_erro_sintatico("""
bora_cumpade main()
simbora
    trem_di_numeru x
cabo
""", "uai")

    def test_parenteses_vazio_expr(self):
        self._assert_erro_sintatico("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao () uai
cabo
""", "fator")

    def test_operador_sem_operando(self):
        self._assert_erro_sintatico("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao 1 + uai
cabo
""", "fator")

    def test_excesso_parenteses(self):
        self._assert_erro_sintatico("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao (1 uai
cabo
""", "RIGHT_PAREN")

    # Casos de robustez com programas maiores.

    def test_programa_grande(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a, b, c uai
    a fica_assim_entao 10 uai
    b fica_assim_entao 20 uai
    c fica_assim_entao a + b veiz 2 uai

    uai_se(c > 10)
        enquanto_tiver_trem(eh)
            para_o_trem uai

    dependenu(c) simbora
        du_casu 1: uai
        default: uai
    cabo
cabo
""")

    def test_muitos_niveis_recursao(self):
        self._assert_valido("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao (((((((((((1))))))))))) uai
cabo
""")

    def test_erro_semantico_variavel_nao_declarada(self):
        self._assert_erro_semantico("""
bora_cumpade main()
simbora
    a fica_assim_entao 1 uai
cabo
""", "nao declarada")

    def test_erro_semantico_redeclaracao(self):
        self._assert_erro_semantico("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    trem_di_numeru a uai
cabo
""", "ja declarada")

    def test_erro_semantico_tipos_incompativeis(self):
        self._assert_erro_semantico("""
bora_cumpade main()
simbora
    trem_di_numeru a uai
    a fica_assim_entao "texto" uai
cabo
""", "tipos incompativeis")

    # Casos de borda.

    def test_programa_vazio_invalido(self):
        self._assert_erro_sintatico("", "BORA_CUMPADE")

    def test_main_sem_bloco(self):
        self._assert_erro_sintatico("""
bora_cumpade main()
""", "SIMBORA")

    def test_lixo_antes_programa(self):
        self._assert_erro_sintatico("""
lixo
bora_cumpade main()
simbora
cabo
""", "BORA_CUMPADE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
