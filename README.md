# Compilador de Minerês

<div align="justify">
<p><strong>Disciplina:</strong> Compiladores<br>
<strong>Instituição:</strong> Centro Federal de Educação Tecnológica de Minas Gerais (CEFET-MG) - Campus V Divinópolis<br>
<strong>Professor:</strong> Eduardo Miranda<br>
</div>

## Sumário
- [Visão Geral do Projeto](#visao-geral-do-projeto)
- [Estrutura Geral do Projeto](#estrutura-geral-do-projeto)
- [Analisador Léxico](#analisador-lexico)
- [Analisador Sintático](#analisador-sintatico)
- [Análise Semântica e Código Intermediário](#analise-semantica-e-codigo-intermediario)
- [Interpretador](#interpretador)
- [Como Executar](#como-executar)
- [Referências](#referencias)

<a id="visao-geral-do-projeto"></a>

## 📌 Visão Geral do Projeto
Este repositório se trata de um projeto da disciplina de Compiladores, sendo a implementação de um compilador para a linguagem **Minerês** [[1]](#ref-1), dividido por fases.

No estado atual, o projeto contempla:
- **Análise léxica:** converte o código-fonte em uma sequência de tokens (tipo, lexema, linha e coluna).
- **Análise sintática:** valida se a sequência de tokens forma um programa válido conforme a gramática fixa da linguagem.
- **Análise semântica:** verifica declarações, escopos, inicialização de variáveis, compatibilidade de tipos e uso correto de comandos.
- **Código intermediário:** gera uma representação em quádruplas durante o parse, sem construção de AST.
- **Interpretador:** executa o código intermediário, com suporte a variáveis, expressões, saltos, entrada/saída e erros de execução.

<a id="estrutura-geral-do-projeto"></a>

## 🗂️ Estrutura Geral do Projeto
Visão geral do repositório e do que é compartilhado entre as fases:

```txt
.
├── src/
│   ├── main.py                      # CLI e orquestração das fases
│   ├── tokentype.py                 # TokenType + mapa de palavras da linguagem
│   ├── mineires_token.py            # Modelo de Token (lexema, tipo, linha, coluna)
│   ├── analisador_lexico/           # Implementação do analisador léxico
│   ├── analisador_sintatico/        # Parser, semântica e código intermediário
│   └── interpretador.py             # Execução do código intermediário
├── automatos/                       # Definição do AFD usado no léxico
├── entradas/                        # Casos válidos e exemplos de erros léxicos, sintáticos e semânticos
├── saida/                           # Artefatos gerados (TXT/JSON) quando aplicável
└── tests/                           # Testes unitários e scripts auxiliares
```

<a id="analisador-lexico"></a>

## Analisador Léxico

### 📌 Visão Geral
A primeira parte deste projeto implementa um analisador léxico para a linguagem Minerês.

O papel do analisador léxico é ler o código-fonte caractere por caractere, identificar lexemas válidos e transformá-los em tokens com tipo, linha e coluna. Esses tokens são a base para as próximas fases de compilação, como análise sintática e semântica.

No projeto, a análise lexical é feita com suporte de um AFD explícito carregado de arquivo (`automatos/automato.txt`), integrado ao lexer em Python.

### 🎯 Objetivos
- Implementar um lexer funcional para Minerês.
- Reconhecer palavras reservadas, identificadores, operadores, delimitadores e literais.
- Manter rastreamento de linha e coluna para depuração e mensagens de erro.
- Reportar erros léxicos com tipo explícito (ex.: string não fechada, número mal formado).
- Disponibilizar execução por CLI com entrada por arquivo, string e seleção interativa.
- Gerar saída em formato humano (tabela TXT) e estruturado (JSON).

### 🏗️ Estrutura da Fase
Principais arquivos desta fase:

- `src/analisador_lexico/automato.py`
  - Carrega e valida a definição do AFD.
  - Executa reconhecimento com estratégia maximal munch.

- `src/analisador_lexico/lexer.py`
  - Implementa o fluxo de tokenização.
  - Trata comentários, validações léxicas adicionais e erros tipados.

- `automatos/automato.txt`
  - Definição textual do AFD (estados e transições) carregada pelo lexer.

### 📥 Formato de Entrada
A entrada é um arquivo texto (`.txt`) contendo código Minerês.

Exemplo:
```txt
bora_cumpade main()
simbora
  trem_discrita mensagem;
  mensagem fica_assim_entao "Uai, mundo!\n" uai
  oia_proce_ve(mensagem) uai
cabo
```

### 📤 Saída
O programa gera dois formatos de saída léxica:

1. Tabela no terminal e em arquivo TXT (`saida/saida_tokens.txt`)
2. JSON estruturado (`saida/saida_tokens.json`)

#### Exemplo de tabela
```txt
LEXEMA                               | TIPO                   | LINHA | COLUNA
----------------------------------------------------------------------------
bora_cumpade                         | BORA_CUMPADE           | 1     | 1
main                                 | MAIN                   | 1     | 14
(                                    | LEFT_PAREN             | 1     | 18
)                                    | RIGHT_PAREN            | 1     | 19
mensagem                             | IDENTIFIER             | 3     | 18
;                                    | SEMICOLON              | 3     | 26
```

#### Exemplo de JSON
```json
[
  {
    "lexeme": "bora_cumpade",
    "type": "BORA_CUMPADE",
    "line": 1,
    "column": 1
  },
  {
    "lexeme": ";",
    "type": "SEMICOLON",
    "line": 3,
    "column": 26
  }
]
```

### 🔤 Tokens Reconhecidos
Categorias principais de tokens:

- Controle: `EOF`
- Identificadores: `IDENTIFIER`
- Literais: `INTEGER_LITERAL`, `FLOAT_LITERAL`, `HEX_LITERAL`, `OCTAL_LITERAL`, `STRING_LITERAL`, `CHAR_LITERAL`
- Palavras reservadas (exemplos): `bora_cumpade`, `simbora`, `cabo`, `uai_se`, `uai_senao`, `dependenu`, `du_casu`, `default`
- Tipos: `trem_di_numeru`, `trem_cum_virgula`, `trem_discrita`, `trem_discolhe`, `trosso`
- Operadores por palavra: `fica_assim_entao`, `mema_coisa`, `neh_nada`, `quarque_um`, `tamem`, `um_o_oto`, `vam_marca`
- Operadores por símbolo: `+`, `-`, `/`, `%`, `<`, `>`, `<=`, `>=`
- Delimitadores: `(`, `)`, `{`, `}`, `,`, `;`, `:`, `uai`
- Comentários: `COMMENT_LINE`, `COMMENT_BLOCK`

### 🤖 Funcionamento do Lexer
Fluxo geral da análise lexical:

1. Leitura da fonte
- O lexer recebe conteúdo por arquivo ou string.

2. Ignorar espaços em branco
- Espaços, tabs e quebras de linha são consumidos com atualização de linha/coluna.

3. Tratamento de comentários
- `// ...` até fim da linha (`COMMENT_LINE`)
- `causo ... fim_do_causo` (`COMMENT_BLOCK`)

4. Reconhecimento via AFD
- O lexer envia o trecho restante ao autômato.
- O autômato retorna o maior prefixo válido e o tipo candidato.

5. Classificação final
- Se o lexema estiver no mapa de palavras, ele vira token da linguagem.
- Caso contrário, usa o tipo retornado pelo autômato (literal, identificador etc.).
- Validações adicionais detectam casos como número mal formado.

### 🔁 Representação Canônica
O projeto adota uma representação canônica de tokens para facilitar etapas futuras do compilador.

Exemplo de equivalência de delimitador:
- `"uai"` e `";"` coexistem como representações léxicas distintas do mesmo papel sintático de delimitador.
- No nível de linguagem, ambos exercem papel de separador de instruções.

Essa representação canônica ajuda a simplificar o parser, pois reduz ambiguidades na etapa sintática.

### ⚠️ Tratamento de Erros
Por padrão, a CLI processa todo o arquivo e lista todos os erros léxicos encontrados.

Cada erro é reportado com tipo, lexema, linha e coluna.

Se existir ao menos um erro léxico:
- a tabela de tokens não é impressa
- os arquivos de saída de sucesso não são gerados
- a análise sintática/semântica não é executada
- a execução termina com código de retorno `1`

Tipos de erro tratados:
- `STRING_NAO_FECHADA`
- `CHAR_NAO_FECHADO`
- `CHAR_MAL_FORMADO`
- `COMENTARIO_NAO_FECHADO`
- `NUMERO_MAL_FORMADO`
- `SIMBOLO_DESCONHECIDO`
- `TOKEN_DESCONHECIDO`

Exemplo de mensagem:
```txt
Erros léxicos encontrados:
1. Erro léxico (NUMERO_MAL_FORMADO): '0x10G' na linha 2, coluna 1
2. Erro léxico (NUMERO_MAL_FORMADO): '12.3.4' na linha 3, coluna 1
```

<a id="analisador-sintatico"></a>

## Analisador Sintático

### 📌 Visão Geral
A segunda parte do projeto implementa um analisador sintático para a linguagem Minerês.

O papel do analisador sintático é receber a sequência de tokens do lexer e validar se ela forma um programa válido de acordo com a gramática fixa da linguagem. Nesta etapa, o objetivo é validar a estrutura (programa, blocos, comandos e expressões) e reportar erros de forma precisa.

No projeto, a análise sintática é feita por um parser descendente recursivo (recursive descent), baseado na gramática de referência em `src/analisador_sintatico/mineres.gmr`. A implementação não constrói AST: ela valida a entrada e, durante o processo, também aciona as rotinas semânticas e a geração de código intermediário.

### 🎯 Objetivos
- Implementar um parser recursivo para Minerês.
- Validar a estrutura do programa (main, bloco e lista de comandos).
- Validar comandos de controle (if/else, while, for, case) e IO.
- Validar expressões com precedência e associatividade definidas na gramática.
- Usar `fatorZinMenorAinda` no `case`, permitindo apenas literais nos rótulos.
- Ignorar comentários na análise sintática (não participam da gramática).
- Reportar erros sintáticos com token esperado/recebido e posição (linha/coluna).
- Integrar a execução ao fluxo da CLI.

### 🏗️ Estrutura da Fase
Principais arquivos desta fase:

- `src/analisador_sintatico/mineres.gmr`
  - Gramática fixa da linguagem usada como referência.
  - Define não-terminais como `<function*>`, `<bloco>`, `<stmt>`, `<expr>` e a precedência de operadores.
  - Define `default` como rótulo padrão do `case`.

- `src/analisador_sintatico/analisador_sintatico.py`
  - Implementa a classe `Parser` e as exceções `ParserError` e `SemanticError`.
  - Filtra tokens de comentário (`COMMENT_LINE` e `COMMENT_BLOCK`) antes do parse.
  - Implementa métodos por regra (ex.: `function()`, `bloco()`, `stmt()`, `expr()`).
  - Aceita `uai` e `;` como delimitadores equivalentes de comando.
  - Mantém a tabela de símbolos, a pilha de escopos e a lista de quádruplas.

### 📥 Formato de Entrada
A entrada do sintático é o mesmo código-fonte Minerês usado no léxico (arquivo `.txt` ou `-s` via CLI). O parser opera sobre os tokens produzidos pelo lexer.

Exemplo válido:
```txt
bora_cumpade main()
simbora
    trem_discrita mensagem;
    mensagem fica_assim_entao "Uai, mundo!\n" uai
    oia_proce_ve(mensagem) uai
cabo
```

Observação:
- O parser aceita `uai` ou `;` como delimitador de comando.

### 📤 Saída
O sintático não gera um arquivo próprio de "resultado sintático"; a validação é reportada no terminal pelo bloco "Resultado" da CLI.

#### Exemplo de sucesso (modo apenas sintático)
```txt
Resultado
---------
Status: sucesso
Fases executadas: sintatica
Total de tokens: 19
```

#### Exemplo de erro sintático (modo apenas sintático)
```txt
Resultado
---------
Status: erro
Fases executadas: sintatica
Detalhe: Erro sintático: esperado COLON, mas recebeu para_o_trem na linha 5, coluna 16
```

No fluxo padrão (léxico + sintático), em caso de sucesso, a CLI também lista os caminhos de saída TXT/JSON gerados pelo léxico.

### 🧩 Regras Sintáticas Suportadas
De forma resumida, o parser valida:

- Programa no formato: `bora_cumpade main() <bloco>`
- Blocos: `simbora ... cabo`
- Declarações: `<type> <identList> (uai ou ;)`
- Atribuições e expressões (com operadores aritméticos, relacionais e lógicos)
- Comandos:
  - `roda_esse_trem (...) <stmt>`
  - `enquanto_tiver_trem (<expr>) <stmt>`
  - `uai_se (<expr>) <stmt> [uai_senao <stmt>]`
  - `dependenu (IDENT) simbora ... cabo` com casos `du_casu <fatorZinMenorAinda> : <stmt>` e opcional `default : <stmt>`
  - IO: `xove(type, IDENT)` e `oia_proce_ve(...)`
  - Controle: `para_o_trem` e `toca_o_trem`
  - Comando vazio: `uai` ou `;`

### 🤖 Funcionamento do Parser
Fluxo geral da análise sintática:

1. Receber tokens do lexer
- O parser recebe a lista de tokens já com linha/coluna.

2. Remover comentários
- Tokens `COMMENT_LINE` e `COMMENT_BLOCK` são descartados antes da validação.

3. Aplicar regras recursivas
- A entrada é validada a partir de `<function*>`.
- Cada regra consome tokens esperados com `consume(...)`.
- Ao final, o parser exige consumo de `EOF`.

4. Delimitadores canônicos
- Para comandos, `consume_delimiter()` aceita tanto `uai` quanto `;`.

### ⚠️ Tratamento de Erros
O parser para no primeiro erro sintático encontrado e levanta `ParserError`.

Formato da mensagem:
```txt
Erro sintático: esperado <X>, mas recebeu <Y> na linha <L>, coluna <C>
```

- Se houver erro léxico, o sintático não é executado.
- O token/comando `ta_bao` não faz parte da gramática do parser no estado atual (main não retorna). Se ele aparecer no código, será reportado como erro sintático.

<a id="analise-semantica-e-codigo-intermediario"></a>

## Análise Semântica e Código Intermediário

### 📌 Visão Geral
A terceira parte do projeto adiciona análise semântica e geração de código intermediário ao parser atual, sem criar uma AST separada.

A análise semântica acontece de forma incremental durante o parse. Ao reconhecer declarações, atribuições, expressões, condições e comandos de controle, o parser valida as regras de tipo e escopo e, quando a construção é válida, gera quádruplas para execução posterior.

### 🎯 Objetivos
- Checar declaração prévia de variáveis.
- Checar redeclaração no mesmo escopo.
- Controlar escopos por bloco.
- Impedir uso de variável antes de receber valor.
- Validar compatibilidade de tipos em atribuições, expressões, condições, `case`, `xove` e `oia_proce_ve`.
- Tratar `trem_di_numeru` e `trem_cum_virgula` como família numérica para compatibilidade semântica.
- Rejeitar operações inválidas, como subtração de string.
- Converter literais octais e hexadecimais para decimal no código intermediário.
- Permitir que `trosso + trosso` resulte em `trem_discrita`.
- Garantir que o lado esquerdo de `fica_assim_entao` seja uma variável.
- Garantir que os rótulos de `case` sejam literais e compatíveis com o tipo da variável testada.
- Garantir que `para_o_trem` e `toca_o_trem` apareçam apenas dentro de laços.

### 🏗️ Estrutura da Fase
Principais elementos implementados em `src/analisador_sintatico/analisador_sintatico.py`:

- `SemanticError`
  - Exceção usada para erros semânticos.

- Tabela de símbolos e pilha de escopos
  - Guardam tipo declarado, escopo e estado de inicialização das variáveis.

- Rastreamento de temporários
  - Propaga tipos gerados por expressões intermediárias.

- Lista `codigo`
  - Armazena quádruplas no formato `(operação, resultado, argumento1, argumento2)`.

### 📤 Código Intermediário
O código intermediário é gerado em quádruplas.

Exemplo:
```txt
(att, x, 10, None)
(+, T1, x, 2)
(print, None, T1, None)
```

Operações principais:
- `att`: atribuição
- `read`: leitura
- `print`: escrita
- `jmp`: salto incondicional
- `jz`: salto condicional quando falso
- `label`: marcação de label
- `+`, `-`, `veiz`, `sob`, `/`, `mod`: operações aritméticas
- `mema_coisa`, `neh_nada`, `<`, `<=`, `>`, `>=`: operações relacionais
- `tamem`, `quarque_um`, `um_o_oto`, `vam_marca`: operações lógicas

### ⚠️ Tratamento de Erros Semânticos
O parser para no primeiro erro semântico encontrado e levanta `SemanticError`.

Exemplos de erros tratados:
- variável não declarada
- variável redeclarada no mesmo escopo
- variável usada antes de inicializar
- atribuição entre tipos incompatíveis
- condição não booleana em `if`, `while` ou `for`
- `case` com literal incompatível com a variável testada
- `case` usando variável como rótulo
- `xove` com tipo incompatível com a variável declarada
- `para_o_trem` ou `toca_o_trem` fora de laço

Os exemplos ficam em:
```txt
entradas/erros_semanticos/
```

<a id="interpretador"></a>

## Interpretador

### 📌 Visão Geral
A quarta parte do projeto implementa um interpretador para executar o código intermediário gerado pelo parser.

O interpretador percorre as quádruplas, mapeia labels, mantém um dicionário de variáveis e executa instruções linha a linha. Ele é acionado pela CLI com a opção `--executar`.

### 🎯 Objetivos
- Mapear labels antes da execução.
- Inicializar o dicionário de variáveis a partir das atribuições e leituras geradas.
- Executar o código intermediário linha a linha.
- Avaliar expressões aritméticas, relacionais e lógicas.
- Executar saltos condicionais e incondicionais.
- Interpretar `if`, `while`, `for`, `case`, `print`, `read`, `para_o_trem` e `toca_o_trem` por meio das quádruplas geradas.
- Reportar erros de execução de forma controlada.

### 🏗️ Estrutura da Fase
Principal arquivo desta fase:

- `src/interpretador.py`
  - Implementa a classe `Interpretador`.
  - Executa as quádruplas geradas pelo parser.
  - Mantém `variaveis`, `labels`, `pc`, `saida` e `erros`.

### ⚠️ Erros de Execução
Erros tratados pelo interpretador:
- variável não declarada
- temporário não inicializado
- divisão por zero
- operação inválida em tempo de execução
- salto para label inexistente

Quando ocorre erro, a execução retorna falha e a CLI imprime a mensagem em `stderr`.

<a id="como-executar"></a>

## ⚙️ Como Executar
Este tópico é geral (vale para o fluxo completo e para cada fase isolada).

### 1) Ativar o ambiente virtual
```bash
source .venv/bin/activate
```

### 2) Rodar em modo interativo (lista arquivos em entradas/)
```bash
python src/main.py --print
```
Padrão: executa análise léxica + sintática + semântica.

### 3) Rodar com arquivo de entrada
```bash
python src/main.py entradas/casos_validos/valido_basico.txt --print
```

### 4) Rodar com código em linha
```bash
python src/main.py -s "bora_cumpade main() simbora uai cabo" --sintatico
```

### 5) Rodar apenas a análise léxica
```bash
python src/main.py entradas/casos_validos/valido_basico.txt --print --lexico
```

### 6) Rodar apenas sintático/semântico
```bash
python src/main.py entradas/casos_validos/valido_basico.txt --sintatico
```
Observação:
- O argumento `--print` é usado para imprimir tokens (saída léxica). No modo `--sintatico`, a CLI imprime apenas o bloco "Resultado", a menos que `--print-codigo` também seja informado.

### 7) Imprimir código intermediário
```bash
python src/main.py entradas/testes_codigo_intermediario/01_atribuicao_simples.txt --sintatico --print-codigo
```

### 8) Executar código intermediário
```bash
python src/main.py entradas/testes_codigo_intermediario/07_print_variavel.txt --sintatico --print-codigo --executar
```

### 9) Rodar a suíte de testes
```bash
python -m unittest discover -s tests -v
```

Também existem scripts auxiliares:
```bash
python tests/run_all_tests.py -c erros_semanticos
python tests/run_all_tests.py -c codigo_intermediario
python tests/run_intermediary_tests.py
```

### Observação sobre o comando do enunciado
```bash
python main.py arquivo.txt
```
No estado atual do repositório, o ponto de entrada está em `src/main.py`.

<a id="referencias"></a>

## Referências
<a id="ref-1"></a>
1. Referência da linguagem Minerês: https://mineres-language.github.io
