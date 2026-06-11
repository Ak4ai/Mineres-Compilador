import argparse
import json
import sys
from pathlib import Path

from analisador_lexico.lexer import LexicalError, Lexer
from analisador_sintatico.analisador_sintatico import Parser, ParserError
from analisador_sintatico.interpretador import Interpretador


def _descricao_fases(executar_saida_lexica: bool, executar_sintatico: bool) -> str:
    if executar_saida_lexica and executar_sintatico:
        return "lexica + sintatica"
    if executar_saida_lexica:
        return "lexica"
    return "sintatica"


def _imprimir_resultado(
    *,
    status: str,
    executar_saida_lexica: bool,
    executar_sintatico: bool,
    total_tokens: int | None = None,
    detalhe: str | None = None,
    detalhes: list[str] | None = None,
    output_path: Path | None = None,
    json_path: Path | None = None,
    stream=sys.stdout,
) -> None:
    print("\nResultado", file=stream)
    print("---------", file=stream)
    print(f"Status: {status}", file=stream)
    print(
        f"Fases executadas: {_descricao_fases(executar_saida_lexica, executar_sintatico)}",
        file=stream,
    )

    if total_tokens is not None:
        print(f"Total de tokens: {total_tokens}", file=stream)

    if detalhe:
        print(f"Detalhe: {detalhe}", file=stream)

    if detalhes:
        print("Detalhes:", file=stream)
        for i, item in enumerate(detalhes, start=1):
            print(f"{i}. {item}", file=stream)

    if output_path is not None:
        print(f"Saida TXT: {output_path}", file=stream)
    if json_path is not None:
        print(f"Saida JSON: {json_path}", file=stream)


# Normaliza caracteres de controle para manter a tabela TXT em uma linha por token.
def _lexema_para_tabela(lexema: str) -> str:
    # Mantem cada token em uma unica linha na tabela TXT.
    return (
        lexema.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
        .replace("\r", "\\r")
    )


def _truncar_texto(texto: str, largura: int) -> str:
    # Mantem largura fixa para colunas e evita quebrar alinhamento em lexemas longos.
    if len(texto) <= largura:
        return texto
    if largura <= 3:
        return texto[:largura]
    return texto[: largura - 3] + "..."


# Monta a representacao tabular padrao usada no terminal e no arquivo .txt.
def _linhas_tabela_tokens(tokens) -> list[str]:
    largura_lexema = 36
    largura_tipo = 22
    largura_linha = 5
    largura_coluna = 6

    linhas = [
        (
            f"{'LEXEMA':<{largura_lexema}}"
            f" | {'TIPO':<{largura_tipo}}"
            f" | {'LINHA':<{largura_linha}}"
            f" | {'COLUNA':<{largura_coluna}}"
        ),
        "-" * (largura_lexema + largura_tipo + largura_linha + largura_coluna + 9),
    ]

    for token in tokens:
        lexema_tabela = _truncar_texto(_lexema_para_tabela(token.lexeme), largura_lexema)
        linhas.append(
            (
                f"{lexema_tabela:<{largura_lexema}}"
                f" | {token.type.name:<{largura_tipo}}"
                f" | {token.line:<{largura_linha}}"
                f" | {token.column:<{largura_coluna}}"
            )
        )

    return linhas


# Impressao simples no stdout para modo interativo/depuracao.
def imprimir_tokens(tokens) -> None:
    for linha in _linhas_tabela_tokens(tokens):
        print(linha)


def _linhas_codigo_intermediario(codigo) -> list[str]:
    return [
        (
            f"({_lexema_para_tabela(str(op))}, {_lexema_para_tabela(str(result))}, "
            f"{_lexema_para_tabela(str(arg1))}, {_lexema_para_tabela(str(arg2))})"
        )
        for op, result, arg1, arg2 in codigo
    ]


def imprimir_codigo_intermediario(codigo, stream=sys.stdout) -> None:
    print("\nCodigo intermediario", file=stream)
    print("--------------------", file=stream)
    for linha in _linhas_codigo_intermediario(codigo):
        print(linha, file=stream)


# Persiste a tabela em disco para uso humano.
def salvar_tokens_tabela(tokens, caminho_saida: Path) -> None:
    with caminho_saida.open("w", encoding="utf-8") as arquivo:
        for linha in _linhas_tabela_tokens(tokens):
            arquivo.write(linha + "\n")


