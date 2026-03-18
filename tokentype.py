"""Definicoes de tokens para o lexer de Mineres.

Este modulo centraliza todos os tipos de token aceitos pela
especificacao da linguagem Mineres.
"""

from enum import Enum


class TokenType(Enum):
    """Enumeracao de todos os tipos de token reconhecidos pelo lexer."""

    # Tokens especiais de controle
    EOF = "EOF"
    ERROR = "ERROR"

    # Identificadores genericos
    IDENTIFIER = "IDENTIFIER"

    # Literais
    INTEGER_LITERAL = "INTEGER_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    HEX_LITERAL = "HEX_LITERAL"
    OCTAL_LITERAL = "OCTAL_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    CHAR_LITERAL = "CHAR_LITERAL"

    # Palavras reservadas
    BORA_CUMPADE = "BORA_CUMPADE"
    SIMBORA = "SIMBORA"
    CABO = "CABO"
    UAI_SE = "UAI_SE"
    UAI_SENAO = "UAI_SENAO"
    ENQUANTO_TIVER_TREM = "ENQUANTO_TIVER_TREM"
    RODA_ESSE_TREM = "RODA_ESSE_TREM"
    DEPENDENU = "DEPENDENU"
    DU_CASU = "DU_CASU"
    TA_BAO = "TA_BAO"
    PARA_O_TREM = "PARA_O_TREM"
    TOCA_O_TREM = "TOCA_O_TREM"
    XOVE = "XOVE"
    OIA_PROCE_VE = "OIA_PROCE_VE"

    # Nomes de tipos
    TREM_DI_NUMERO = "TREM_DI_NUMERO"
    TREM_CUM_VIRGULA = "TREM_CUM_VIRGULA"
    TREM_DISCRITA = "TREM_DISCRITA"
    TREM_DISCOLHE = "TREM_DISCOLHE"
    TROSSO = "TROSSO"

    # Literais booleanos
    TRUE = "TRUE"
    FALSE = "FALSE"

    # Operadores por palavra
    FICA_ASSIM_ENTAO = "FICA_ASSIM_ENTAO"
    MEMA_COISA = "MEMA_COISA"
    NEH_NADA = "NEH_NADA"
    QUARQUE_UM = "QUARQUE_UM"
    TAMEM = "TAMEM"
    VAM_MARCA = "VAM_MARCA"
    UM_O_OTO = "UM_O_OTO"
    VEIZ = "VEIZ"
    SOB = "SOB"

    # Operadores por simbolo
    PLUS = "PLUS"
    MINUS = "MINUS"
    INT_DIV = "INT_DIV"
    LT = "LT"
    GT = "GT"
    LE = "LE"
    GE = "GE"

    # Delimitadores
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    COMMA = "COMMA"
    UAI = "UAI"


KEYWORD_TOKENS = {
    "bora_cumpade": TokenType.BORA_CUMPADE,
    "simbora": TokenType.SIMBORA,
    "cabo": TokenType.CABO,
    "uai_se": TokenType.UAI_SE,
    "uai_senao": TokenType.UAI_SENAO,
    "enquanto_tiver_trem": TokenType.ENQUANTO_TIVER_TREM,
    "roda_esse_trem": TokenType.RODA_ESSE_TREM,
    "dependenu": TokenType.DEPENDENU,
    "du_casu": TokenType.DU_CASU,
    "ta_bao": TokenType.TA_BAO,
    "para_o_trem": TokenType.PARA_O_TREM,
    "toca_o_trem": TokenType.TOCA_O_TREM,
    "xove": TokenType.XOVE,
    "oia_proce_ve": TokenType.OIA_PROCE_VE,
}


TYPE_TOKENS = {
    "trem_di_numero": TokenType.TREM_DI_NUMERO,
    "trem_cum_virgula": TokenType.TREM_CUM_VIRGULA,
    "trem_discrita": TokenType.TREM_DISCRITA,
    "trem_discolhe": TokenType.TREM_DISCOLHE,
    "trosso": TokenType.TROSSO,
}


BOOLEAN_TOKENS = {
    "eh": TokenType.TRUE,
    "num_eh": TokenType.FALSE,
}


WORD_OPERATOR_TOKENS = {
    "fica_assim_entao": TokenType.FICA_ASSIM_ENTAO,
    "mema_coisa": TokenType.MEMA_COISA,
    "neh_nada": TokenType.NEH_NADA,
    "quarque_um": TokenType.QUARQUE_UM,
    "tamem": TokenType.TAMEM,
    "vam_marca": TokenType.VAM_MARCA,
    "um_o_oto": TokenType.UM_O_OTO,
    "veiz": TokenType.VEIZ,
    "sob": TokenType.SOB,
}


WORD_DELIMITER_TOKENS = {
    "uai": TokenType.UAI,
}


ALL_WORD_TOKENS = {
    **KEYWORD_TOKENS,
    **TYPE_TOKENS,
    **BOOLEAN_TOKENS,
    **WORD_OPERATOR_TOKENS,
    **WORD_DELIMITER_TOKENS,
}