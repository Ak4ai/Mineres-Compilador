# Lexer para a linguagem Mineres usando AFD explicito.

from __future__ import annotations

from typing import Any

from mineires_token import Token
from tokentype import ALL_WORD_TOKENS, TokenType


class Lexer:
    # Tokeniza o codigo-fonte usando o automato carregado.

    def __init__(self, source: str, automato: Any) -> None:
        self.source = source
        self.automato = automato
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def is_at_end(self) -> bool:
        # Indica se a posicao atual chegou ao fim da entrada.
        return self.pos >= len(self.source)

    def _handle_whitespace(self, char: str) -> None:
        # Consome espacos em branco e atualiza linha/coluna.
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.pos += 1

    def _advance_position(self, lexeme: str) -> None:
        # Avanca linha/coluna de acordo com o lexema consumido.
        for char in lexeme:
            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1

    def _emit_error_and_advance(self, lexeme: str, line: int, column: int) -> None:
        # Emite token de erro e avanca linha/coluna + posicao absoluta.
        self.tokens.append(Token(TokenType.ERROR, lexeme, line, column))
        self._advance_position(lexeme)
        self.pos += len(lexeme)

    def tokenize(self) -> list[Token]:
        # Executa o loop principal de analise lexica.
        while not self.is_at_end():
            char_atual = self.source[self.pos]

            if char_atual in {" ", "\t", "\r", "\n"}:
                self._handle_whitespace(char_atual)
                continue

            inicio_linha = self.line
            inicio_coluna = self.column
            restante = self.source[self.pos :]

            # Detecta string nao fechada antes do automato.
            if restante.startswith('"'):
                fechamento = restante.find('"', 1)
                if fechamento == -1:
                    self._emit_error_and_advance(restante, inicio_linha, inicio_coluna)
                    continue

            # Detecta char nao fechado no formato .'<char>'.
            if restante.startswith(".'"):
                fechamento = restante.find("'.", 2)
                if fechamento == -1:
                    self._emit_error_and_advance(restante, inicio_linha, inicio_coluna)
                    continue

            # Trata comentario de linha antes do automato.
            if restante.startswith("//"):
                fim_linha = restante.find("\n")
                if fim_linha == -1:
                    lexeme = restante
                else:
                    lexeme = restante[:fim_linha]

                self.tokens.append(
                    Token(TokenType.COMMENT_LINE, lexeme, inicio_linha, inicio_coluna)
                )
                self._advance_position(lexeme)
                self.pos += len(lexeme)
                continue

            # Trata comentario de bloco antes do automato.
            if restante.startswith("causo"):
                marcador_fim = "fim do causo"
                indice_fim = restante.find(marcador_fim)

                if indice_fim == -1:
                    # Comentario de bloco nao fechado ate EOF.
                    lexeme = restante
                    self._emit_error_and_advance(lexeme, inicio_linha, inicio_coluna)
                    continue

                fim_comentario = indice_fim + len(marcador_fim)
                lexeme = restante[:fim_comentario]
                self.tokens.append(
                    Token(TokenType.COMMENT_BLOCK, lexeme, inicio_linha, inicio_coluna)
                )
                self._advance_position(lexeme)
                self.pos += len(lexeme)
                continue

            ok, token_type_str, tamanho = self.automato.reconhecer(restante)

            # Em falha de reconhecimento, emite erro e avanca um caractere.
            if not ok or tamanho == 0:
                self._emit_error_and_advance(char_atual, inicio_linha, inicio_coluna)
                continue

            lexeme = self.source[self.pos : self.pos + tamanho]

            # Classificacao final: palavras conhecidas vencem IDENTIFIER.
            if lexeme in ALL_WORD_TOKENS:
                token_type = ALL_WORD_TOKENS[lexeme]
            else:
                # Validacoes extras para numeros mal formados.
                numero_invalido = False

                if lexeme.startswith("0x"):
                    try:
                        int(lexeme, 16)
                    except ValueError:
                        numero_invalido = True

                if (
                    not numero_invalido
                    and lexeme.startswith("0")
                    and lexeme.isdigit()
                    and lexeme != "0"
                ):
                    try:
                        int(lexeme, 8)
                    except ValueError:
                        numero_invalido = True

                if not numero_invalido and "." in lexeme:
                    try:
                        float(lexeme)
                    except ValueError:
                        numero_invalido = True

                if numero_invalido:
                    self._emit_error_and_advance(lexeme, inicio_linha, inicio_coluna)
                    continue

                # Valida o token retornado pelo automato antes de converter.
                if not token_type_str or token_type_str not in TokenType._value2member_map_:
                    self._emit_error_and_advance(lexeme, inicio_linha, inicio_coluna)
                    continue
                token_type = TokenType(token_type_str)

            self.tokens.append(Token(token_type, lexeme, inicio_linha, inicio_coluna))
            self._advance_position(lexeme)
            self.pos += len(lexeme)

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens