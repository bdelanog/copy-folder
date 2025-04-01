import os
import shutil
import logging
import uuid
from datetime import datetime
from tkinter import (
    Tk, Label, Button, Entry, Checkbutton, IntVar, Text, filedialog,
    END, Scrollbar, RIGHT, Y, messagebox, DISABLED, NORMAL
)

# --- Configurações fixas ---
EXTENSOES_VALIDAS = ('.txt', '.sql', '.pdf', '.rtf')
LOGFILE = 'programa/logs.log'

# --- Inicializa o logger ---
os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
logging.basicConfig(filename=LOGFILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Funções auxiliares ---
def escrever_log(widget, mensagem):
    widget.config(state=NORMAL)
    widget.insert(END, mensagem)
    widget.see(END)
    widget.config(state=DISABLED)

def logar(widget, mensagem, level="info"):
    if level == "info":
        logging.info(mensagem)
    elif level == "aviso":
        logging.warning(mensagem)
    elif level == "error":
        logging.error(mensagem)
    escrever_log(widget, f"{mensagem}\n")

def validar_pastas(origem, destino, log_widget):
    if not origem or not destino:
        messagebox.showerror("Erro", "Por favor, selecione a pasta de origem e a pasta de destino.")
        return False
    if os.path.abspath(origem) == os.path.abspath(destino):
        messagebox.showerror("Erro", "A pasta de origem e destino não podem ser iguais.")
        return False
    if not os.path.exists(origem):
        msg = f"[ERRO] Pasta de origem não encontrada: {origem}"
        logar(log_widget, msg, "error")
        return False
    try:
        os.makedirs(destino, exist_ok=True)
    except Exception as e:
        msg = f"[ERRO] Ao criar pasta de destino: {e}"
        logar(log_widget, msg, "error")
        return False
    return True

def copiar_arquivo(entry, destino, dry_run, log_widget):
    nome_arquivo = entry.name
    caminho_origem = entry.path
    caminho_destino = os.path.join(destino, nome_arquivo)

    try:
        with open(caminho_origem, 'rb'):
            pass
    except Exception as e:
        logar(log_widget, f"Arquivo não pode ser lido: {nome_arquivo}. Erro: {e}", "warning")
        return "ignorado"

    if os.path.exists(caminho_destino):
        if os.stat(caminho_origem).st_size == os.stat(caminho_destino).st_size:
            logar(log_widget, f"Arquivo ignorado (duplicado): {nome_arquivo}")
            return "ignorado"
        else:
            base, ext = os.path.splitext(nome_arquivo)
            novo_nome = f"{base}_{uuid.uuid4().hex[:6]}{ext}"
            caminho_destino = os.path.join(destino, novo_nome)
            logar(log_widget, f"Arquivo existente: {nome_arquivo}. Renomeado para: {novo_nome}", "warning")

    if dry_run:
        logar(log_widget, f"[DRY-RUN] Simulando cópia: {nome_arquivo}")
        return "simulado"
    else:
        try:
            shutil.copy2(caminho_origem, caminho_destino)
            logar(log_widget, f"[OK] Arquivo copiado: {nome_arquivo}")
            return "copiado"
        except Exception as e:
            logar(log_widget, f"[ERRO] Falha ao copiar {nome_arquivo}: {e}", "error")
            return "erro"

# --- Função principal de cópia ---
def copiar_arquivos(origem, destino, dry_run, log_widget):
    log_widget.config(state=NORMAL)
    log_widget.delete(1.0, END)

    if not validar_pastas(origem, destino, log_widget):
        log_widget.config(state=DISABLED)
        return

    copiados = 0
    ignorados = 0
    erros = 0
    simulados = 0

    with os.scandir(origem) as arquivos:
        for entry in arquivos:
            if not entry.name.lower().endswith(EXTENSOES_VALIDAS):
                continue
            if not entry.is_file():
                continue

            resultado = copiar_arquivo(entry, destino, dry_run, log_widget)
            if resultado == "copiado":
                copiados += 1
            elif resultado == "ignorado":
                ignorados += 1
            elif resultado == "simulado":
                simulados += 1
            elif resultado == "erro":
                erros += 1

    resumo = (
        f"\nResumo da exportação ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n"
        f"- Arquivos copiados: {copiados}\n"
        f"- Simulados (dry-run): {simulados}\n"
        f"- Ignorados (duplicados ou sem permissão): {ignorados}\n"
        f"- Erros: {erros}\n"
    )
    logar(log_widget, resumo)

# --- Função de seleção de pasta ---
def selecionar_pasta(entry_widget):
    pasta = filedialog.askdirectory()
    if pasta:
        entry_widget.delete(0, END)
        entry_widget.insert(0, pasta)

# --- Interface Tkinter ---
root = Tk()
root.title("Exportador de Arquivos")
root.geometry("500x550")

Label(root, text="Pasta de Origem:").pack()
entrada_origem = Entry(root, width=50)
entrada_origem.pack(pady=(0, 5))
Button(root, text="Selecionar Pasta", command=lambda: selecionar_pasta(entrada_origem)).pack()

Label(root, text="Pasta de Destino:").pack(pady=(10, 0))
entrada_destino = Entry(root, width=50)
entrada_destino.pack(pady=(0, 5))
Button(root, text="Selecionar Pasta", command=lambda: selecionar_pasta(entrada_destino)).pack()

var_dry_run = IntVar()
Checkbutton(root, text="Modo Simulação (Dry-Run)", variable=var_dry_run).pack(pady=5)

log_label = Label(root, text="Log de Execução:")
log_label.pack()

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

log_text = Text(root, height=15, width=90, yscrollcommand=scrollbar.set, wrap="none")
log_text.pack(padx=10, pady=10)
log_text.config(state=DISABLED)
scrollbar.config(command=log_text.yview)

executar_btn = Button(
    root,
    text="Executar Exportação",
    command=lambda: copiar_arquivos(
        entrada_origem.get(),
        entrada_destino.get(),
        var_dry_run.get(),
        log_text
    )
)
executar_btn.pack(pady=10)

root.mainloop()
