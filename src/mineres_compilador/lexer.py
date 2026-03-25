"""Análise lexical de programas escritos em Mineres."""

from pathlib import Path
from typing import List, Optional

from .automato import Automato
from .token import Token
from .tokentype import ALL_WORD_TOKENS, TokenType


class Lexer:
    """Converte texto-fonte em uma sequência de tokens."""

    def __init__(self, caminho_automato: str) -> None:
        self.automato = Automato()
        self.automato.carregar_do_arquivo(caminho_automato)

        self.input_str: str = ""
        self.posicao: int = 0
        self.linha: int = 1
        self.coluna: int = 1
        self.tokens: List[Token] = []

    def carregar_arquivo(self, caminho: str) -> None:
        """Carrega o conteúdo do arquivo de entrada no lexer."""
        caminho_arquivo = Path(caminho)
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            self.input_str = arquivo.read()
        self._resetar_estado()

    def carregar_string(self, conteudo: str) -> None:
        """Carrega entrada a partir de uma string."""
        self.input_str = conteudo
        self._resetar_estado()

    def _resetar_estado(self) -> None:
        """Reinicia ponteiros internos para uma nova análise."""
        self.posicao = 0
        self.linha = 1
        self.coluna = 1
        self.tokens = []

    def analisar(self) -> List[Token]:
        """Percorre toda a entrada, ignorando espaços e extraindo tokens."""
        self.tokens = []

        while self.posicao < len(self.input_str):
            char = self.input_str[self.posicao]

            # Quebra de linha altera linha e reinicia coluna.
            if char == "\n":
                self.posicao += 1
                self.linha += 1
                self.coluna = 1
                continue

            # Espaços em branco fora de tokens são ignorados.
            if char in (" ", "\t", "\r"):
                self.posicao += 1
                self.coluna += 1
                continue

            token = self._reconhecer_proximo_token()
            if token is not None:
                self.tokens.append(token)

        return self.tokens

    def _reconhecer_proximo_token(self) -> Optional[Token]:
        """Reconhece um token a partir da posição atual."""
        linha_inicio = self.linha
        coluna_inicio = self.coluna
        restante = self.input_str[self.posicao :]

        aceito, token_type_nome, comprimento = self.automato.reconhecer(restante)

        if aceito and token_type_nome is not None and comprimento > 0:
            lexeme = restante[:comprimento]

            # O autômato retorna IDENTIFIER; aqui resolvemos palavra reservada.
            if token_type_nome == "IDENTIFIER":
                token_type = ALL_WORD_TOKENS.get(lexeme.lower(), TokenType.IDENTIFIER)
            else:
                try:
                    token_type = TokenType[token_type_nome]
                except KeyError:
                    token_type = TokenType.ERROR
        else:
            # Falha de reconhecimento consome 1 caractere como erro léxico.
            lexeme = restante[0] if restante else ""
            token_type = TokenType.ERROR

        self.posicao += len(lexeme)

        # Atualiza linha/coluna com base no lexema efetivamente consumido.
        for char in lexeme:
            if char == "\n":
                self.linha += 1
                self.coluna = 1
            else:
                self.coluna += 1

        return Token(
            type=token_type,
            lexeme=lexeme,
            line=linha_inicio,
            column=coluna_inicio,
        )