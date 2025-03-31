#EXEMPLO

from ftplib import FTP

ftp = FTP('ip_do_as400')
ftp.login(user='usuario', passwd='senha')
ftp.cwd('/pasta/com/arquivos')

arquivos = ftp.nlst()
for arquivo in arquivos:
    if arquivo.lower().endswith(('.txt', '.sql')):
        with open(f'/home//destino/{arquivo}', 'wb') as f:
            ftp.retrbinary(f'RETR {arquivo}', f.write)

ftp.quit()
