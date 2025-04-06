# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from gui.main_window import MainWindow
from utils.config import Config

def main():
    """Função principal do sistema"""

    os.makedirs('data', exist_ok=True)
    os.makedirs('relatorios', exist_ok=True)
    
    config = Config()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Inventário Rotativo de Ativos")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()