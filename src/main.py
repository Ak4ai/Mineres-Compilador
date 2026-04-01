import argparse
import json
import sys
from pathlib import Path

from mineres_compilador.lexer import LexicalError, Lexer


def _lexema_para_tabela(lexema: str) -> str:
    # Mantem cada token em uma unica linha na tabela TXT.
    return (
        lexema.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
        .replace("\r", "\\r")
    )


def _linhas_tabela_tokens(tokens) -> list[str]:
    linhas = [
        f"{'LEXEMA':<20} {'TIPO':<20} {'LINHA':<5} {'COLUNA':<6}",
        "-" * 60,
    ]

    for token in tokens:
        lexema_tabela = _lexema_para_tabela(token.lexeme)
        linhas.append(
            f"{lexema_tabela:<20} {token.type.name:<20} {token.line:<5} {token.column:<6}"
        )

    return linhas


def imprimir_tokens(tokens) -> None:
    for linha in _linhas_tabela_tokens(tokens):
        print(linha)


def salvar_tokens_tabela(tokens, caminho_saida: Path) -> None:
    with caminho_saida.open("w", encoding="utf-8") as arquivo:
        for linha in _linhas_tabela_tokens(tokens):
            arquivo.write(linha + "\n")


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


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI do analisador lexico da linguagem Mineres."
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
        "--automato",
        help="Caminho opcional para o arquivo de definicao do automato.",
    )

    return parser


def run() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    # Garante uma unica fonte de entrada: arquivo ou string.
    if bool(args.input) == bool(args.source):
        parser.error("Informe exatamente uma entrada: arquivo ou --source.")

    lexer = Lexer(caminho_automato=args.automato)

    try:
        if args.source is not None:
            lexer.carregar_string(args.source)
        else:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Arquivo de entrada nao encontrado: {input_path}", file=sys.stderr)
                return 2
            lexer.carregar_arquivo(str(input_path))

        tokens = lexer.analisar()

        saida_dir = Path("saida")
        saida_dir.mkdir(parents=True, exist_ok=True)

        output_path = saida_dir / Path(args.output).name
        salvar_tokens_tabela(tokens, output_path)

        json_path = saida_dir / "saida_tokens.json"
        salvar_tokens_json(tokens, json_path)

        if args.print_tokens:
            imprimir_tokens(tokens)

        print(f"Analise concluida com sucesso. Tokens salvos em: {output_path}")
        print(f"Arquivo JSON gerado em: {json_path}")
        return 0

    except LexicalError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(run())
