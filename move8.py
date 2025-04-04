import os
import shutil
import logging
import uuid
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, Checkbutton, IntVar, Text, filedialog, END, Scrollbar, RIGHT, Y, messagebox

# --- Configurações fixas ---
extensoes_validas = ('.txt', '.sql', '.pdf', '.rtf')
logfile = 'programa/logs.log'

# --- Inicializa o logger ---
os.makedirs(os.path.dirname(logfile), exist_ok=True)
logging.basicConfig(filename=logfile, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Função principal de cópia ---
def copiar_arquivos(origem, destino, dry_run, log_widget):
    if not origem or not destino:
        messagebox.showerror("Erro", "Por favor, selecione a pasta de origem/pasta de destino.")
        return

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
            if not os.access(caminho_origem, os.R_OK):
                ignorados += 1
                logging.warning(f"Sem permissão de leitura: {arquivo}")
                continue

            if os.path.exists(caminho_destino):
                if os.stat(caminho_origem).st_size == os.stat(caminho_destino).st_size:
                    ignorados += 1
                    logging.info(f"Arquivo ignorado (duplicado): {arquivo}")
                    continue
                else:
                    base, ext = os.path.splitext(arquivo)
                    novo_nome = f"{base}_{uuid.uuid4().hex[:6]}{ext}"
                    caminho_destino = os.path.join(destino, novo_nome)
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

# --- Função de seleção de pasta ---
def selecionar_pasta(entry_widget):
    pasta = filedialog.askdirectory()
    if pasta:
        entry_widget.delete(0, END)
        entry_widget.insert(0, pasta)

# --- Interface Tkinter ---
root = Tk()
root.title("CC")
root.geometry("600x400")

Label(root, text="Pasta de Origem:").pack()
entrada_origem = Entry(root, width=50)
entrada_origem.pack()
Button(root, text="Selecionar Pasta", command=lambda: selecionar_pasta(entrada_origem)).pack()

Label(root, text="Pasta de Destino:").pack(pady=(10, 0))
entrada_destino = Entry(root, width=50)
entrada_destino.pack()
Button(root, text="Selecionar Pasta", command=lambda: selecionar_pasta(entrada_destino)).pack()

var_dry_run = IntVar()
Checkbutton(root, text="Modo Simulação (Dry-Run)", variable=var_dry_run).pack(pady=5)

Button(root, text="Executar Exportação", command=lambda: copiar_arquivos(entrada_origem.get(), entrada_destino.get(), var_dry_run.get(), log_text)).pack(pady=10)

Label(root, text="Log de Execução:").pack()

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

log_text = Text(root, height=10, width=70, yscrollcommand=scrollbar.set)
log_text.pack()
scrollbar.config(command=log_text.yview)

root.mainloop()
