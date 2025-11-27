"""
Módulo de alertas e diálogos da interface gráfica.

Este módulo contém funções para exibir alertas e mensagens ao usuário.
"""

import customtkinter as ctk
from src.config import GUI_CONFIG


def exibir_alerta(parent: ctk.CTk, titulo: str, mensagem: str):
    """
    Exibe um alerta modal genérico.

    Args:
        parent: Janela pai.
        titulo: Título do alerta.
        mensagem: Mensagem a ser exibida.
    """
    alerta = ctk.CTkToplevel(parent)
    alerta.title(titulo)
    alerta.geometry("300x150")
    alerta.grab_set()

    label = ctk.CTkLabel(
        alerta,
        text=mensagem,
        font=(GUI_CONFIG.FONT_FAMILY, GUI_CONFIG.FONT_SIZE),
        text_color="Black"
    )
    label.pack(pady=20)

    btn_ok = ctk.CTkButton(
        alerta,
        text="OK",
        command=alerta.destroy,
        font=(GUI_CONFIG.FONT_FAMILY, GUI_CONFIG.FONT_SIZE),
        text_color="Black"
    )
    btn_ok.pack(pady=10)


def exibir_alerta_fim_de_curso_bocal(parent: ctk.CTk):
    """Exibe alerta de fim de curso do bocal dinâmico."""
    exibir_alerta(parent, "Alerta", "Fim de curso do Bocal Dinâmico")


def exibir_alerta_conexao_sucesso(parent: ctk.CTk):
    """Exibe alerta de conexão bem-sucedida."""
    exibir_alerta(parent, "Conectado", "Bocal Dinâmico conectado")


def exibir_alerta_erro(parent: ctk.CTk, mensagem: str):
    """
    Exibe alerta de erro.

    Args:
        parent: Janela pai.
        mensagem: Mensagem de erro.
    """
    exibir_alerta(parent, "Erro", mensagem)
