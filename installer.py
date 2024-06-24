import subprocess
import sys
import os

# Instalar dependencias
def install_dependencies():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

# Ejecutar el script principal
def run_main_script():
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'main.py')
        subprocess.check_call([sys.executable, script_path])
    except subprocess.CalledProcessError as e:
        print(f"Error running main script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()
    run_main_script()