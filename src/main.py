import sys
import os
import argparse
from pathlib import Path

from lexer import Lexer, LexerError
from parser import Parser, ParserError
from semantic import analisar_semantica
from interpreter import executar_programa, Interpretador
from ast_nodes import visualizar_ast_grafico

def compilar_arquivo(caminho_arquivo: str, opcoes: dict) -> bool:
    """Compila um arquivo Fortall"""
    
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado")
        return False
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            codigo = arquivo.read()
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return False
    
    if opcoes.get('verbose'):
        print(f"Compilando arquivo: {caminho_arquivo}")
        print("=" * 50)
    
    try:
        # Análise Léxica
        if opcoes.get('verbose'):
            print("1. Análise Léxica...")
        
        lexer = Lexer(codigo)
        tokens = lexer.tokenizar()
        
        if opcoes.get('verbose'):
            print(f"   -> {len([t for t in tokens if t.tipo.name != 'EOF'])} tokens reconhecidos")
        
        # Análise Sintática
        if opcoes.get('verbose'):
            print("2. Análise Sintática...")
        
        parser = Parser(codigo)
        ast = parser.parse()
        
        if not ast:
            print("Erro na análise sintática")
            return False
        
        if opcoes.get('verbose'):
            print(f"   -> Programa: {ast.nome}")
            print(f"   -> Declarações: {len(ast.declaracoes)} variáveis")
            print(f"   -> Comandos: {len(ast.comandos)} instruções")
        
        # Mostrar AST 
        if opcoes.get('mostrar_ast'):
            visualizar_ast_grafico(ast)
        
        # Análise Semântica
        if opcoes.get('verbose'):
            print("3. Análise Semântica...")
        
        erros_semanticos = analisar_semantica(ast)
        
        if erros_semanticos:
            print("Erros semânticos encontrados:")
            for i, erro in enumerate(erros_semanticos, 1):
                print(f"   {i}. {erro}")
            return False
        
        if opcoes.get('verbose'):
            print("   -> Nenhum erro semântico detectado")
        
        # Execução
        if opcoes.get('executar'):
            if opcoes.get('verbose'):
                print("4. Execução do Programa")
                print("=" * 30)
            
            interpretador = Interpretador()
            sucesso = interpretador.interpretar(ast)
            
            if opcoes.get('verbose'):
                print("=" * 30)
            
            if sucesso:
                if opcoes.get('verbose'):
                    print("Programa executado com sucesso!")
            else:
                print("Erro durante execução")
                return False
        
        if opcoes.get('verbose'):
            print(f"Compilação de '{caminho_arquivo}' concluída com sucesso!")
        
        return True
        
    except LexerError as e:
        print(f"Erro léxico: {e}")
        return False
    except ParserError as e:
        print(f"Erro sintático: {e}")
        return False
    except Exception as e:
        print(f"Erro: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Compilador Fortall',
        epilog='''
Exemplos de uso:
  python main.py programa.fortall              # Compilar arquivo
  python main.py programa.fortall -e           # Compilar e executar
  python main.py programa.fortall -v           # Modo verboso
  python main.py programa.fortall --ast        # Árvore Sintática
  python main.py programa.fortall -e -v --ast  # Tudo junto
        '''
    )
    
    # Argumentos
    parser.add_argument('arquivo', help='Arquivo Fortall para compilar')
    parser.add_argument('-e', '--executar', action='store_true', 
                       help='Executar programa após compilação')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Mostrar detalhes da compilação')
    parser.add_argument('--ast', action='store_true',
                       help='Mostrar árvore sintática')
    
    args = parser.parse_args()
    
    # Opções de compilação
    opcoes = {
        'executar': args.executar,
        'verbose': args.verbose,
        'mostrar_ast': args.ast,
    }
    
    # Compilar arquivo
    sucesso = compilar_arquivo(args.arquivo, opcoes)
    return 0 if sucesso else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOperação interrompida pelo usuário")
        sys.exit(1)