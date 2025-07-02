from typing import Dict, Any, List
from ast_nodes import *

class RuntimeError(Exception):
    def __init__(self, mensagem: str, linha: int, coluna: int):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"Erro de execução na linha {linha}, coluna {coluna}: {mensagem}")

class Ambiente:
    """Ambiente de execução para armazenar valores de variáveis"""
    
    def __init__(self):
        self.variaveis: Dict[str, Any] = {}
    
    def definir(self, nome: str, valor: Any):
        self.variaveis[nome] = valor
    
    def obter(self, nome: str, linha: int, coluna: int) -> Any:
        if nome not in self.variaveis:
            raise RuntimeError(f"Variável '{nome}' não definida", linha, coluna)
        return self.variaveis[nome]
    
    def atribuir(self, nome: str, valor: Any, linha: int, coluna: int):
        if nome not in self.variaveis:
            raise RuntimeError(f"Variável '{nome}' não declarada", linha, coluna)
        self.variaveis[nome] = valor

class Interpretador(VisitorAST):
    """Interpretador que executa a árvore sintática"""
    
    def __init__(self):
        self.ambiente = Ambiente()
        
    def interpretar(self, programa: Programa):
        """Executa o programa"""
        try:
            programa.aceitar(self)
            return True
        except RuntimeError as e:
            print(f"Erro de execução: {e}")
            return False
        except KeyboardInterrupt:
            print("\nExecução interrompida pelo usuário")
            return False
    
    def visitar_programa(self, no: Programa):
        # Declarar variáveis com valores padrão
        if no.declaracoes:
            for declaracao in no.declaracoes:
                declaracao.aceitar(self)
        
        # Executar comandos
        for comando in no.comandos:
            comando.aceitar(self)
    
    def visitar_declaracao(self, no: Declaracao):
        # Inicializar variáveis com valores padrão
        valor_padrao = 0  # Apenas inteiro na versão simplificada
        
        for variavel in no.variaveis:
            self.ambiente.definir(variavel, valor_padrao)
    
    def visitar_atribuicao(self, no: Atribuicao):
        valor = no.expressao.aceitar(self)
        self.ambiente.atribuir(no.variavel, valor, no.linha, no.coluna)
    
    def visitar_leitura(self, no: Leitura):
        for variavel in no.variaveis:
            try:
                entrada = input(f"Digite o valor para {variavel}: ")
                try:
                    valor = int(entrada)
                except ValueError:
                    print(f"Valor inválido. Atribuindo 0 para {variavel}")
                    valor = 0
                
                self.ambiente.atribuir(variavel, valor, no.linha, no.coluna)
                
            except EOFError:
                print(f"\nEntrada terminada. Atribuindo 0 para {variavel}")
                self.ambiente.atribuir(variavel, 0, no.linha, no.coluna)
    
    def visitar_escrita(self, no: Escrita):
        valores = []
        
        for expressao in no.expressoes:
            valor = expressao.aceitar(self)
            valores.append(str(valor))
        
        output = "".join(valores)
        print(output)
    
    def visitar_bloco(self, no: Bloco):
        for comando in no.comandos:
            comando.aceitar(self)
    
    def visitar_se(self, no: Se):
        condicao = no.condicao.aceitar(self)
        
        # Converter condição para booleano (0 = falso, != 0 = verdadeiro)
        if isinstance(condicao, (int, float)):
            condicao_bool = condicao != 0
        else:
            condicao_bool = bool(condicao)
        
        if condicao_bool:
            no.comando_entao.aceitar(self)
        elif no.comando_senao:
            no.comando_senao.aceitar(self)
    
    def visitar_enquanto(self, no: Enquanto):
        iteracao = 0
        
        while True:
            iteracao += 1
            
            condicao = no.condicao.aceitar(self)
            
            # Converter condição para booleano
            if isinstance(condicao, (int, float)):
                condicao_bool = condicao != 0
            else:
                condicao_bool = bool(condicao)
            
            if not condicao_bool:
                break
            
            no.comando.aceitar(self)
            
            # Proteção contra loop infinito
            if iteracao > 1000:
                resposta = input(f"\nLoop executou {iteracao} vezes. Continuar? (s/n): ")
                if resposta.lower() != 's':
                    raise KeyboardInterrupt()
    
    def visitar_expressao_binaria(self, no: ExpressaoBinaria):
        esquerda = no.esquerda.aceitar(self)
        direita = no.direita.aceitar(self)
        
        try:
            if no.operador == '+':
                resultado = esquerda + direita
            elif no.operador == '-':
                resultado = esquerda - direita
            elif no.operador == '*':
                resultado = esquerda * direita
            elif no.operador == '/':
                if direita == 0:
                    raise RuntimeError("Divisão por zero", no.linha, no.coluna)
                resultado = esquerda // direita  # Divisão inteira
            elif no.operador == '=':
                resultado = 1 if esquerda == direita else 0
            elif no.operador == '<>':
                resultado = 1 if esquerda != direita else 0
            elif no.operador == '<':
                resultado = 1 if esquerda < direita else 0
            elif no.operador == '<=':
                resultado = 1 if esquerda <= direita else 0
            elif no.operador == '>':
                resultado = 1 if esquerda > direita else 0
            elif no.operador == '>=':
                resultado = 1 if esquerda >= direita else 0
            else:
                raise RuntimeError(f"Operador não suportado: {no.operador}", no.linha, no.coluna)
            
            return resultado
        
        except TypeError:
            raise RuntimeError(f"Tipos incompatíveis para operação {no.operador}", no.linha, no.coluna)
    
    def visitar_expressao_unaria(self, no: ExpressaoUnaria):
        expressao = no.expressao.aceitar(self)
        
        if no.operador == '-':
            try:
                return -expressao
            except TypeError:
                raise RuntimeError("Operador unário '-' requer operando numérico", no.linha, no.coluna)
        else:
            raise RuntimeError(f"Operador unário não suportado: {no.operador}", no.linha, no.coluna)
    
    def visitar_variavel(self, no: Variavel):
        return self.ambiente.obter(no.nome, no.linha, no.coluna)
    
    def visitar_numero(self, no: Numero):
        return no.valor
    
    def visitar_string(self, no: StringLiteral):
        return no.valor

def executar_programa(codigo: str) -> bool:
    """Função principal para executar um programa Fortall"""
    from parser import Parser
    from semantic import analisar_semantica
    
    try:
        # 1. Análise Léxica e Sintática
        parser = Parser(codigo)
        ast = parser.parse()
        
        if not ast:
            print("Erro na análise sintática")
            return False
        
        # 2. Análise Semântica
        erros_semanticos = analisar_semantica(ast)
        
        if erros_semanticos:
            print("Erros semânticos encontrados:")
            for erro in erros_semanticos:
                print(f"   {erro}")
            return False
        
        # 3. Execução
        interpretador = Interpretador()
        sucesso = interpretador.interpretar(ast)
        
        return sucesso
        
    except Exception as e:
        print(f"Erro: {e}")
        return False