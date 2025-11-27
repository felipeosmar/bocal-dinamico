"""
Utilitários para comunicação serial.

Este módulo fornece funções para detecção e gerenciamento de portas seriais.
"""

import sys
import glob
import serial
from typing import List


def listar_portas_seriais() -> List[str]:
    """
    Detecta e retorna uma lista de portas seriais disponíveis no sistema.

    Returns:
        Lista de strings com os nomes das portas seriais disponíveis.

    Raises:
        EnvironmentError: Se a plataforma não for suportada.
    """
    if sys.platform.startswith('win'):
        portas_candidatas = [f'COM{i + 1}' for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        portas_candidatas = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        portas_candidatas = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Plataforma não suportada')

    portas_disponiveis = []
    for porta in portas_candidatas:
        try:
            conexao = serial.Serial(porta)
            conexao.close()
            portas_disponiveis.append(porta)
        except (OSError, serial.SerialException):
            pass

    return portas_disponiveis


def validar_porta(porta: str, portas_disponiveis: List[str]) -> bool:
    """
    Valida se uma porta está na lista de portas disponíveis.

    Args:
        porta: Nome da porta a ser validada.
        portas_disponiveis: Lista de portas disponíveis.

    Returns:
        True se a porta é válida, False caso contrário.
    """
    return porta in portas_disponiveis