# Persiste tokens em JSON para consumo por outras ferramentas.
def salvar_tokens_json(tokens, caminho_saida: Path) -> None:
    dados = [
        {
            "lexeme": token.lexeme,
            "type": token.type.name,
            "line": token.line,
            "column": token.column,
        }
        for token in tokens
    ]

    with caminho_saida.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


# Centraliza definicao de argumentos da CLI.
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI principal do compilador Mineres (lexico e sintatico)."
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Caminho do arquivo fonte Mineres.",
    )
    parser.add_argument(
        "-s",
        "--source",
        help="Codigo-fonte em linha unica (alternativa ao arquivo).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="saida_tokens.txt",
        help="Nome do arquivo de saida dentro da pasta 'saida' (padrao: saida_tokens.txt).",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_tokens",
        help="Imprime os tokens no terminal.",
    )
    parser.add_argument(
        "--print-codigo",
        action="store_true",
        dest="print_codigo",
        help="Imprime o codigo intermediario gerado durante a analise sintatica.",
    )
    parser.add_argument(
        "--executar",
        action="store_true",
        dest="executar_codigo",
        help="Executa o codigo intermediario usando o interpretador.",
    )
    parser.add_argument(
        "--automato",
        help="Caminho opcional para o arquivo de definicao do automato.",
    )
    # Os modos sao exclusivos para evitar combinacoes ambiguas (ex.: --lexico e --sintatico juntos).
    modo_execucao = parser.add_mutually_exclusive_group()
    modo_execucao.add_argument(
        "--lexico",
        action="store_true",
        help="Executa apenas a analise lexica.",
    )
    modo_execucao.add_argument(
        "--sintatico",
        action="store_true",
        help="Executa apenas a analise sintatica (sem gerar .txt/.json lexico).",
    )

    return parser


# Permite escolher arquivo por indice quando nenhum input e informado.
def _selecionar_arquivo_entrada_interativo() -> Path | None:
    pasta_entradas = Path("entradas")

    if not pasta_entradas.exists() or not pasta_entradas.is_dir():
        print("Pasta de entradas nao encontrada: entradas/", file=sys.stderr)
        return None

    arquivos = sorted([p for p in pasta_entradas.rglob("*") if p.is_file()])

    if not arquivos:
        print("Nenhum arquivo encontrado em entradas/", file=sys.stderr)
        return None

    grupos_ordenados = ["casos_validos", "erros_lexicos", "erros_sintaticos"]
    titulos_grupo = {
        "casos_validos": "CASOS_VALIDOS",
        "erros_lexicos": "ERROS LEXICOS",
        "erros_sintaticos": "ERROS SINTATICOS",
    }

    arquivos_por_grupo: dict[str, list[Path]] = {}
    for arquivo in arquivos:
        rel = arquivo.relative_to(pasta_entradas)
        grupo = rel.parts[0] if len(rel.parts) > 1 else "outros"
        arquivos_por_grupo.setdefault(grupo, []).append(arquivo)

    ordem_grupos = [g for g in grupos_ordenados if g in arquivos_por_grupo]
    grupos_restantes = sorted(g for g in arquivos_por_grupo if g not in grupos_ordenados)
    ordem_grupos.extend(grupos_restantes)

    print("Arquivos de entrada disponiveis:")
    arquivos_indexados: list[Path] = []

    for grupo in ordem_grupos:
        titulo = titulos_grupo.get(grupo, grupo.upper())
        print(f"\n----- {titulo} -----")

        for arquivo in arquivos_por_grupo[grupo]:
            arquivos_indexados.append(arquivo)
            indice = len(arquivos_indexados)
            rel = arquivo.relative_to(pasta_entradas)

            # Para grupos conhecidos, mostra o caminho sem o prefixo do grupo.
            if rel.parts and rel.parts[0] in titulos_grupo:
                exibicao = Path(*rel.parts[1:]) if len(rel.parts) > 1 else rel
            else:
                exibicao = rel

            print(f"{indice} - {exibicao}")

    while True:
        escolha = input("Digite o numero do arquivo de entrada: ").strip()

        if not escolha.isdigit():
            print("Entrada invalida. Digite apenas um numero.")
            continue

        indice = int(escolha)
        if indice < 1 or indice > len(arquivos_indexados):
            print(
                f"Opcao invalida. Escolha um numero entre 1 e {len(arquivos_indexados)}."
            )
            continue

        return arquivos_indexados[indice - 1]


