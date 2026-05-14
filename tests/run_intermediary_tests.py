#!/usr/bin/env python3
"""
Script para rodar todos os testes de código intermediário (01-20)
e exibir as saídas de forma organizada.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_tests():
    project_root = Path(__file__).parent
    tests_dir = project_root / "entradas" / "testes_codigo_intermediario"
    
    if not tests_dir.exists():
        print(f"❌ Diretório não encontrado: {tests_dir}")
        sys.exit(1)
    
    # Coleta todos os arquivos de teste
    test_files = sorted([f for f in tests_dir.glob("*.txt")])
    
    if not test_files:
        print("❌ Nenhum arquivo de teste encontrado!")
        sys.exit(1)
    
    print(f"🧪 Executando {len(test_files)} testes de código intermediário...\n")
    print("=" * 80)
    
    for i, test_file in enumerate(test_files, 1):
        test_name = test_file.name
        print(f"\n📝 Teste {i}: {test_name}")
        print("-" * 80)
        
        try:
            # Executa o compilador com o arquivo de teste
            result = subprocess.run(
                ["python", "src/main.py", "--print-codigo", str(test_file)],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Mostra a saída
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            if result.returncode != 0:
                print(f"⚠️  Código de saída: {result.returncode}")
        
        except subprocess.TimeoutExpired:
            print("❌ Teste expirou (timeout)")
        except Exception as e:
            print(f"❌ Erro ao executar: {e}")
    
    print("\n" + "=" * 80)
    print(f"✅ Todos os {len(test_files)} testes foram executados!")

if __name__ == "__main__":
    run_tests()
