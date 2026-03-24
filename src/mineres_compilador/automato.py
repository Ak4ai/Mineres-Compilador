from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Set, Tuple


class EstadoTipo(Enum):
    INICIAL = "INICIAL"
    INTERMEDIARIO = "INTERMEDIARIO"
    FINAL = "FINAL"


@dataclass(slots=True)
class Estado:
    nome: str
    tipo: EstadoTipo
    token_type: Optional[str] = None


class Automato:
    def __init__(self) -> None:
        self.estados: Dict[str, Estado] = {}
        self.transicoes: Dict[Tuple[str, str], str] = {}
        self.estado_inicial: Optional[str] = None
        self.estados_finais: Set[str] = set()

    def carregar_do_arquivo(self, caminho: str) -> None:
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

        if self.estado_inicial is None:
            raise ValueError(
                "Definicao do automato invalida: estado inicial nao definido."
            )

    def _processar_estados(self, linhas: list[str]) -> None:
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

            if tipo == EstadoTipo.INICIAL:
                if self.estado_inicial is not None:
                    raise ValueError(
                        "Definicao do automato invalida: multiplos estados iniciais definidos."
                    )
                self.estado_inicial = nome

            if tipo == EstadoTipo.FINAL:
                self.estados_finais.add(nome)

    def _processar_transicoes(self, linhas: list[str]) -> None:
        for linha in linhas:
            partes = linha.split()
            if len(partes) != 3:
                continue

            origem, destino, char = partes

            if origem not in self.estados:
                raise ValueError(f"Estado de origem nao definido: {origem}")
            if destino not in self.estados:
                raise ValueError(f"Estado de destino nao definido: {destino}")

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

        if ultimo_estado_final is None:
            return (False, None, 0)

        token_type = self.obter_token_type(ultimo_estado_final)
        comprimento = ultimo_indice_final + 1
        return (True, token_type, comprimento)