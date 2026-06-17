"""
Interpretador de código intermediário de 3 endereços.
Executa código gerado pelo parser recursivo descendente.
Formato: (op, result, arg1, arg2)
Operandos: var:nome, lit:valor, tempN, labelN, null
"""

from __future__ import annotations


class ErroExecucao(Exception):
    """Exceção disparada durante execução do código intermediário."""
    pass


class Interpretador:
    """Executa código intermediário de 3 endereços."""

    def __init__(self, codigo_fonte: list):
        """
        Inicializa o interpretador.
        
        Args:
            codigo_fonte: Lista de tuplas (op, result, arg1, arg2)
        """
        self.codigo_fonte = codigo_fonte
        self.labels = {}  # Mapeamento label -> índice
        self.variaveis = {}  # Dicionário de valores de variáveis
        self.saida = []  # Buffer de saída (prints)
        self.erros = []  # Buffer de erros
        self.pc = 0  # Program counter (instruction pointer)

    def mapear_labels(self) -> None:
        """Cria mapeamento de labels para índices de instruções."""
        for idx, instrucao in enumerate(self.codigo_fonte):
            if instrucao[0] == "label":
                label_nome = instrucao[1]
                self.labels[label_nome] = idx

    def iniciar_dicionario(self) -> None:
        """
        Inicializa dicionário de variáveis.
        Varre o código procurando destinos de escrita e inicializa com 0.
        """
        for instrucao in self.codigo_fonte:
            op, result, arg1, _ = instrucao

            if op == "att":
                var_nome = self._extrair_nome_var(result)
                if var_nome:
                    self.variaveis[var_nome] = 0

            if op == "call" and result == "read":
                var_nome = self._extrair_nome_var(arg1)
                if var_nome:
                    self.variaveis[var_nome] = 0

    def executar(self) -> bool:
        """
        Executa o código intermediário.
        
        Returns:
            True se execução bem-sucedida, False se houver erro.
        """
        try:
            self.mapear_labels()
            self.iniciar_dicionario()
            self.pc = 0

            while self.pc < len(self.codigo_fonte):
                instrucao = self.codigo_fonte[self.pc]
                self._executar_instrucao(instrucao)
                self.pc += 1

            return True
        except ErroExecucao as e:
            self.erros.append(str(e))
            return False

    def _extrair_nome_var(self, operando: str) -> str:
        """
        Extrai nome de variável de um operando.
        
        Args:
            operando: String no formato "var:nome" ou "null"
            
        Returns:
            Nome da variável ou None se não for uma variável.
        """
        if operando is None or operando == "null":
            return None
        if isinstance(operando, str) and operando.startswith("var:"):
            return operando[4:]  # Remove "var:" prefix
        return None

    def _extrair_valor_literal(self, operando: str):
        """
        Extrai valor literal de um operando.
        
        Args:
            operando: String no formato "lit:valor"
            
        Returns:
            Valor literal (int, float ou string)
        """
        if not isinstance(operando, str) or not operando.startswith("lit:"):
            return None

        valor_str = operando[4:]  # Remove "lit:" prefix

        if valor_str == "eh":
            return 1

        if valor_str == "num_eh":
            return 0

        # Se for string ou char com aspas, remove apenas os delimitadores.
        if (valor_str.startswith('"') and valor_str.endswith('"')) or \
           (valor_str.startswith("'") and valor_str.endswith("'")):
            return valor_str[1:-1]

        # Hexadecimal
        if valor_str.lower().startswith("-0x"):
            return -int(valor_str[3:], 16)

        if valor_str.lower().startswith("0x"):
            return int(valor_str, 16)

        # Octal
        if len(valor_str) > 1 and valor_str.startswith("-0") and valor_str[2:].isdigit():
            if all(char in "01234567" for char in valor_str[2:]):
                return -int(valor_str[2:], 8)

        if len(valor_str) > 1 and valor_str.startswith("0") and valor_str.isdigit():
            if all(char in "01234567" for char in valor_str[1:]):
                return int(valor_str, 8)

        # Inteiro decimal
        if valor_str.isdigit() or (valor_str.startswith('-') and valor_str[1:].isdigit()):
            return int(valor_str)

        # Float decimal
        if "." in valor_str:
            try:
                return float(valor_str)
            except ValueError:
                pass

        # Retorna como string se não conseguir converter
        return valor_str

    def _avaliar_operando(self, operando: str):
        """
        Avalia um operando e retorna seu valor.
        
        Args:
            operando: Pode ser "var:nome", "lit:valor", "tempN", "labelN", ou "null"
            
        Returns:
            Valor do operando
            
        Raises:
            ErroExecucao: Se variável não existe ou operando inválido
        """
        if operando is None or operando == "null":
            return 0

        if isinstance(operando, str):
            # Operando é literal
            if operando.startswith("lit:"):
                return self._extrair_valor_literal(operando)

            # Operando é variável
            if operando.startswith("var:"):
                var_nome = self._extrair_nome_var(operando)
                if var_nome not in self.variaveis:
                    raise ErroExecucao(f"Variável não declarada: '{var_nome}'")
                return self.variaveis[var_nome]

            # Operando é temporário (resultado de expressão anterior)
            if operando.startswith("temp") and operando[4:].isdigit():
                if operando not in self.variaveis:
                    raise ErroExecucao(f"Temporário não inicializado: '{operando}'")
                return self.variaveis[operando]

            # Label: retorna o próprio nome (não deveria ser avaliado)
            if operando.startswith("label"):
                raise ErroExecucao(f"Label não pode ser usado como operando: '{operando}'")

        raise ErroExecucao(f"Operando inválido: '{operando}'")

    def _executar_instrucao(self, instrucao: tuple) -> None:
        """
        Executa uma instrução de código intermediário.
        
        Args:
            instrucao: Tupla (op, result, arg1, arg2)
            
        Raises:
            ErroExecucao: Se houver erro na execução
        """
        op, result, arg1, arg2 = instrucao

        # Instrução de label: não faz nada (apenas marca posição)
        if op == "label":
            return

        # Instrução de atribuição
        if op == "att":
            var_nome = self._extrair_nome_var(result)
            if not var_nome:
                raise ErroExecucao(f"Atribuição a destino inválido: '{result}'")
            
            valor = self._avaliar_operando(arg1)
            if var_nome not in self.variaveis:
                self.variaveis[var_nome] = 0
            self.variaveis[var_nome] = valor
            return

        # Salto incondicional
        if op == "jump":
            label = result  # resultado contém o label
            if label not in self.labels:
                raise ErroExecucao(f"Label não encontrada: '{label}'")
            self.pc = self.labels[label] - 1  # -1 porque pc será incrementado após
            return

        # Salto condicional
        if op == "if":
            condicao = self._avaliar_operando(result)  # condição em result
            label_true = arg1  # label true em arg1
            label_false = arg2  # label false em arg2

            destino = label_true if condicao != 0 else label_false
            if destino not in self.labels:
                raise ErroExecucao(f"Label não encontrada: '{destino}'")
            self.pc = self.labels[destino] - 1
            return

        # Chamadas de função (print, read)
        if op == "call":
            func_name = result  # result contém o nome da função
            operando = arg1  # arg1 contém o operando
            
            if func_name == "print":
                if operando is None or operando == "null":
                    self.saida.append('')
                else:
                    valor = self._avaliar_operando(operando)
                    self.saida.append(str(valor))
                return

            if func_name == "read":
                var_nome = self._extrair_nome_var(operando)
                if not var_nome:
                    raise ErroExecucao(f"Read para destino inválido: '{operando}'")

                try:
                    entrada = input()
                except EOFError:
                    entrada = ""
                except Exception as e:
                    raise ErroExecucao(f"Erro lendo entrada: {e}")

                entrada = entrada.strip()

                # Converte entrada para número se possível
                valor = entrada
                if entrada == "":
                    valor = 0
                elif entrada.isdigit() or (entrada.startswith('-') and entrada[1:].isdigit()):
                    try:
                        valor = int(entrada)
                    except ValueError:
                        valor = entrada
                else:
                    try:
                        valor = float(entrada)
                    except ValueError:
                        valor = entrada

                self.variaveis[var_nome] = valor
                return

            raise ErroExecucao(f"Chamada não suportada: '{func_name}'")

        # Operações binárias e unárias
        operacoes = {
            "add", "sub", "mult", "div", "divI", "mod",
            "eq", "dif", "les", "leq", "grt", "geq",
            "and", "or", "xor", "not"
        }

        if op in operacoes:
            var_nome = self._extrair_nome_var(result) or result
            resultado = self._avaliar_operacao(op, arg1, arg2)
            
            if var_nome not in self.variaveis:
                self.variaveis[var_nome] = 0
            self.variaveis[var_nome] = resultado
            return

        raise ErroExecucao(f"Instrução desconhecida: '{op}'")

    def _avaliar_operacao(self, op: str, arg1: str, arg2: str = None):
        """
        Avalia uma operação aritmética ou lógica.
        
        Args:
            op: Operador (add, sub, mult, etc)
            arg1: Primeiro operando
            arg2: Segundo operando (None para operadores unários)
            
        Returns:
            Resultado da operação
            
        Raises:
            ErroExecucao: Se houver erro na avaliação
        """
        try:
            # Operador unário NOT
            if op == "not":
                valor = self._avaliar_operando(arg1)
                return 0 if valor != 0 else 1

            # Operadores binários
            esq = self._avaliar_operando(arg1)
            dir = self._avaliar_operando(arg2)

            if op == "add":
                # Concatenação de strings ou adição numérica
                if isinstance(esq, str) and isinstance(dir, str):
                    return esq + dir
                return esq + dir

            if op == "sub":
                return esq - dir

            if op == "mult":
                return esq * dir

            if op in {"div", "divI", "mod"}:
                if dir == 0:
                    raise ErroExecucao("Divisão por zero")
                if op == "div":
                    return esq / dir
                if op == "divI":
                    return esq // dir
                if op == "mod":
                    return esq % dir

            # Operadores relacionais
            if op == "eq":
                return 1 if esq == dir else 0

            if op == "dif":
                return 1 if esq != dir else 0

            if op == "les":
                return 1 if esq < dir else 0

            if op == "leq":
                return 1 if esq <= dir else 0

            if op == "grt":
                return 1 if esq > dir else 0

            if op == "geq":
                return 1 if esq >= dir else 0

            # Operadores lógicos
            if op == "and":
                return 1 if (esq != 0 and dir != 0) else 0

            if op == "or":
                return 1 if (esq != 0 or dir != 0) else 0

            if op == "xor":
                return 1 if ((esq != 0) ^ (dir != 0)) else 0

            raise ErroExecucao(f"Operação inválida: '{op}'")
        except ErroExecucao:
            raise
        except Exception as exc:
            raise ErroExecucao(f"Erro na operação '{op}': {exc}") from exc

    def get_saida(self) -> str:
        """Retorna saída do programa como string."""
        return "\n".join(self.saida)

    def get_erros(self) -> str:
        """Retorna erros como string ou None se sem erros."""
        return "\n".join(self.erros) if self.erros else None

    def printar_info(self) -> None:
        """Imprime informações de debug sobre a execução."""
        print("\n== INTERPRETADOR ==")
        print("Código intermediário:")
        for i, instr in enumerate(self.codigo_fonte):
            print(f"  {i:3d}: {instr}")

        print("\nMapeamento de labels:")
        for label, idx in sorted(self.labels.items()):
            print(f"  {label} -> {idx}")

        print("\nVariáveis:")
        for var, valor in sorted(self.variaveis.items()):
            print(f"  {var} = {valor}")

        if self.saida:
            print("\nSaída do programa:")
            print(self.get_saida())

        if self.erros:
            print("\nErros durante execução:")
            for erro in self.erros:
                print(f"  ! {erro}")
