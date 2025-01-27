import os
import time
import psutil
from colorama import Fore, init
from dotenv import load_dotenv
import ctypes


# Carrega o arquivo .env
load_dotenv()

caminho_bat_1 = os.getenv("CAMINHO_BAT_1")
caminho_arquivo_py_1 = os.getenv("CAMINHO_ARQUIVO_PY_1")
caminho_bat_2 = os.getenv("CAMINHO_BAT_2")
caminho_arquivo_py_2 = os.getenv("CAMINHO_ARQUIVO_PY_2")

ctypes.windll.kernel32.SetConsoleTitleW("Monitor do Jobs")

# Inicializa o colorama
init(autoreset=True)

def is_python_script_running(py_file_path):
    """
    Verifica se o script Python chamado pelo .bat está em execução.
    """
    py_file_name = os.path.basename(py_file_path).lower()
    for process in psutil.process_iter(attrs=['cmdline']):
        try:
            cmdline = process.info['cmdline']
            # Verifica se o nome do script Python está nos argumentos do processo
            if cmdline and any(py_file_name in os.path.basename(arg).lower() for arg in cmdline):
                return True  # O script Python já está em execução
        except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
            continue
    return False

def open_bat_file(bat_file_path):
    """
    Tenta abrir o arquivo .bat e retorna True se for bem-sucedido, False caso contrário.
    """
    if not os.path.exists(bat_file_path):
        print(Fore.RED + f"Erro: Arquivo .bat não encontrado: {bat_file_path}")
        return False

    print(f"Tentando abrir o arquivo .bat: {bat_file_path}")
    result = os.system(bat_file_path)  # Abre o arquivo .bat em um novo terminal
    if result == 0:  # Verifica se o comando foi bem-sucedido
        return True
    else:
        print(Fore.RED + f"Erro ao tentar abrir o arquivo .bat: {bat_file_path}")
        return False

def print_dynamic_status(bat_files, statuses):
    """
    Exibe uma animação e cores para os estados dinâmicos, usando o nome do arquivo .bat.
    """
    status_art = [
        "[■□□□□] Verificando...",
        "[■■□□□] Status Atualizando...",
        "[■■■□□] Processando...",
        "[■■■■□] Quase lá...",
        "[■■■■■] Concluído!"
    ]

    for frame in status_art:
        os.system('cls' if os.name == 'nt' else 'clear')  # Limpa a tela
        print(Fore.YELLOW + "=== MONITORANDO JOBS ===\n")
        for bat_file, status in zip(bat_files, statuses):
            color = Fore.GREEN if status == "EM EXECUÇÃO" else (Fore.YELLOW if status == "REABERTO" else Fore.RED)
            print(color + f"{frame} {os.path.basename(bat_file)}: {status}")
        time.sleep(0.5)

def monitor_py_files(bat_files_mapping):
    """
    Verifica o status de múltiplos scripts Python chamados pelos arquivos .bat.
    """
    statuses = []
    for bat_file, py_file in bat_files_mapping.items():
        # Verifica se o script Python está em execução
        is_running = is_python_script_running(py_file)

        if not is_running:
            # Tenta abrir o arquivo .bat novamente
            reaberto = open_bat_file(bat_file)
            if reaberto:
                statuses.append("REABERTO")
            else:
                statuses.append("ERRO AO ABRIR")
        else:
            statuses.append("EM EXECUÇÃO")

    print_dynamic_status(list(bat_files_mapping.keys()), statuses)

# Mapeamento de arquivos .bat para os scripts Python que eles chamam
bat_files_mapping = {
    caminho_bat_1 : caminho_arquivo_py_1,
    caminho_bat_2 : caminho_arquivo_py_2,
}

while True:
    monitor_py_files(bat_files_mapping)
    time.sleep(600)  # Verifica a cada 10 minutos
