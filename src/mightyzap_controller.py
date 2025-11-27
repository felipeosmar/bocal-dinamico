"""
Controlador dos motores MightyZap (Bocal).

Este módulo encapsula toda a lógica de controle dos 3 atuadores lineares MightyZap.
"""

import time
from typing import Optional, Callable, Tuple
import lib.PythonLibMightyZap_FC as MightyZapLib
from src.config import MIGHTYZAP_CONFIG


class MightyZapController:
    """Controlador para os 3 motores MightyZap do bocal dinâmico."""

    def __init__(self, config=MIGHTYZAP_CONFIG):
        """
        Inicializa o controlador MightyZap.

        Args:
            config: Configurações do MightyZap (usa padrão se não especificado).
        """
        self.config = config
        self._conectado = False

    @property
    def conectado(self) -> bool:
        """Retorna True se os motores estão conectados."""
        return self._conectado

    @property
    def num_motores(self) -> int:
        """Retorna o número de motores configurados."""
        return len(self.config.MOTOR_IDS)

    def conectar(self, porta: str,
                 callback_sucesso: Optional[Callable] = None) -> bool:
        """
        Conecta aos motores MightyZap e realiza o procedimento de homing.

        Args:
            porta: Porta serial para conexão.
            callback_sucesso: Função a ser chamada após conexão bem-sucedida.

        Returns:
            True se a conexão foi bem-sucedida, False caso contrário.
        """
        try:
            print(f"Conectando a {porta}...")
            MightyZapLib.OpenMightyZap(porta, self.config.BAUD_RATE)
            time.sleep(0.1)

            # Define velocidade inicial para todos os motores
            for motor_id in self.config.MOTOR_IDS:
                MightyZapLib.GoalSpeed(motor_id, self.config.VELOCIDADE_HOMING)

            # Executa scan de homing
            self._executar_homing()

            self._conectado = True

            if callback_sucesso:
                callback_sucesso()

            return True

        except Exception as e:
            print(f"Erro ao conectar MightyZap: {e}")
            self._conectado = False
            return False

    def _executar_homing(self):
        """Executa o procedimento de homing dos 3 motores."""
        limite_inferior = self.config.limite_inferior
        limite_superior = self.config.limite_superior
        offset = self.config.offset_posicao

        # Scan do limite inferior ao superior
        for pos in range(limite_inferior, limite_superior + 1, 10):
            for motor_id in self.config.MOTOR_IDS:
                MightyZapLib.GoalPosition(motor_id, pos)
            time.sleep(0.05)

        # Retorno à posição de offset
        for pos in range(limite_superior, offset, -10):
            for motor_id in self.config.MOTOR_IDS:
                MightyZapLib.GoalPosition(motor_id, pos)
            time.sleep(0.05)

    def definir_velocidade(self, velocidade_percentual: float) -> int:
        """
        Define a velocidade dos motores em porcentagem.

        Args:
            velocidade_percentual: Velocidade de 0 a 100%.

        Returns:
            Velocidade em unidades internas.
        """
        # Limita a velocidade entre 0 e 100%
        velocidade_percentual = max(0, min(100, velocidade_percentual))

        speed = int((velocidade_percentual / 100) * self.config.MAX_VELOCIDADE)
        print(f"Definindo velocidade para {speed} ({velocidade_percentual}%)...")

        for motor_id in self.config.MOTOR_IDS:
            MightyZapLib.GoalSpeed(motor_id, speed)

        return speed

    def mover_para(self, posicao_mm: float, velocidade_percentual: float) -> bool:
        """
        Move os 3 motores para uma posição específica em mm.

        Args:
            posicao_mm: Posição desejada em mm (relativa ao offset).
            velocidade_percentual: Velocidade de 0 a 100%.

        Returns:
            True se o movimento foi iniciado, False se está fora dos limites.
        """
        # Verifica limites
        if posicao_mm > self.config.UPPER_MM or posicao_mm < self.config.LOWER_MM:
            return False

        # Define velocidade
        self.definir_velocidade(velocidade_percentual)

        # Converte para unidades internas
        position = (
            int(round(posicao_mm * self.config.CONVERSAO_MM_PARA_POSICAO))
            + self.config.offset_posicao
        )

        # Verifica limites internos
        if position < self.config.limite_inferior:
            print(f"Erro: posição {position} abaixo do limite inferior "
                  f"({self.config.limite_inferior})")
            return False

        if position > self.config.limite_superior:
            print(f"Erro: posição {position} acima do limite superior "
                  f"({self.config.limite_superior})")
            return False

        print(f"Movendo 3 motores para posição {position}...")
        for motor_id in self.config.MOTOR_IDS:
            MightyZapLib.GoalPosition(motor_id, position)

        return True

    def obter_posicao_atual(self, motor_index: int = 0) -> float:
        """
        Obtém a posição atual de um motor em mm.

        Args:
            motor_index: Índice do motor (0, 1 ou 2).

        Returns:
            Posição atual em mm (relativa ao offset).
        """
        if motor_index >= len(self.config.MOTOR_IDS):
            return 0.0

        motor_id = self.config.MOTOR_IDS[motor_index]
        pos_interna = (
            MightyZapLib.PresentPosition(motor_id) - self.config.offset_posicao
        )
        return pos_interna / self.config.CONVERSAO_MM_PARA_POSICAO

    def obter_posicoes(self) -> Tuple[float, float, float]:
        """
        Obtém as posições atuais dos 3 motores.

        Returns:
            Tupla com (posição_motor_1, posição_motor_2, posição_motor_3) em mm.
        """
        return (
            self.obter_posicao_atual(0),
            self.obter_posicao_atual(1),
            self.obter_posicao_atual(2)
        )
