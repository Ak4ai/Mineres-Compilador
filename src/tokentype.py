from enum import Enum

# Lista de tipos de token da linguagem.
class TokenType(Enum):

    # Tokens internos do fluxo do compilador.
    EOF = "EOF"
    ERROR = "ERROR"

    # Identificadores
    IDENTIFIER = "IDENTIFIER"

    # Literais
    INTEGER_LITERAL = "INTEGER_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    HEX_LITERAL = "HEX_LITERAL"
    OCTAL_LITERAL = "OCTAL_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    CHAR_LITERAL = "CHAR_LITERAL"

    # Estrutura principal do programa
    BORA_CUMPADE = "bora_cumpade"
    SIMBORA = "simbora"
    CABO = "cabo"

    # Controle condicional
    UAI_SE = "uai_se"
    UAI_SENAO = "uai_senao"

    # Controle de repeticao
    ENQUANTO_TIVER_TREM = "enquanto_tiver_trem"
    RODA_ESSE_TREM = "roda_esse_trem"

    # Estrutura de selecao por casos
    DEPENDENU = "dependenu"
    DU_CASU = "du_casu"
    UAI_SO = "uai_so"

    # Comandos de fluxo simples
    TA_BAO = "ta_bao"
    PARA_O_TREM = "para_o_trem"
    TOCA_O_TREM = "toca_o_trem"

    # Entrada e saida
    XOVE = "xove"
    OIA_PROCE_VE = "oia_proce_ve"

    # TIPOS
    TREM_DI_NUMERU = "trem_di_numeru"
    TREM_CUM_VIRGULA = "trem_cum_virgula"
    TREM_DISCRITA = "trem_discrita"
    TREM_DISCOLHE = "trem_discolhe"
    TROSSO = "trosso"

    # Booleanos
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

    # OPERADORES (SIMBOLO)
    PLUS = "+"
    MINUS = "-"
    INT_DIV = "/"     # divisao inteira
    MOD = "%"         # modulo

    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="
    MULT = "*"
    ASSIGN = "="

    # DELIMITADORES
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"
    UAI = "uai"   # equivalente a ;

    # COMENTARIOS
    COMMENT_LINE = "COMMENT_LINE"
    COMMENT_BLOCK = "COMMENT_BLOCK"

    # MAIN
    MAIN = "main"

# Mapas usados pelo lexer para converter lexema textual em TokenType.
# Mapa de palavras-chave reservadas.
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
    "uai_so": TokenType.UAI_SO,

    "ta_bao": TokenType.TA_BAO,
    "para_o_trem": TokenType.PARA_O_TREM,
    "toca_o_trem": TokenType.TOCA_O_TREM,

    "xove": TokenType.XOVE,
    "oia_proce_ve": TokenType.OIA_PROCE_VE,
}

# Mapa de palavras associadas a tipos da linguagem.
TYPE_TOKENS = {
    "trem_di_numeru": TokenType.TREM_DI_NUMERU,
    "trem_cum_virgula": TokenType.TREM_CUM_VIRGULA,
    "trem_discrita": TokenType.TREM_DISCRITA,
    "trem_discolhe": TokenType.TREM_DISCOLHE,
    "trosso": TokenType.TROSSO,
}

# Mapa de literais/operadores booleanos por palavra.
BOOLEAN_TOKENS = {
    "eh": TokenType.EH,
    "num_eh": TokenType.NUM_EH,
}

# Mapa de operadores escritos por extenso.
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

# Mapa de delimitadores escritos por palavra (ex.: uai).
WORD_DELIMITER_TOKENS = {
    "uai": TokenType.UAI,
}

# Uniao de todos os mapas por palavra para classificacao final no lexer.
# Se uma palavra existir aqui, o lexer classifica direto pelo mapa.
ALL_WORD_TOKENS = {
    **KEYWORD_TOKENS,
    **TYPE_TOKENS,
    **BOOLEAN_TOKENS,
    **WORD_OPERATOR_TOKENS,
    **WORD_DELIMITER_TOKENS,
}