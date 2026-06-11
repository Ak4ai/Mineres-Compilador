#!/usr/bin/env python3
"""
Script elegante para rodar todos os testes do compilador Mineres.
Integra testes válidos, erros léxicos, erros sintáticos e código intermediário.
"""

import subprocess
import sys
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TestCategory(Enum):
    """Categorias de testes disponíveis."""
    VALIDOS = ("Testes Válidos", "entradas/casos_validos")
    ERROS_LEXICOS = ("Erros Léxicos", "entradas/erros_lexicos")
    ERROS_SINTATICOS = ("Erros Sintáticos", "entradas/erros_sintaticos")
    CODIGO_INTERMEDIARIO = ("Código Intermediário", "entradas/testes_codigo_intermediario")
    EXEMPLOS_BASE = ("Exemplos do Projeto Base", "entradas/exemplos_base")
    
    def __init__(self, descricao: str, caminho: str):
        self.descricao = descricao
        self.caminho = caminho


@dataclass
class TestResult:
    """Resultado de um teste individual."""
    nome: str
    categoria: str
    sucesso: bool
    retorno: int
    mensagem: str
    stdout: str = ""
    stderr: str = ""


class TestRunner:
    """Executor de testes para o compilador Mineres."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.resultados: list[TestResult] = []
        
    def _executar_teste(self, arquivo_teste: Path, categoria: str) -> TestResult:
        """Executa um arquivo de teste individual."""
        try:
            result = subprocess.run(
                ["python", "src/main.py", "--print-codigo", str(arquivo_teste)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Testes de erro devem retornar código 1 (isso é sucesso)
            # Testes válidos devem retornar código 0
            eh_teste_de_erro = "erro" in categoria.lower() or "erros" in categoria.lower()
            sucesso = (result.returncode == 1) if eh_teste_de_erro else (result.returncode == 0)
            mensagem = "✅ OK" if sucesso else f"❌ Falha (código {result.returncode})"
            
            return TestResult(
                nome=arquivo_teste.name,
                categoria=categoria,
                sucesso=sucesso,
                retorno=result.returncode,
                mensagem=mensagem,
                stdout=result.stdout,
                stderr=result.stderr
            )
        
        except subprocess.TimeoutExpired:
            return TestResult(
                nome=arquivo_teste.name,
                categoria=categoria,
                sucesso=False,
                retorno=-1,
                mensagem="⏱️  Timeout",
            )
        except Exception as e:
            return TestResult(
                nome=arquivo_teste.name,
                categoria=categoria,
                sucesso=False,
                retorno=-1,
                mensagem=f"❌ Erro: {e}",
            )
    
    def rodar_categoria(self, categoria: TestCategory, verboso: bool = False) -> None:
        """Executa todos os testes de uma categoria."""
        caminho_categoria = self.project_root / categoria.caminho
        
        if not caminho_categoria.exists():
            print(f"⚠️  Diretório não encontrado: {caminho_categoria}")
            return
        
        # Filtra arquivos de teste válidos (exclui saída e arquivos especiais)
        arquivos_excluir = {"saida.txt", "saida_tokens.txt", "output.txt"}
        testes = sorted([
            f for f in caminho_categoria.glob("*.txt")
            if f.name not in arquivos_excluir
        ])
        
        if not testes:
            print(f"⚠️  Nenhum teste encontrado em {categoria.caminho}")
            return
        
        print(f"\n{'='*80}")
        print(f"🧪 {categoria.descricao} ({len(testes)} testes)")
        print(f"{'='*80}")
        
        for i, arquivo_teste in enumerate(testes, 1):
            resultado = self._executar_teste(arquivo_teste, categoria.descricao)
            self.resultados.append(resultado)
            
            print(f"  [{i:2d}/{len(testes)}] {resultado.nome:<40} {resultado.mensagem}")
            
            if verboso and not resultado.sucesso:
                if resultado.stderr:
                    print(f"        STDERR: {resultado.stderr[:100]}")
                if resultado.stdout:
                    print(f"        STDOUT: {resultado.stdout[:100]}")
    
    def rodar_todos(self, verboso: bool = False, categorias: Optional[list[TestCategory]] = None) -> None:
        """Executa todos os testes ou categorias específicas."""
        categorias_para_testar = categorias or list(TestCategory)
        
        for categoria in categorias_para_testar:
            self.rodar_categoria(categoria, verboso)
    
    def imprimir_resumo(self) -> None:
        """Imprime um resumo dos testes executados."""
        if not self.resultados:
            print("❌ Nenhum teste foi executado.")
            return
        
        print(f"\n{'='*80}")
        print("📊 RESUMO DOS TESTES")
        print(f"{'='*80}")
        
        # Agrupar por categoria
        por_categoria = {}
        for resultado in self.resultados:
            if resultado.categoria not in por_categoria:
                por_categoria[resultado.categoria] = {"total": 0, "sucesso": 0}
            por_categoria[resultado.categoria]["total"] += 1
            if resultado.sucesso:
                por_categoria[resultado.categoria]["sucesso"] += 1
        
        # Exibir estatísticas por categoria
        total_geral = 0
        sucesso_geral = 0
        
        for categoria in sorted(por_categoria.keys()):
            stats = por_categoria[categoria]
            taxa = (stats["sucesso"] / stats["total"] * 100) if stats["total"] > 0 else 0
            emoji = "✅" if taxa == 100 else "⚠️ " if taxa > 0 else "❌"
            
            print(f"{emoji} {categoria:.<40} {stats['sucesso']:2d}/{stats['total']:2d} ({taxa:5.1f}%)")
            
            total_geral += stats["total"]
            sucesso_geral += stats["sucesso"]
        
        # Resumo geral
        print(f"{'='*80}")
        taxa_geral = (sucesso_geral / total_geral * 100) if total_geral > 0 else 0
        emoji_final = "✅" if taxa_geral == 100 else "⚠️ " if taxa_geral > 0 else "❌"
        
        print(f"{emoji_final} TOTAL:{'.'*35} {sucesso_geral:2d}/{total_geral:2d} ({taxa_geral:5.1f}%)")
        print(f"{'='*80}\n")
        
        return taxa_geral == 100


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Execute testes do compilador Mineres de forma elegante."
    )
    parser.add_argument(
        "-v", "--verboso",
        action="store_true",
        help="Modo verboso: mostra erros detalhados"
    )
    parser.add_argument(
        "-c", "--categoria",
        choices=[cat.name.lower() for cat in TestCategory],
        help="Executa apenas uma categoria de testes"
    )
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    runner = TestRunner(project_root)
    
    # Selecionar categorias
    categorias = None
    if args.categoria:
        categoria_nome = args.categoria.upper()
        categorias = [TestCategory[categoria_nome]]
    
    # Executar testes
    runner.rodar_todos(verboso=args.verboso, categorias=categorias)
    
    # Exibir resumo
    sucesso = runner.imprimir_resumo()
    
    # Código de saída
    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    main()