# Fluxo principal da aplicacao:
# 1) ler entrada,
# 2) executar lexer,
# 3) executar sintatico (opcional),
# 4) gerar saidas,
# 5) retornar codigo de status.
def run() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    # Modo padrao: executa lexico + sintatico.
    executar_saida_lexica = not args.sintatico
    executar_sintatico = not args.lexico

    if args.print_codigo and not executar_sintatico:
        parser.error("A opcao --print-codigo exige execucao da analise sintatica.")
    
    if args.executar_codigo and not executar_sintatico:
        parser.error("A opcao --executar exige execucao da analise sintatica.")

    # Nao permite arquivo e --source ao mesmo tempo.
    if args.input is not None and args.source is not None:
        parser.error("Informe somente uma entrada: arquivo OU --source.")

    lexer = Lexer(caminho_automato=args.automato)

    try:
        if args.source is not None:
            lexer.carregar_string(args.source)
        else:
            if args.input is not None:
                input_path = Path(args.input)
            else:
                input_path = _selecionar_arquivo_entrada_interativo()
                if input_path is None:
                    return 2
                print(f"Arquivo selecionado: {input_path}")

            if not input_path.exists():
                print(f"Arquivo de entrada nao encontrado: {input_path}", file=sys.stderr)
                return 2
            lexer.carregar_arquivo(str(input_path))

        # Comportamento padrao: analisar todo o arquivo e acumular erros lexicos.
        tokens = lexer.analisar(continuar_apos_erro=True)

        # Se houver erro lexico, nao imprime tabela e nao gera saida de sucesso.
        if lexer.errors:
            # Em erro lexico, o sintatico nao deve ser reportado como executado.
            _imprimir_resultado(
                status="erro",
                executar_saida_lexica=executar_saida_lexica,
                executar_sintatico=False,
                detalhe=f"Foram encontrados {len(lexer.errors)} erro(s) lexicos.",
                detalhes=[str(erro) for erro in lexer.errors],
                stream=sys.stderr,
            )
            return 1

        # Opcional: valida sintaxe com o parser recursivo descendente.
        parser_sintatico = None
        if executar_sintatico:
            try:
                parser_sintatico = Parser(tokens)
                parser_sintatico.parse()
            except ParserError as error:
                _imprimir_resultado(
                    status="erro",
                    executar_saida_lexica=executar_saida_lexica,
                    executar_sintatico=executar_sintatico,
                    detalhe=str(error),
                    stream=sys.stderr,
                )
                return 1
        
        # Executa código intermediário se solicitado
        if args.executar_codigo and parser_sintatico is not None:
            print("\nExecutando codigo intermediario...")
            print("=" * 70)
            interpretador = Interpretador(parser_sintatico.codigo)
            sucesso = interpretador.executar()
            
            if sucesso:
                saida = interpretador.get_saida()
                if saida:
                    print(saida)
            else:
                erros = interpretador.get_erros()
                print(f"Erro durante execução: {erros}", file=sys.stderr)
                return 1

        # Modo dedicado para validar apenas sintaxe, sem artefatos lexicos.
        if not executar_saida_lexica:
            if args.print_codigo and parser_sintatico is not None:
                imprimir_codigo_intermediario(parser_sintatico.codigo)
            _imprimir_resultado(
                status="sucesso",
                executar_saida_lexica=executar_saida_lexica,
                executar_sintatico=executar_sintatico,
                total_tokens=len(tokens),
            )
            return 0

        if args.print_codigo and parser_sintatico is not None:
            imprimir_codigo_intermediario(parser_sintatico.codigo)

        saida_dir = Path("saida")
        saida_dir.mkdir(parents=True, exist_ok=True)

        # Usa apenas o nome do arquivo para impedir escrita fora de `saida/`.
        output_path = saida_dir / Path(args.output).name
        salvar_tokens_tabela(tokens, output_path)

        json_path = saida_dir / "saida_tokens.json"
        salvar_tokens_json(tokens, json_path)

        if args.print_tokens:
            imprimir_tokens(tokens)

        _imprimir_resultado(
            status="sucesso",
            executar_saida_lexica=executar_saida_lexica,
            executar_sintatico=executar_sintatico,
            total_tokens=len(tokens),
            output_path=output_path,
            json_path=json_path,
        )
        return 0

    except LexicalError as error:
        _imprimir_resultado(
            status="erro",
            executar_saida_lexica=executar_saida_lexica,
            executar_sintatico=False,
            detalhe=str(error),
            stream=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(run())
