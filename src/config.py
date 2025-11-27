"""
Configurações e constantes do sistema Bocal Dinâmico.

Este módulo centraliza todas as configurações dos motores MightyZap
e da interface gráfica.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class MightyZapConfig:
    """Configurações dos motores MightyZap (Bocal)."""

    # IDs dos 3 motores
    MOTOR_IDS: Tuple[int, int, int] = (0, 1, 2)
    BAUD_RATE: int = 57600

    # Conversão de unidades
    CONVERSAO_MM_PARA_POSICAO: float = 136.518518519  # 3686/27 [MM^-1]

    # Posição inicial (offset)
    OFFSET_POSICAO_MM: float = 7.0

    # Limites de movimentação em mm
    UPPER_MM: float = 1.01
    LOWER_MM: float = -2.01

    # Velocidade máxima em unidades internas
    MAX_VELOCIDADE: int = 1024

    # Velocidade inicial para homing
    VELOCIDADE_HOMING: int = 64

    @property
    def limite_inferior(self) -> int:
        """Limite inferior em unidades internas."""
        return int(round(
            (self.OFFSET_POSICAO_MM + self.LOWER_MM) * self.CONVERSAO_MM_PARA_POSICAO
        ))

    @property
    def limite_superior(self) -> int:
        """Limite superior em unidades internas."""
        return int(round(
            (self.OFFSET_POSICAO_MM + self.UPPER_MM) * self.CONVERSAO_MM_PARA_POSICAO
        ))

    @property
    def offset_posicao(self) -> int:
        """Posição de offset em unidades internas."""
        return int(round(self.OFFSET_POSICAO_MM * self.CONVERSAO_MM_PARA_POSICAO))


@dataclass(frozen=True)
class GUIConfig:
    """Configurações da interface gráfica."""

    WINDOW_TITLE: str = "Bocal Dinâmico"
    WINDOW_WIDTH: int = 900
    WINDOW_HEIGHT: int = 350
    RESIZABLE: bool = False
    APPEARANCE_MODE: str = "light"

    # Dimensões de widgets
    LARGURA_FIXA: int = 300
    LARGURA_LABEL: int = 250
    LARGURA_BOTAO: int = 230

    # Estilo
    CORNER_RADIUS: int = 10
    ESPACAMENTO_VERTICAL: int = 5
    FONT_FAMILY: str = "Helvetica"
    FONT_SIZE: int = 18
    FONT_SIZE_SMALL: int = 16

    # Cores dos frames
    COR_FRAME_CONEXAO: str = "AntiqueWhite1"
    COR_FRAME_BOCAL: str = "steel blue"
    COR_FRAME_FEEDBACK: str = "PaleGreen1"

    # Cores dos botões
    COR_BTN_CONEXAO: str = "AntiqueWhite3"
    COR_BTN_BOCAL: str = "Navy"

    # Intervalo de atualização do feedback (ms)
    INTERVALO_ATUALIZACAO: int = 200


# Instâncias globais das configurações
MIGHTYZAP_CONFIG = MightyZapConfig()
GUI_CONFIG = GUIConfig()
