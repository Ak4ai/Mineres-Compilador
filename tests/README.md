# 🧪 Testes do Compilador Mineres

Script elegante para executar testes do compilador Mineres de forma organizada e com relatório detalhado.

## 📋 Categorias de Testes

O script executa **5 categorias** de testes:

| Categoria | Descrição | Localização |
|-----------|-----------|-------------|
| **Testes Válidos** | Código correto que deve compilar sem erros | `entradas/casos_validos/` |
| **Erros Léxicos** | Código com erros de tokenização | `entradas/erros_lexicos/` |
| **Erros Sintáticos** | Código com erros de parsing | `entradas/erros_sintaticos/` |
| **Código Intermediário** | Testes para validar geração de código intermediário | `entradas/testes_codigo_intermediario/` |
| **Exemplos do Projeto Base** | Exemplos do projeto base original | `entradas/exemplos_base/` |

## 🚀 Como Usar

### Executar todos os testes
```bash
python tests/run_all_tests.py
```

### Modo verboso (com detalhes de erros)
```bash
python tests/run_all_tests.py -v
```
ou
```bash
python tests/run_all_tests.py --verboso
```

### Executar apenas uma categoria
```bash
python tests/run_all_tests.py -c testes_validos
```

Categorias disponíveis:
- `validos`
- `erros_lexicos`
- `erros_sintaticos`
- `codigo_intermediario`
- `exemplos_base`

### Exemplos de uso
```bash
# Apenas testes válidos
python tests/run_all_tests.py -c validos

# Apenas erros léxicos em modo verboso
python tests/run_all_tests.py -c erros_lexicos -v

# Todos os testes com saída detalhada
python tests/run_all_tests.py -v
```

## 📊 Saída

O script gera um relatório formatado com:

- ✅ Testes que passaram (código 0 para válidos, código 1 para erros)
- ❌ Testes que falharam
- 📈 Estatísticas por categoria
- 🎯 Taxa de sucesso geral

### Exemplo de saída
```
================================================================================
📊 RESUMO DOS TESTES
================================================================================
✅ Testes Válidos.......................... 12/12 (100.0%)
✅ Erros Léxicos...........................  5/ 5 (100.0%)
✅ Erros Sintáticos........................ 18/18 (100.0%)
⚠️  Código Intermediário.................... 19/20 ( 95.0%)
⚠️  Exemplos do Projeto Base................  6/11 ( 54.5%)
================================================================================
⚠️  TOTAL:................................... 60/66 ( 90.9%)
================================================================================
```

## 🔍 Interpretando os Resultados

- **✅ OK**: Teste passou (código de retorno esperado)
- **❌ Falha**: Teste não retornou o código esperado
  - Testes válidos esperam código 0
  - Testes de erro esperam código 1
- **⏱️ Timeout**: Teste demorou mais de 5 segundos

## 📁 Estrutura

```
tests/
├── run_all_tests.py          # Script principal (este arquivo)
├── run_intermediary_tests.py # Script legado (mantido para compatibilidade)
└── ...

entradas/
├── casos_validos/            # Testes com código correto
├── erros_lexicos/            # Testes com erros léxicos
├── erros_sintaticos/         # Testes com erros sintáticos
├── testes_codigo_intermediario/  # Testes de código intermediário
└── exemplos_base/            # Exemplos do projeto base
```

## 🛠️ Funcionamento Interno

- Cada teste é executado com: `python src/main.py --print-codigo <arquivo>`
- O timeout é de 5 segundos por teste
- Testes de erro (lexical/syntax) são considerados bem-sucedidos quando retornam código 1
- Testes válidos são considerados bem-sucedidos quando retornam código 0
- Arquivos de saída (`saida.txt`, `saida_tokens.txt`) são automaticamente excluídos

## 📝 Adicionar Novos Testes

Para adicionar novos testes:

1. Coloque o arquivo `.txt` na categoria apropriada:
   - Código correto → `entradas/casos_validos/`
   - Erro léxico → `entradas/erros_lexicos/`
   - Erro sintático → `entradas/erros_sintaticos/`
   - Teste intermediário → `entradas/testes_codigo_intermediario/`

2. Execute o script novamente - os novos testes serão automaticamente incluídos!

## 🎯 Objetivo

Este script oferece uma forma **elegante e organizada** de:
- ✨ Validar o compilador continuamente
- 📊 Acompanhar o progresso
- 🔍 Identificar regressões rapidamente
- 📈 Gerar relatórios claros e informativos
