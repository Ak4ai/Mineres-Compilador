# Lexer para a linguagem Mineres usando AFD explicito.

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .automato import Automato
from mineires_token import Token
from tokentype import ALL_WORD_TOKENS, TokenType


class LexicalError(Exception):
    # Excecao com contexto completo para erro lexico.
    def __init__(
        self,
        lexeme: str,
        line: int,
        column: int,
        error_type: str = "ERRO_LEXICO",
    ) -> None:
        self.error_type = error_type
        self.lexeme = lexeme
        self.line = line
        self.column = column
        lexeme_preview = lexeme

        # Evita poluir a saida em erros de comentario de bloco sem fechamento.
        if error_type == "COMENTARIO_NAO_FECHADO" and lexeme.startswith("causo"):
            lexeme_preview = "causo..."

        super().__init__(
            f"Erro lexico ({error_type}): '{lexeme_preview}' na linha {line}, coluna {column}"
        )


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
        self.errors: list[LexicalError] = []

    def carregar_arquivo(self, caminho: str) -> None:
        # Le fonte de arquivo e reinicia estado interno.
        with open(caminho, "r", encoding="utf-8") as arquivo:
            self.source = arquivo.read()
        self._resetar_estado()

    def carregar_string(self, conteudo: str) -> None:
        # Le fonte direta (CLI -s) e reinicia estado interno.
        self.source = conteudo
        self._resetar_estado()

    def _resetar_estado(self) -> None:
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.errors = []

    def analisar(self, continuar_apos_erro: bool = False) -> list[Token]:
        # API principal do lexer; opcionalmente coleta multiplos erros.
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.errors = []
        return self.tokenize(continuar_apos_erro=continuar_apos_erro)

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

    def _recuperar_posicao_apos_erro(self, erro: LexicalError) -> None:
        # Em modo de coleta de erros, tenta pular para um ponto util de retomada.
        restante = self.source[self.pos :]

        # Para string/char nao fechado, consome ate fim da linha para evitar loop.
        if erro.error_type in {"STRING_NAO_FECHADA", "CHAR_NAO_FECHADO"}:
            fim_linha = restante.find("\n")
            trecho = restante if fim_linha == -1 else restante[: fim_linha + 1]
        elif erro.error_type == "COMENTARIO_NAO_FECHADO":
            # Sem marcador de fim, o comentario consome o restante da entrada.
            trecho = restante
        else:
            # Regra geral: pula o lexema ofensivo detectado.
            tamanho = max(1, len(erro.lexeme))
            trecho = self.source[self.pos : self.pos + tamanho]

        if not trecho:
            trecho = self.source[self.pos : self.pos + 1]

        self._advance_position(trecho)
        self.pos += len(trecho)

    def tokenize(self, continuar_apos_erro: bool = False) -> list[Token]:
        # Executa o loop principal de analise lexica.
        while not self.is_at_end():
            char_atual = self.source[self.pos]

            if char_atual in {" ", "\t", "\r", "\n"}:
                self._handle_whitespace(char_atual)
                continue

            inicio_linha = self.line
            inicio_coluna = self.column
            restante = self.source[self.pos :]

            try:
                # Detecta string nao fechada antes do automato.
                if restante.startswith('"'):
                    fechamento = restante.find('"', 1)
                    fim_linha = restante.find("\n")

                    if fechamento == -1 or (fim_linha != -1 and fim_linha < fechamento):
                        lexeme = restante[:fim_linha] if fim_linha != -1 else restante
                        raise LexicalError(
                            lexeme,
                            inicio_linha,
                            inicio_coluna,
                            "STRING_NAO_FECHADA",
                        )

                # Valida char no formato canonico antes do automato.
                # Aceita um caractere simples ('c') ou um escape valido ('\\n', '\\t', etc.).
                if restante.startswith("'"):
                    fechamento = restante.find("'", 1)
                    fim_linha = restante.find("\n")

                    if fechamento == -1 or (fim_linha != -1 and fim_linha < fechamento):
                        raise LexicalError(
                            restante,
                            inicio_linha,
                            inicio_coluna,
                            "CHAR_NAO_FECHADO",
                        )

                    conteudo = restante[1:fechamento]
                    escapes_validos = {"n", "t", "r", "\\", "'", '"', "0", "b", "f", "v"}

                    if not conteudo:
                        raise LexicalError(
                            restante[: fechamento + 1],
                            inicio_linha,
                            inicio_coluna,
                            "CHAR_MAL_FORMADO",
                        )

                    if conteudo.startswith("\\"):
                        if len(conteudo) != 2 or conteudo[1] not in escapes_validos:
                            raise LexicalError(
                                restante[: fechamento + 1],
                                inicio_linha,
                                inicio_coluna,
                                "CHAR_MAL_FORMADO",
                            )
                    elif len(conteudo) != 1:
                        raise LexicalError(
                            restante[: fechamento + 1],
                            inicio_linha,
                            inicio_coluna,
                            "CHAR_MAL_FORMADO",
                        )

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
                        raise LexicalError(
                            lexeme,
                            inicio_linha,
                            inicio_coluna,
                            "COMENTARIO_NAO_FECHADO",
                        )

                    fim_comentario = indice_fim + len(marcador_fim)
                    lexeme = restante[:fim_comentario]
                    self.tokens.append(
                        Token(TokenType.COMMENT_BLOCK, lexeme, inicio_linha, inicio_coluna)
                    )
                    self._advance_position(lexeme)
                    self.pos += len(lexeme)
                    continue

                # O AFD reconhece o maior prefixo valido a partir da posicao atual.
                ok, token_type_str, tamanho = self.automato.reconhecer(restante)

                # Em falha de reconhecimento, emite erro e avanca um caractere.
                if not ok or tamanho == 0:
                    raise LexicalError(
                        char_atual,
                        inicio_linha,
                        inicio_coluna,
                        "SIMBOLO_DESCONHECIDO",
                    )

                lexeme = self.source[self.pos : self.pos + tamanho]

                # Classificacao final: palavras conhecidas vencem IDENTIFIER.
                if lexeme in ALL_WORD_TOKENS:
                    token_type = ALL_WORD_TOKENS[lexeme]
                else:
                    # Tipos numericos para validacoes adicionais de sufixo invalido.
                    tipos_numericos = {
                        "INTEGER_LITERAL",
                        "FLOAT_LITERAL",
                        "HEX_LITERAL",
                        "OCTAL_LITERAL",
                    }
                    separadores = set(" \t\r\n(){}[],:;+-*/%<>=\"'")

                    # Se um numero eh seguido por sufixo colado (ex.: 0x10G, 12.3.4),
                    # classifica como numero mal formado em vez de simbolo desconhecido.
                    if token_type_str in tipos_numericos:
                        proxima_pos = self.pos + tamanho
                        if proxima_pos < len(self.source):
                            proximo_char = self.source[proxima_pos]
                            if proximo_char not in separadores:
                                fim_lexema = proxima_pos
                                while (
                                    fim_lexema < len(self.source)
                                    and self.source[fim_lexema] not in separadores
                                ):
                                    fim_lexema += 1

                                lexema_invalido = self.source[self.pos : fim_lexema]
                                raise LexicalError(
                                    lexema_invalido,
                                    inicio_linha,
                                    inicio_coluna,
                                    "NUMERO_MAL_FORMADO",
                                )

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
                        raise LexicalError(
                            lexeme,
                            inicio_linha,
                            inicio_coluna,
                            "NUMERO_MAL_FORMADO",
                        )

                    # Valida o token retornado pelo automato antes de converter.
                    if not token_type_str or token_type_str not in TokenType._value2member_map_:
                        raise LexicalError(
                            lexeme,
                            inicio_linha,
                            inicio_coluna,
                            "TOKEN_DESCONHECIDO",
                        )
                    token_type = TokenType(token_type_str)

                self.tokens.append(Token(token_type, lexeme, inicio_linha, inicio_coluna))
                self._advance_position(lexeme)
                self.pos += len(lexeme)
            except LexicalError as erro:
                # Comportamento padrao: falha rapida no primeiro erro.
                if not continuar_apos_erro:
                    raise

                # Modo alternativo: acumula erros e tenta seguir a analise.
                self.errors.append(erro)
                self._recuperar_posicao_apos_erro(erro)
                continue

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens