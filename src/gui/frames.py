"""
Módulo de frames da interface gráfica.

Este módulo contém as classes de frames que compõem a interface.
"""

import customtkinter as ctk
from typing import List, Callable, Optional
from src.config import GUI_CONFIG


class FrameConexao(ctk.CTkFrame):
    """Frame para configuração de conexão da porta serial."""

    def __init__(self, parent: ctk.CTk, portas_disponiveis: List[str],
                 comando_conectar: Callable):
        """
        Inicializa o frame de conexão.

        Args:
            parent: Widget pai.
            portas_disponiveis: Lista de portas seriais disponíveis.
            comando_conectar: Função a ser chamada ao clicar em conectar.
        """
        super().__init__(
            parent,
            fg_color=GUI_CONFIG.COR_FRAME_CONEXAO,
            corner_radius=GUI_CONFIG.CORNER_RADIUS,
            border_width=1,
            border_color="Black"
        )

        self._criar_widgets(portas_disponiveis, comando_conectar)

    def _criar_widgets(self, portas: List[str], comando_conectar: Callable):
        """Cria os widgets do frame."""
        font = (GUI_CONFIG.FONT_FAMILY, GUI_CONFIG.FONT_SIZE)
        cr = GUI_CONFIG.CORNER_RADIUS
        esp = GUI_CONFIG.ESPACAMENTO_VERTICAL

        # Bocal Dinâmico (MightyZap - 3 motores)
        ctk.CTkLabel(
            self, text="Conexão: Bocal Dinâmico (3 motores)",
            font=font, text_color="Black",
            corner_radius=cr, width=GUI_CONFIG.LARGURA_LABEL
        ).grid(row=0, column=0, padx=10, pady=esp, sticky="w")

        self.porta_bocal = ctk.StringVar(value="Selecione a Porta Serial")
        ctk.CTkOptionMenu(
            self, values=portas, variable=self.porta_bocal,
            font=font, text_color="White", fg_color="Navy",
            width=GUI_CONFIG.LARGURA_FIXA, corner_radius=cr
        ).grid(row=0, column=1, padx=10, pady=esp, sticky="w")

        # Botão Conectar
        ctk.CTkButton(
            self, text="Conectar Bocal Dinâmico",
            command=comando_conectar,
            width=GUI_CONFIG.LARGURA_BOTAO, height=50,
            font=font, fg_color=GUI_CONFIG.COR_BTN_CONEXAO,
            text_color="Black", corner_radius=cr,
            border_color="Black", border_width=1
        ).grid(row=0, column=2, padx=10, pady=esp, sticky="w")

    def obter_porta(self) -> str:
        """Retorna a porta selecionada."""
        return self.porta_bocal.get()


class FrameControleBocal(ctk.CTkFrame):
    """Frame para controle dos 3 motores do bocal (MightyZap)."""

    def __init__(self, parent: ctk.CTk, comando_mover: Callable):
        """
        Inicializa o frame de controle do bocal.

        Args:
            parent: Widget pai.
            comando_mover: Função a ser chamada ao clicar em posicionar.
        """
        super().__init__(
            parent,
            fg_color=GUI_CONFIG.COR_FRAME_BOCAL,
            corner_radius=GUI_CONFIG.CORNER_RADIUS,
            border_color="Black",
            border_width=1
        )

        self._criar_widgets(comando_mover)

    def _criar_widgets(self, comando_mover: Callable):
        """Cria os widgets do frame."""
        font = (GUI_CONFIG.FONT_FAMILY, GUI_CONFIG.FONT_SIZE)
        cr = GUI_CONFIG.CORNER_RADIUS
        esp = GUI_CONFIG.ESPACAMENTO_VERTICAL

        # Posição
        ctk.CTkLabel(
            self, text="Posição: Bocal (mm):",
            font=font, text_color="White",
            corner_radius=cr, width=GUI_CONFIG.LARGURA_LABEL
        ).grid(row=0, column=0, padx=10, pady=esp, sticky="w")

        self.entry_posicao = ctk.CTkEntry(
            self, width=GUI_CONFIG.LARGURA_FIXA,
            font=font, corner_radius=cr,
            border_width=1, border_color="black"
        )
        self.entry_posicao.grid(row=0, column=1, padx=10, pady=esp, sticky="w")

        # Velocidade
        ctk.CTkLabel(
            self, text="Velocidade: Bocal (%):",
            font=font, text_color="White",
            corner_radius=cr, width=GUI_CONFIG.LARGURA_LABEL
        ).grid(row=1, column=0, padx=10, pady=esp, sticky="w")

        self.entry_velocidade = ctk.CTkEntry(
            self, width=GUI_CONFIG.LARGURA_FIXA,
            font=font, corner_radius=cr,
            border_width=1, border_color="black"
        )
        self.entry_velocidade.grid(row=1, column=1, padx=10, pady=esp, sticky="w")

        # Botão Posicionar
        ctk.CTkButton(
            self, text="Posicionar Bocal",
            command=comando_mover,
            font=font, fg_color=GUI_CONFIG.COR_BTN_BOCAL,
            text_color="White", height=80,
            width=GUI_CONFIG.LARGURA_BOTAO, corner_radius=cr,
            border_color="Black", border_width=1
        ).grid(row=0, column=2, columnspan=2, rowspan=2,
               padx=10, pady=esp, sticky="w")

    def obter_valores(self) -> tuple[Optional[float], Optional[float]]:
        """
        Retorna os valores de posição e velocidade.

        Returns:
            Tupla (posição, velocidade) ou (None, None) se inválidos.
        """
        try:
            posicao = float(self.entry_posicao.get())
            velocidade = float(self.entry_velocidade.get())
            return (posicao, velocidade)
        except ValueError:
            return (None, None)


class FrameFeedback(ctk.CTkFrame):
    """Frame para exibição de feedback de posição dos 3 motores."""

    def __init__(self, parent: ctk.CTk):
        """
        Inicializa o frame de feedback.

        Args:
            parent: Widget pai.
        """
        super().__init__(
            parent,
            fg_color=GUI_CONFIG.COR_FRAME_FEEDBACK,
            corner_radius=GUI_CONFIG.CORNER_RADIUS,
            border_color="Black",
            border_width=1
        )

        self._criar_widgets()

    def _criar_widgets(self):
        """Cria os widgets do frame."""
        font = (GUI_CONFIG.FONT_FAMILY, GUI_CONFIG.FONT_SIZE_SMALL)
        esp = GUI_CONFIG.ESPACAMENTO_VERTICAL

        # Posição dos 3 motores MightyZap
        self.var_posicao_bocal = ctk.StringVar(
            value="Bocal: M1 = 0.000 mm | M2 = 0.000 mm | M3 = 0.000 mm"
        )
        ctk.CTkLabel(
            self, textvariable=self.var_posicao_bocal,
            font=font, width=600
        ).grid(row=0, column=0, padx=10, pady=esp, sticky="w")

    def atualizar_posicao_bocal(self, pos_1: float, pos_2: float, pos_3: float):
        """Atualiza a exibição da posição dos 3 motores do bocal."""
        self.var_posicao_bocal.set(
            f"Bocal: M1 = {pos_1:.3f} mm | M2 = {pos_2:.3f} mm | M3 = {pos_3:.3f} mm"
        )
