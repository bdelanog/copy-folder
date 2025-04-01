import os
import shutil
import logging
import uuid
import json
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, Checkbutton, IntVar, Text, filedialog, END, Scrollbar, RIGHT, Y, messagebox, W, E, NSEW

# --- Configurações fixas ---
extensoes_validas = ('.txt', '.sql', '.pdf', '.rtf')
logfile = 'programa/para/logs.log'
configfile = 'programa/para/paths.json'

# --- Inicializa o logger ---
os.makedirs(os.path.dirname(logfile), exist_ok=True)
os.makedirs(os.path.dirname(configfile), exist_ok=True)
logging.basicConfig(filename=logfile, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Função principal de cópia ---
def copiar_arquivos(origem, destino, dry_run, log_widget):
    log_widget.configure(state="normal")
    log_widget.delete(1.0, END)

    if not origem or not destino:
        messagebox.showerror("Erro", "Por favor, selecione a pasta de origem e a pasta de destino.")
        return

    if os.path.abspath(origem) == os.path.abspath(destino):
        messagebox.showerror("Erro", "A pasta de origem e destino não podem ser iguais.")
        return

    with open(configfile, 'w') as f:
        json.dump({"origem": origem, "destino": destino}, f)

    copiados = 0
    ignorados = 0
    erros = 0

    if not os.path.exists(origem):
        msg = f"[ERRO] Pasta de origem não encontrada: {origem}\n"
        log_widget.insert(END, msg)
        logging.error(f'Pasta de origem não encontrada: {origem}')
        return

    try:
        os.makedirs(destino, exist_ok=True)
    except Exception as e:
        msg = f"[ERRO] Ao criar pasta de destino: {e}\n"
        log_widget.insert(END, msg)
        logging.error(f'Erro ao criar pasta destino: {e}')
        return

    arquivos = os.listdir(origem)
    for arquivo in arquivos:
        if not arquivo.lower().endswith(extensoes_validas):
            continue

        caminho_origem = os.path.join(origem, arquivo)
        caminho_destino = os.path.join(destino, arquivo)

        try:
            try:
                with open(caminho_origem, 'rb'):
                    pass
            except Exception as e:
                ignorados += 1
                logging.warning(f"Arquivo não pode ser lido: {arquivo}. Erro: {e}")
                continue

            if os.path.exists(caminho_destino):
                if os.stat(caminho_origem).st_size == os.stat(caminho_destino).st_size:
                    ignorados += 1
                    logging.info(f"Arquivo ignorado (duplicado): {arquivo}")
                    continue
                else:
                    base, ext = os.path.splitext(arquivo)
                    while True:
                        novo_nome = f"{base}_{uuid.uuid4().hex[:6]}{ext}"
                        caminho_destino = os.path.join(destino, novo_nome)
                        if not os.path.exists(caminho_destino):
                            break
                    logging.warning(f'Arquivo existente: {arquivo}. Renomeado para: {novo_nome}')

            if dry_run:
                msg = f"[DRY-RUN] Simulando cópia: {arquivo}\n"
                logging.info(f"[DRY-RUN] Simulando cópia de: {arquivo}")
            else:
                shutil.copy2(caminho_origem, caminho_destino)
                copiados += 1
                msg = f"[OK] Arquivo copiado: {arquivo}\n"
                logging.info(f"Arquivo copiado: {arquivo}")

            log_widget.insert(END, msg)
            log_widget.see(END)

        except Exception as e:
            msg = f"[ERRO] Falha ao copiar {arquivo}: {e}\n"
            log_widget.insert(END, msg)
            logging.error(f"Erro ao copiar {arquivo}: {e}")
            erros += 1

    resumo = f"\nResumo da exportação ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n- Arquivos copiados: {copiados}\n- Ignorados (duplicados ou sem permissão): {ignorados}\n- Erros: {erros}\n"
    log_widget.insert(END, resumo)
    log_widget.see(END)
    logging.info(resumo)
    log_widget.configure(state="disabled")

# --- Funções adicionais para log ---
def salvar_log(log_widget):
    conteudo = log_widget.get("1.0", END)
    if conteudo.strip():
        caminho = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Arquivo de Texto", "*.txt")])
        if caminho:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo)

def limpar_log(log_widget):
    log_widget.configure(state="normal")
    log_widget.delete(1.0, END)
    log_widget.configure(state="disabled")

# --- Função de seleção de pasta ---
def selecionar_pasta(entry_widget):
    pasta = filedialog.askdirectory()
    if pasta:
        entry_widget.delete(0, END)
        entry_widget.insert(0, pasta)

# --- Interface Tkinter ---
root = Tk()
root.title("Exportador de Arquivos")
root.geometry("800x600")

for i in range(7):
    root.grid_rowconfigure(i, weight=1)
for j in range(3):
    root.grid_columnconfigure(j, weight=1)

Label(root, text="Pasta de Origem:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
entrada_origem = Entry(root)
entrada_origem.grid(row=0, column=1, sticky=E+W, padx=5, pady=5)
Button(root, text="Selecionar", command=lambda: selecionar_pasta(entrada_origem)).grid(row=0, column=2, padx=5)

Label(root, text="Pasta de Destino:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
entrada_destino = Entry(root)
entrada_destino.grid(row=1, column=1, sticky=E+W, padx=5, pady=5)
Button(root, text="Selecionar", command=lambda: selecionar_pasta(entrada_destino)).grid(row=1, column=2, padx=5)

var_dry_run = IntVar()
Checkbutton(root, text="Modo Simulação (Dry-Run)", variable=var_dry_run).grid(row=2, column=0, columnspan=2, sticky=W, padx=5, pady=5)
Button(root, text="Executar Exportação", command=lambda: copiar_arquivos(entrada_origem.get(), entrada_destino.get(), var_dry_run.get(), log_text)).grid(row=2, column=2, padx=5)
Button(root, text="Salvar Log", command=lambda: salvar_log(log_text)).grid(row=3, column=2, padx=5, pady=2)
Button(root, text="Limpar Log", command=lambda: limpar_log(log_text)).grid(row=4, column=2, padx=5, pady=2)

Label(root, text="Log de Execução:").grid(row=5, column=0, sticky=W, padx=5, pady=5, columnspan=3)

scrollbar = Scrollbar(root)
scrollbar.grid(row=6, column=2, sticky='ns')

log_text = Text(root, yscrollcommand=scrollbar.set, wrap="none")
log_text.grid(row=6, column=0, columnspan=2, sticky=NSEW, padx=5, pady=5)
scrollbar.config(command=log_text.yview)

if os.path.exists(configfile):
    try:
        with open(configfile, 'r') as f:
            dados = json.load(f)
            entrada_origem.insert(0, dados.get("origem", ""))
            entrada_destino.insert(0, dados.get("destino", ""))
    except Exception:
        pass

root.mainloop()
