# Busca-de-CNPJ-com-interface
## Descrição
Aplicação GUI para consulta e validação de CNPJs em massa via BrasilAPI. Permite carregar um arquivo CSV com CNPJs, valida cada um (formato e dígiyos verificadores), consulta dados da empresa na API e exporta resultados para CSV. Desenvolvido com Tkinter e ttkbootstrap para uma interface moderna, com threads para não travar a UI durante consultas.

## Funcionalidades
* **Carregar Arquivo CSV**: Selecionar arquivo CSV contendo coluna "CNPJ" para processamento.
* **Validação de CNPJ**: Checa formato, dígiyos verificadores e sequências inválidas (ex: 000...)
* **Consulta à BrasilAPI**: Busca detalhes da empresa (razão social, endereço, contatos etc.) vi a API pública.
* **Progresso em Tempo Real**: Barra de progresso e log de operações com detalhes de cada CNPJ processado.
* **Exportação de Resultados**: Gera dois arquivos CSV ("cnpjs_ok.csv" e "cnpjs_erros.csv") ao final.
* **Cancelamento Seguro**: Botão para interromper o processamento a qualquer momento.

## Como Usar
### 1. **Selecionar Arquivo**:
* Clique em "Selecionar" e escolha CSV com a coluna "CNPJ".
* Certifique-se que o arquivo tem cabeçalho e os CNPJs estão em uma coluna nomeada "CNPJ".
### 2. **Iniciar Consulta**:
* Clique em "Iniciar Consulta" para começar o processamento.
* Acompanhe o progresso na barra e no log de texto.
### 3. **Resultados**:
* Ao final, selecione uma pasta para salvar os arquivos de saída.
* CNPJs válidos e consultados com sucesso estarão em 'cnpjs_ok.csv'.
* Erros de validação/consulta estarão em 'cnpjs_erros.csv'.

## Dependências
* **Pandas**: Manipulação de dados CSV
* **Requests**: Requisições HTTP à API
* **ttkbootstrap**: Interface gráfica moderna (Tkinter)
* **Tkinter**: Biblioteca base para GUI (já incluída no Python)
* **Outras**: re, os, datetime, threading (bibliotecas padrão)

## Como Instalar
### 1. **Clone o repositório**:
```bash
git clone https://github.com/Sankhya-ABC/Busca-de-CNPJ-c-interface.git.
```
### 2. **Instale as dependências**:
```bash
pip install pandas requests ttkbootstrap
```
### 3. **Execute o aplicativo**:
```bash
python main.py
```
## Exemplo de Uso
* **CNPJ Válido**: "33.014.556/0001-96" será validado e retornará dados completos da empresa.
* **CNPJ Inválido**: "11.111.111/1111-11" será marcado como erro ("Sequência inválida").
* **Erro na API**: Se a API estiver indisponível, mostrará "Erro de conexão" no log.
#### **Nota**: A aplicação faz até 3 tentativas de consulta em caso de erro 429 (muitas requisições) com delays crescentes.