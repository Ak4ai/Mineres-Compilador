# Compilador de Minerês

<div align="justify">
<p><strong>Disciplina:</strong> Compiladores<br>
<strong>Instituição:</strong> Centro Federal de Educação Tecnológica de Minas Gerais (CEFET-MG) - Campus V Divinópolis<br>
<strong>Professor:</strong> Eduardo Miranda<br>
</div>

## Analisador Léxico

### 📌 Visão Geral
A primeira parte deste projeto implementa um analisador léxico para a linguagem Mineres.

O papel do analisador léxico é ler o código-fonte caractere por caractere, identificar lexemas válidos e transformá-los em tokens com tipo, linha e coluna. Esses tokens são a base para as próximas fases de compilação, como análise sintática e semântica.

No projeto, a análise lexical é feita com suporte de um AFD explícito carregado de arquivo (automatos/automato.txt), integrado ao lexer em Python.

### 🎯 Objetivos
- Implementar um lexer funcional para Mineres.
- Reconhecer palavras reservadas, identificadores, operadores, delimitadores e literais.
- Manter rastreamento de linha e coluna para depuração e mensagens de erro.
- Reportar erros léxicos com tipo explícito (ex.: string não fechada, número mal formado).
- Disponibilizar execução por CLI com entrada por arquivo, string e seleção interativa.
- Gerar saída em formato humano (tabela TXT) e estruturado (JSON).

### 🏗️ Estrutura do Projeto
Principais arquivos e responsabilidades:

- src/analisador_lexico/automato.py
  - Carrega e valida a definição do AFD.
  - Executa reconhecimento com estratégia maximal munch.

- src/analisador_lexico/lexer.py
  - Implementa o fluxo de tokenização.
  - Trata comentários, validações léxicas adicionais e erros tipados.

- src/analisador_lexico/tokentype.py
  - Define TokenType e os mapas de palavras da linguagem.
  - Centraliza o catálogo de tokens reconhecidos.

- src/analisador_lexico/mineires_token.py
  - Modelo de token com campos de tipo, lexema e posição.

- src/analisador_lexico/main.py
  - CLI da aplicação.
  - Recebe entrada por arquivo, por string ou por seleção interativa.
  - Gera saída em TXT e JSON.

- automatos/automato.txt
  - Definição textual do automato (estados e transições).

- entradas/
  - Arquivos de entrada de exemplo.

- saida/
  - Arquivos gerados na execução (saida_tokens.txt e saida_tokens.json).

### ⚙️ Como Executar
#### 1) Ativar o ambiente virtual
```bash
source .venv/bin/activate
```

#### 2) Rodar em modo interativo (lista arquivos em entradas)
```bash
python src/analisador_lexico/main.py --print
```

#### 3) Rodar com arquivo de entrada
```bash
python src/analisador_lexico/main.py entradas/01_valido_basico.mineires.txt --print
```

#### 4) Rodar com código em linha
```bash
python src/analisador_lexico/main.py -s "simbora" --print
```

Observação sobre o comando do enunciado:
```bash
python main.py arquivo.txt
```
No estado atual do repositório, o ponto de entrada está em src/analisador_lexico/main.py.

### 📥 Formato de Entrada
A entrada é um arquivo texto (.txt) contendo código Mineres.

Exemplo:
```txt
bora_cumpade main()
simbora
    trem_discrita mensagem ;
    fica_assim_entao "Uai, mundo!\\n" uai
    oia_proce_ve(mensagem) uai
    ta_bao 0 uai
cabo
```

### 📤 Saída
O programa gera dois formatos de saída:

1. Tabela no terminal e em arquivo TXT (saida/saida_tokens.txt)
2. JSON estruturado (saida/saida_tokens.json)

#### Exemplo de tabela
```txt
LEXEMA               TIPO                 LINHA COLUNA
------------------------------------------------------------
bora_cumpade         BORA_CUMPADE         1     1
main                 MAIN                 1     14
(                    LEFT_PAREN           1     18
)                    RIGHT_PAREN          1     19
mensagem             IDENTIFIER           3     19
;                    SEMICOLON            3     27
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
    "column": 27
  }
]
```

