from analisador_lexico.tokentype import TokenType
from analisador_lexico.mineires_token import Token


class AnalisadorSintatico:

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.posicao = 0

    def token_atual(self) -> Token:
        return self.tokens[self.posicao]

    def comparar_token(self, tipo: str) -> bool:
        tok = self.token_atual()
        return tok.type.value == tipo or tok.type.name == tipo

    def verificar(self, tipo: str) -> bool:
        if self.comparar_token(tipo):
            self.posicao += 1
            return True
        tok = self.token_atual()
        print(f"Erro sintático: esperado '{tipo}', encontrado '{tok.lexeme}' "
              f"(linha {tok.line}, coluna {tok.column})")
        return False

