# Lexer para a linguagem Mineres usando AFD explicito.

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .automato import Automato
from .mineires_token import Token
from .tokentype import ALL_WORD_TOKENS, TokenType


class LexicalError(Exception):
    def __init__(self, lexeme: str, line: int, column: int) -> None:
        super().__init__(f"Erro lexico: '{lexeme}' na linha {line}, coluna {column}")


class Lexer:
    # Tokeniza o codigo-fonte usando o automato carregado.

    def __init__(self, caminho_automato: Optional[str] = None) -> None:
        if caminho_automato is None:
            caminho_automato = str(
                Path(__file__).resolve().parents[2] / "automatos" / "automato.txt"
            )

        self.automato = Automato()
        self.automato.carregar_do_arquivo(caminho_automato)

        self.source = ""
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def carregar_arquivo(self, caminho: str) -> None:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            self.source = arquivo.read()
        self._resetar_estado()

    def carregar_string(self, conteudo: str) -> None:
        self.source = conteudo
        self._resetar_estado()

    def _resetar_estado(self) -> None:
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def analisar(self) -> list[Token]:
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        return self.tokenize()

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
                fim_linha = restante.find("\n")

                if fechamento == -1 or (fim_linha != -1 and fim_linha < fechamento):
                    lexeme = restante[:fim_linha] if fim_linha != -1 else restante
                    raise LexicalError(lexeme, inicio_linha, inicio_coluna)

            # Valida char no formato canonico antes do automato.
            # Aceita um caractere simples ('c') ou um escape valido ('\\n', '\\t', etc.).
            if restante.startswith("'"):
                fechamento = restante.find("'", 1)
                fim_linha = restante.find("\n")

                if fechamento == -1 or (fim_linha != -1 and fim_linha < fechamento):
                    raise LexicalError(restante, inicio_linha, inicio_coluna)

                conteudo = restante[1:fechamento]
                escapes_validos = {"n", "t", "r", "\\", "'", '"', "0", "b", "f", "v"}

                if not conteudo:
                    raise LexicalError(restante[: fechamento + 1], inicio_linha, inicio_coluna)

                if conteudo.startswith("\\"):
                    if len(conteudo) != 2 or conteudo[1] not in escapes_validos:
                        raise LexicalError(restante[: fechamento + 1], inicio_linha, inicio_coluna)
                elif len(conteudo) != 1:
                    raise LexicalError(restante[: fechamento + 1], inicio_linha, inicio_coluna)

            # Trata comentario de linha antes do automato.
            if restante.startswith("//"):
                fim_linha = restante.find("\n")
                if fim_linha == -1:
                    lexeme = restante
                else:
                    lexeme = restante[: fim_linha + 1]

                self.tokens.append(
                    Token(TokenType.COMMENT_LINE, lexeme, inicio_linha, inicio_coluna)
                )
                self._advance_position(lexeme)
                self.pos += len(lexeme)
                continue

            # Trata comentario de bloco antes do automato.
            if restante.startswith("causo"):
                marcador_fim = "fim_do_causo"
                indice_fim = restante.find(marcador_fim)

                if indice_fim == -1:
                    # Comentario de bloco nao fechado ate EOF.
                    lexeme = restante
                    raise LexicalError(lexeme, inicio_linha, inicio_coluna)

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
                raise LexicalError(char_atual, inicio_linha, inicio_coluna)

            lexeme = self.source[self.pos : self.pos + tamanho]

            # Classificacao final: palavras conhecidas vencem IDENTIFIER.
            if lexeme in ALL_WORD_TOKENS:
                token_type = ALL_WORD_TOKENS[lexeme]
            else:
                # Validacoes extras para numeros mal formados.
                numero_invalido = False

                if lexeme.lower().startswith("0x"):
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

                # Valida float apenas quando o AFD classificar como FLOAT_LITERAL.
                if not numero_invalido and token_type_str == "FLOAT_LITERAL":
                    try:
                        float(lexeme)
                    except ValueError:
                        numero_invalido = True

                if numero_invalido:
                    raise LexicalError(lexeme, inicio_linha, inicio_coluna)

                # Valida o token retornado pelo automato antes de converter.
                if not token_type_str or token_type_str not in TokenType._value2member_map_:
                    raise LexicalError(lexeme, inicio_linha, inicio_coluna)
                token_type = TokenType(token_type_str)

            self.tokens.append(Token(token_type, lexeme, inicio_linha, inicio_coluna))
            self._advance_position(lexeme)
            self.pos += len(lexeme)

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens