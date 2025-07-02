from typing import List, Optional
from lexer import Lexer, Token, TokenType, LexerError
from ast_nodes import *

class ParserError(Exception):
    def __init__(self, mensagem: str, token: Token):
        self.mensagem = mensagem
        self.token = token
        super().__init__(f"Erro sintático na linha {token.linha}, coluna {token.coluna}: {mensagem}")

class Parser:
    def __init__(self, codigo: str):
        self.lexer = Lexer(codigo)
        try:
            self.tokens = self.lexer.tokenizar()
        except LexerError as e:
            raise ParserError(f"Erro léxico: {e.mensagem}", 
                            Token(TokenType.EOF, "", e.linha, e.coluna))
        
        self.posicao = 0
        self.token_atual = self.tokens[0] if self.tokens else None
    
    def erro(self, mensagem: str):
        raise ParserError(mensagem, self.token_atual)
    
    def avancar(self):
        if self.posicao < len(self.tokens) - 1:
            self.posicao += 1
            self.token_atual = self.tokens[self.posicao]
    
    def verificar(self, *tipos: TokenType) -> bool:
        return self.token_atual.tipo in tipos
    
    def consumir(self, tipo: TokenType, mensagem: str = None) -> Token:
        if self.token_atual.tipo == tipo:
            token = self.token_atual
            self.avancar()
            return token
        else:
            if mensagem is None:
                mensagem = f"Esperado {tipo.value}, encontrado {self.token_atual.valor}"
            self.erro(mensagem)
    
    def parse(self) -> Programa:
        """Ponto de entrada do parser"""
        try:
            return self.programa()
        except ParserError:
            raise
    
    def programa(self) -> Programa:
        """programa ::= 'programa' IDENTIFICADOR ';' [declarações] 'inicio' lista_comandos 'fim' '.'"""
        linha = self.token_atual.linha
        coluna = self.token_atual.coluna
        
        self.consumir(TokenType.PROGRAMA, "Esperado 'programa'")
        nome_token = self.consumir(TokenType.IDENTIFICADOR, "Esperado nome do programa")
        self.consumir(TokenType.PONTO_VIRGULA, "Esperado ';' após nome do programa")
        
        declaracoes = []
        if self.verificar(TokenType.VAR):
            declaracoes = self.declaracoes()
        
        self.consumir(TokenType.INICIO, "Esperado 'inicio'")
        comandos = self.lista_comandos()
        self.consumir(TokenType.FIM, "Esperado 'fim'")
        self.consumir(TokenType.PONTO, "Esperado '.' no final do programa")
        
        return Programa(nome_token.valor, declaracoes, comandos, linha, coluna)
    
    def declaracoes(self) -> List[Declaracao]:
        """declarações ::= 'var' lista_declaracao { lista_declaracao }"""
        declaracoes = []
        self.consumir(TokenType.VAR, "Esperado 'var'")
        
        declaracoes.append(self.declaracao())
        
        while self.verificar(TokenType.IDENTIFICADOR):
            declaracoes.append(self.declaracao())
        
        return declaracoes
    
    def declaracao(self) -> Declaracao:
        """declaração ::= IDENTIFICADOR { ',' IDENTIFICADOR } ':' tipo ';'"""
        linha = self.token_atual.linha
        coluna = self.token_atual.coluna
        
        variaveis = []
        variaveis.append(self.consumir(TokenType.IDENTIFICADOR, "Esperado nome da variável").valor)
        
        while self.verificar(TokenType.VIRGULA):
            self.avancar()
            variaveis.append(self.consumir(TokenType.IDENTIFICADOR, "Esperado nome da variável").valor)
        
        self.consumir(TokenType.DOIS_PONTOS, "Esperado ':' após lista de variáveis")
        tipo = self.tipo()
        self.consumir(TokenType.PONTO_VIRGULA, "Esperado ';' após declaração")
        
        return Declaracao(variaveis, tipo, linha, coluna)
    
    def tipo(self) -> str:
        """tipo ::= 'inteiro'"""
        if self.verificar(TokenType.INTEIRO):
            token = self.token_atual
            self.avancar()
            return token.valor
        else:
            self.erro("Esperado tipo 'inteiro'")
    
    def lista_comandos(self) -> List[Comando]:
        """lista_comandos ::= comando { ';' comando }"""
        comandos = []
        comandos.append(self.comando())
        
        while self.verificar(TokenType.PONTO_VIRGULA):
            self.avancar()
            if not self.verificar(TokenType.FIM):
                comandos.append(self.comando())
        
        return comandos
    
    def comando(self) -> Comando:
        """comando ::= atribuição | leitura | escrita | bloco | condicional | repetição"""
        if self.verificar(TokenType.IDENTIFICADOR):
            return self.atribuicao()
        elif self.verificar(TokenType.LER):
            return self.leitura()
        elif self.verificar(TokenType.ESCREVER):
            return self.escrita()
        elif self.verificar(TokenType.INICIO):
            return self.bloco()
        elif self.verificar(TokenType.SE):
            return self.condicional()
        elif self.verificar(TokenType.ENQUANTO):
            return self.repeticao()
        else:
            self.erro("Comando inválido")
    
    def atribuicao(self) -> Atribuicao:
        """atribuição ::= IDENTIFICADOR ':=' expressão"""
        linha = self.token_atual.linha
        coluna = self.token_atual.coluna
        
        variavel = self.consumir(TokenType.IDENTIFICADOR, "Esperado nome da variável").valor
        self.consumir(TokenType.ATRIBUICAO, "Esperado ':=' na atribuição")
        expressao = self.expressao()
        
        return Atribuicao(variavel, expressao, linha, coluna)
    
    def leitura(self) -> Leitura:
        """leitura ::= 'ler' '(' IDENTIFICADOR { ',' IDENTIFICADOR } ')'"""
        linha = self.token_atual.linha
        coluna = self.token_atual.coluna
        
        self.consumir(TokenType.LER, "Esperado 'ler'")
        self.consumir(TokenType.PARENTESE_ESQ, "Esperado '(' após 'ler'")
        
        variaveis = []
        variaveis.append(self.consumir(TokenType.IDENTIFICADOR, "Esperado nome da variável").valor)
        
        while self.verificar(TokenType.VIRGULA):
            self.avancar()
            variaveis.append(self.consumir(TokenType.IDENTIFICADOR, "Esperado nome da variável").valor)
        
        self.consumir(TokenType.PARENTESE_DIR, "Esperado ')' após lista de variáveis")
        
        return Leitura(variaveis, linha, coluna)
    
    def escrita(self) -> Escrita:
        """escrita ::= 'escrever' '(' expressão { ',' expressão } ')'"""
        linha = self.token_atual.linha
        coluna = self.token_atual.coluna
        
        self.consumir(TokenType.ESCREVER, "Esperado 'escrever'")
        self.consumir(TokenType.PARENTESE_ESQ, "Esperado '(' após 'escrever'")
        
        expressoes = []
        expressoes.append(self.expressao())
        
        while self.verificar(TokenType.VIRGULA):
            self.avancar()
            expressoes.append(self.expressao())
        
        self.consumir(TokenType.PARENTESE_DIR, "Esperado ')' após lista de expressões")
        
        return Escrita(expressoes, linha, coluna)
    
    def bloco(self) -> Bloco:
        """bloco ::= 'inicio' lista_comandos 'fim'"""
        linha = self.token_atual.linha
        coluna = self.token_atual.coluna
        
        self.consumir(TokenType.INICIO, "Esperado 'inicio'")
        comandos = self.lista_comandos()
        self.consumir(TokenType.FIM, "Esperado 'fim'")
        
        return Bloco(comandos, linha, coluna)
    
    def condicional(self) -> Se:
        """condicional ::= 'se' expressão 'entao' comando [ 'senao' comando ]"""
        linha = self.token_atual.linha
        coluna = self.token_atual.coluna
        
        self.consumir(TokenType.SE, "Esperado 'se'")
        condicao = self.expressao()
        self.consumir(TokenType.ENTAO, "Esperado 'entao' após condição")
        comando_entao = self.comando()
        
        comando_senao = None
        if self.verificar(TokenType.SENAO):
            self.avancar()
            comando_senao = self.comando()
        
        return Se(condicao, comando_entao, comando_senao, linha, coluna)
    
    def repeticao(self) -> Enquanto:
        """repetição ::= 'enquanto' expressão 'faca' comando"""
        linha = self.token_atual.linha
        coluna = self.token_atual.coluna
        
        self.consumir(TokenType.ENQUANTO, "Esperado 'enquanto'")
        condicao = self.expressao()
        self.consumir(TokenType.FACA, "Esperado 'faca' após condição")
        comando = self.comando()
        
        return Enquanto(condicao, comando, linha, coluna)
    
    def expressao(self) -> Expressao:
        """expressão ::= expressão_relacional"""
        return self.expressao_relacional()
    
    def expressao_relacional(self) -> Expressao:
        """expressão_relacional ::= expressão_aritmetica [ operador_relacional expressão_aritmetica ]"""
        expr = self.expressao_aritmetica()
        
        if self.verificar(TokenType.IGUAL, TokenType.DIFERENTE, TokenType.MENOR,
                         TokenType.MENOR_IGUAL, TokenType.MAIOR, TokenType.MAIOR_IGUAL):
            operador = self.token_atual.valor
            linha = self.token_atual.linha
            coluna = self.token_atual.coluna
            self.avancar()
            direita = self.expressao_aritmetica()
            expr = ExpressaoBinaria(expr, operador, direita, linha, coluna)
        
        return expr
    
    def expressao_aritmetica(self) -> Expressao:
        """expressão_aritmética ::= termo { ('+' | '-') termo }"""
        expr = self.termo()
        
        while self.verificar(TokenType.MAIS, TokenType.MENOS):
            operador = self.token_atual.valor
            linha = self.token_atual.linha
            coluna = self.token_atual.coluna
            self.avancar()
            direita = self.termo()
            expr = ExpressaoBinaria(expr, operador, direita, linha, coluna)
        
        return expr
    
    def termo(self) -> Expressao:
        """termo ::= fator { ('*' | '/') fator }"""
        expr = self.fator()
        
        while self.verificar(TokenType.MULTIPLICACAO, TokenType.DIVISAO):
            operador = self.token_atual.valor
            linha = self.token_atual.linha
            coluna = self.token_atual.coluna
            self.avancar()
            direita = self.fator()
            expr = ExpressaoBinaria(expr, operador, direita, linha, coluna)
        
        return expr
    
    def fator(self) -> Expressao:
        """fator ::= NUMERO | IDENTIFICADOR | STRING | '-' fator | '(' expressão ')'"""
        linha = self.token_atual.linha
        coluna = self.token_atual.coluna
        
        if self.verificar(TokenType.NUMERO):
            valor = int(self.token_atual.valor)
            self.avancar()
            return Numero(valor, linha, coluna)
        
        elif self.verificar(TokenType.IDENTIFICADOR):
            nome = self.token_atual.valor
            self.avancar()
            return Variavel(nome, linha, coluna)
        
        elif self.verificar(TokenType.STRING):
            valor = self.token_atual.valor
            self.avancar()
            return StringLiteral(valor, linha, coluna)
        
        elif self.verificar(TokenType.MENOS):
            self.avancar()
            expr = self.fator()
            return ExpressaoUnaria("-", expr, linha, coluna)
        
        elif self.verificar(TokenType.PARENTESE_ESQ):
            self.avancar()
            expr = self.expressao()
            self.consumir(TokenType.PARENTESE_DIR, "Esperado ')' após expressão")
            return expr
        
        else:
            self.erro("Esperado número, identificador, string ou '('")