import os
import shutil
import logging
import uuid
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, Checkbutton, IntVar, Text, filedialog, END, Scrollbar, RIGHT, Y

# --- Configurações fixas ---
extensoes_validas = ('.txt', '.sql', '.pdf', '.rtf')
destino = 'programa/para/pasta_destino'
logfile = 'programa/para/logs.log'

# --- Inicializa o logger ---
os.makedirs(os.path.dirname(logfile), exist_ok=True)
logging.basicConfig(filename=logfile, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Função principal de cópia ---
def copiar_arquivos(origem, dry_run, log_widget):
    copiados = 0
    ignorados = 0
    erros = 0

    if not origem or not os.path.exists(origem):
        msg = f"[ERRO] Pasta de origem não encontrada: {origem}\n"
        log_widget.insert(END, msg)
        return

    try:
        os.makedirs(destino, exist_ok=True)
    except Exception as e:
        msg = f"[ERRO] Ao criar pasta de destino: {e}\n"
        log_widget.insert(END, msg)
        return

    arquivos = os.listdir(origem)
    for arquivo in arquivos:
        if not arquivo.lower().endswith(extensoes_validas):
            continue

        caminho_origem = os.path.join(origem, arquivo)
        caminho_destino = os.path.join(destino, arquivo)

        try:
            if not os.access(caminho_origem, os.R_OK):
                ignorados += 1
                continue

            if os.path.exists(caminho_destino):
                if os.stat(caminho_origem).st_size == os.stat(caminho_destino).st_size:
                    ignorados += 1
                    continue
                else:
                    base, ext = os.path.splitext(arquivo)
                    novo_nome = f"{base}_{uuid.uuid4().hex[:6]}{ext}"
                    caminho_destino = os.path.join(destino, novo_nome)

            if dry_run:
                msg = f"[DRY-RUN] Simulando cópia: {arquivo}\n"
            else:
                shutil.copy2(caminho_origem, caminho_destino)
                copiados += 1
                msg = f"[OK] Arquivo copiado: {arquivo}\n"

            log_widget.insert(END, msg)
            log_widget.see(END)

        except Exception as e:
            msg = f"[ERRO] Falha ao copiar {arquivo}: {e}\n"
            log_widget.insert(END, msg)
            erros += 1

    resumo = f"\nResumo:\nCopiados: {copiados}\nIgnorados: {ignorados}\nErros: {erros}\n"
    log_widget.insert(END, resumo)
    log_widget.see(END)
    logging.info(resumo)

# --- Função de seleção de pasta ---
def selecionar_pasta(entry_widget):
    pasta = filedialog.askdirectory()
    if pasta:
        entry_widget.delete(0, END)
        entry_widget.insert(0, pasta)





# --- Interface Tkinter ---
root = Tk()
root.title("Exportador de Arquivos")
root.geometry("600x400")

Label(root, text="Pasta de Origem:").pack()
entrada_origem = Entry(root, width=60)
entrada_origem.pack()
Button(root, text="Selecionar Pasta", command=lambda: selecionar_pasta(entrada_origem)).pack()

var_dry_run = IntVar()
Checkbutton(root, text="Modo Simulação (Dry-Run)", variable=var_dry_run).pack(pady=5)

Button(root, text="Executar Exportação", command=lambda: copiar_arquivos(entrada_origem.get(), var_dry_run.get(), log_text)).pack(pady=10)

Label(root, text="Log de Execução:").pack()

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

log_text = Text(root, height=10, width=70, yscrollcommand=scrollbar.set)
log_text.pack()
scrollbar.config(command=log_text.yview)

root.mainloop()
