#!/usr/bin/env python3
"""
Bocal Dinâmico - Ponto de entrada da aplicação.

Sistema de controle de motores para posicionamento preciso de bocal e lentes.
"""

from src.serial_utils import listar_portas_seriais
from src.gui.main_window import MainWindow


def main():
    """Função principal da aplicação."""
    # Detecta portas seriais disponíveis
    portas = listar_portas_seriais()
    print(f"Portas seriais disponíveis: {portas}")

    # Cria e executa a janela principal
    app = MainWindow(portas)
    app.executar()


if __name__ == "__main__":
    main()
