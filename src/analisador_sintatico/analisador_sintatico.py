from __future__ import annotations

from mineires_token import Token
from tokentype import TokenType


class ParserError(Exception):
    # Erro sintatico: para no primeiro ponto invalido.
    def __init__(self, expected: str, received: str, line: int, column: int) -> None:
        super().__init__(
            f"Erro sintático: esperado {expected}, mas recebeu {received} "
            f"na linha {line}, coluna {column}"
        )


class Parser:
    # Parser recursivo: valida a estrutura do programa.

    def __init__(self, tokens: list[Token]):
        # Ignora comentarios: eles nao entram na analise sintatica.
        self.tokens = [
            t
            for t in tokens
            if t.type not in {TokenType.COMMENT_LINE, TokenType.COMMENT_BLOCK}
        ]
        self.pos = 0
        self.codigo = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self) -> str:
        self.temp_count += 1
        return f"temp{self.temp_count}"

    def new_label(self) -> str:
        self.label_count += 1
        return f"label{self.label_count}"

    def emit(self, op, result=None, arg1=None, arg2=None) -> None:
        # Padroniza campos ausentes como "null" para manter a saida estavel.
        self.codigo.append(
            (
                op,
                "null" if result is None else result,
                "null" if arg1 is None else arg1,
                "null" if arg2 is None else arg2,
            )
        )

    def print_codigo(self) -> None:
        for op, result, arg1, arg2 in self.codigo:
            print(f"({op}, {result}, {arg1}, {arg2})")

    # Parte 1: navegacao na lista de tokens
    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        # Fallback de seguranca (normalmente sempre existe EOF).
        return self.tokens[-1]

    def advance(self) -> None:
        if self.pos < len(self.tokens) - 1:
            self.pos += 1

    def consume(self, expected_type) -> Token:
        # Consome token esperado; se nao casar, dispara erro com linha/coluna.
        tok = self.current()
        if self._matches(expected_type):
            self.advance()
            return tok

        expected_label = self._expected_label(expected_type)
        raise ParserError(expected_label, self._received_label(tok), tok.line, tok.column)

    # Parte 2: porta de entrada do parser
    def parse(self) -> bool:
        # Regra inicial + EOF: garante que todo o arquivo foi consumido.
        self.function()
        self.consume(TokenType.EOF)
        return True

    # Parte 3: estrutura geral do programa
    def function(self) -> None:
        # Programa obrigatorio: bora_cumpade main() seguido de bloco.
        self.consume(TokenType.BORA_CUMPADE)
        self.consume(TokenType.MAIN)
        self.consume(TokenType.LEFT_PAREN)
        self.consume(TokenType.RIGHT_PAREN)
        self.bloco()

    def type_rule(self) -> None:
        # Aceita um dos tipos primitivos da linguagem.
        tok = self.current()
        if tok.type in {
            TokenType.TREM_DI_NUMERU,
            TokenType.TREM_CUM_VIRGULA,
            TokenType.TREM_DISCRITA,
            TokenType.TREM_DISCOLHE,
            TokenType.TROSSO,
        }:
            self.consume(tok.type)
            return
        raise ParserError("<type>", self._received_label(tok), tok.line, tok.column)

    def bloco(self) -> None:
        # Bloco: abre com simbora e fecha com cabo.
        self.consume(TokenType.SIMBORA)
        self.stmt_list()
        self.consume(TokenType.CABO)

    def stmt_list(self) -> None:
        # Lista de comandos: repete enquanto houver inicio de stmt.
        if self._is_stmt_start(self.current()):
            self.stmt()
            self.stmt_list()

    # Parte 4: comandos
    def stmt(self) -> None:
        # Escolhe qual comando parsear olhando o token atual.
        tok = self.current()

        # FOR
        if tok.type == TokenType.RODA_ESSE_TREM:
            self.for_stmt()
            return

        # IO (entrada/saida)
        if tok.type in {TokenType.XOVE, TokenType.OIA_PROCE_VE}:
            self.io_stmt()
            return

        # WHILE
        if tok.type == TokenType.ENQUANTO_TIVER_TREM:
            self.while_stmt()
            return

        # IF
        if tok.type == TokenType.UAI_SE:
            self.if_stmt()
            return

        # CASE
        if tok.type == TokenType.DEPENDENU:
            self.case_stmt()
            return

        # BLOCO
        if tok.type == TokenType.SIMBORA:
            self.bloco()
            return

        # PARA_O_TREM
        if tok.type == TokenType.PARA_O_TREM:
            self.consume(TokenType.PARA_O_TREM)
            self.consume_delimiter()
            return

        # TOCA_O_TREM
        if tok.type == TokenType.TOCA_O_TREM:
            self.consume(TokenType.TOCA_O_TREM)
            self.consume_delimiter()
            return

        # DECLARACAO
        if self._is_type_start(tok):
            self.declaration()
            return

        if tok.type == TokenType.UAI:
            # Comando vazio (apenas delimitador).
            self.consume_delimiter()
            return

        # Se comecar com expressao, trata como atribuicao/comando de expressao.
        if self._is_expr_start(tok):
            self.atrib()
            self.consume_delimiter()
            return

        raise ParserError("<stmt>", self._received_label(tok), tok.line, tok.column)

    def declaration(self) -> None:
        # Declaracao: tipo + lista de nomes + uai.
        self.type_rule()
        self.ident_list()
        self.consume_delimiter()

    def ident_list(self) -> None:
        # Primeiro identificador da declaracao.
        self.consume(TokenType.IDENTIFIER)
        self.resto_ident_list()

    def resto_ident_list(self) -> None:
        # Continua lista de identificadores separados por virgula.
        if self._matches(TokenType.COMMA):
            self.consume(TokenType.COMMA)
            self.consume(TokenType.IDENTIFIER)
            self.resto_ident_list()

    def for_stmt(self) -> None:
        # For: roda_esse_trem(expr; expr; expr) + comando/bloco.
        self.consume(TokenType.RODA_ESSE_TREM)
        self.consume(TokenType.LEFT_PAREN)
        self.opt_expr()
        self.consume(TokenType.SEMICOLON)
        self.opt_expr()
        self.consume(TokenType.SEMICOLON)
        self.opt_expr()
        self.consume(TokenType.RIGHT_PAREN)
        self.stmt()

    def opt_expr(self) -> None:
        # Expressao opcional (pode ficar vazia no for).
        if self._is_expr_start(self.current()):
            self.atrib()

    def io_stmt(self) -> None:
        # Comandos de entrada/saida.
        if self._matches(TokenType.XOVE):
            self.consume(TokenType.XOVE)
            self.consume(TokenType.LEFT_PAREN)
            self.type_rule()
            self.consume(TokenType.COMMA)
            ident = self.consume(TokenType.IDENTIFIER)
            self.consume(TokenType.RIGHT_PAREN)
            self.consume_delimiter()
            self.emit("call", "read", ident.lexeme)
            return

        self.consume(TokenType.OIA_PROCE_VE)
        self.consume(TokenType.LEFT_PAREN)
        self.out_list()
        self.consume(TokenType.RIGHT_PAREN)
        self.consume_delimiter()

    def out_list(self) -> None:
        # Lista de itens para saida.
        self.out()
        self.resto_out_list()

    def out(self) -> str:
        # Um item de saida.
        value = self.fator_zin()
        self.emit("call", "print", value)
        return value

    def resto_out_list(self) -> None:
        # Itens extras da lista de saida.
        if self._matches(TokenType.COMMA):
            self.consume(TokenType.COMMA)
            self.out()
            self.resto_out_list()

    def while_stmt(self) -> None:
        # While: enquanto tiver trem (expr) + comando/bloco.
        self.consume(TokenType.ENQUANTO_TIVER_TREM)
        self.consume(TokenType.LEFT_PAREN)
        self.expr()
        self.consume(TokenType.RIGHT_PAREN)
        self.stmt()

    def if_stmt(self) -> None:
        # If com else opcional.
        self.consume(TokenType.UAI_SE)
        self.consume(TokenType.LEFT_PAREN)
        self.expr()
        self.consume(TokenType.RIGHT_PAREN)
        self.stmt()
        self.else_part()

    def else_part(self) -> None:
        # Parte opcional do senao.
        if self._matches(TokenType.UAI_SENAO):
            self.consume(TokenType.UAI_SENAO)
            self.stmt()

    def case_stmt(self) -> None:
        # Estrutura dependenu/du_casu/uai_so.
        self.consume(TokenType.DEPENDENU)
        self.consume(TokenType.LEFT_PAREN)
        self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.RIGHT_PAREN)
        self.consume(TokenType.SIMBORA)
        self.dos_casos()
        self.consume(TokenType.CABO)

    def dos_casos(self) -> None:
        # Primeiro caso obrigatorio.
        self.do_caso()
        self.resto_dos_casos()

    def do_caso(self) -> None:
        # Um bloco du_casu.
        self.consume(TokenType.DU_CASU)
        self.fator_zin()
        self.consume(TokenType.COLON)
        self.stmt()

    def resto_dos_casos(self) -> None:
        # Casos seguintes e opcional uai_so.
        if self._matches(TokenType.DU_CASU):
            self.do_caso()
            self.resto_dos_casos()
            return

        if self._matches(TokenType.UAI_SO):
            self.consume(TokenType.UAI_SO)
            self.consume(TokenType.COLON)
            self.stmt()

    # Parte 5: expressoes (com precedencia)
    def expr(self) -> str:
        # Entrada da expressao.
        return self.atrib()

    def atrib(self) -> str:
        # Nivel de atribuicao.
        left = self.or_rule()
        return self.resto_atrib(left)

    def resto_atrib(self, left: str) -> str:
        # Continua atribuicao (associativa a direita).
        if self._matches(TokenType.FICA_ASSIM_ENTAO):
            self.consume(TokenType.FICA_ASSIM_ENTAO)
            right = self.atrib()
            self.emit("att", left, right)
            return left
        return left

    def or_rule(self) -> str:
        # Operador logico OR.
        left = self.xor_rule()
        return self.resto_or(left)

    def resto_or(self, left: str) -> str:
        # Encadeamento de OR.
        if self._matches(TokenType.QUARQUE_UM):
            self.consume(TokenType.QUARQUE_UM)
            right = self.xor_rule()
            temp = self.new_temp()
            self.emit("or", temp, left, right)
            return self.resto_or(temp)
        return left

    def xor_rule(self) -> str:
        # Operador logico XOR.
        left = self.and_rule()
        return self.resto_xor(left)

    def resto_xor(self, left: str) -> str:
        # Encadeamento de XOR.
        if self._matches(TokenType.UM_O_OTO):
            self.consume(TokenType.UM_O_OTO)
            right = self.and_rule()
            temp = self.new_temp()
            self.emit("xor", temp, left, right)
            return self.resto_xor(temp)
        return left

    def and_rule(self) -> str:
        # Operador logico AND.
        left = self.not_rule()
        return self.resto_and(left)

    def resto_and(self, left: str) -> str:
        # Encadeamento de AND.
        if self._matches(TokenType.TAMEM):
            self.consume(TokenType.TAMEM)
            right = self.not_rule()
            temp = self.new_temp()
            self.emit("and", temp, left, right)
            return self.resto_and(temp)
        return left

    def not_rule(self) -> str:
        # Operador logico NOT unario.
        if self._matches(TokenType.VAM_MARCA):
            self.consume(TokenType.VAM_MARCA)
            value = self.not_rule()
            temp = self.new_temp()
            self.emit("not", temp, value)
            return temp
        return self.rel()

    def rel(self) -> str:
        # Comparacoes relacionais.
        left = self.add()
        return self.resto_rel(left)

    def resto_rel(self, left: str) -> str:
        # Operadores ==, !=, <, <=, >, >=.
        if self._matches(TokenType.MEMA_COISA):
            self.consume(TokenType.MEMA_COISA)
            right = self.add()
            temp = self.new_temp()
            self.emit("eq", temp, left, right)
            return temp
        if self._matches(TokenType.NEH_NADA):
            self.consume(TokenType.NEH_NADA)
            right = self.add()
            temp = self.new_temp()
            self.emit("dif", temp, left, right)
            return temp
        if self._matches(TokenType.LT):
            self.consume(TokenType.LT)
            right = self.add()
            temp = self.new_temp()
            self.emit("les", temp, left, right)
            return temp
        if self._matches(TokenType.LE):
            self.consume(TokenType.LE)
            right = self.add()
            temp = self.new_temp()
            self.emit("leq", temp, left, right)
            return temp
        if self._matches(TokenType.GT):
            self.consume(TokenType.GT)
            right = self.add()
            temp = self.new_temp()
            self.emit("grt", temp, left, right)
            return temp
        if self._matches(TokenType.GE):
            self.consume(TokenType.GE)
            right = self.add()
            temp = self.new_temp()
            self.emit("geq", temp, left, right)
            return temp
        return left

    def add(self) -> str:
        # Soma e subtracao.
        left = self.mult()
        return self.resto_add(left)

    def resto_add(self, left: str) -> str:
        # Encadeamento de + e -.
        if self._matches(TokenType.PLUS):
            self.consume(TokenType.PLUS)
            right = self.mult()
            temp = self.new_temp()
            self.emit("add", temp, left, right)
            return self.resto_add(temp)
        if self._matches(TokenType.MINUS):
            self.consume(TokenType.MINUS)
            right = self.mult()
            temp = self.new_temp()
            self.emit("sub", temp, left, right)
            return self.resto_add(temp)
        return left

    def mult(self) -> str:
        # Multiplicacao e divisoes.
        left = self.uno()
        return self.resto_mult(left)

    def resto_mult(self, left: str) -> str:
        # Encadeamento de veiz/sob///%.
        if self._matches(TokenType.VEIZ):
            self.consume(TokenType.VEIZ)
            right = self.uno()
            temp = self.new_temp()
            self.emit("mult", temp, left, right)
            return self.resto_mult(temp)
        if self._matches(TokenType.SOB):
            self.consume(TokenType.SOB)
            right = self.uno()
            temp = self.new_temp()
            self.emit("div", temp, left, right)
            return self.resto_mult(temp)
        if self._matches(TokenType.INT_DIV):
            self.consume(TokenType.INT_DIV)
            right = self.uno()
            temp = self.new_temp()
            self.emit("divI", temp, left, right)
            return self.resto_mult(temp)
        if self._matches(TokenType.MOD):
            self.consume(TokenType.MOD)
            right = self.uno()
            temp = self.new_temp()
            self.emit("divI", temp, left, right)
            return self.resto_mult(temp)
        return left

    def uno(self) -> str:
        # Unarios + e -.
        if self._matches(TokenType.PLUS):
            self.consume(TokenType.PLUS)
            return self.uno()
        if self._matches(TokenType.MINUS):
            self.consume(TokenType.MINUS)
            value = self.uno()
            temp = self.new_temp()
            self.emit("sub", temp, "0", value)
            return temp
        return self.fator_zao()

    def fator_zao(self) -> str:
        # Fator com ou sem parenteses.
        if self._matches(TokenType.LEFT_PAREN):
            self.consume(TokenType.LEFT_PAREN)
            value = self.atrib()
            self.consume(TokenType.RIGHT_PAREN)
            return value
        return self.fator_zin()

    def fator_zin(self) -> str:
        # Menor unidade de expressao: literal ou identificador.
        if self._matches(TokenType.STRING_LITERAL):
            return self.consume(TokenType.STRING_LITERAL).lexeme
        if self._matches(TokenType.IDENTIFIER):
            return self.consume(TokenType.IDENTIFIER).lexeme
        if self._matches(TokenType.INTEGER_LITERAL):
            return self.consume(TokenType.INTEGER_LITERAL).lexeme
        if self._matches(TokenType.HEX_LITERAL):
            return self.consume(TokenType.HEX_LITERAL).lexeme
        if self._matches(TokenType.OCTAL_LITERAL):
            return self.consume(TokenType.OCTAL_LITERAL).lexeme
        if self._matches(TokenType.FLOAT_LITERAL):
            return self.consume(TokenType.FLOAT_LITERAL).lexeme
        if self._matches(TokenType.EH):
            return self.consume(TokenType.EH).lexeme
        if self._matches(TokenType.NUM_EH):
            return self.consume(TokenType.NUM_EH).lexeme
        if self._matches(TokenType.CHAR_LITERAL):
            return self.consume(TokenType.CHAR_LITERAL).lexeme

        tok = self.current()
        raise ParserError(
            "fator (STR | IDENT | NUMint | NUMfloat | valorBooleano | valorChar)",
            self._received_label(tok),
            tok.line,
            tok.column,
        )

    # Bloco 6: helpers de validacao
    def consume_delimiter(self) -> Token:
        # Delimitador de comando fora do for.
        tok = self.current()
        if self._matches(TokenType.UAI):
            return self.consume(TokenType.UAI)
        raise ParserError("uai", self._received_label(tok), tok.line, tok.column)

    def _is_type_start(self, tok: Token) -> bool:
        # Diz se o token pode iniciar declaracao de tipo.
        return tok.type in {
            TokenType.TREM_DI_NUMERU,
            TokenType.TREM_CUM_VIRGULA,
            TokenType.TREM_DISCRITA,
            TokenType.TREM_DISCOLHE,
            TokenType.TROSSO,
        }

    def _is_expr_start(self, tok: Token) -> bool:
        # Diz se o token pode iniciar uma expressao.
        return tok.type in {
            TokenType.IDENTIFIER,
            TokenType.STRING_LITERAL,
            TokenType.INTEGER_LITERAL,
            TokenType.FLOAT_LITERAL,
            TokenType.HEX_LITERAL,
            TokenType.OCTAL_LITERAL,
            TokenType.CHAR_LITERAL,
            TokenType.EH,
            TokenType.NUM_EH,
            TokenType.LEFT_PAREN,
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.VAM_MARCA,
        }

    def _is_stmt_start(self, tok: Token) -> bool:
        # FIRST(stmt): ajuda stmt_list a saber quando parar.
        return (
            tok.type
            in {
                TokenType.RODA_ESSE_TREM,
                TokenType.XOVE,
                TokenType.OIA_PROCE_VE,
                TokenType.ENQUANTO_TIVER_TREM,
                TokenType.UAI_SE,
                TokenType.DEPENDENU,
                TokenType.SIMBORA,
                TokenType.PARA_O_TREM,
                TokenType.TOCA_O_TREM,
                TokenType.UAI,
            }
            or self._is_type_start(tok)
            or self._is_expr_start(tok)
        )

    def _matches(self, expected) -> bool:
        # Compara token atual com TokenType ou com atalhos textuais.
        tok = self.current()

        if isinstance(expected, TokenType):
            return tok.type == expected

        if isinstance(expected, str):
            # Atalhos de notacao da gramatica.
            if expected == "IDENT":
                return tok.type == TokenType.IDENTIFIER
            if expected == "NUMint":
                return tok.type in {
                    TokenType.INTEGER_LITERAL,
                    TokenType.HEX_LITERAL,
                    TokenType.OCTAL_LITERAL,
                }
            if expected == "NUMfloat":
                return tok.type == TokenType.FLOAT_LITERAL
            if expected == "STR":
                return tok.type == TokenType.STRING_LITERAL
            if expected == "valorBooleano":
                return tok.type in {TokenType.EH, TokenType.NUM_EH}
            if expected == "valorChar":
                return tok.type == TokenType.CHAR_LITERAL

            # Delimitador de comando fora do for.
            if expected == "uai":
                return tok.type == TokenType.UAI

            # Compatibilidade com terminais por nome, valor ou lexema literal.
            return (
                tok.type.name == expected
                or tok.type.value == expected
                or tok.lexeme == expected
            )

        return False

    def _expected_label(self, expected) -> str:
        # Texto amigavel do "esperado" para mensagem de erro.
        if isinstance(expected, TokenType):
            return expected.name
        return str(expected)

    def _received_label(self, tok: Token) -> str:
        # Texto do token recebido: lexema quando possivel.
        return tok.lexeme if tok.lexeme else tok.type.name
