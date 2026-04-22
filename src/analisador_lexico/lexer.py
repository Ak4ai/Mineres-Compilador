# Lexer para a linguagem Mineres usando AFD explicito.

# Permite usar anotacoes de tipo mais modernas sem custo de resolucao imediata.
from __future__ import annotations

# Path e usado para montar o caminho padrao do arquivo do automato.
from pathlib import Path
# Optional e usado para parametros que podem ser None.
from typing import Optional

# Importa a implementacao do automato finito deterministico (AFD).
from .automato import Automato
# Importa a estrutura de token gerada pelo lexer.
from mineires_token import Token
# Importa enum de tipos de token e mapa de palavras reservadas.
from tokentype import ALL_WORD_TOKENS, TokenType


class LexicalError(Exception):
    # Excecao com contexto completo para erro lexico.
    def __init__(
        self,
        # Trecho da entrada que causou o erro.
        lexeme: str,
        # Linha em que o erro comeca (base 1).
        line: int,
        # Coluna em que o erro comeca (base 1).
        column: int,
        # Categoria do erro lexico para diagnostico.
        error_type: str = "ERRO_LEXICO",
    ) -> None:
        # Salva o tipo/categoria do erro para consumo externo.
        self.error_type = error_type
        # Salva o lexema ofensivo completo.
        self.lexeme = lexeme
        # Salva a linha de ocorrencia.
        self.line = line
        # Salva a coluna de ocorrencia.
        self.column = column
        # Preview textual usado na mensagem final.
        lexeme_preview = lexeme

        # Evita poluir a saida em erros de comentario de bloco sem fechamento.
        if error_type == "COMENTARIO_NAO_FECHADO" and lexeme.startswith("causo"):
            # Mostra apenas prefixo amigavel em vez de todo o restante do arquivo.
            lexeme_preview = "causo..."

        # Mensagem padronizada exibindo tipo, lexema e posicao.
        super().__init__(
            f"Erro lexico ({error_type}): '{lexeme_preview}' na linha {line}, coluna {column}"
        )


