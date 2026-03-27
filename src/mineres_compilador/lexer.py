"""Análise lexical de programas escritos em Mineres."""

from pathlib import Path
from typing import List, Optional

from .automato import Automato
from .token import Token
from .tokentype import TokenType, ALL_WORD_TOKENS


class Lexer:
    def __init__(self, caminho_automato: Optional[str] = None) -> None:
        if caminho_automato is None:
            caminho_automato = str(
                Path(__file__).resolve().parents[2] / "grafos" / "automato_simples.txt"
            )

        # Carrega o AFD uma vez na inicializacao do lexer.
        self.automato = Automato()
        self.automato.carregar_do_arquivo(caminho_automato)

        # Estado interno da varredura da entrada.
        self.input_str: str = ""
        self.posicao: int = 0
        self.linha: int = 1
        self.coluna: int = 1
        self.tokens: List[Token] = []
        
    def carregar_arquivo(self, caminho: str) -> None:
        # Le todo o conteudo fonte para memoria.
        with open(caminho, "r", encoding="utf-8") as f:
            self.input_str = f.read()
        # Sempre reinicia o cursor para nova analise.
        self._resetar_estado()
        
    def carregar_string(self, conteudo: str) -> None:
        # Alternativa ao arquivo: injeta o codigo diretamente.
        self.input_str = conteudo
        self._resetar_estado()
        
    def _resetar_estado(self) -> None:
        # Reinicia posicao e lista de tokens para evitar estado residual.
        self.posicao = 0
        self.linha = 1
        self.coluna = 1
        self.tokens = []
        
    def analisar(self) -> List[Token]:
        # Garante saida limpa caso analisar() seja chamado mais de uma vez.
        self.tokens = []
        while self.posicao < len(self.input_str):
            char = self.input_str[self.posicao]
            
            if char == "\n":
                # Quebra de linha muda linha e avanca cursor.
                self.posicao += 1
                self.linha += 1
                self.coluna = 1
                continue
            
            if char in (" ", "\t", "\r"):
                # Espacos em branco sao ignorados como separadores.
                self.posicao += 1
                self.coluna += 1
                continue
            
            token = self._reconhecer_proximo_token()
            if token is not None:
                self.tokens.append(token)
                
        return self.tokens

    def _reconhecer_proximo_token(self) -> Optional[Token]:
        linha_inicio = self.linha
        coluna_inicio = self.coluna
        restante = self.input_str[self.posicao:]
        
        aceito, token_type_nome, comprimento = self.automato.reconhecer(restante)
        
        if aceito and comprimento > 0:
            lexeme = restante[:comprimento]
            
            if token_type_nome == "IDENTIFIER":
                token_type = ALL_WORD_TOKENS.get(lexeme.lower(), TokenType.IDENTIFIER)
            else:
                try:
                    token_type = TokenType[token_type_nome] if token_type_nome else TokenType.ERROR
                except KeyError:
                    token_type = TokenType.ERROR
        
        else:
            lexeme = restante[0] if restante else ""
            token_type = TokenType.ERROR

        self.posicao += len(lexeme)

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