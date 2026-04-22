from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Set, Tuple

# Enum usado para padronizar os tipos de estado aceitos.
# Tipos de estado aceitos no arquivo de definicao do AFD.
class EstadoTipo(Enum):
    # Estado de entrada do automato (deve existir exatamente um).
    INICIAL = "INICIAL"
    # Estado comum de passagem, sem aceitacao de token.
    INTERMEDIARIO = "INTERMEDIARIO"
    # Estado de aceitacao, normalmente associado a um token.
    FINAL = "FINAL"


# Representa um estado do automato e o token associado (quando final).
@dataclass(slots=True)
class Estado:
    # Nome textual do estado, como aparece no arquivo do automato.
    nome: str
    # Classificacao do estado (INICIAL, INTERMEDIARIO ou FINAL).
    tipo: EstadoTipo
    # Tipo de token aceito neste estado (quando aplicavel).
    token_type: Optional[str] = None


# Estrutura principal do AFD usado pelo lexer.
class Automato:
    def __init__(self) -> None:
        # Dicionario principal de estados, indexado por nome.
        # Mapa nome_estado -> Estado.
        self.estados: Dict[str, Estado] = {}
        # Tabela de transicao deterministica: (origem, char) -> destino.
        # Mapa (estado_origem, caractere) -> estado_destino.
        self.transicoes: Dict[Tuple[str, str], str] = {}
        # Nome do estado inicial; fica None ate o parse de estados.
        # Nome do estado inicial unico do automato.
        self.estado_inicial: Optional[str] = None
        # Estrutura auxiliar para consulta O(1) de estados de aceitacao.
        # Conjunto para consulta rapida de estados finais.
        self.estados_finais: Set[str] = set()

    def carregar_do_arquivo(self, caminho: str) -> None:
        # Converte caminho textual para objeto Path para facilitar validacoes.
        # Le e valida o arquivo-texto com secoes [ESTADOS] e [TRANSICOES].
        path = Path(caminho)
        # Falha cedo se o arquivo nao existir no caminho informado.
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo de definicao do automato nao encontrado: {caminho}"
            )

        # Le todo o arquivo em memoria para fazer parse em duas etapas.
        texto = path.read_text(encoding="utf-8")
        # Guarda a secao atual encontrada durante o scan linear.
        secao_atual: Optional[str] = None
        # Acumula linhas brutas da secao [ESTADOS].
        linhas_estados: list[str] = []
        # Acumula linhas brutas da secao [TRANSICOES].
        linhas_transicoes: list[str] = []

        # Primeiro separa o arquivo por secao; o parse detalhado acontece abaixo.
        for linha in texto.splitlines():
            # Remove espacos nas pontas para simplificar comparacoes.
            linha = linha.strip()
            # Ignora linhas vazias e comentarios iniciados por '#'.
            if not linha or linha.startswith("#"):
                continue

            # Detecta troca para secao de estados.
            if linha == "[ESTADOS]":
                secao_atual = "ESTADOS"
                continue

            # Detecta troca para secao de transicoes.
            if linha == "[TRANSICOES]":
                secao_atual = "TRANSICOES"
                continue

            # Encaminha a linha para a lista da secao ativa.
            if secao_atual == "ESTADOS":
                linhas_estados.append(linha)
            elif secao_atual == "TRANSICOES":
                linhas_transicoes.append(linha)

        # Etapa 1: cria estados e valida consistencia basica.
        self._processar_estados(linhas_estados)
        # Etapa 2: cria transicoes e valida referencias de origem/destino.
        self._processar_transicoes(linhas_transicoes)

        # O automato so e valido se houver exatamente um estado inicial.
        if self.estado_inicial is None:
            raise ValueError(
                "Definicao do automato invalida: estado inicial nao definido."
            )

    # Converte linhas de [ESTADOS] para objetos Estado e valida regras globais.
    def _processar_estados(self, linhas: list[str]) -> None:
        # Formato esperado por linha: nome tipo [token_type].
        for linha in linhas:
            # Divide a definicao em colunas separadas por espaco.
            partes = linha.split()
            # Linhas incompletas sao ignoradas para manter tolerancia a ruido.
            if len(partes) < 2:
                continue

            # Coluna 0: nome do estado.
            nome = partes[0]
            # Coluna 1: tipo do estado em texto.
            tipo_str = partes[1]

            try:
                # Converte string para membro do enum (com validacao implicita).
                tipo = EstadoTipo(tipo_str)
            except ValueError as exc:
                # Repassa erro com mensagem mais clara para quem configurou o arquivo.
                raise ValueError(f"Tipo de estado invalido: {tipo_str}") from exc

            # Coluna 2 (opcional): token associado ao estado final.
            token_type = partes[2] if len(partes) >= 3 else None
            # Registra/atualiza estado no dicionario principal.
            self.estados[nome] = Estado(nome=nome, tipo=tipo, token_type=token_type)

            # Garante unicidade do estado inicial.
            if tipo == EstadoTipo.INICIAL:
                # Se ja existe inicial, a definicao quebra a regra do AFD.
                if self.estado_inicial is not None:
                    raise ValueError(
                        "Definicao do automato invalida: multiplos estados iniciais definidos."
                    )
                # Guarda o nome do unico estado inicial encontrado.
                self.estado_inicial = nome

            # Guarda estados finais para validacao rapida no reconhecimento.
            if tipo == EstadoTipo.FINAL:
                # Usa set para evitar duplicidade e acelerar consultas.
                self.estados_finais.add(nome)

    # Converte linhas de [TRANSICOES] para o mapa (origem, char) -> destino.
    def _processar_transicoes(self, linhas: list[str]) -> None:
        # Formato esperado por linha: origem destino char.
        for linha in linhas:
            # Quebra a linha em 3 partes obrigatorias.
            partes = linha.split()
            # Ignora linhas fora do formato esperado.
            if len(partes) != 3:
                continue

            # Desempacota os campos da transicao.
            origem, destino, char = partes

            # Marcadores textuais para caracteres de controle no arquivo do AFD.
            if char == "<SPACE>":
                # Converte marcador textual para o caractere espaco real.
                char = " "

            # Origem precisa existir na tabela de estados.
            if origem not in self.estados:
                raise ValueError(f"Estado de origem nao definido: {origem}")
            # Destino tambem precisa existir na tabela de estados.
            if destino not in self.estados:
                raise ValueError(f"Estado de destino nao definido: {destino}")

            # Nao pode haver duas transicoes para o mesmo par (estado, char).
            chave = (origem, char)
            if chave in self.transicoes:
                raise ValueError(
                    f"Definicao do automato invalida: transicao ja definida para {origem} com '{char}'"
                )

            # Registra a transicao deterministica valida.
            self.transicoes[chave] = destino

    # Busca direta de transicao; retorna None quando nao existe caminho.
    def obter_proximo_estado(self, estado_atual: str, char: str) -> Optional[str]:
        # Acesso direto por chave composta; .get evita KeyError.
        return self.transicoes.get((estado_atual, char))

    # Consulta rapida para saber se um estado e final.
    def eh_estado_final(self, estado: str) -> bool:
        # Consulta de pertencimento em set (tipicamente O(1)).
        return estado in self.estados_finais

    # Retorna o token associado a um estado final.
    def obter_token_type(self, estado: str) -> Optional[str]:
        # Busca objeto Estado no dicionario principal.
        estado_obj = self.estados.get(estado)
        # Retorna token se estado existir; senao retorna None.
        return estado_obj.token_type if estado_obj else None

    def reconhecer(self, entrada: str) -> tuple[bool, Optional[str], int]:
        # Reconhecimento maximal munch: para no primeiro bloqueio,
        # mas retorna o ultimo estado final alcançado.
        # Se entrada e vazia ou automato esta incompleto, nao ha reconhecimento.
        if not entrada or self.estado_inicial is None:
            return (False, None, 0)

        # Inicializa no estado inicial previamente validado.
        estado_atual = self.estado_inicial
        # Guarda o ultimo estado de aceitacao visitado durante a caminhada.
        ultimo_estado_final: Optional[str] = None
        # Guarda o indice do ultimo caractere aceito.
        ultimo_indice_final = -1

        # Caminha caractere a caractere pelo prefixo da entrada.
        for i, char in enumerate(entrada):
            # Tenta avancar no AFD com o caractere atual.
            proximo = self.obter_proximo_estado(estado_atual, char)
            # Sem transicao, o reconhecimento para aqui.
            if proximo is None:
                break

            # Atualiza estado corrente para o estado de destino.
            estado_atual = proximo

            # Sempre que cair em estado final, atualiza o melhor prefixo valido.
            if self.eh_estado_final(estado_atual):
                ultimo_estado_final = estado_atual
                ultimo_indice_final = i

        # Se nenhum estado final foi visitado, nao existe token valido.
        if ultimo_estado_final is None:
            return (False, None, 0)

        # Busca o token associado ao ultimo estado final alcancado.
        token_type = self.obter_token_type(ultimo_estado_final)
        # Converte indice final em comprimento do lexema (indice + 1).
        comprimento = ultimo_indice_final + 1
        # Retorna sucesso, token identificado e tamanho do prefixo reconhecido.
        return (True, token_type, comprimento)