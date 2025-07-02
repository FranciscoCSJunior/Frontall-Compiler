from typing import Dict, List, Any
from ast_nodes import *

class SemanticError(Exception):
    def __init__(self, mensagem: str, linha: int, coluna: int):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"Erro semântico na linha {linha}, coluna {coluna}: {mensagem}")

class TabelaSimbolos:
    def __init__(self):
        self.simbolos: Dict[str, str] = {}
    
    def declarar(self, nome: str, tipo: str, linha: int, coluna: int):
        if nome in self.simbolos:
            raise SemanticError(f"Variável '{nome}' já foi declarada", linha, coluna)
        self.simbolos[nome] = tipo
    
    def obter_tipo(self, nome: str, linha: int, coluna: int) -> str:
        if nome not in self.simbolos:
            raise SemanticError(f"Variável '{nome}' não foi declarada", linha, coluna)
        return self.simbolos[nome]
    
    def existe(self, nome: str) -> bool:
        return nome in self.simbolos

class AnalisadorSemantico(VisitorAST):
    def __init__(self):
        self.tabela_simbolos = TabelaSimbolos()
        self.erros: List[SemanticError] = []
    
    def erro(self, mensagem: str, no: NoAST):
        erro = SemanticError(mensagem, no.linha, no.coluna)
        self.erros.append(erro)
    
    def analisar(self, programa: Programa) -> List[SemanticError]:
        """Analisa semanticamente o programa e retorna lista de erros"""
        self.erros = []
        try:
            programa.aceitar(self)
        except Exception as e:
            print(f"Erro durante análise semântica: {e}")
        return self.erros
    
    def visitar_programa(self, no: Programa):
        for declaracao in no.declaracoes:
            declaracao.aceitar(self)
        
        for comando in no.comandos:
            comando.aceitar(self)
    
    def visitar_declaracao(self, no: Declaracao):
        for variavel in no.variaveis:
            try:
                self.tabela_simbolos.declarar(variavel, no.tipo, no.linha, no.coluna)
            except SemanticError as e:
                self.erros.append(e)
    
    def visitar_atribuicao(self, no: Atribuicao):
        try:
            tipo_var = self.tabela_simbolos.obter_tipo(no.variavel, no.linha, no.coluna)
        except SemanticError as e:
            self.erros.append(e)
            return
        
        no.expressao.aceitar(self)
        
        if hasattr(no.expressao, 'tipo') and no.expressao.tipo:
            if tipo_var != no.expressao.tipo:
                self.erro(f"Tipos incompatíveis: tentando atribuir {no.expressao.tipo} a {tipo_var}", no)
    
    def visitar_leitura(self, no: Leitura):
        for variavel in no.variaveis:
            try:
                self.tabela_simbolos.obter_tipo(variavel, no.linha, no.coluna)
            except SemanticError as e:
                self.erros.append(e)
    
    def visitar_escrita(self, no: Escrita):
        for expressao in no.expressoes:
            expressao.aceitar(self)
    
    def visitar_bloco(self, no: Bloco):
        for comando in no.comandos:
            comando.aceitar(self)
    
    def visitar_se(self, no: Se):
        no.condicao.aceitar(self)
        
        if hasattr(no.condicao, 'tipo') and no.condicao.tipo:
            if no.condicao.tipo not in ['inteiro']:
                self.erro(f"Condição deve ser do tipo inteiro, encontrado {no.condicao.tipo}", no)
        
        no.comando_entao.aceitar(self)
        if no.comando_senao:
            no.comando_senao.aceitar(self)
    
    def visitar_enquanto(self, no: Enquanto):
        no.condicao.aceitar(self)
        
        if hasattr(no.condicao, 'tipo') and no.condicao.tipo:
            if no.condicao.tipo not in ['inteiro']:
                self.erro(f"Condição deve ser do tipo inteiro, encontrado {no.condicao.tipo}", no)
        
        no.comando.aceitar(self)
    
    def visitar_expressao_binaria(self, no: ExpressaoBinaria):
        no.esquerda.aceitar(self)
        no.direita.aceitar(self)
        
        if hasattr(no.esquerda, 'tipo') and hasattr(no.direita, 'tipo'):
            tipo_esq = no.esquerda.tipo
            tipo_dir = no.direita.tipo
            
            if no.operador in ['+', '-', '*', '/']:
                if tipo_esq == 'inteiro' and tipo_dir == 'inteiro':
                    no.tipo = 'inteiro'
                else:
                    self.erro(f"Operadores aritméticos requerem operandos inteiros", no)
            
            elif no.operador in ['=', '<>', '<', '<=', '>', '>=']:
                if tipo_esq == tipo_dir:
                    no.tipo = 'inteiro'  # Resultado é inteiro (0 ou 1)
                else:
                    self.erro(f"Operadores relacionais requerem operandos do mesmo tipo", no)
    
    def visitar_expressao_unaria(self, no: ExpressaoUnaria):
        no.expressao.aceitar(self)
        
        if no.operador == '-':
            if hasattr(no.expressao, 'tipo') and no.expressao.tipo == 'inteiro':
                no.tipo = 'inteiro'
            else:
                self.erro("Operador unário '-' requer operando inteiro", no)
    
    def visitar_variavel(self, no: Variavel):
        try:
            tipo = self.tabela_simbolos.obter_tipo(no.nome, no.linha, no.coluna)
            no.tipo = tipo
        except SemanticError as e:
            self.erros.append(e)
    
    def visitar_numero(self, no: Numero):
        no.tipo = 'inteiro'
    
    def visitar_string(self, no: StringLiteral):
        no.tipo = 'string'

def analisar_semantica(programa: Programa) -> List[SemanticError]:
    """Função auxiliar para análise semântica"""
    analisador = AnalisadorSemantico()
    erros = analisador.analisar(programa)
    return erros