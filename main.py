# Bibliotecas padrão
import pandas as pd
import requests
import time
import os
import re
from datetime import datetime
# Bibliotecas de interface gráfica
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, scrolledtext, BOTH, X, LEFT, END
from threading import Thread

# Classe principal da aplicação GUI para consulta de CNPJs
class CNPJConsultorGUI(tb.Window):
    
    def __init__(self):
        # Inicializa a janela principal e configura os componentes
        super().__init__(
            title="Consultor de CNPJ",
            themename="cosmo",  # Tema visual da interface
            size=(900, 650)     # Tamanho inicial da janela
        )
        # Lista de campos que serão exportados no CSV final
        self.campos_saida = [
            'CNPJ', 'Razao Social', 'Nome Fantasia', 'Inscrição Estadual',
            'Cep', 'Endereço', 'Numero', 'Complemento', 'Bairro',
            'Cidade', 'UF', 'Telefone', 'E-mail'
        ]
        # Variáveis de controle
        self.running = False        # Flag para controle de execução
        self.df_entrada = None      # DataFrame para armazenar os dados de entrada
        self._build_ui()            # Constrói a interface gráfica

    def _build_ui(self):
        # Frame principal que contém todos os elementos
        main_frame = tb.Frame(self, padding=15)
        main_frame.pack(fill=BOTH, expand=True)

        # Cabeçalho com título
        header = tb.Frame(main_frame, padding=(5, 10))
        header.pack(fill=X, pady=(0, 10))
        tb.Label(header,
                 text="📊 Consultor de CNPJ",
                 font=("Helvetica", 20, "bold"),
                 bootstyle="inverse-info").pack()

        # Seção de seleção de arquivo
        file_frame = tb.Labelframe(main_frame,
                                   text="Arquivo de Entrada",
                                   bootstyle="secondary",
                                   padding=10)
        file_frame.pack(fill=X, pady=10)

        # Campo para exibir caminho do arquivo
        self.file_entry = tb.Entry(
            file_frame,
            width=60,
            bootstyle="primary"
        )
        self.file_entry.pack(side=LEFT, padx=(5, 10))

        # Botão para selecionar arquivo
        tb.Button(file_frame,
                  text="📂 Selecionar",
                  bootstyle="primary",
                  command=self.selecionar_arquivo).pack(side=LEFT)

        # Seção de progresso e logs
        progress_frame = tb.Labelframe(main_frame,
                                      text="Progresso",
                                      bootstyle="secondary",
                                      padding=10)
        progress_frame.pack(fill=BOTH, expand=True, pady=10)

        # Barra de progresso
        self.progress_bar = tb.Progressbar(progress_frame,
                                          bootstyle="success-striped",
                                          mode='determinate')
        self.progress_bar.pack(fill=X, pady=(0, 10))

        # Área de logs com scroll
        self.log_text = scrolledtext.ScrolledText(progress_frame,
                                                 height=15,
                                                 state='disabled',
                                                 font=("Consolas", 10))
        self.log_text.pack(fill=BOTH, expand=True)

        # Botões de controle
        button_frame = tb.Frame(main_frame, padding=(0, 10))
        button_frame.pack(fill=X)

        # Botão de iniciar processamento
        self.start_btn = tb.Button(button_frame,
                                   text="▶ Iniciar Consulta",
                                   bootstyle="success",
                                   command=self.iniciar_processamento)
        self.start_btn.pack(side=LEFT, padx=10)

        # Botão de cancelamento
        self.cancel_btn = tb.Button(button_frame,
                                    text="■ Cancelar",
                                    bootstyle="danger",
                                    state=DISABLED,
                                    command=self.cancelar_processamento)
        self.cancel_btn.pack(side=LEFT)

    def selecionar_arquivo(self):
        # Abre diálogo para seleção de arquivo CSV
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.file_entry.delete(0, END)
            self.file_entry.insert(0, path)

    def log(self, message, style=None):
        # Adiciona mensagens à área de logs
        # Args:
        # message (str): Mensagem a ser exibida
        # style (strm optional): Estilo especial (ex:'error')
        self.log_text.configure(state='normal')
        if style == 'error':
            self.log_text.insert(END, message + "\n", 'red')
        else:
            self.log_text.insert(END, message + "\n")
        self.log_text.see(END)
        self.log_text.configure(state='disabled')

    def atualizar_progresso(self, value):
        # Atualiza a barra de progresso
        # Args:
        # Value (int): Valor atual do progresso (0-100)
        self.progress_bar['value'] = value
        self.update_idletasks()

    def iniciar_processamento(self):
        # Inicia o processamento dos CNPJs em thread separada
        if self.running:
            return
        arquivo = self.file_entry.get()
        if not arquivo:
            messagebox.showerror("Erro", "Selecione um arquivo de entrada!")
            return
        try:
            # Carrega e valida o arquivo CSV
            self.df_entrada = pd.read_csv(arquivo)
            self.df_entrada.columns = self.df_entrada.columns.str.strip()
            if 'CNPJ' not in self.df_entrada.columns:
                raise ValueError("Coluna 'CNPJ' não encontrada")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler arquivo:\n{e}")
            return
        
        # Configura estado inicial do processamento
        self.running = True
        self.start_btn.configure(state=DISABLED)
        self.cancel_btn.configure(state=NORMAL)
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, END)
        self.log_text.configure(state='disabled')

        # Inicia thread para não travar a interface
        Thread(target=self.processar_cnpjs, daemon=True).start()

    def cancelar_processamento(self):
        # Interrompe o processamento em andamento
        self.running = False
        self.log("⚠️ Processamento cancelado pelo usuário", style='error')
        self.start_btn.configure(state=NORMAL)
        self.cancel_btn.configure(state=DISABLED)

    # Funções de validação e consulta (mantidas do script original)
    def validar_cnpj(self, cnpj):
        # Valida o formato e dígitos verificadoes de CCNPJ
        # Args:
        #     cnpj (str): CNPJ a ser valido
        # Return:
        #     tuple: (bool, str) Resultado e mensagem de erro

        # Limpa caracteres não numéricos
        cnpj_limpo = re.sub(r'\D', '', str(cnpj)).zfill(14)
        # Validações básicas
        if len(cnpj_limpo) != 14:
            return False, "Tamanho inválido"
        if all(c == cnpj_limpo[0] for c in cnpj_limpo):
            return False, "Sequência inválida"
        
        # Cálculo do primeiro dígito verificador
        pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj_limpo[i]) * pesos[i] for i in range(12))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        if digito1 != int(cnpj_limpo[12]):
            return False, "Dígito verificador 1 inválido"
        
        # Cálculo do segundo dígito verificador
        pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj_limpo[i]) * pesos[i] for i in range(13))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        if digito2 != int(cnpj_limpo[13]):
            return False, "Dígito verificador 2 inválido"
        return True, ""

    def consultar_cnpj(self, cnpj, tentativa=1):
        # Consulta os dados do CNPJ na BrasilAPI
        # Args:
        #     cnpj (str): CNPJ formatado
        #     tentativa (int): Número da tentativa atual
        # Returns:
        #     dict: Dados da empresa ou mensagem de erro
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            # Tratamento de respostas HTTP
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429 and tentativa <= 3:
                time.sleep(10 * tentativa)          # Backoof exponencial
                return self.consultar_cnpj(cnpj, tentativa+1)
            elif resp.status_code == 404:
                return {'erro': 'CNPJ não encontrado'}
            else:
                return {'erro': f'HTTP {resp.status_code}'}
        except Exception as e:
            return {'erro': f'Erro de conexão: {e}'}

    def processar_dados(self, cnpj, dados):
        # Processa a resposta da API para extrair dados relevantes
        # Args: 
        #       cnpj (str): CNPJ consultado
        #       dados (dict): Resposta da API
        # Returns:
        #       tuple (dict, str) Dados formatados e mensagem de erro

        if 'erro' in dados:
            return None, dados['erro']
        # Mapeamento dos campos da API para nossa estrutura
        return ({
            'CNPJ': cnpj,
            'Razao Social': dados.get('razao_social'),
            'Nome Fantasia': dados.get('nome_fantasia'),
            'Inscrição Estadual': dados.get('inscricoes_estaduais', [{}])[0].get('inscricao_estadual', ''),
            'Cep': dados.get('cep'),
            'Endereço': dados.get('logradouro'),
            'Numero': dados.get('numero'),
            'Complemento': dados.get('complemento'),
            'Bairro': dados.get('bairro'),
            'Cidade': dados.get('municipio'),
            'UF': dados.get('uf'),
            'Telefone': dados.get('ddd_telefone_1'),
            'E-mail': dados.get('correio_eletronico')
        }, '')

    def processar_cnpjs(self):
        # Processa todos os CNPJs do arquivo de entrada
        dados_ok, erros = [], []
        total = len(self.df_entrada)
        # Configura progresso
        self.progress_bar.configure(maximum=total)
        self.atualizar_progresso(0)
        start = datetime.now().strftime('%H:%M:%S')
        self.log(f"--- Início: {start} ---")
        # Loop principal de processamento
        for idx, row in self.df_entrada.iterrows():
            if not self.running:
                break
            cnpj_raw = str(row['CNPJ'])
            cnpj_limpo = re.sub(r'\D', '', cnpj_raw).zfill(14)
            # Validação local
            valido, motivo = self.validar_cnpj(cnpj_limpo)
            if not valido:
                erros.append({'CNPJ': cnpj_raw, 'Erro': motivo})
                self.log(f"{cnpj_limpo} inválido: {motivo}", style='error')
            else:
                # Consulta na API
                res = self.consultar_cnpj(cnpj_limpo)
                dados, err = self.processar_dados(cnpj_limpo, res)
                if err:
                    erros.append({'CNPJ': cnpj_limpo, 'Erro': err})
                    self.log(f"Erro: {err}", style='error')
                else:
                    dados_ok.append(dados)
                    self.log(f"{cnpj_limpo} OK")
            # Atualiza interface        
            self.atualizar_progresso(idx+1)
            time.sleep(0.2) # Delay para evitar sobrecarga da API
        self.running = False
        self.after(0, self.finalizar, dados_ok, erros)

    def finalizar(self, dados_ok, erros):
        # Finaliza o processamento e salva os resultados
        # Args:
        #     dados_ok (list): Lista de CNPJs válidos
        #     erros (list): Lista de erros encontrados
        self.log("--- Concluído! ---")
        save_dir = filedialog.askdirectory(title="Salvar resultados")
        if save_dir:
            # Salva arquivo de sucessos
            if dados_ok:
                pd.DataFrame(dados_ok)[self.campos_saida].to_csv(
                    os.path.join(save_dir, 'cnpjs_ok.csv'), index=False)
            # Salva arquivo de erros
            if erros:
                pd.DataFrame(erros).to_csv(
                    os.path.join(save_dir, 'cnpjs_erros.csv'), index=False)
        # Restaura estado dos botões
        self.start_btn.configure(state=NORMAL)
        self.cancel_btn.configure(state=DISABLED)

if __name__ == "__main__":
    # Inicializa e executa a aplicação
    app = CNPJConsultorGUI()
    app.mainloop()
