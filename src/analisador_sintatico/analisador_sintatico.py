from __future__ import annotations

from mineires_token import Token
from tokentype import TokenType

COMMENT_TOKEN_TYPES = frozenset({TokenType.COMMENT_LINE, TokenType.COMMENT_BLOCK})

TYPE_START_TOKEN_TYPES = frozenset(
    {
        TokenType.TREM_DI_NUMERU,
        TokenType.TREM_CUM_VIRGULA,
        TokenType.TREM_DISCRITA,
        TokenType.TREM_DISCOLHE,
        TokenType.TROSSO,
    }
)

NUMINT_TOKEN_TYPES = frozenset(
    {
        TokenType.INTEGER_LITERAL,
        TokenType.HEX_LITERAL,
        TokenType.OCTAL_LITERAL,
    }
)

BOOLEAN_LITERAL_TOKEN_TYPES = frozenset({TokenType.EH, TokenType.NUM_EH})

EXPR_START_TOKEN_TYPES = frozenset(
    {
        TokenType.IDENTIFIER,
        TokenType.STRING_LITERAL,
        TokenType.INTEGER_LITERAL,
        TokenType.FLOAT_LITERAL,
        TokenType.HEX_LITERAL,
        TokenType.OCTAL_LITERAL,
        TokenType.CHAR_LITERAL,
        *BOOLEAN_LITERAL_TOKEN_TYPES,
        TokenType.LEFT_PAREN,
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.VAM_MARCA,
    }
)

