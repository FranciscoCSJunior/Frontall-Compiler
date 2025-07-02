from abc import ABC, abstractmethod
from typing import List, Any, Optional

class NoAST(ABC):
    """Classe base para todos os nós da árvore sintática"""
    
    def __init__(self, linha: int = 0, coluna: int = 0):
        self.linha = linha
        self.coluna = coluna
    
    @abstractmethod
    def aceitar(self, visitor):
        pass

class Programa(NoAST):
    def __init__(self, nome: str, declaracoes: List['Declaracao'], 
                 comandos: List['Comando'], linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.nome = nome
        self.declaracoes = declaracoes
        self.comandos = comandos
    
    def aceitar(self, visitor):
        return visitor.visitar_programa(self)

class Declaracao(NoAST):
    def __init__(self, variaveis: List[str], tipo: str, linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.variaveis = variaveis
        self.tipo = tipo
    
    def aceitar(self, visitor):
        return visitor.visitar_declaracao(self)

# Comandos
class Comando(NoAST):
    pass

class Atribuicao(Comando):
    def __init__(self, variavel: str, expressao: 'Expressao', linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.variavel = variavel
        self.expressao = expressao
    
    def aceitar(self, visitor):
        return visitor.visitar_atribuicao(self)

class Leitura(Comando):
    def __init__(self, variaveis: List[str], linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.variaveis = variaveis
    
    def aceitar(self, visitor):
        return visitor.visitar_leitura(self)

class Escrita(Comando):
    def __init__(self, expressoes: List['Expressao'], linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.expressoes = expressoes
    
    def aceitar(self, visitor):
        return visitor.visitar_escrita(self)

class Bloco(Comando):
    def __init__(self, comandos: List[Comando], linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.comandos = comandos
    
    def aceitar(self, visitor):
        return visitor.visitar_bloco(self)

class Se(Comando):
    def __init__(self, condicao: 'Expressao', comando_entao: Comando,
                 comando_senao: Optional[Comando] = None, linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.condicao = condicao
        self.comando_entao = comando_entao
        self.comando_senao = comando_senao
    
    def aceitar(self, visitor):
        return visitor.visitar_se(self)

class Enquanto(Comando):
    def __init__(self, condicao: 'Expressao', comando: Comando, linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.condicao = condicao
        self.comando = comando
    
    def aceitar(self, visitor):
        return visitor.visitar_enquanto(self)

# Expressões
class Expressao(NoAST):
    def __init__(self, linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.tipo = None

class ExpressaoBinaria(Expressao):
    def __init__(self, esquerda: Expressao, operador: str, direita: Expressao,
                 linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.esquerda = esquerda
        self.operador = operador
        self.direita = direita
    
    def aceitar(self, visitor):
        return visitor.visitar_expressao_binaria(self)

class ExpressaoUnaria(Expressao):
    def __init__(self, operador: str, expressao: Expressao, linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.operador = operador
        self.expressao = expressao
    
    def aceitar(self, visitor):
        return visitor.visitar_expressao_unaria(self)

class Variavel(Expressao):
    def __init__(self, nome: str, linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.nome = nome
    
    def aceitar(self, visitor):
        return visitor.visitar_variavel(self)

class Numero(Expressao):
    def __init__(self, valor: int, linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.valor = valor
    
    def aceitar(self, visitor):
        return visitor.visitar_numero(self)

class StringLiteral(Expressao):
    def __init__(self, valor: str, linha: int = 0, coluna: int = 0):
        super().__init__(linha, coluna)
        self.valor = valor
    
    def aceitar(self, visitor):
        return visitor.visitar_string(self)

# Visitor Pattern
class VisitorAST(ABC):
    """Interface para implementar o padrão Visitor"""
    
    @abstractmethod
    def visitar_programa(self, no: Programa):
        pass
    
    @abstractmethod
    def visitar_declaracao(self, no: Declaracao):
        pass
    
    @abstractmethod
    def visitar_atribuicao(self, no: Atribuicao):
        pass
    
    @abstractmethod
    def visitar_leitura(self, no: Leitura):
        pass
    
    @abstractmethod
    def visitar_escrita(self, no: Escrita):
        pass
    
    @abstractmethod
    def visitar_bloco(self, no: Bloco):
        pass
    
    @abstractmethod
    def visitar_se(self, no: Se):
        pass
    
    @abstractmethod
    def visitar_enquanto(self, no: Enquanto):
        pass
    
    @abstractmethod
    def visitar_expressao_binaria(self, no: ExpressaoBinaria):
        pass
    
    @abstractmethod
    def visitar_expressao_unaria(self, no: ExpressaoUnaria):
        pass
    
    @abstractmethod
    def visitar_variavel(self, no: Variavel):
        pass
    
    @abstractmethod
    def visitar_numero(self, no: Numero):
        pass
    
    @abstractmethod
    def visitar_string(self, no: StringLiteral):
        pass

class ImpressorArvore(VisitorAST):
    """Visitor para imprimir a árvore sintática como uma árvore real no terminal"""
    
    def __init__(self):
        self.prefixos = []
    
    def _obter_prefixo(self, eh_ultimo=True):
        """Gera o prefixo com linhas de conexão da árvore"""
        if not self.prefixos:
            return ""
        
        prefixo = ""
        for i in range(len(self.prefixos) - 1):
            if self.prefixos[i]:
                prefixo += "│   "
            else:
                prefixo += "    "
        
        if eh_ultimo:
            return prefixo + "└── "
        else:
            return prefixo + "├── "
    
    def _imprimir_no(self, texto, eh_ultimo=True):
        """Imprime um nó com as conexões apropriadas"""
        print(self._obter_prefixo(eh_ultimo) + texto)
    
    def _processar_filhos(self, filhos, funcao_processar):
        """Processa uma lista de filhos mantendo a estrutura da árvore"""
        if not filhos:
            return
        
        for i, filho in enumerate(filhos):
            eh_ultimo = (i == len(filhos) - 1)
            self.prefixos.append(not eh_ultimo)
            funcao_processar(filho)
            self.prefixos.pop()
    
    def visitar_programa(self, no: Programa):
        print(f"Programa: {no.nome}")
        
        # Coletar todos os filhos em ordem
        filhos = []
        
        # Adicionar declarações
        for decl in no.declaracoes:
            filhos.append(('declaracao', decl))
        
        # Adicionar comandos
        for cmd in no.comandos:
            filhos.append(('comando', cmd))
        
        # Processar filhos
        for i, (tipo, filho) in enumerate(filhos):
            eh_ultimo = (i == len(filhos) - 1)
            self.prefixos.append(not eh_ultimo)
            filho.aceitar(self)
            self.prefixos.pop()
    
    def visitar_declaracao(self, no: Declaracao):
        vars_str = ", ".join(no.variaveis)
        self._imprimir_no(f"Declaracao: {vars_str} : {no.tipo}")
    
    def visitar_atribuicao(self, no: Atribuicao):
        self._imprimir_no(f"Atribuicao: {no.variavel} :=")
        
        # Processar expressão do lado direito
        self.prefixos.append(False)
        no.expressao.aceitar(self)
        self.prefixos.pop()
    
    def visitar_leitura(self, no: Leitura):
        vars_str = ", ".join(no.variaveis)
        self._imprimir_no(f"Leitura: {vars_str}")
    
    def visitar_escrita(self, no: Escrita):
        self._imprimir_no("Escrita")
        
        # Processar expressões
        self._processar_filhos(no.expressoes, lambda expr: expr.aceitar(self))
    
    def visitar_bloco(self, no: Bloco):
        self._imprimir_no("Bloco")
        
        # Processar comandos do bloco
        self._processar_filhos(no.comandos, lambda cmd: cmd.aceitar(self))
    
    def visitar_se(self, no: Se):
        self._imprimir_no("Se")
        
        # Criar estrutura hierárquica
        filhos = []
        
        # Adicionar condição
        filhos.append(('condicao', no.condicao))
        
        # Adicionar comando então
        filhos.append(('entao', no.comando_entao))
        
        # Adicionar comando senão se existir
        if no.comando_senao:
            filhos.append(('senao', no.comando_senao))
        
        # Processar cada parte
        for i, (tipo, componente) in enumerate(filhos):
            eh_ultimo = (i == len(filhos) - 1)
            self.prefixos.append(not eh_ultimo)
            
            if tipo == 'condicao':
                self._imprimir_no("Condicao")
                self.prefixos.append(False)
                componente.aceitar(self)
                self.prefixos.pop()
            elif tipo == 'entao':
                self._imprimir_no("Entao")
                self.prefixos.append(False)
                componente.aceitar(self)
                self.prefixos.pop()
            elif tipo == 'senao':
                self._imprimir_no("Senao")
                self.prefixos.append(False)
                componente.aceitar(self)
                self.prefixos.pop()
            
            self.prefixos.pop()
    
    def visitar_enquanto(self, no: Enquanto):
        self._imprimir_no("Enquanto")
        
        # Condição
        self.prefixos.append(False)
        self._imprimir_no("Condicao")
        self.prefixos.append(False)
        no.condicao.aceitar(self)
        self.prefixos.pop()
        self.prefixos.pop()
        
        # Comando
        self.prefixos.append(False)
        self._imprimir_no("Comando")
        self.prefixos.append(False)
        no.comando.aceitar(self)
        self.prefixos.pop()
        self.prefixos.pop()
    
    def visitar_expressao_binaria(self, no: ExpressaoBinaria):
        self._imprimir_no(f"Op: {no.operador}")
        
        # Operando esquerdo
        self.prefixos.append(False)
        no.esquerda.aceitar(self)
        self.prefixos.pop()
        
        # Operando direito
        self.prefixos.append(False)
        no.direita.aceitar(self)
        self.prefixos.pop()
    
    def visitar_expressao_unaria(self, no: ExpressaoUnaria):
        self._imprimir_no(f"Op: {no.operador} (unario)")
        
        # Operando
        self.prefixos.append(False)
        no.expressao.aceitar(self)
        self.prefixos.pop()
    
    def visitar_variavel(self, no: Variavel):
        self._imprimir_no(f"Var: {no.nome}")
    
    def visitar_numero(self, no: Numero):
        self._imprimir_no(f"Num: {no.valor}")
    
    def visitar_string(self, no: StringLiteral):
        self._imprimir_no(f'String: "{no.valor}"')

def visualizar_ast_grafico(no_raiz: NoAST):
    """Função para visualizar a AST como uma árvore no terminal"""
    print("\n" + "="*60)
    print("                    ÁRVORE SINTÁTICA")
    print("="*60)
    
    impressor = ImpressorArvore()
    no_raiz.aceitar(impressor)
    
    print("="*60)