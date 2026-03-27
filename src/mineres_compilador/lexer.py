"""Análise lexical de programas escritos em Mineres."""

from pathlib import Path
from typing import List, Optional

from .automato import Automato
from .token import Token
from .tokentype import TokenType, ALL_WORD_TOKENS


class Lexer:
    def __init__(self, caminho_automato: str) -> None:
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
                self.coluna += 1
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
        """
        Reconhece um token a partir da posicao atual.

        O que ainda falta implementar neste metodo:
        1) Salvar linha/coluna de inicio do token atual.
        2) Obter a substring restante a partir de self.posicao.
        3) Chamar self.automato.reconhecer(restante).
        4) Se aceito e comprimento > 0:
           - Extrair lexeme com o comprimento reconhecido.
           - Se token_type_nome for IDENTIFIER, verificar palavra reservada em
             ALL_WORD_TOKENS (normalmente com lexeme.lower()).
           - Caso contrario, mapear token_type_nome para TokenType via enum.
        5) Se nao aceito:
           - Consumir 1 caractere como erro lexico (TokenType.ERROR).
        6) Atualizar self.posicao conforme o lexeme consumido.
        7) Atualizar self.linha/self.coluna caractere a caractere.
        8) Retornar Token(type=..., lexeme=..., line=..., column=...).

        Criterio de pronto:
        - analisar() percorre toda a entrada sem loop infinito.
        - palavras reservadas nao ficam como IDENTIFIER.
        - token invalido gera ERROR consumindo 1 caractere.
        - linha/coluna ficam coerentes para cada token retornado.
        """
        raise NotImplementedError("Implemente _reconhecer_proximo_token manualmente")


    