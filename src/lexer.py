import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Palavras reservadas
    PROGRAMA = "programa"
    VAR = "var"
    INICIO = "inicio"
    FIM = "fim"
    INTEIRO = "inteiro"
    SE = "se"
    ENTAO = "entao"
    SENAO = "senao"
    ENQUANTO = "enquanto"
    FACA = "faca"
    LER = "ler"
    ESCREVER = "escrever"
    
    # Operadores
    MAIS = "+"
    MENOS = "-"
    MULTIPLICACAO = "*"
    DIVISAO = "/"
    ATRIBUICAO = ":="
    IGUAL = "="
    DIFERENTE = "<>"
    MENOR = "<"
    MENOR_IGUAL = "<="
    MAIOR = ">"
    MAIOR_IGUAL = ">="
    
    # Delimitadores
    PONTO_VIRGULA = ";"
    PONTO = "."
    VIRGULA = ","
    DOIS_PONTOS = ":"
    PARENTESE_ESQ = "("
    PARENTESE_DIR = ")"
    
    # Literais
    IDENTIFICADOR = "IDENTIFICADOR"
    NUMERO = "NUMERO"
    STRING = "STRING"
    EOF = "EOF"

@dataclass
class Token:
    tipo: TokenType
    valor: str
    linha: int
    coluna: int

class LexerError(Exception):
    def __init__(self, mensagem: str, linha: int, coluna: int):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"Erro léxico na linha {linha}, coluna {coluna}: {mensagem}")

class Lexer:
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.posicao = 0
        self.linha = 1
        self.coluna = 1
        
        self.palavras_reservadas = {
            "programa": TokenType.PROGRAMA,
            "var": TokenType.VAR,
            "inicio": TokenType.INICIO,
            "fim": TokenType.FIM,
            "inteiro": TokenType.INTEIRO,
            "se": TokenType.SE,
            "entao": TokenType.ENTAO,
            "senao": TokenType.SENAO,
            "enquanto": TokenType.ENQUANTO,
            "faca": TokenType.FACA,
            "ler": TokenType.LER,
            "escrever": TokenType.ESCREVER
        }
        
        self.operadores_duplos = {
            ":=": TokenType.ATRIBUICAO,
            "<>": TokenType.DIFERENTE,
            "<=": TokenType.MENOR_IGUAL,
            ">=": TokenType.MAIOR_IGUAL
        }
        
        self.operadores_simples = {
            "+": TokenType.MAIS,
            "-": TokenType.MENOS,
            "*": TokenType.MULTIPLICACAO,
            "/": TokenType.DIVISAO,
            "=": TokenType.IGUAL,
            "<": TokenType.MENOR,
            ">": TokenType.MAIOR,
            ";": TokenType.PONTO_VIRGULA,
            ".": TokenType.PONTO,
            ",": TokenType.VIRGULA,
            ":": TokenType.DOIS_PONTOS,
            "(": TokenType.PARENTESE_ESQ,
            ")": TokenType.PARENTESE_DIR
        }
    
    def char_atual(self) -> Optional[str]:
        if self.posicao >= len(self.codigo):
            return None
        return self.codigo[self.posicao]
    
    def proximo_char(self) -> Optional[str]:
        if self.posicao + 1 >= len(self.codigo):
            return None
        return self.codigo[self.posicao + 1]
    
    def avancar(self):
        if self.posicao < len(self.codigo):
            if self.codigo[self.posicao] == '\n':
                self.linha += 1
                self.coluna = 1
            else:
                self.coluna += 1
            self.posicao += 1
    
    def pular_espacos(self):
        while self.char_atual() and self.char_atual().isspace():
            self.avancar()
    
    def ler_comentario(self):
        self.avancar()  # /
        self.avancar()  # *
        
        while self.char_atual():
            if self.char_atual() == '*' and self.proximo_char() == '/':
                self.avancar()  # *
                self.avancar()  # /
                return
            self.avancar()
        
        raise LexerError("Comentário não fechado", self.linha, self.coluna)
    
    def ler_string(self) -> str:
        valor = ""
        self.avancar()  # pula primeira aspas
        
        while self.char_atual() and self.char_atual() != '"':
            if self.char_atual() == '\\':
                self.avancar()
                if self.char_atual() == 'n':
                    valor += '\n'
                elif self.char_atual() == 't':
                    valor += '\t'
                elif self.char_atual() == '\\':
                    valor += '\\'
                elif self.char_atual() == '"':
                    valor += '"'
                else:
                    valor += self.char_atual()
                self.avancar()
            else:
                valor += self.char_atual()
                self.avancar()
        
        if not self.char_atual():
            raise LexerError("String não fechada", self.linha, self.coluna)
        
        self.avancar()  # pula última aspas
        return valor
    
    def ler_numero(self) -> str:
        valor = ""
        while self.char_atual() and self.char_atual().isdigit():
            valor += self.char_atual()
            self.avancar()
        return valor
    
    def ler_identificador(self) -> str:
        valor = ""
        while (self.char_atual() and 
               (self.char_atual().isalnum() or self.char_atual() == '_')):
            valor += self.char_atual()
            self.avancar()
        return valor
    
    def proximo_token(self) -> Token:
        self.pular_espacos()
        
        if not self.char_atual():
            return Token(TokenType.EOF, "", self.linha, self.coluna)
        
        linha_atual = self.linha
        coluna_atual = self.coluna
        char = self.char_atual()
        
        # Comentários
        if char == '/' and self.proximo_char() == '*':
            self.ler_comentario()
            return self.proximo_token()
        
        # Strings
        if char == '"':
            valor = self.ler_string()
            return Token(TokenType.STRING, valor, linha_atual, coluna_atual)
        
        # Números
        if char.isdigit():
            valor = self.ler_numero()
            return Token(TokenType.NUMERO, valor, linha_atual, coluna_atual)
        
        # Identificadores e palavras reservadas
        if char.isalpha() or char == '_':
            valor = self.ler_identificador()
            tipo = self.palavras_reservadas.get(valor.lower(), TokenType.IDENTIFICADOR)
            return Token(tipo, valor, linha_atual, coluna_atual)
        
        # Operadores de dois caracteres
        if self.proximo_char():
            operador_duplo = char + self.proximo_char()
            if operador_duplo in self.operadores_duplos:
                self.avancar()
                self.avancar()
                return Token(self.operadores_duplos[operador_duplo], operador_duplo, 
                           linha_atual, coluna_atual)
        
        # Operadores simples
        if char in self.operadores_simples:
            self.avancar()
            return Token(self.operadores_simples[char], char, linha_atual, coluna_atual)
        
        raise LexerError(f"Caractere inválido: '{char}'", linha_atual, coluna_atual)
    
    def tokenizar(self) -> List[Token]:
        tokens = []
        while True:
            token = self.proximo_token()
            tokens.append(token)
            if token.tipo == TokenType.EOF:
                break
        return tokens