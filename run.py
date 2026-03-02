import os
import subprocess
import sys
from pathlib import Path

VENV_DIR = Path(".venv")


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_venv():
    if not VENV_DIR.exists():
        print("🔧 Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])


def install_requirements(python: Path):
    marker = VENV_DIR / ".deps_installed"
    if marker.exists():
        return
    
    print("📦 Installing requirements...")
    subprocess.check_call([python, "-m", "pip", "install", "-r", "requirements.txt" ])
    marker.touch()


def run_app(python: Path):
    print("🚀 Running application...")
    #subprocess.check_call([ python, "cli.py", *sys.argv[1:] ])
    subprocess.check_call([python, "gui.py", *sys.argv[1:]])


def main():
    ensure_venv()
    python = venv_python()
    install_requirements(python)
    run_app(python)


if __name__ == "__main__":
    main()
