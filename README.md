# Parser e Simulador para Linguagem Fortall
##Linguagem Fortall
Implementação completa de um compilador para a linguagem Fortall (analisador léxico, sintático, semântico e interpretador), uma sublinguagem inspirada em Pascal/C.

[![Versão do Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Pré-requisitos

Para executar este compilador, você precisará de:

-**Sistema Operacional: Linux, macOS ou Windows**
- **Python 3.8 ou superior**
  - Download: [python.org/downloads](https://www.python.org/downloads/)
- **Nenhuma dependência adicional** (todas as bibliotecas usadas são nativas do Python)
- 
### 1. Instalar o Python

- **Linux**:

```bash

sudo apt update
sudo apt install python3 python3-pip

```

- **macOS (via Homebrew)**:

```bash

brew install python
```

- **Windows (via Chocolatey)**:

```bash

choco install python --version=3.8.0
```


### 2. Clonar o repositório
git clone https://github.com/FranciscoCSJunior/Frontall-Compiler.git
cd Frontall-Compiler

### 3. Compilar e executar
python src/main.py exemplos_entrada/fatorial.txt -e

## Modo detalhado (mostra cada etapa)
python src/main.py exemplos_entrada/fatorial.txt -v

## Mostrar árvore sintática
python src/main.py exemplos_entrada/fatorial.txt -ast

## Todas as opções juntas
python src/main.py exemplos_entrada/fatorial.txt -e -v --ast

## Estrutura do Código

### `lexer.py` - **Análise Léxica**
- Reconhece mais de 20 tipos de tokens
- Trata strings com sequências de escape (`\n`, `\t`)
- Localização precisa de erros (linha/coluna)

### `parser.py` - **Análise Sintática**
- Implementa parsing preditivo LL(1)
- Constrói AST tipada
- Recuperação de erros no modo pânico

### `ast_nodes.py`
- Define a estrutura da Árvore Sintática Abstrata (AST)

### `semantic.py` - **Análise Semântica**
- Verificação estática de tipos
- Detecção de variáveis não declaradas
- Validação de estruturas de controle

### `interpreter.py` - **Interpretador**
- Ambiente de execução com variáveis globais
- Suporte a:
  - Atribuições
  - Entrada/saída interativa
  - Loops (`enquanto`)
  - Condicionais (`se`)

### `main.py` - **Ponto de Entrada**
- Coordena todo o processo de compilação/execução
- Tratamento de argumentos CLI:
  - `-e`: Execução após compilação
  - `-v`: Modo verboso
  - `--ast`: Exibição da árvore sintática
- Leitura e processamento de arquivos 
## Exemplo de Script

Arquivo de entrada (`fatorial.txt`):

```fortall

/* Programa para calcular o fatorial de um número */
programa fatorial;
var numero, resultado, i : inteiro;
inicio
    escrever("CÁLCULO DE FATORIAL");
    escrever("Digite um número para calcular o fatorial: ");
    ler(numero);
    
    se numero < 0 entao
        escrever("Fatorial não é definido para números negativos!")
    senao
    inicio
        resultado := 1;
        i := 1;
        
        enquanto i <= numero faca
        inicio
            resultado := resultado * i;
            escrever(i, "! parcial = ", resultado);
            i := i + 1
        fim;
        
        escrever("O fatorial de ", numero, " é: ", resultado)
    fim
fim.
```
