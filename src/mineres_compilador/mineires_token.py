"""Modelo de token usado pelo lexer de Mineres."""

from dataclasses import dataclass

from .tokentype import TokenType


# Token imutavel: depois de criado, nao deve ser alterado.
@dataclass(slots=True, frozen=True)
class Token:
    """Representa uma unidade lexica produzida pelo lexer."""

    type: TokenType
    lexeme: str
    line: int
    column: int

    def to_output_row(self) -> str:
        # Formato compacto utilizado em exportacoes tabulares.
        """Retorna uma representacao estavel separada por tab para saida."""
        return f"{self.type.value}\t{self.lexeme}\t{self.line}\t{self.column}"

    def __str__(self) -> str:
        # Mantem conversao para string alinhada ao formato tabular.
        return self.to_output_row()