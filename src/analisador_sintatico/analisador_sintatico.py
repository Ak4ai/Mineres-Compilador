from __future__ import annotations

from analisador_lexico.mineires_token import Token
from analisador_lexico.tokentype import TokenType


class ParserError(Exception):
    # Erro sintatico fatal: o parser para no primeiro erro encontrado.
    def __init__(self, expected: str, received: str, line: int, column: int) -> None:
        super().__init__(
            f"Erro sintático: esperado {expected}, mas recebeu {received} "
            f"na linha {line}, coluna {column}"
        )


class Parser:
    # Parser recursivo para validar sintaxe da linguagem Mineres.

    def __init__(self, tokens: list[Token]):
        # Comentarios nao participam da sintaxe da gramatica.
        self.tokens = [
            t
            for t in tokens
            if t.type not in {TokenType.COMMENT_LINE, TokenType.COMMENT_BLOCK}
        ]
        self.pos = 0

    # Metodos basicos
    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        # Seguranca para listas sem EOF (na pratica o lexer gera EOF).
        return self.tokens[-1]

    def advance(self) -> None:
        if self.pos < len(self.tokens) - 1:
            self.pos += 1

    def consume(self, expected_type) -> Token:
        tok = self.current()
        if self._matches(expected_type):
            self.advance()
            return tok

        expected_label = self._expected_label(expected_type)
        raise ParserError(expected_label, self._received_label(tok), tok.line, tok.column)

    # API principal
    def parse(self) -> bool:
        self.function()
        self.consume(TokenType.EOF)
        return True

    # Regras da gramatica
    def function(self) -> None:
        # <function*> -> 'bora_cumpade' 'main' '(' ')' <bloco>
        self.consume(TokenType.BORA_CUMPADE)
        self.consume(TokenType.MAIN)
        self.consume(TokenType.LEFT_PAREN)
        self.consume(TokenType.RIGHT_PAREN)
        self.bloco()

    def type_rule(self) -> None:
        # <type> -> trem_di_numeru | trem_cum_virgula | trem_discrita | trem_discolhe | trosso
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
        # <bloco> -> 'simbora' <stmtList> 'cabo'
        self.consume(TokenType.SIMBORA)
        self.stmt_list()
        self.consume(TokenType.CABO)

    def stmt_list(self) -> None:
        # <stmtList> -> <stmt> <stmtList> | &
        if self._is_stmt_start(self.current()):
            self.stmt()
            self.stmt_list()

    def stmt(self) -> None:
        # <stmt> -> varias alternativas
        tok = self.current()

        if tok.type == TokenType.RODA_ESSE_TREM:
            self.for_stmt()
            return

        if tok.type in {TokenType.XOVE, TokenType.OIA_PROCE_VE}:
            self.io_stmt()
            return

        if tok.type == TokenType.ENQUANTO_TIVER_TREM:
            self.while_stmt()
            return

        if tok.type == TokenType.UAI_SE:
            self.if_stmt()
            return

        if tok.type == TokenType.DEPENDENU:
            self.case_stmt()
            return

        if tok.type == TokenType.SIMBORA:
            self.bloco()
            return

        if tok.type == TokenType.PARA_O_TREM:
            self.consume(TokenType.PARA_O_TREM)
            self.consume_delimiter()
            return

        if tok.type == TokenType.TOCA_O_TREM:
            self.consume(TokenType.TOCA_O_TREM)
            self.consume_delimiter()
            return

        if self._is_type_start(tok):
            self.declaration()
            return

        if tok.type in {TokenType.UAI, TokenType.SEMICOLON}:
            # Comando vazio.
            self.consume_delimiter()
            return

        # Se nao caiu em nenhuma alternativa, tenta <atrib> 'uai'.
        if self._is_expr_start(tok):
            self.atrib()
            self.consume_delimiter()
            return

        raise ParserError("<stmt>", self._received_label(tok), tok.line, tok.column)

    def declaration(self) -> None:
        # <declaration> -> <type> <identList> 'uai'
        self.type_rule()
        self.ident_list()
        self.consume_delimiter()

    def ident_list(self) -> None:
        # <identList> -> IDENT <restoIdentList>
        self.consume(TokenType.IDENTIFIER)
        self.resto_ident_list()

    def resto_ident_list(self) -> None:
        # <restoIdentList> -> ',' IDENT <restoIdentList> | &
        if self._matches(TokenType.COMMA):
            self.consume(TokenType.COMMA)
            self.consume(TokenType.IDENTIFIER)
            self.resto_ident_list()

    def for_stmt(self) -> None:
        # <forStmt> -> roda_esse_trem '(' <optExpr> ';' <optExpr> ';' <optExpr> ')' <stmt>
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
        # <optExpr> -> <atrib> | &
        if self._is_expr_start(self.current()):
            self.atrib()

    def io_stmt(self) -> None:
        # <ioStmt> -> xove(...) uai | oia_proce_ve(...) uai
        if self._matches(TokenType.XOVE):
            self.consume(TokenType.XOVE)
            self.consume(TokenType.LEFT_PAREN)
            self.type_rule()
            self.consume(TokenType.COMMA)
            self.consume(TokenType.IDENTIFIER)
            self.consume(TokenType.RIGHT_PAREN)
            self.consume_delimiter()
            return

        self.consume(TokenType.OIA_PROCE_VE)
        self.consume(TokenType.LEFT_PAREN)
        self.out_list()
        self.consume(TokenType.RIGHT_PAREN)
        self.consume_delimiter()

    def out_list(self) -> None:
        # <outList> -> <out> <restoOutList>
        self.out()
        self.resto_out_list()

    def out(self) -> None:
        # <out> -> <fatorZin>
        self.fator_zin()

    def resto_out_list(self) -> None:
        # <restoOutList> -> ',' <out> <restoOutList> | &
        if self._matches(TokenType.COMMA):
            self.consume(TokenType.COMMA)
            self.out()
            self.resto_out_list()

    def while_stmt(self) -> None:
        # <whileStmt> -> enquanto_tiver_trem '(' <expr> ')' <stmt>
        self.consume(TokenType.ENQUANTO_TIVER_TREM)
        self.consume(TokenType.LEFT_PAREN)
        self.expr()
        self.consume(TokenType.RIGHT_PAREN)
        self.stmt()

    def if_stmt(self) -> None:
        # <ifStmt> -> uai_se '(' <expr> ')' <stmt> <elsePart>
        self.consume(TokenType.UAI_SE)
        self.consume(TokenType.LEFT_PAREN)
        self.expr()
        self.consume(TokenType.RIGHT_PAREN)
        self.stmt()
        self.else_part()

    def else_part(self) -> None:
        # <elsePart> -> uai_senao <stmt> | &
        if self._matches(TokenType.UAI_SENAO):
            self.consume(TokenType.UAI_SENAO)
            self.stmt()

    def case_stmt(self) -> None:
        # <caseStmt> -> dependenu '(' IDENT ')' simbora <dosCasos> cabo
        self.consume(TokenType.DEPENDENU)
        self.consume(TokenType.LEFT_PAREN)
        self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.RIGHT_PAREN)
        self.consume(TokenType.SIMBORA)
        self.dos_casos()
        self.consume(TokenType.CABO)

    def dos_casos(self) -> None:
        # <dosCasos> -> <doCaso> <restoDosCasos>
        self.do_caso()
        self.resto_dos_casos()

    def do_caso(self) -> None:
        # <doCaso> -> du_casu <fatorZin> ':' <stmt>
        self.consume(TokenType.DU_CASU)
        self.fator_zin()
        self.consume(TokenType.COLON)
        self.stmt()

    def resto_dos_casos(self) -> None:
        # <restoDosCasos> -> <doCaso><restoDosCasos> | default ':' <stmt> | &
        if self._matches(TokenType.DU_CASU):
            self.do_caso()
            self.resto_dos_casos()
            return

        if self._matches(TokenType.DEFAULT):
            self.consume(TokenType.DEFAULT)
            self.consume(TokenType.COLON)
            self.stmt()

    def expr(self) -> None:
        # <expr> -> <atrib>
        self.atrib()

    def atrib(self) -> None:
        # <atrib> -> <or> <restoAtrib>
        self.or_rule()
        self.resto_atrib()

    def resto_atrib(self) -> None:
        # <restoAtrib> -> fica_assim_entao <atrib> | &
        if self._matches(TokenType.FICA_ASSIM_ENTAO):
            self.consume(TokenType.FICA_ASSIM_ENTAO)
            self.atrib()

    def or_rule(self) -> None:
        # <or> -> <xor> <restoOr>
        self.xor_rule()
        self.resto_or()

    def resto_or(self) -> None:
        # <restoOr> -> quarque_um <xor> <restoOr> | &
        if self._matches(TokenType.QUARQUE_UM):
            self.consume(TokenType.QUARQUE_UM)
            self.xor_rule()
            self.resto_or()

    def xor_rule(self) -> None:
        # <xor> -> <and> <restoXor>
        self.and_rule()
        self.resto_xor()

    def resto_xor(self) -> None:
        # <restoXor> -> um_o_oto <and> <restoXor> | &
        if self._matches(TokenType.UM_O_OTO):
            self.consume(TokenType.UM_O_OTO)
            self.and_rule()
            self.resto_xor()

    def and_rule(self) -> None:
        # <and> -> <not> <restoAnd>
        self.not_rule()
        self.resto_and()

    def resto_and(self) -> None:
        # <restoAnd> -> tamem <not> <restoAnd> | &
        if self._matches(TokenType.TAMEM):
            self.consume(TokenType.TAMEM)
            self.not_rule()
            self.resto_and()

    def not_rule(self) -> None:
        # <not> -> vam_marca <not> | <rel>
        if self._matches(TokenType.VAM_MARCA):
            self.consume(TokenType.VAM_MARCA)
            self.not_rule()
            return
        self.rel()

    def rel(self) -> None:
        # <rel> -> <add> <restoRel>
        self.add()
        self.resto_rel()

    def resto_rel(self) -> None:
        # <restoRel> -> mema_coisa <add> | neh_nada <add>
        #            | '<' <add> | '<=' <add> | '>' <add> | '>=' <add> | &
        if self._matches(TokenType.MEMA_COISA):
            self.consume(TokenType.MEMA_COISA)
            self.add()
            return
        if self._matches(TokenType.NEH_NADA):
            self.consume(TokenType.NEH_NADA)
            self.add()
            return
        if self._matches(TokenType.LT):
            self.consume(TokenType.LT)
            self.add()
            return
        if self._matches(TokenType.LE):
            self.consume(TokenType.LE)
            self.add()
            return
        if self._matches(TokenType.GT):
            self.consume(TokenType.GT)
            self.add()
            return
        if self._matches(TokenType.GE):
            self.consume(TokenType.GE)
            self.add()

    def add(self) -> None:
        # <add> -> <mult> <restoAdd>
        self.mult()
        self.resto_add()

    def resto_add(self) -> None:
        # <restoAdd> -> '+' <mult> <restoAdd> | '-' <mult> <restoAdd> | &
        if self._matches(TokenType.PLUS):
            self.consume(TokenType.PLUS)
            self.mult()
            self.resto_add()
            return
        if self._matches(TokenType.MINUS):
            self.consume(TokenType.MINUS)
            self.mult()
            self.resto_add()

    def mult(self) -> None:
        # <mult> -> <uno> <restoMult>
        self.uno()
        self.resto_mult()

    def resto_mult(self) -> None:
        # <restoMult> -> veiz <uno> <restoMult>
        #             | sob <uno> <restoMult>
        #             | '/' <uno> <restoMult>
        #             | '%' <uno> <restoMult>
        #             | &
        if self._matches(TokenType.VEIZ):
            self.consume(TokenType.VEIZ)
            self.uno()
            self.resto_mult()
            return
        if self._matches(TokenType.SOB):
            self.consume(TokenType.SOB)
            self.uno()
            self.resto_mult()
            return
        if self._matches(TokenType.INT_DIV):
            self.consume(TokenType.INT_DIV)
            self.uno()
            self.resto_mult()
            return
        if self._matches(TokenType.MOD):
            self.consume(TokenType.MOD)
            self.uno()
            self.resto_mult()

    def uno(self) -> None:
        # <uno> -> '+' <uno> | '-' <uno> | <fatorZao>
        if self._matches(TokenType.PLUS):
            self.consume(TokenType.PLUS)
            self.uno()
            return
        if self._matches(TokenType.MINUS):
            self.consume(TokenType.MINUS)
            self.uno()
            return
        self.fator_zao()

    def fator_zao(self) -> None:
        # <fatorZao> -> <fatorZin> | '(' <atrib> ')'
        if self._matches(TokenType.LEFT_PAREN):
            self.consume(TokenType.LEFT_PAREN)
            self.atrib()
            self.consume(TokenType.RIGHT_PAREN)
            return
        self.fator_zin()

    def fator_zin(self) -> None:
        # <fatorZin> -> STR | IDENT | NUMint | NUMfloat | valorBooleano | valorChar
        if self._matches(TokenType.STRING_LITERAL):
            self.consume(TokenType.STRING_LITERAL)
            return
        if self._matches(TokenType.IDENTIFIER):
            self.consume(TokenType.IDENTIFIER)
            return
        if self._matches(TokenType.INTEGER_LITERAL):
            self.consume(TokenType.INTEGER_LITERAL)
            return
        if self._matches(TokenType.HEX_LITERAL):
            self.consume(TokenType.HEX_LITERAL)
            return
        if self._matches(TokenType.OCTAL_LITERAL):
            self.consume(TokenType.OCTAL_LITERAL)
            return
        if self._matches(TokenType.FLOAT_LITERAL):
            self.consume(TokenType.FLOAT_LITERAL)
            return
        if self._matches(TokenType.EH):
            self.consume(TokenType.EH)
            return
        if self._matches(TokenType.NUM_EH):
            self.consume(TokenType.NUM_EH)
            return
        if self._matches(TokenType.CHAR_LITERAL):
            self.consume(TokenType.CHAR_LITERAL)
            return

        tok = self.current()
        raise ParserError(
            "fator (STR | IDENT | NUMint | NUMfloat | valorBooleano | valorChar)",
            self._received_label(tok),
            tok.line,
            tok.column,
        )

    # -----------------------------
    # Helpers de validacao
    # -----------------------------
    def consume_delimiter(self) -> Token:
        # Regra pragmatica: aceita tanto 'uai' quanto ';' como delimitador de stmt.
        tok = self.current()
        if self._matches(TokenType.UAI):
            return self.consume(TokenType.UAI)
        if self._matches(TokenType.SEMICOLON):
            return self.consume(TokenType.SEMICOLON)
        raise ParserError("uai ou ;", self._received_label(tok), tok.line, tok.column)

    def _is_type_start(self, tok: Token) -> bool:
        return tok.type in {
            TokenType.TREM_DI_NUMERU,
            TokenType.TREM_CUM_VIRGULA,
            TokenType.TREM_DISCRITA,
            TokenType.TREM_DISCOLHE,
            TokenType.TROSSO,
        }

    def _is_expr_start(self, tok: Token) -> bool:
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
                TokenType.SEMICOLON,
            }
            or self._is_type_start(tok)
            or self._is_expr_start(tok)
        )

    def _matches(self, expected) -> bool:
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

            # Delimitador flexivel: aceita palavra e simbolo.
            if expected in {"uai", ";"}:
                return tok.type in {TokenType.UAI, TokenType.SEMICOLON}

            # Compatibilidade com terminais por nome, valor ou lexema literal.
            return (
                tok.type.name == expected
                or tok.type.value == expected
                or tok.lexeme == expected
            )

        return False

    def _expected_label(self, expected) -> str:
        if isinstance(expected, TokenType):
            return expected.name
        return str(expected)

    def _received_label(self, tok: Token) -> str:
        # Prioriza lexema para mensagem mais intuitiva; em EOF usa o nome do tipo.
        return tok.lexeme if tok.lexeme else tok.type.name