### 🔤 Tokens Reconhecidos
Categorias principais de tokens:

- Controle: EOF
- Identificadores: IDENTIFIER
- Literais:
  - INTEGER_LITERAL
  - FLOAT_LITERAL
  - HEX_LITERAL
  - OCTAL_LITERAL
  - STRING_LITERAL
  - CHAR_LITERAL
- Palavras reservadas (exemplos):
  - bora_cumpade, simbora, cabo
  - uai_se, uai_senao
  - dependenu, du_casu
- Tipos (exemplos):
  - trem_di_numeru
  - trem_cum_virgula
  - trem_discrita
  - trem_discolhe
  - trosso
- Operadores por palavra (exemplos):
  - fica_assim_entao
  - mema_coisa
  - neh_nada
- Operadores por símbolo:
  - +, -, /, %, <, >, <=, >=
- Delimitadores:
  - (, ), {, }, ,, ;
  - uai (delimitador por palavra)
- Comentários:
  - COMMENT_LINE
  - COMMENT_BLOCK

### 🤖 Funcionamento do Lexer
Fluxo geral da análise lexical:

1. Leitura da fonte
- O lexer recebe conteudo por arquivo ou string.

2. Ignorar espaços em branco
- Espaços, tabs e quebras de linha são consumidos com atualização de linha/coluna.

3. Tratamento de comentários
- // ... ate fim da linha (COMMENT_LINE)
- causo ... fim_do_causo (COMMENT_BLOCK)

4. Reconhecimento via AFD
- O lexer envia o trecho restante ao automato.
- O automato retorna o maior prefixo válido e o tipo candidato.

5. Classificação final
- Se o lexema estiver no mapa de palavras, ele vira token da linguagem.
- Caso contrário, usa o tipo retornado pelo automato (literal, identificador etc.).
- Validações adicionais detectam casos como numero mal formado.

### 🔁 Representação Canônica
O projeto adota uma representação canônica de tokens para facilitar etapas futuras do compilador.

Exemplo de equivalência de delimitador:
- - "uai" e ";" coexistem como representações léxicas distintas do mesmo papel sintático de delimitador.
- No nível de linguagem, ambos exercem papel de separador de instruções.

Essa representação canônica ajuda a simplificar o parser, pois reduz ambiguidades na etapa sintática.

### ⚠️ Tratamento de Erros
Por padrao, a CLI processa todo o arquivo e lista todos os erros léxicos encontrados.

Cada erro e reportado com tipo, lexema, linha e coluna.

Se existir ao menos um erro léxico:
- a tabela de tokens nao é impressa
- os arquivos de saida de sucesso não são gerados
- a execução termina com codigo de retorno 1

Tipos de erro tratados:
- STRING_NAO_FECHADA
- CHAR_NAO_FECHADO
- CHAR_MAL_FORMADO
- COMENTARIO_NAO_FECHADO
- NUMERO_MAL_FORMADO
- SIMBOLO_DESCONHECIDO
- TOKEN_DESCONHECIDO

Exemplo de mensagem:
```txt
Erros léxicos encontrados:
1. Erro léxico (NUMERO_MAL_FORMADO): '0x10G' na linha 2, coluna 1
2. Erro léxico (NUMERO_MAL_FORMADO): '12.3.4' na linha 3, coluna 1
```

### 🧪 Exemplo Completo
#### Entrada
```txt
bora_cumpade main()
simbora
    trem_discrita mensagem ;
    fica_assim_entao "Uai, mundo!\\n" uai
    oia_proce_ve(mensagem) uai
    ta_bao 0 uai
cabo
```

#### Saida (trecho)
```txt
LEXEMA               TIPO                 LINHA COLUNA
------------------------------------------------------------
bora_cumpade         BORA_CUMPADE         1     1
main                 MAIN                 1     14
mensagem             IDENTIFIER           3     19
"Uai, mundo!\\n"     STRING_LITERAL       4     22
0                    INTEGER_LITERAL      6     12
cabo                 CABO                 7     1
```
