import os
import shutil

# Caminhos da origem e destino
origem = 'para/pasta_origem'
destino = 'para/pasta_destino'

# Cria o destino se não existir
os.makedirs(destino, exist_ok=True)

# Loop para copiar apenas arquivos .txt
for arquivo in os.listdir(origem):
    if arquivo.endswith(('.txt','.sql')):
        caminho_origem = os.path.join(origem, arquivo)
        caminho_destino = os.path.join(destino, arquivo)
        shutil.copy2(caminho_origem, caminho_destino) # caso seja para mover ao inves de copiar == shutil.move

print("Arquivos .txt copiados com sucesso!")
