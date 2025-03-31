import os
import shutil
import logging
from datetime import datetime
import uuid

# --- Configurações ---
origem = 'programa/para/pasta_origem'
destino = 'programa/para/pasta_destino'
logfile = 'programa/para/logs.log'
dry_run = True # True para simular sem copiar
"""
DRY RUN :

O script verifica os arquivos como se fosse copiar.

Registra no log e mostra no terminal o que faria.

Não copia nenhum arquivo de fato para a pasta destino.

"""

# --- Garantir que a pasta do log existe ---
os.makedirs(os.path.dirname(logfile), exist_ok=True)

# --- Configurar logging ---
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Criação da pasta de destino ---
try:
    os.makedirs(destino, exist_ok=True)
except Exception as e:
    logging.error(f'Erro ao criar pasta destino: {e}')
    print("Erro ao criar a pasta de destino.")
    exit(1)

# --- Contadores ---
copiados = 0
ignorados = 0
erros = 0

# --- Loop de cópia ---
try:
    arquivos = os.listdir(origem)
except FileNotFoundError:
    logging.error(f'Pasta de origem não encontrada: {origem}')
    print(f"Erro: a pasta de origem '{origem}' não existe.")
    exit(1)

for arquivo in arquivos:
    if arquivo.lower().endswith(('.txt', '.sql','.pdf', '.rtf')):
        caminho_origem = os.path.join(origem, arquivo)
        caminho_destino = os.path.join(destino, arquivo)

        try:
            if not os.access(caminho_origem, os.R_OK):
                logging.warning(f"Sem permissão de leitura: {arquivo}")
                ignorados += 1
                continue

            if os.path.exists(caminho_destino):
                if os.stat(caminho_origem).st_size == os.stat(caminho_destino).st_size:
                    logging.info(f"Arquivo ignorado (duplicado): {arquivo}")
                    ignorados += 1
                    continue
                else:
                    base, ext = os.path.splitext(arquivo)
                    novo_nome = f"{base}_{uuid.uuid4().hex[:6]}{ext}"
                    caminho_destino = os.path.join(destino, novo_nome)
                    logging.warning(f'Arquivo existente: {arquivo}. Renomeado para: {novo_nome}')

            if dry_run:
                logging.info(f'[DRY-RUN] Simulando cópia de: {arquivo}')
            else:
                shutil.copy2(caminho_origem, caminho_destino)
                logging.info(f'Arquivo copiado: {arquivo}')
                copiados += 1

        except Exception as e:
            logging.error(f'Erro ao copiar {arquivo}: {e}')
            erros += 1

# --- Resumo ---
resumo = f"""
Resumo da exportação ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):
- Arquivos copiados: {copiados}
- Ignorados (duplicados ou sem permissão): {ignorados}
- Erros: {erros}
"""

print(resumo)
logging.info(resumo)
