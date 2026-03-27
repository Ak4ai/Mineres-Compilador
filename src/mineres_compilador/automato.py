from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Set, Tuple


# Tipos de estado aceitos no arquivo de definicao do AFD.
class EstadoTipo(Enum):
    INICIAL = "INICIAL"
    INTERMEDIARIO = "INTERMEDIARIO"
    FINAL = "FINAL"


# Representa um estado do automato e o token associado (quando final).
@dataclass(slots=True)
class Estado:
    nome: str
    tipo: EstadoTipo
    token_type: Optional[str] = None


# Estrutura principal do AFD usado pelo lexer.
class Automato:
    def __init__(self) -> None:
        # Mapa nome_estado -> Estado.
        self.estados: Dict[str, Estado] = {}
        # Mapa (estado_origem, caractere) -> estado_destino.
        self.transicoes: Dict[Tuple[str, str], str] = {}
        # Nome do estado inicial unico do automato.
        self.estado_inicial: Optional[str] = None
        # Conjunto para consulta rapida de estados finais.
        self.estados_finais: Set[str] = set()

    def carregar_do_arquivo(self, caminho: str) -> None:
        # Le e valida o arquivo-texto com secoes [ESTADOS] e [TRANSICOES].
        path = Path(caminho)
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo de definicao do automato nao encontrado: {caminho}"
            )

        texto = path.read_text(encoding="utf-8")
        secao_atual: Optional[str] = None
        linhas_estados: list[str] = []
        linhas_transicoes: list[str] = []

        for linha in texto.splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue

            if linha == "[ESTADOS]":
                secao_atual = "ESTADOS"
                continue

            if linha == "[TRANSICOES]":
                secao_atual = "TRANSICOES"
                continue

            if secao_atual == "ESTADOS":
                linhas_estados.append(linha)
            elif secao_atual == "TRANSICOES":
                linhas_transicoes.append(linha)

        self._processar_estados(linhas_estados)
        self._processar_transicoes(linhas_transicoes)

        # O automato so e valido se houver exatamente um estado inicial.
        if self.estado_inicial is None:
            raise ValueError(
                "Definicao do automato invalida: estado inicial nao definido."
            )

    def _processar_estados(self, linhas: list[str]) -> None:
        # Formato esperado por linha: nome tipo [token_type].
        for linha in linhas:
            partes = linha.split()
            if len(partes) < 2:
                continue

            nome = partes[0]
            tipo_str = partes[1]

            try:
                tipo = EstadoTipo(tipo_str)
            except ValueError as exc:
                raise ValueError(f"Tipo de estado invalido: {tipo_str}") from exc

            token_type = partes[2] if len(partes) >= 3 else None
            self.estados[nome] = Estado(nome=nome, tipo=tipo, token_type=token_type)

            # Garante unicidade do estado inicial.
            if tipo == EstadoTipo.INICIAL:
                if self.estado_inicial is not None:
                    raise ValueError(
                        "Definicao do automato invalida: multiplos estados iniciais definidos."
                    )
                self.estado_inicial = nome

            # Guarda estados finais para validacao rapida no reconhecimento.
            if tipo == EstadoTipo.FINAL:
                self.estados_finais.add(nome)

    def _processar_transicoes(self, linhas: list[str]) -> None:
        # Formato esperado por linha: origem destino char.
        for linha in linhas:
            partes = linha.split()
            if len(partes) != 3:
                continue

            origem, destino, char = partes

            if origem not in self.estados:
                raise ValueError(f"Estado de origem nao definido: {origem}")
            if destino not in self.estados:
                raise ValueError(f"Estado de destino nao definido: {destino}")

            # Nao pode haver duas transicoes para o mesmo par (estado, char).
            chave = (origem, char)
            if chave in self.transicoes:
                raise ValueError(
                    f"Definicao do automato invalida: transicao ja definida para {origem} com '{char}'"
                )

            self.transicoes[chave] = destino

    def obter_proximo_estado(self, estado_atual: str, char: str) -> Optional[str]:
        return self.transicoes.get((estado_atual, char))

    def eh_estado_final(self, estado: str) -> bool:
        return estado in self.estados_finais

    def obter_token_type(self, estado: str) -> Optional[str]:
        estado_obj = self.estados.get(estado)
        return estado_obj.token_type if estado_obj else None

    def reconhecer(self, entrada: str) -> tuple[bool, Optional[str], int]:
        # Reconhecimento maximal munch: para no primeiro bloqueio,
        # mas retorna o ultimo estado final alcançado.
        if not entrada or self.estado_inicial is None:
            return (False, None, 0)

        estado_atual = self.estado_inicial
        ultimo_estado_final: Optional[str] = None
        ultimo_indice_final = -1

        for i, char in enumerate(entrada):
            proximo = self.obter_proximo_estado(estado_atual, char)
            if proximo is None:
                break

            estado_atual = proximo

            if self.eh_estado_final(estado_atual):
                ultimo_estado_final = estado_atual
                ultimo_indice_final = i

        # Se nenhum estado final foi visitado, nao existe token valido.
        if ultimo_estado_final is None:
            return (False, None, 0)

        token_type = self.obter_token_type(ultimo_estado_final)
        comprimento = ultimo_indice_final + 1
        return (True, token_type, comprimento)