class Lexer:
    # Tokeniza o codigo-fonte usando o automato carregado.

    def __init__(self, caminho_automato: Optional[str] = None) -> None:
        # Se nao receber caminho, usa o arquivo padrao dentro da pasta automatos.
        if caminho_automato is None:
            caminho_automato = str(
                Path(__file__).resolve().parents[2] / "automatos" / "automato.txt"
            )

        # Instancia o AFD e carrega sua definicao textual.
        self.automato = Automato()
        self.automato.carregar_do_arquivo(caminho_automato)

        # Buffer da entrada completa que sera tokenizada.
        self.source = ""
        # Ponteiro de leitura atual na string source.
        self.pos = 0
        # Linha atual durante a varredura.
        self.line = 1
        # Coluna atual durante a varredura.
        self.column = 1
        # Lista de tokens reconhecidos em ordem.
        self.tokens: list[Token] = []
        # Lista de erros acumulados (usada quando continuar_apos_erro=True).
        self.errors: list[LexicalError] = []

    def carregar_arquivo(self, caminho: str) -> None:
        # Le fonte de arquivo e reinicia estado interno.
        # Usa utf-8 para manter compatibilidade com o projeto.
        with open(caminho, "r", encoding="utf-8") as arquivo:
            # Le todo o arquivo para memoria (tokenizacao sequencial).
            self.source = arquivo.read()
        # Sempre reseta ponteiro, linha, coluna, tokens e erros.
        self._resetar_estado()

    def carregar_string(self, conteudo: str) -> None:
        # Le fonte direta (CLI -s) e reinicia estado interno.
        # Permite analisar texto em memoria sem arquivo fisico.
        self.source = conteudo
        # Garante estado limpo antes da proxima analise.
        self._resetar_estado()

    def _resetar_estado(self) -> None:
        # Reinicia ponteiro para o comeco da entrada.
        self.pos = 0
        # Reinicia contagem de linha para 1.
        self.line = 1
        # Reinicia contagem de coluna para 1.
        self.column = 1
        # Limpa qualquer token antigo.
        self.tokens = []
        # Limpa qualquer erro antigo.
        self.errors = []

    def analisar(self, continuar_apos_erro: bool = False) -> list[Token]:
        # API principal do lexer; opcionalmente coleta multiplos erros.
        # Reforca reset completo para cada chamada de analise.
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.errors = []
        # Delega a tokenizacao real para o metodo tokenize.
        return self.tokenize(continuar_apos_erro=continuar_apos_erro)

    def is_at_end(self) -> bool:
        # Indica se a posicao atual chegou ao fim da entrada.
        # Retorna True quando nao ha mais caracteres para ler.
        return self.pos >= len(self.source)

    def _handle_whitespace(self, char: str) -> None:
        # Consome espacos em branco e atualiza linha/coluna.
        # Quebra de linha altera linha e reseta coluna.
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            # Espaco, tab e carriage return contam como avanco de coluna.
            self.column += 1

        # Em todos os casos, avanca uma posicao no buffer da entrada.
        self.pos += 1

    def _advance_position(self, lexeme: str) -> None:
        # Avanca linha/coluna de acordo com o lexema consumido.
        # Percorre cada caractere para contabilizar novas linhas corretamente.
        for char in lexeme:
            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                # Caractere comum avanca apenas a coluna.
                self.column += 1

    def _recuperar_posicao_apos_erro(self, erro: LexicalError) -> None:
        # Em modo de coleta de erros, tenta pular para um ponto util de retomada.
        # Captura tudo que ainda nao foi consumido a partir da posicao atual.
        restante = self.source[self.pos :]

        # Para string/char nao fechado, consome ate fim da linha para evitar loop.
        if erro.error_type in {"STRING_NAO_FECHADA", "CHAR_NAO_FECHADO"}:
            # Procura quebra de linha para retomar no proximo contexto seguro.
            fim_linha = restante.find("\n")
            # Se nao houver nova linha, consome ate o fim da entrada.
            trecho = restante if fim_linha == -1 else restante[: fim_linha + 1]
        elif erro.error_type == "COMENTARIO_NAO_FECHADO":
            # Sem marcador de fim, o comentario consome o restante da entrada.
            trecho = restante
        else:
            # Regra geral: pula o lexema ofensivo detectado.
            # Garante avanco minimo de 1 caractere para nao travar em loop infinito.
            tamanho = max(1, len(erro.lexeme))
            trecho = self.source[self.pos : self.pos + tamanho]

        # Protecao extra para cenarios extremos de fatia vazia.
        if not trecho:
            trecho = self.source[self.pos : self.pos + 1]

        # Atualiza linha/coluna com base no trecho descartado.
        self._advance_position(trecho)
        # Move o ponteiro bruto da entrada pelo mesmo tamanho.
        self.pos += len(trecho)

    def tokenize(self, continuar_apos_erro: bool = False) -> list[Token]:
        # Executa o loop principal de analise lexica.
        # O loop so termina quando o ponteiro alcanca o fim da source.
        while not self.is_at_end():
            # Captura o caractere atual para decisoes rapidas de fluxo.
            char_atual = self.source[self.pos]

            # Whitespace puro e descartado (nao gera token aqui).
            if char_atual in {" ", "\t", "\r", "\n"}:
                self._handle_whitespace(char_atual)
                continue

            # Salva posicao inicial do proximo token/erro.
            inicio_linha = self.line
            inicio_coluna = self.column
            # Fatia do texto ainda nao consumido; usada em validacoes locais.
            restante = self.source[self.pos :]

            try:
                # Detecta string nao fechada antes do automato.
                if restante.startswith('"'):
                    # Procura aspas de fechamento e eventual quebra de linha.
                    fechamento = restante.find('"', 1)
                    fim_linha = restante.find("\n")

                    if fechamento == -1 or (fim_linha != -1 and fim_linha < fechamento):
                        # Lexema com problema vai ate fim da linha ou EOF.
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
                    # Busca fechamento de literal char e detecta quebra de linha precoce.
                    fechamento = restante.find("'", 1)
                    fim_linha = restante.find("\n")

                    if fechamento == -1 or (fim_linha != -1 and fim_linha < fechamento):
                        raise LexicalError(
                            restante,
                            inicio_linha,
                            inicio_coluna,
                            "CHAR_NAO_FECHADO",
                        )

                    # Extrai conteudo interno entre aspas simples.
                    conteudo = restante[1:fechamento]
                    # Lista branca de escapes permitidos para literal char.
                    escapes_validos = {"n", "t", "r", "\\", "'", '"', "0", "b", "f", "v"}

                    # Rejeita char vazio ('').
                    if not conteudo:
                        raise LexicalError(
                            restante[: fechamento + 1],
                            inicio_linha,
                            inicio_coluna,
                            "CHAR_MAL_FORMADO",
                        )

                    # Caso de escape: deve ter exatamente dois caracteres (ex.: \n).
                    if conteudo.startswith("\\"):
                        if len(conteudo) != 2 or conteudo[1] not in escapes_validos:
                            raise LexicalError(
                                restante[: fechamento + 1],
                                inicio_linha,
                                inicio_coluna,
                                "CHAR_MAL_FORMADO",
                            )
                    elif len(conteudo) != 1:
                        # Caso sem escape: deve ter exatamente um unico caractere.
                        raise LexicalError(
                            restante[: fechamento + 1],
                            inicio_linha,
                            inicio_coluna,
                            "CHAR_MAL_FORMADO",
                        )

                # Trata comentario de linha antes do automato.
                if restante.startswith("//"):
                    # Captura ate quebra de linha para formar o lexema do comentario.
                    fim_linha = restante.find("\n")
                    if fim_linha == -1:
                        # Comentario ate EOF.
                        lexeme = restante
                    else:
                        # Comentario ate o fim da linha atual (inclui \n).
                        lexeme = restante[: fim_linha + 1]

                    # Emite token de comentario de linha.
                    self.tokens.append(
                        Token(TokenType.COMMENT_LINE, lexeme, inicio_linha, inicio_coluna)
                    )
                    # Atualiza linha/coluna pelo tamanho real do lexema consumido.
                    self._advance_position(lexeme)
                    # Avanca o ponteiro de leitura no buffer.
                    self.pos += len(lexeme)
                    continue

                # Trata comentario de bloco antes do automato.
                if restante.startswith("causo"):
                    # Marcador de fechamento definido pela linguagem Mineres.
                    marcador_fim = "fim_do_causo"
                    # Busca o primeiro fechamento valido no restante da entrada.
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

                    # Calcula limite final do comentario incluindo o marcador de fim.
                    fim_comentario = indice_fim + len(marcador_fim)
                    lexeme = restante[:fim_comentario]
                    # Emite token de comentario de bloco.
                    self.tokens.append(
                        Token(TokenType.COMMENT_BLOCK, lexeme, inicio_linha, inicio_coluna)
                    )
                    # Avanca metadados de posicao e ponteiro bruto.
                    self._advance_position(lexeme)
                    self.pos += len(lexeme)
                    continue

                # O AFD reconhece o maior prefixo valido a partir da posicao atual.
                # Retorno: (sucesso, token_em_texto, tamanho_do_lexema).
                ok, token_type_str, tamanho = self.automato.reconhecer(restante)

                # Em falha de reconhecimento, emite erro e avanca um caractere.
                if not ok or tamanho == 0:
                    raise LexicalError(
                        char_atual,
                        inicio_linha,
                        inicio_coluna,
                        "SIMBOLO_DESCONHECIDO",
                    )

                # Recorta exatamente o lexema reconhecido pelo automato.
                lexeme = self.source[self.pos : self.pos + tamanho]

                # Classificacao final: palavras conhecidas vencem IDENTIFIER.
                if lexeme in ALL_WORD_TOKENS:
                    # Se for palavra reservada/keyword, usa o tipo mapeado.
                    token_type = ALL_WORD_TOKENS[lexeme]
                else:
                    # Tipos numericos para validacoes adicionais de sufixo invalido.
                    tipos_numericos = {
                        "INTEGER_LITERAL",
                        "FLOAT_LITERAL",
                        "HEX_LITERAL",
                        "OCTAL_LITERAL",
                    }
                    # Separadores que delimitam o fim natural de um lexema.
                    separadores = set(" \t\r\n(){}[],:;+-*/%<>=\"'")

                    # Se um numero eh seguido por sufixo colado (ex.: 0x10G, 12.3.4),
                    # classifica como numero mal formado em vez de simbolo desconhecido.
                    if token_type_str in tipos_numericos:
                        # Posicao imediatamente apos o numero reconhecido.
                        proxima_pos = self.pos + tamanho
                        if proxima_pos < len(self.source):
                            proximo_char = self.source[proxima_pos]
                            # Se nao houver separador, existe sufixo colado.
                            if proximo_char not in separadores:
                                fim_lexema = proxima_pos
                                while (
                                    fim_lexema < len(self.source)
                                    and self.source[fim_lexema] not in separadores
                                ):
                                    # Expande ate o fim do bloco sem separador.
                                    fim_lexema += 1

                                # Captura o lexema inteiro mal formado para mensagem clara.
                                lexema_invalido = self.source[self.pos : fim_lexema]
                                raise LexicalError(
                                    lexema_invalido,
                                    inicio_linha,
                                    inicio_coluna,
                                    "NUMERO_MAL_FORMADO",
                                )

                    # Validacoes extras para numeros mal formados.
                    numero_invalido = False

                    # Se comeca com 0x, tenta validar como hexadecimal.
                    if lexeme.lower().startswith("0x"):
                        try:
                            int(lexeme, 16)
                        except ValueError:
                            numero_invalido = True

                    # Numeros com zero a esquerda sao testados como octal.
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

                    # Qualquer falha numerica vira erro lexico de numero mal formado.
                    if numero_invalido:
                        raise LexicalError(
                            lexeme,
                            inicio_linha,
                            inicio_coluna,
                            "NUMERO_MAL_FORMADO",
                        )

                    # Valida o token retornado pelo automato antes de converter.
                    if not token_type_str or token_type_str not in TokenType._value2member_map_:
                        # Defesa contra inconsistencias entre automato e enum de tokens.
                        raise LexicalError(
                            lexeme,
                            inicio_linha,
                            inicio_coluna,
                            "TOKEN_DESCONHECIDO",
                        )
                    # Converte string do automato para membro do enum TokenType.
                    token_type = TokenType(token_type_str)

                # Emite token reconhecido com posicao inicial de origem.
                self.tokens.append(Token(token_type, lexeme, inicio_linha, inicio_coluna))
                # Atualiza linha/coluna pelo conteudo consumido.
                self._advance_position(lexeme)
                # Avanca ponteiro principal para depois do lexema.
                self.pos += len(lexeme)
            except LexicalError as erro:
                # Comportamento padrao: falha rapida no primeiro erro.
                if not continuar_apos_erro:
                    # Relanca o erro para o chamador tratar imediatamente.
                    raise

                # Modo alternativo: acumula erros e tenta seguir a analise.
                # Guarda o erro para relatorio posterior.
                self.errors.append(erro)
                # Aplica estrategia de recuperacao para nao travar no mesmo ponto.
                self._recuperar_posicao_apos_erro(erro)
                continue

        # Sempre finaliza com token EOF para simplificar parser sintatico.
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        # Retorna lista final de tokens em ordem de leitura.
        return self.tokens