STMT_START_TOKEN_TYPES = frozenset(
    {
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
)

IO_STMT_TOKEN_TYPES = frozenset({TokenType.XOVE, TokenType.OIA_PROCE_VE})

GRAMMAR_TOKEN_ALIASES: dict[str, frozenset[TokenType]] = {
    "IDENT": frozenset({TokenType.IDENTIFIER}),
    "NUMint": NUMINT_TOKEN_TYPES,
    "NUMfloat": frozenset({TokenType.FLOAT_LITERAL}),
    "STR": frozenset({TokenType.STRING_LITERAL}),
    "valorBooleano": BOOLEAN_LITERAL_TOKEN_TYPES,
    "valorChar": frozenset({TokenType.CHAR_LITERAL}),
    "uai": frozenset({TokenType.UAI}),
}


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
            if t.type not in COMMENT_TOKEN_TYPES
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

    def make_var(self, nome: str) -> str:
        return f"var:{nome}"

    def make_lit(self, valor: str) -> str:
        return f"lit:{valor}"

    def is_temp(self, valor: str) -> bool:
        return valor.startswith("temp") and valor[4:].isdigit()

    def is_label(self, valor: str) -> bool:
        return valor.startswith("label") and valor[5:].isdigit()

    def normalize_operand(self, valor):
        if valor is None:
            return "null"
        if not isinstance(valor, str):
            return valor
        if valor == "null":
            return valor
        if valor.startswith(("var:", "lit:")):
            return valor
        if self.is_temp(valor) or self.is_label(valor):
            return valor
        return valor

    def emit(self, op, result=None, arg1=None, arg2=None) -> None:
        # Padroniza campos ausentes como "null" para manter a saida estavel.
        self.codigo.append(
            (
                op,
                self.normalize_operand(result),
                self.normalize_operand(arg1),
                self.normalize_operand(arg2),
            )
        )

    def print_codigo(self) -> None:
        for op, result, arg1, arg2 in self.codigo:
            print(f"({op}, {result}, {arg1}, {arg2})")

    def _capture_stmt_code(self) -> list[tuple[str, str, str, str]]:
        # Permite montar codigo de controle de fluxo sem mudar a gramatica.
        codigo_anterior = self.codigo
        self.codigo = []
        self.stmt()
        codigo_capturado = self.codigo
        self.codigo = codigo_anterior
        return codigo_capturado

    def _capture_expr_code(self) -> tuple[list[tuple[str, str, str, str]], str]:
        # Captura codigo de expressoes usadas fora do fluxo linear padrao.
        codigo_anterior = self.codigo
        self.codigo = []
        result = self.atrib()
        codigo_capturado = self.codigo
        self.codigo = codigo_anterior
        return codigo_capturado, result

    def _is_temp_name(self, value: str) -> bool:
        return self.is_temp(value)

    def _refresh_temp_names(
        self, codigo: list[tuple[str, str, str, str]]
    ) -> list[tuple[str, str, str, str]]:
        # Recria nomes temporarios na ordem de emissao efetiva.
        mapping: dict[str, str] = {}
        codigo_atualizado = []

        for op, result, arg1, arg2 in codigo:
            new_result = result
            if self._is_temp_name(result):
                new_result = mapping.setdefault(result, self.new_temp())

            new_arg1 = arg1
            if self._is_temp_name(arg1) and arg1 in mapping:
                new_arg1 = mapping[arg1]

            new_arg2 = arg2
            if self._is_temp_name(arg2) and arg2 in mapping:
                new_arg2 = mapping[arg2]

            codigo_atualizado.append((op, new_result, new_arg1, new_arg2))

        return codigo_atualizado

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
        if tok.type in TYPE_START_TOKEN_TYPES:
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
        if tok.type in IO_STMT_TOKEN_TYPES:
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
        codigo_init = []
        if self._is_expr_start(self.current()):
            codigo_init, _ = self._capture_expr_code()
        self.consume(TokenType.SEMICOLON)
        codigo_cond = []
        cond = self.make_lit("eh")
        if self._is_expr_start(self.current()):
            codigo_cond, cond = self._capture_expr_code()
        self.consume(TokenType.SEMICOLON)
        codigo_inc = []
        if self._is_expr_start(self.current()):
            temp_count_before_inc = self.temp_count
            codigo_inc, _ = self._capture_expr_code()
            self.temp_count = temp_count_before_inc
        self.consume(TokenType.RIGHT_PAREN)
        codigo_body = self._capture_stmt_code()

        label_start = self.new_label()
        label_body = self.new_label()
        label_end = self.new_label()

        self.codigo.extend(codigo_init)
        self.emit("label", label_start)
        self.codigo.extend(codigo_cond)
        self.emit("if", cond, label_body, label_end)
        self.emit("label", label_body)
        self.codigo.extend(codigo_body)
        self.codigo.extend(self._refresh_temp_names(codigo_inc))
        self.emit("jump", label_start)
        self.emit("label", label_end)

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
            self.emit("call", "read", self.make_var(ident.lexeme))
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
        label_start = self.new_label()
        label_body = self.new_label()
        label_end = self.new_label()

        self.consume(TokenType.ENQUANTO_TIVER_TREM)
        self.consume(TokenType.LEFT_PAREN)
        self.emit("label", label_start)
        cond = self.expr()
        self.consume(TokenType.RIGHT_PAREN)
        self.emit("if", cond, label_body, label_end)
        self.emit("label", label_body)
        self.stmt()
        self.emit("jump", label_start)
        self.emit("label", label_end)

    def if_stmt(self) -> None:
        # If com else opcional.
        self.consume(TokenType.UAI_SE)
        self.consume(TokenType.LEFT_PAREN)
        cond = self.expr()
        self.consume(TokenType.RIGHT_PAREN)

        codigo_if = self._capture_stmt_code()

        if self._matches(TokenType.UAI_SENAO):
            label_true = self.new_label()
            label_false = self.new_label()
            label_end = self.new_label()

            self.emit("if", cond, label_true, label_false)
            self.emit("label", label_true)
            self.codigo.extend(codigo_if)
            self.emit("jump", label_end)

            self.consume(TokenType.UAI_SENAO)
            codigo_else = self._capture_stmt_code()

            self.emit("label", label_false)
            self.codigo.extend(codigo_else)
            self.emit("label", label_end)
            return

        label_true = self.new_label()
        label_end = self.new_label()
        self.emit("if", cond, label_true, label_end)
        self.emit("label", label_true)
        self.codigo.extend(codigo_if)
        self.emit("label", label_end)

    def else_part(self) -> None:
        # Parte opcional do senao.
        if self._matches(TokenType.UAI_SENAO):
            self.consume(TokenType.UAI_SENAO)
            self.stmt()

    def case_stmt(self) -> None:
        # Estrutura dependenu/du_casu/uai_so.
        self.consume(TokenType.DEPENDENU)
        self.consume(TokenType.LEFT_PAREN)
        ident = self.make_var(self.consume(TokenType.IDENTIFIER).lexeme)
        self.consume(TokenType.RIGHT_PAREN)
        self.consume(TokenType.SIMBORA)
        label_end = self.new_label()
        self.dos_casos(ident, label_end)
        self.emit("label", label_end)
        self.consume(TokenType.CABO)

    def dos_casos(self, ident: str, label_end: str) -> None:
        # Primeiro caso obrigatorio.
        self.do_caso(ident, label_end)
        self.resto_dos_casos(ident, label_end)

    def do_caso(self, ident: str, label_end: str) -> None:
        # Um bloco du_casu.
        self.consume(TokenType.DU_CASU)
        valor = self.fator_zin()
        self.consume(TokenType.COLON)
        codigo_case = self._capture_stmt_code()

        temp = self.new_temp()
        label_case = self.new_label()
        label_next = self.new_label()

        self.emit("eq", temp, ident, valor)
        self.emit("if", temp, label_case, label_next)
        self.emit("label", label_case)
        self.codigo.extend(codigo_case)
        self.emit("jump", label_end)
        self.emit("label", label_next)

    def resto_dos_casos(self, ident: str, label_end: str) -> None:
        # Casos seguintes e opcional uai_so.
        if self._matches(TokenType.DU_CASU):
            self.do_caso(ident, label_end)
            self.resto_dos_casos(ident, label_end)
            return

        if self._matches(TokenType.UAI_SO):
            self.consume(TokenType.UAI_SO)
            self.consume(TokenType.COLON)
            codigo_default = self._capture_stmt_code()
            self.codigo.extend(codigo_default)

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
        # Aceita `fica_assim_entao` ou operador `=` como alternativa de atribuicao.
        if self._matches(TokenType.FICA_ASSIM_ENTAO) or self._matches(TokenType.ASSIGN):
            if self._matches(TokenType.FICA_ASSIM_ENTAO):
                self.consume(TokenType.FICA_ASSIM_ENTAO)
            else:
                self.consume(TokenType.ASSIGN)
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
        # Aceita operador palavra `veiz` ou simbolo '*' como multiplicacao.
        if self._matches(TokenType.VEIZ) or self._matches(TokenType.MULT):
            if self._matches(TokenType.VEIZ):
                self.consume(TokenType.VEIZ)
            else:
                self.consume(TokenType.MULT)
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
            self.emit("sub", temp, self.make_lit("0"), value)
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
            return self.make_lit(self.consume(TokenType.STRING_LITERAL).lexeme)
        if self._matches(TokenType.IDENTIFIER):
            return self.make_var(self.consume(TokenType.IDENTIFIER).lexeme)
        if self._matches(TokenType.INTEGER_LITERAL):
            return self.make_lit(self.consume(TokenType.INTEGER_LITERAL).lexeme)
        if self._matches(TokenType.HEX_LITERAL):
            return self.make_lit(self.consume(TokenType.HEX_LITERAL).lexeme)
        if self._matches(TokenType.OCTAL_LITERAL):
            return self.make_lit(self.consume(TokenType.OCTAL_LITERAL).lexeme)
        if self._matches(TokenType.FLOAT_LITERAL):
            return self.make_lit(self.consume(TokenType.FLOAT_LITERAL).lexeme)
        if self._matches(TokenType.EH):
            return self.make_lit(self.consume(TokenType.EH).lexeme)
        if self._matches(TokenType.NUM_EH):
            return self.make_lit(self.consume(TokenType.NUM_EH).lexeme)
        if self._matches(TokenType.CHAR_LITERAL):
            return self.make_lit(self.consume(TokenType.CHAR_LITERAL).lexeme)

        tok = self.current()
        raise ParserError(
            "fator (STR | IDENT | NUMint | NUMfloat | valorBooleano | valorChar)",
            self._received_label(tok),
            tok.line,
            tok.column,
        )

    # Bloco 6: helpers de validacao
    def consume_delimiter(self) -> Token:
        # Delimitador de comando: aceita tanto 'uai' quanto ';'
        tok = self.current()
        if self._matches(TokenType.UAI):
            return self.consume(TokenType.UAI)
        if self._matches(TokenType.SEMICOLON):
            return self.consume(TokenType.SEMICOLON)
        raise ParserError("uai ou ;", self._received_label(tok), tok.line, tok.column)

    def _is_type_start(self, tok: Token) -> bool:
        # Diz se o token pode iniciar declaracao de tipo.
        return tok.type in TYPE_START_TOKEN_TYPES

    def _is_expr_start(self, tok: Token) -> bool:
        # Diz se o token pode iniciar uma expressao.
        return tok.type in EXPR_START_TOKEN_TYPES

    def _is_stmt_start(self, tok: Token) -> bool:
        # FIRST(stmt): ajuda stmt_list a saber quando parar.
        return (
            tok.type in STMT_START_TOKEN_TYPES
            or self._is_type_start(tok)
            or self._is_expr_start(tok)
        )

    def _matches(self, expected) -> bool:
        # Compara token atual com TokenType ou com atalhos textuais.
        tok = self.current()

        if isinstance(expected, TokenType):
            return tok.type == expected

        if isinstance(expected, str):
            # Atalhos de notacao da gramatica ficam centralizados em um unico mapa.
            if expected in GRAMMAR_TOKEN_ALIASES:
                return tok.type in GRAMMAR_TOKEN_ALIASES[expected]

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
