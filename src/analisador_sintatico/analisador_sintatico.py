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


class SemanticError(Exception):
    # Erro semantico: para na primeira inconsistencia detectada.
    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(f"Erro semantico: {message} na linha {line}, coluna {column}")


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
        self.scopes = [{}]
        self.vars_table = self.scopes[0]
        self.temp_types = {}
        self.loop_depth = 0

    def _raise_semantic_error(self, message: str, tok: Token) -> None:
        raise SemanticError(message, tok.line, tok.column)

    def _type_family(self, tipo) -> str | None:
        if tipo == TokenType.TREM_DI_NUMERU:
            return "int"
        if tipo == TokenType.TREM_CUM_VIRGULA:
            return "float"
        if tipo == TokenType.TREM_DISCRITA:
            return "str"
        if tipo == TokenType.TREM_DISCOLHE:
            return "bool"
        if tipo == TokenType.TROSSO:
            return "char"
        if tipo in {"int", "float", "str", "bool", "char"}:
            return tipo
        return None

    def _literal_type_family(self, valor: str) -> str:
        if valor in {"eh", "num_eh"}:
            return "bool"
        if valor.startswith('"'):
            return "str"
        if valor.startswith("'"):
            return "char"
        if "." in valor:
            return "float"
        return "int"

    def _is_numeric_type(self, tipo: str | None) -> bool:
        return tipo in {"int", "float"}

    def _numeric_result_type(self, left_type: str, right_type: str) -> str:
        if "float" in {left_type, right_type}:
            return "float"
        return "int"

    def _push_scope(self) -> None:
        self.scopes.append({})

    def _pop_scope(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()

    def _lookup_symbol(self, nome: str):
        for scope in reversed(self.scopes):
            if nome in scope:
                return scope[nome]
        return None

    def _operand_type_family(
        self,
        operando: str,
        tok: Token | None = None,
        require_initialized: bool = False,
    ) -> str | None:
        if operando == "null":
            return None
        if operando.startswith("var:"):
            nome = operando[4:]
            symbol = self._lookup_symbol(nome)
            if symbol is None and tok is not None:
                self._raise_semantic_error(f"variavel '{nome}' nao declarada", tok)
            if (
                symbol is not None
                and require_initialized
                and not symbol["initialized"]
                and tok is not None
            ):
                self._raise_semantic_error(
                    f"variavel '{nome}' usada antes de receber valor",
                    tok,
                )
            if symbol is None:
                return None
            return self._type_family(symbol["type"])
        if operando.startswith("lit:"):
            return self._literal_type_family(operando[4:])
        if self.is_temp(operando):
            tipo = self.temp_types.get(operando)
            if tipo is None and tok is not None:
                self._raise_semantic_error(
                    f"tipo desconhecido para temporario '{operando}'",
                    tok,
                )
            return tipo
        return None

    def _register_temp_type(self, temp: str, tipo: str) -> None:
        if self.is_temp(temp):
            self.temp_types[temp] = tipo

    def _declare_identifier(self, ident: Token, tipo) -> None:
        current_scope = self.scopes[-1]
        if ident.lexeme in current_scope:
            self._raise_semantic_error(
                f"variavel '{ident.lexeme}' ja declarada",
                ident,
            )
        current_scope[ident.lexeme] = {"type": tipo, "initialized": False}

    def _ensure_declared_identifier(self, ident: Token) -> None:
        if self._lookup_symbol(ident.lexeme) is None:
            self._raise_semantic_error(
                f"variavel '{ident.lexeme}' nao declarada",
                ident,
            )

    def _mark_initialized(self, operando: str) -> None:
        if not operando.startswith("var:"):
            return
        symbol = self._lookup_symbol(operando[4:])
        if symbol is not None:
            symbol["initialized"] = True

    def _ensure_assignable(self, operando: str, tok: Token) -> None:
        if not operando.startswith("var:"):
            self._raise_semantic_error(
                "lado esquerdo da atribuicao deve ser uma variavel",
                tok,
            )

    def _ensure_same_family(
        self,
        left: str,
        right: str,
        tok: Token,
        contexto: str,
        check_left_initialized: bool = True,
        check_right_initialized: bool = True,
    ) -> str:
        left_type = self._operand_type_family(left, tok, check_left_initialized)
        right_type = self._operand_type_family(right, tok, check_right_initialized)

        if left_type != right_type:
            self._raise_semantic_error(
                f"tipos incompativeis em {contexto}: {left_type} e {right_type}",
                tok,
            )

        return left_type

    def _ensure_numeric(self, operando: str, tok: Token, contexto: str) -> None:
        tipo = self._operand_type_family(operando, tok, True)
        if not self._is_numeric_type(tipo):
            self._raise_semantic_error(
                f"{contexto} exige operando numerico, mas recebeu {tipo}",
                tok,
            )

    def _ensure_add_types(self, left: str, right: str, tok: Token) -> str:
        left_type = self._operand_type_family(left, tok, True)
        right_type = self._operand_type_family(right, tok, True)

        if self._is_numeric_type(left_type) and self._is_numeric_type(right_type):
            return self._numeric_result_type(left_type, right_type)
        if left_type == right_type and left_type == "str":
            return "str"

        self._raise_semantic_error(
            f"tipos incompativeis em soma: {left_type} e {right_type}",
            tok,
        )

    def _ensure_boolean(self, operando: str, tok: Token, contexto: str) -> None:
        tipo = self._operand_type_family(operando, tok, True)
        if tipo != "bool":
            self._raise_semantic_error(
                f"{contexto} exige expressao booleana, mas recebeu {tipo}",
                tok,
            )

    def _ensure_read_type(self, ident: Token, tipo_lido) -> None:
        self._ensure_declared_identifier(ident)
        symbol = self._lookup_symbol(ident.lexeme)
        tipo_variavel = symbol["type"]
        if tipo_variavel != tipo_lido:
            self._raise_semantic_error(
                (
                    f"tipo de leitura incompativel para '{ident.lexeme}': "
                    f"{tipo_lido.value} em variavel {tipo_variavel.value}"
                ),
                ident,
            )
        symbol["initialized"] = True

    def _ensure_loop_control(self, tok: Token) -> None:
        if self.loop_depth == 0:
            self._raise_semantic_error(
                f"'{tok.lexeme}' so pode ser usado dentro de laco",
                tok,
            )

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

    def type_rule(self):
        # Aceita um dos tipos primitivos da linguagem.
        tok = self.current()
        if tok.type in TYPE_START_TOKEN_TYPES:
            self.consume(tok.type)
            return tok.type
        raise ParserError("<type>", self._received_label(tok), tok.line, tok.column)

    def bloco(self) -> None:
        # Bloco: abre com simbora e fecha com cabo.
        self.consume(TokenType.SIMBORA)
        self._push_scope()
        self.stmt_list()
        self.consume(TokenType.CABO)
        self._pop_scope()

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
            control_tok = self.consume(TokenType.PARA_O_TREM)
            self._ensure_loop_control(control_tok)
            self.consume_delimiter()
            return

        # TOCA_O_TREM
        if tok.type == TokenType.TOCA_O_TREM:
            control_tok = self.consume(TokenType.TOCA_O_TREM)
            self._ensure_loop_control(control_tok)
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
        tipo = self.type_rule()
        self.ident_list(tipo)
        self.consume_delimiter()

    def ident_list(self, tipo) -> None:
        # Primeiro identificador da declaracao.
        ident = self.consume(TokenType.IDENTIFIER)
        self._declare_identifier(ident, tipo)
        self.resto_ident_list(tipo)

    def resto_ident_list(self, tipo) -> None:
        # Continua lista de identificadores separados por virgula.
        if self._matches(TokenType.COMMA):
            self.consume(TokenType.COMMA)
            ident = self.consume(TokenType.IDENTIFIER)
            self._declare_identifier(ident, tipo)
            self.resto_ident_list(tipo)

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
            self._ensure_boolean(cond, self.current(), "condicao do for")
        self.consume(TokenType.SEMICOLON)
        codigo_inc = []
        if self._is_expr_start(self.current()):
            temp_count_before_inc = self.temp_count
            codigo_inc, _ = self._capture_expr_code()
            self.temp_count = temp_count_before_inc
        self.consume(TokenType.RIGHT_PAREN)
        self.loop_depth += 1
        codigo_body = self._capture_stmt_code()
        self.loop_depth -= 1

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
            tipo_lido = self.type_rule()
            self.consume(TokenType.COMMA)
            ident = self.consume(TokenType.IDENTIFIER)
            self._ensure_read_type(ident, tipo_lido)
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
        self._ensure_boolean(cond, self.current(), "condicao do enquanto")
        self.consume(TokenType.RIGHT_PAREN)
        self.emit("if", cond, label_body, label_end)
        self.emit("label", label_body)
        self.loop_depth += 1
        self.stmt()
        self.loop_depth -= 1
        self.emit("jump", label_start)
        self.emit("label", label_end)

    def if_stmt(self) -> None:
        # If com else opcional.
        self.consume(TokenType.UAI_SE)
        self.consume(TokenType.LEFT_PAREN)
        cond = self.expr()
        self._ensure_boolean(cond, self.current(), "condicao do if")
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
        ident_tok = self.consume(TokenType.IDENTIFIER)
        self._ensure_declared_identifier(ident_tok)
        ident = self.make_var(ident_tok.lexeme)
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
        self._ensure_same_family(ident, valor, self.current(), "case")
        self.consume(TokenType.COLON)
        codigo_case = self._capture_stmt_code()

        temp = self.new_temp()
        self._register_temp_type(temp, "bool")
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
                op_tok = self.consume(TokenType.FICA_ASSIM_ENTAO)
            else:
                op_tok = self.consume(TokenType.ASSIGN)
            self._ensure_assignable(left, op_tok)
            right = self.atrib()
            self._ensure_same_family(
                left,
                right,
                op_tok,
                "atribuicao",
                check_left_initialized=False,
            )
            self.emit("att", left, right)
            self._mark_initialized(left)
            return left
        return left

    def or_rule(self) -> str:
        # Operador logico OR.
        left = self.xor_rule()
        return self.resto_or(left)

    def resto_or(self, left: str) -> str:
        # Encadeamento de OR.
        if self._matches(TokenType.QUARQUE_UM):
            op_tok = self.consume(TokenType.QUARQUE_UM)
            right = self.xor_rule()
            self._ensure_boolean(left, op_tok, "operacao logica")
            self._ensure_boolean(right, op_tok, "operacao logica")
            temp = self.new_temp()
            self._register_temp_type(temp, "bool")
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
            op_tok = self.consume(TokenType.UM_O_OTO)
            right = self.and_rule()
            self._ensure_boolean(left, op_tok, "operacao logica")
            self._ensure_boolean(right, op_tok, "operacao logica")
            temp = self.new_temp()
            self._register_temp_type(temp, "bool")
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
            op_tok = self.consume(TokenType.TAMEM)
            right = self.not_rule()
            self._ensure_boolean(left, op_tok, "operacao logica")
            self._ensure_boolean(right, op_tok, "operacao logica")
            temp = self.new_temp()
            self._register_temp_type(temp, "bool")
            self.emit("and", temp, left, right)
            return self.resto_and(temp)
        return left

    def not_rule(self) -> str:
        # Operador logico NOT unario.
        if self._matches(TokenType.VAM_MARCA):
            op_tok = self.consume(TokenType.VAM_MARCA)
            value = self.not_rule()
            self._ensure_boolean(value, op_tok, "operacao not")
            temp = self.new_temp()
            self._register_temp_type(temp, "bool")
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
            op_tok = self.consume(TokenType.MEMA_COISA)
            right = self.add()
            self._ensure_same_family(left, right, op_tok, "comparacao")
            temp = self.new_temp()
            self._register_temp_type(temp, "bool")
            self.emit("eq", temp, left, right)
            return temp
        if self._matches(TokenType.NEH_NADA):
            op_tok = self.consume(TokenType.NEH_NADA)
            right = self.add()
            self._ensure_same_family(left, right, op_tok, "comparacao")
            temp = self.new_temp()
            self._register_temp_type(temp, "bool")
            self.emit("dif", temp, left, right)
            return temp
        if self._matches(TokenType.LT):
            op_tok = self.consume(TokenType.LT)
            right = self.add()
            self._ensure_numeric(left, op_tok, "comparacao relacional")
            self._ensure_numeric(right, op_tok, "comparacao relacional")
            temp = self.new_temp()
            self._register_temp_type(temp, "bool")
            self.emit("les", temp, left, right)
            return temp
        if self._matches(TokenType.LE):
            op_tok = self.consume(TokenType.LE)
            right = self.add()
            self._ensure_numeric(left, op_tok, "comparacao relacional")
            self._ensure_numeric(right, op_tok, "comparacao relacional")
            temp = self.new_temp()
            self._register_temp_type(temp, "bool")
            self.emit("leq", temp, left, right)
            return temp
        if self._matches(TokenType.GT):
            op_tok = self.consume(TokenType.GT)
            right = self.add()
            self._ensure_numeric(left, op_tok, "comparacao relacional")
            self._ensure_numeric(right, op_tok, "comparacao relacional")
            temp = self.new_temp()
            self._register_temp_type(temp, "bool")
            self.emit("grt", temp, left, right)
            return temp
        if self._matches(TokenType.GE):
            op_tok = self.consume(TokenType.GE)
            right = self.add()
            self._ensure_numeric(left, op_tok, "comparacao relacional")
            self._ensure_numeric(right, op_tok, "comparacao relacional")
            temp = self.new_temp()
            self._register_temp_type(temp, "bool")
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
            op_tok = self.consume(TokenType.PLUS)
            right = self.mult()
            result_type = self._ensure_add_types(left, right, op_tok)
            temp = self.new_temp()
            self._register_temp_type(temp, result_type)
            self.emit("add", temp, left, right)
            return self.resto_add(temp)
        if self._matches(TokenType.MINUS):
            op_tok = self.consume(TokenType.MINUS)
            right = self.mult()
            self._ensure_numeric(left, op_tok, "operacao aritmetica")
            self._ensure_numeric(right, op_tok, "operacao aritmetica")
            temp = self.new_temp()
            left_type = self._operand_type_family(left, op_tok, True)
            right_type = self._operand_type_family(right, op_tok, True)
            self._register_temp_type(temp, self._numeric_result_type(left_type, right_type))
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
                op_tok = self.consume(TokenType.VEIZ)
            else:
                op_tok = self.consume(TokenType.MULT)
            right = self.uno()
            self._ensure_numeric(left, op_tok, "operacao aritmetica")
            self._ensure_numeric(right, op_tok, "operacao aritmetica")
            temp = self.new_temp()
            left_type = self._operand_type_family(left, op_tok, True)
            right_type = self._operand_type_family(right, op_tok, True)
            self._register_temp_type(temp, self._numeric_result_type(left_type, right_type))
            self.emit("mult", temp, left, right)
            return self.resto_mult(temp)
        if self._matches(TokenType.SOB):
            op_tok = self.consume(TokenType.SOB)
            right = self.uno()
            self._ensure_numeric(left, op_tok, "operacao aritmetica")
            self._ensure_numeric(right, op_tok, "operacao aritmetica")
            temp = self.new_temp()
            self._register_temp_type(temp, "float")
            self.emit("div", temp, left, right)
            return self.resto_mult(temp)
        if self._matches(TokenType.INT_DIV):
            op_tok = self.consume(TokenType.INT_DIV)
            right = self.uno()
            self._ensure_numeric(left, op_tok, "operacao aritmetica")
            self._ensure_numeric(right, op_tok, "operacao aritmetica")
            temp = self.new_temp()
            self._register_temp_type(temp, "int")
            self.emit("divI", temp, left, right)
            return self.resto_mult(temp)
        if self._matches(TokenType.MOD):
            op_tok = self.consume(TokenType.MOD)
            right = self.uno()
            self._ensure_numeric(left, op_tok, "operacao aritmetica")
            self._ensure_numeric(right, op_tok, "operacao aritmetica")
            temp = self.new_temp()
            self._register_temp_type(temp, "int")
            self.emit("divI", temp, left, right)
            return self.resto_mult(temp)
        return left

    def uno(self) -> str:
        # Unarios + e -.
        if self._matches(TokenType.PLUS):
            op_tok = self.consume(TokenType.PLUS)
            value = self.uno()
            self._ensure_numeric(value, op_tok, "sinal unario")
            return value
        if self._matches(TokenType.MINUS):
            op_tok = self.consume(TokenType.MINUS)
            value = self.uno()
            self._ensure_numeric(value, op_tok, "sinal unario")
            temp = self.new_temp()
            self._register_temp_type(temp, self._operand_type_family(value, op_tok, True))
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
            ident = self.consume(TokenType.IDENTIFIER)
            self._ensure_declared_identifier(ident)
            return self.make_var(ident.lexeme)
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
        # Delimitador de comando fora do for.
        tok = self.current()
        if self._matches(TokenType.UAI):
            return self.consume(TokenType.UAI)
        raise ParserError("uai", self._received_label(tok), tok.line, tok.column)

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
