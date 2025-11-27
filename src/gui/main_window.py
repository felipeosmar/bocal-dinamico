"""
Janela principal da aplicação Bocal Dinâmico.

Este módulo contém a classe principal que gerencia a interface gráfica
e coordena o controlador dos motores MightyZap.
"""

import customtkinter as ctk
from typing import List

from src.config import GUI_CONFIG
from src.serial_utils import validar_porta
from src.mightyzap_controller import MightyZapController
from src.gui.frames import (
    FrameConexao,
    FrameControleBocal,
    FrameFeedback
)
from src.gui.alerts import (
    exibir_alerta_fim_de_curso_bocal,
    exibir_alerta_conexao_sucesso,
    exibir_alerta_erro
)


class MainWindow:
    """Janela principal da aplicação Bocal Dinâmico."""

    def __init__(self, portas_disponiveis: List[str]):
        """
        Inicializa a janela principal.

        Args:
            portas_disponiveis: Lista de portas seriais disponíveis.
        """
        self.portas_disponiveis = portas_disponiveis

        # Controlador dos motores
        self.mightyzap = MightyZapController()

        # Configuração da janela
        self._criar_janela()
        self._criar_frames()
        self._iniciar_atualizacao_posicoes()

    def _criar_janela(self):
        """Configura a janela principal."""
        self.root = ctk.CTk()
        self.root.title(GUI_CONFIG.WINDOW_TITLE)
        self.root.geometry(f"{GUI_CONFIG.WINDOW_WIDTH}x{GUI_CONFIG.WINDOW_HEIGHT}")
        self.root.resizable(GUI_CONFIG.RESIZABLE, GUI_CONFIG.RESIZABLE)
        ctk.set_appearance_mode(GUI_CONFIG.APPEARANCE_MODE)

        # Configura o grid
        for i in range(3):
            self.root.grid_rowconfigure(i, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _criar_frames(self):
        """Cria e posiciona os frames na janela."""
        # Frame de Conexão
        self.frame_conexao = FrameConexao(
            self.root,
            self.portas_disponiveis,
            self._conectar
        )
        self.frame_conexao.grid(
            row=0, column=0,
            padx=10, pady=10, sticky="nsew"
        )

        # Frame de Controle do Bocal
        self.frame_bocal = FrameControleBocal(
            self.root,
            self._mover_bocal
        )
        self.frame_bocal.grid(
            row=1, column=0,
            padx=10, pady=10, sticky="nsew"
        )

        # Frame de Feedback
        self.frame_feedback = FrameFeedback(self.root)
        self.frame_feedback.grid(
            row=2, column=0,
            padx=10, pady=10, sticky="nsew"
        )

    def _conectar(self):
        """Conecta aos 3 motores MightyZap."""
        porta_bocal = self.frame_conexao.obter_porta()

        # Valida a porta
        if not validar_porta(porta_bocal, self.portas_disponiveis):
            exibir_alerta_erro(self.root, "Porta inválida ou não selecionada")
            return

        # Conecta MightyZap
        sucesso = self.mightyzap.conectar(
            porta_bocal,
            callback_sucesso=lambda: exibir_alerta_conexao_sucesso(self.root)
        )

        if not sucesso:
            exibir_alerta_erro(self.root, "Erro ao conectar aos motores")

    def _mover_bocal(self):
        """Move os 3 motores do bocal."""
        posicao, velocidade = self.frame_bocal.obter_valores()

        if posicao is None or velocidade is None:
            print("Erro: Insira valores numéricos válidos.")
            return

        sucesso = self.mightyzap.mover_para(posicao, velocidade)
        if not sucesso:
            exibir_alerta_fim_de_curso_bocal(self.root)

    def _iniciar_atualizacao_posicoes(self):
        """Inicia o loop de atualização das posições na interface."""
        self._atualizar_posicoes()

    def _atualizar_posicoes(self):
        """Atualiza as posições exibidas na interface."""
        if self.mightyzap.conectado:
            pos_1, pos_2, pos_3 = self.mightyzap.obter_posicoes()
            self.frame_feedback.atualizar_posicao_bocal(pos_1, pos_2, pos_3)

        # Agenda próxima atualização
        self.root.after(
            GUI_CONFIG.INTERVALO_ATUALIZACAO,
            self._atualizar_posicoes
        )

    def executar(self):
        """Inicia o loop principal da interface."""
        self.root.mainloop()
