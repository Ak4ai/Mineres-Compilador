"""Definicoes de tokens para o lexer de Mineres.

Este modulo centraliza todos os tipos de token aceitos pela
especificacao da linguagem Mineres.
"""

from enum import Enum


class TokenType(Enum):
    
    # CONTROLE
    EOF = "EOF"
    ERROR = "ERROR"

    # IDENTIFICADORES
    IDENTIFIER = "IDENTIFIER"

    # LITERAIS
    INTEGER_LITERAL = "INTEGER_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    HEX_LITERAL = "HEX_LITERAL"
    OCTAL_LITERAL = "OCTAL_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    CHAR_LITERAL = "CHAR_LITERAL"

    # PALAVRAS RESERVADAS
    BORA_CUMPADE = "bora_cumpade"
    SIMBORA = "simbora"
    CABO = "cabo"

    UAI_SE = "uai_se"
    UAI_SENAO = "uai_senao"

    ENQUANTO_TIVER_TREM = "enquanto_tiver_trem"
    RODA_ESSE_TREM = "roda_esse_trem"

    DEPENDENU = "dependenu"
    DU_CASU = "du_casu"

    TA_BAO = "ta_bao"
    PARA_O_TREM = "para_o_trem"
    TOCA_O_TREM = "toca_o_trem"

    XOVE = "xove"
    OIA_PROCE_VE = "oia_proce_ve"

    # TIPOS    
    TREM_DI_NUMERU = "trem_di_numeru"
    TREM_CUM_VIRGULA = "trem_cum_virgula"
    TREM_DISCRITA = "trem_discrita"
    TREM_DISCOLHE = "trem_discolhe"
    TROSSO = "trosso"

    # BOOLEANOS
    EH = "eh"
    NUM_EH = "num_eh"

    # OPERADORES (PALAVRA)    
    FICA_ASSIM_ENTAO = "fica_assim_entao"
    MEMA_COISA = "mema_coisa"
    NEH_NADA = "neh_nada"

    QUARQUE_UM = "quarque_um"
    TAMEM = "tamem"
    VAM_MARCA = "vam_marca"
    UM_O_OTO = "um_o_oto"

    VEIZ = "veiz"
    SOB = "sob"

    # OPERADORES (SÍMBOLO)
    PLUS = "+"
    MINUS = "-"
    INT_DIV = "/"     # divisão inteira
    MOD = "%"         # módulo

    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="
    
    # DELIMITADORES    
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    UAI = "uai"   # equivalente a ;
    
    # COMENTÁRIOS
    COMMENT_LINE = "COMMENT_LINE"
    COMMENT_BLOCK = "COMMENT_BLOCK"
    
    # MAIN
    MAIN = "main"
    
KEYWORD_TOKENS = {
    "bora_cumpade": TokenType.BORA_CUMPADE,
    "main": TokenType.MAIN,
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
    "trem_di_numeru": TokenType.TREM_DI_NUMERU,
    "trem_cum_virgula": TokenType.TREM_CUM_VIRGULA,
    "trem_discrita": TokenType.TREM_DISCRITA,
    "trem_discolhe": TokenType.TREM_DISCOLHE,
    "trosso": TokenType.TROSSO,
}
    
BOOLEAN_TOKENS = {
    "eh": TokenType.EH,
    "num_eh": TokenType.NUM_EH,
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