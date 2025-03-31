import os
import shutil

origem = '/home/bruno/documentos/origem'
destino = '/home/bruno/documentos/destino'

for arquivo in os.listdir(origem):
    if arquivo.lower().endswith(('.txt', '.sql')):
        caminho_origem = os.path.join(origem, arquivo)
        caminho_destino = os.path.join(destino, arquivo)
        shutil.copy2(caminho_origem, caminho_destino)  # ou shutil.move para mover e não copiar
