from Xeryon import *
import threading
import time
import customtkinter as ctk
import PythonLibMightyZap_FC
import sys
import serial
import glob

# --------------------------------------------------------------------------------------------
# ------------------------------ CONFIGURAÇÃO MIGHTYZAP (BOCAL) ------------------------------
# --------------------------------------------------------------------------------------------

MightyZap = PythonLibMightyZap_FC                                                                                               # CHAMA A BIBLIOTECA MIGHTYZAP
Actuator_ID = 0                                                                                                                 # ID DO MOTOR MIGHTYZAP (BOCAL) 1
Actuator_ID_1 = 2                                                                                                               # ID DO MOTOR MIGHTYZAP (BOCAL) 2
CONVERSAO_MM_PARA_POSICAO = 136.518518519                                                                                       # CONVERSÃO DE MM PARA INTEIRO 3686/27 [MM^-1]
OFFSET_POSICAO_MM_MIGHTYZAP = 7.                                                                                                # POSIÇÃO INICIAL DO MOTOR MIGHTYZAP [MM]
UPPER_MIGHTYZAP_MM = 1.01                                                                                                       # LIMITE SUPERIOR DE MOVIMENTAÇÃO DO BOCAL [MM]
LOWER_MIGHTYZAP_MM = -2.01                                                                                                      # LIMITE INFERIOR DE MOVIMENTAÇÃO DO BOCAL [MM] 
LIMITE_INFERIOR_MIGHTYZAP = int(round((OFFSET_POSICAO_MM_MIGHTYZAP + LOWER_MIGHTYZAP_MM) * CONVERSAO_MM_PARA_POSICAO))          # LIMITE INFERIOR DE MOVIMENTAÇÃO DO MOTOR MIGHTYZAP EM INTEIROS
LIMITE_SUPERIOR_MIGHTYZAP = int(round((OFFSET_POSICAO_MM_MIGHTYZAP + UPPER_MIGHTYZAP_MM) * CONVERSAO_MM_PARA_POSICAO))          # LIMITE SUPERIOR DE MOVIMENTAÇÃO DO MOTOR MIGHTYZAP EM INTEIROS
OFFSET_POSICAO_MIGHTYZAP = int(round(OFFSET_POSICAO_MM_MIGHTYZAP * CONVERSAO_MM_PARA_POSICAO))                                  # POSIÇÃO INICIAL DO MOTOR MIGHTYZAP EM INTEIROS
MAX_VELOCIDADE_MIGTHYZAP = 1024                                                                                                 # VELOCIDADE MÁXIMA DO MOTOR MIGHTYZAP EM INTEIROS   

# --------------------------------------------------------------------------------------------
# ------------------------------- CONFIGURAÇÃO XERYON (LENTES) -------------------------------
# --------------------------------------------------------------------------------------------

OFFSET_XERYON_MM = 6.                                                   # POSIÇÃO INICIAL DOS MOTORES DA LENTE (XERYON)                                                                                                     
UPPER_XERYON_MM = 2.                                                    # LIMITE SUPERIOR DE MOVIMENTAÇÃO DOS MOTORES DA LENTE (XERYON) [MM]
LOWER_XERYON_MM = -8.                                                   # LIMITE INFERIOR DE MOVIMENTAÇÃO DOS MOTORES DA LENTE (XERYON) [MM]
LIMITE_INFERIOR_XERYON = OFFSET_XERYON_MM + LOWER_XERYON_MM             # LIMITE INFERIOR DE MOVIMENTAÇÃO DOS MOTORES DA LENTE (XERYON) EM INTEIROS 
LIMITE_SUPERIOR_XERYON = OFFSET_XERYON_MM + UPPER_XERYON_MM             # LIMITE SUPERIOR DE MOVIMENTAÇÃO DOS MOTORES DA LENTE (XERYON) EM INTEIROS
MAX_VELOCIDADE_XERYON = 400                                             # VELOCIDADE MÁXIMA DOS MOTORES DA LENTE (XERYON) EM MM/S   
controllerX = None                                                      # CRIA O CONTROLADOR DO MOTOR XERYON 1
controllerY = None                                                      # CRIA O CONTROLADOR DO MOTOR XERYON 2
axisX = None                                                            # CRIA O EIXO DO MOTOR XERYON 1
axisY = None                                                            # CRIA O EIXO DO MOTOR XERYON 2

# --------------------------------------------------------------------------------------------
# ------------------------ FUNÇÃO PARA IDENTIFICAR AS PORTAS SERIAIS -------------------------
# --------------------------------------------------------------------------------------------

def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

PortalSerialConectadas = serial_ports()                             # ATRIBUI A VARIÁVEL O NOME DAS PORTAS SERIAIS

# --------------------------------------------------------------------------------------------
# ---------------------- FUNÇÃO PARA INICIAR OS MOTORES XERYON (LENTE) -----------------------
# --------------------------------------------------------------------------------------------

def iniciar_motores():
    global controllerX, controllerY, axisX, axisY                   # CHAMA AS VARIÁVEIS GLOBAIS
    controllerX = Xeryon(porta_x.get(), 115200)                     # ATRIBUI AO CONTROLADOR 1 A PORTA SELECIONADA NA INTERFACE GRÁFICA
    controllerY = Xeryon(porta_y.get(), 115200)                     # ATRIBUI AO CONTROLADOR 2 A PORTA SELECIONADA NA INTERFACE GRÁFICA
    axisX = controllerX.addAxis(Stage.XLS_1250, "X")                # CRIA O EIXO 1 NO CONTROLADOR
    axisY = controllerY.addAxis(Stage.XLS_1250, "Y")                # CRIA O EIXO 2 NO CONTROLADOR
    controllerX.start()                                             # INICIA A COMUNICAÇÃO DO CONTROLADOR DO EIXO 1
    controllerY.start()                                             # INICIA A COMUNICAÇÃO DO CONTROLADOR DO EIXO 2
    axisX.setPTOL(2)
    axisY.setPTOL(2)
    axisX.setPTO2(4)
    axisY.setPTO2(4)
    thread_x = threading.Thread(target=axisX.findIndex)             # DEFINE A PARALELIZAÇÃO DO ZERAMENTO DO MOTOR XERYON 1
    thread_y = threading.Thread(target=axisY.findIndex)             # DEFINE A PARALELIZAÇÃO DO ZERAMENTO DO MOTOR XERYON 2
    thread_x.start()                                                # INICIA A PARALELIZAÇÃO DO ZERAMENTO DO MOTOR XERYON 2
    thread_y.start()                                                # INICIA A PARALELIZAÇÃO DO ZERAMENTO DO MOTOR XERYON 2
    thread_x.join()                                                 # SINCRONIZA O ZERAMENTO DO MOTOR XERYON 1
    thread_y.join()                                                 # SINCRONIZA O ZERAMENTO DO MOTOR XERYON 2
    axisX.reset()                                                   # RESETA O EIXO DO MOTOR 1 PARA EVITAR ERRO DE SOBRECARGA TÉRMICA
    axisY.reset()                                                   # RESETA O EIXO DO MOTOR 2 PARA EVITAR ERRO DE SOBRECARGA TÉRMICA
    axisX.setUnits(Units.mm)                                        # DEFINE A UNIDADE DO MOTOR 1 PARA O CONJUNTO [MM] E [MM/S]
    axisY.setUnits(Units.mm)                                        # DEFINE A UNIDADE DO MOTOR 2 PARA O CONJUNTO [MM] E [MM/S]

    # Mover os motores Xeryon para a posição de offset
    def mover_eixo_x():
        axisX.setSpeed(20)
        axisX.setDPOS(OFFSET_XERYON_MM)


    def mover_eixo_y():
        axisY.setSpeed(20)
        axisY.setDPOS(OFFSET_XERYON_MM)


    thread_move_x = threading.Thread(target=mover_eixo_x)
    thread_move_y = threading.Thread(target=mover_eixo_y)
    thread_move_x.start()
    thread_move_y.start()
    thread_move_x.join()
    thread_move_y.join()

    print(f"Posição de offset de {OFFSET_XERYON_MM} mm alcançada.") 

# --------------------------------------------------------------------------------------------
# ----------------------- FUNÇÃO PARA MOVER OS MOTORES XERYON (LENTE) ------------------------
# --------------------------------------------------------------------------------------------

# ALERTA DE FIM DE CURSO DA LENTE
def exibir_alerta_fim_de_curso_lente():
    alerta = ctk.CTkToplevel(root)
    alerta.title("Alerta")
    alerta.geometry("300x150")
    alerta.grab_set()
    LabelAlerta = ctk.CTkLabel(alerta, 
                               text="Fim de curso da lente", 
                               font=("Helvetica", 18),
                               text_color="Black")
    LabelAlerta.pack(pady=20)
    btnOK = ctk.CTkButton(alerta, 
                          text="OK", 
                          command=alerta.destroy,
                          font = ("Helvetica", 18),
                          text_color="Black")
    btnOK.pack(pady=10)

# MOVE OS MOTORES XERYON (LENTE)
def mover_Xeryon():
    try:
        pos_x = float(entry_posicao_lente.get())        # ADQUIRE A POSIÇÃO DO VALOR DIGITADO NA INTERFACE GRÁFICA [MM]
        velocidade_percentual = float(entry_velocidade_lente.get())  # ADQUIRE A VELOCIDADE EM PORCENTAGEM DIGITADA NA INTERFACE GRÁFICA
        

        # VERIFICAÇÃO DO VALOR DE POS_X CONSIDERANDO O OFFSET
        if pos_x > UPPER_XERYON_MM or pos_x < LOWER_XERYON_MM:
            exibir_alerta_fim_de_curso_lente()
            return
        
        pos_x = pos_x + OFFSET_XERYON_MM                                    # ADICIONA O OFFSET À POSIÇÃO DIGITADA NA INTERFACE GRÁFICA

        # CONVERTE A VELOCIDADE DE PORCENTAGEM PARA MM/S
        if velocidade_percentual < 0:
            velocidade_percentual = 0
        elif velocidade_percentual > 100:
            velocidade_percentual = 100
        
        speed = (velocidade_percentual / 100) * MAX_VELOCIDADE_XERYON       # 100% CORRESPONDE A 400 MM/S
        axisX.setSpeed(speed)                                               # DEFINE A VELOCIDADE DO EIXO 1 PARA O VALOR CONVERTIDO
        axisY.setSpeed(speed)                                               # DEFINE A VELOCIDADE DO EIXO 2 PARA O VALOR CONVERTIDO

        print("Iniciando movimentação dos motores Xeryon...")

        def move_axis_x():
            print("Movendo eixo X para posição:", pos_x)
            axisX.setDPOS(pos_x)
            if abs(axisX.getEPOS() - axisX.getDPOS()) < 0.002:
                time.sleep(0.1)
            print("Eixo X alcançou a posição:", pos_x)

        def move_axis_y():
            print("Movendo eixo Y para posição:", pos_x)
            axisY.setDPOS(pos_x)
            if abs(axisY.getEPOS() - axisY.getDPOS()) < 0.002:
                time.sleep(0.1)
            print("Eixo Y alcançou a posição:", pos_x)

        thread_move_x = threading.Thread(target=move_axis_x)        # DEFINE A PARALELIZAÇÃO DA MOVIMENTAÇÃO DO MOTOR XERYON 1
        thread_move_y = threading.Thread(target=move_axis_y)        # DEFINE A PARALELIZAÇÃO DA MOVIMENTAÇÃO DO MOTOR XERYON 2
        thread_move_x.start()                                       # INICIA A PARALELIZAÇÃO DA MOVIMENTAÇÃO DO MOTOR XERYON 1
        thread_move_y.start()                                       # INICIA A PARALELIZAÇÃO DA MOVIMENTAÇÃO DO MOTOR XERYON 2
        thread_move_x.join()                                        # SINCRONIZA A MOVIMENTAÇÃO DO MOTOR XERYON 1
        thread_move_y.join()                                        # SINCRONIZA A MOVIMENTAÇÃO DO MOTOR XERYON 2

        print("Movimentação dos motores Xeryon concluída.")
    except ValueError:
        print("Erro: Insira um valor numérico válido para a posição ou velocidade.")

# --------------------------------------------------------------------------------------------
# -------------------------- FUNÇÃO PARA CONECTAR O MOTOR MIGHTYZAP --------------------------
# --------------------------------------------------------------------------------------------

def conectar_mightyzap():
    porta = bocal_var.get()
    if porta in PortalSerialConectadas:
        print(f"Conectando a {porta}...")
        MightyZap.OpenMightyZap(porta, 57600)
        time.sleep(0.1)
        MightyZap.GoalSpeed(Actuator_ID,64)
        MightyZap.GoalSpeed(Actuator_ID_1,64)
        
        # SCAN DE POSIÇÃO DURANTE O ZERAMENTO
        for pos in range(LIMITE_INFERIOR_MIGHTYZAP, LIMITE_SUPERIOR_MIGHTYZAP + 1, 10):
            MightyZap.GoalPosition(Actuator_ID, pos)
            MightyZap.GoalPosition(Actuator_ID_1, pos)
            time.sleep(0.05)
        
        for pos in range(LIMITE_SUPERIOR_MIGHTYZAP, OFFSET_POSICAO_MIGHTYZAP, -10):
            MightyZap.GoalPosition(Actuator_ID, pos)
            MightyZap.GoalPosition(Actuator_ID_1, pos)
            time.sleep(0.05)
        
        exibir_alerta_motor_conectado()
    else:
        print("Erro: Porta não selecionada ou inválida")

# --------------------------------------------------------------------------------------------
# --------------------------------- EXIBIR ALERTA DE CONEXÃO ---------------------------------
# --------------------------------------------------------------------------------------------

def exibir_alerta_motor_conectado():
    alerta = ctk.CTkToplevel(root)
    alerta.title("Conectado")
    alerta.geometry("300x150")
    alerta.grab_set()
    LabelAlerta = ctk.CTkLabel( alerta, 
                                text = "Bocal Dinâmico conectado", 
                                font=("Helvetica", 18),
                                text_color = "Black")
    
    LabelAlerta.pack(pady = 20)
    btnOK = ctk.CTkButton(  alerta, 
                            text = "OK", 
                            command = alerta.destroy,
                            font = ("Helvetica", 18),
                            text_color = "Black")
    
    btnOK.pack(pady = 10)

# --------------------------------------------------------------------------------------------
# ------------------ FUNÇÃO PARA DEFINIR A VELOCIDADE DOS MOTORES MIGHTYZAP ------------------
# --------------------------------------------------------------------------------------------

# FUNÇÃO PARA DEFINIR A VELOCIDADE DOS MOTORES MIGHTYZAP EM PORCENTAGEM
def definir_velocidade():
    try:
        velocidade_percentual = float(velocidade_var.get())
        if velocidade_percentual < 0:
            velocidade_percentual = 0
        elif velocidade_percentual > 100:
            velocidade_percentual = 100
        
        speed = int((velocidade_percentual / 100) * MAX_VELOCIDADE_MIGTHYZAP)
        print(f"Definindo velocidade para {speed} ({velocidade_percentual}%)...")
        MightyZap.GoalSpeed(Actuator_ID, speed)
        MightyZap.GoalSpeed(Actuator_ID_1, speed)
    except ValueError:
        print("Erro: Insira um valor numérico válido para a velocidade.")

# --------------------------------------------------------------------------------------------
# -------------------------- FUNÇÃO PARA MOVER OS MOTORES MIGHTYZAP --------------------------
# --------------------------------------------------------------------------------------------

# FUNÇÃO PARA EXIBIR ALERTA DE FIM DE CURSO
def exibir_alerta_fim_de_curso():
    alerta = ctk.CTkToplevel(root)
    alerta.title("Alerta")
    alerta.geometry("300x150")
    alerta.grab_set()
    LabelAlerta = ctk.CTkLabel(alerta, 
                               text = "Fim de curso do Bocal Dinâmico", 
                               font = ("Helvetica", 18),
                               text_color = "Black")
    LabelAlerta.pack(pady=20)

    btnOK = ctk.CTkButton(alerta, 
                          text = "OK", 
                          command = alerta.destroy,
                          font = ("Helvetica", 18),
                          text_color = "Black")
    btnOK.pack(pady=10)

# FUNÇÃO PARA MOVER OS MOTORES MIGHTYZAP
def mover_MightyZap():
    try:
        definir_velocidade()
        mm_value = float(posicao_var.get())
        
        # VERIFICAÇÃO DO FIM DE CURSO DO BOCAL
        if mm_value > UPPER_MIGHTYZAP_MM or mm_value < LOWER_MIGHTYZAP_MM:
            exibir_alerta_fim_de_curso()
            return
        
        position = int(round(mm_value * CONVERSAO_MM_PARA_POSICAO)) + OFFSET_POSICAO_MIGHTYZAP
        
        if position < LIMITE_INFERIOR_MIGHTYZAP or position > LIMITE_SUPERIOR_MIGHTYZAP:
            print(f"Erro: posição {position} fora do limite ({LIMITE_INFERIOR_MIGHTYZAP}-{LIMITE_SUPERIOR_MIGHTYZAP})")
        else:
            print(f"Movendo motores para posição {position}...")
            MightyZap.GoalPosition(Actuator_ID, position)
            MightyZap.GoalPosition(Actuator_ID_1, position)
    except ValueError:
        print("Erro: Insira um valor numérico válido para a posição.")

                                        
# --------------------------------------------------------------------------------------------
# -------------------------- FUNÇÃO PARA CONECTAR TODOS OS MOTORES ---------------------------
# --------------------------------------------------------------------------------------------

def conectar_todos_motores():
    iniciar_motores()                           # CONECTA OS MOTORES XERYON (LENTE) 
    conectar_mightyzap()                        # CONECTA OS MOTORES MIGHTYZAP (BOCAL)

# --------------------------------------------------------------------------------------------
# -------------------------- FUNÇÃO PARA MOVER TODOS OS MOTORES ------------------------------
# --------------------------------------------------------------------------------------------

def mover_todos_motores():
    mover_MightyZap()                           # MOVE OS MOTORES MIGHTYZAP (BOCAL)
    mover_Xeryon()                              # MOVE OS MOTORES XERYON (LENTE)

# --------------------------------------------------------------------------------------------
# ------------------------------------ INTERFACE GRÁFICA -------------------------------------
# --------------------------------------------------------------------------------------------

root = ctk.CTk()                                # CRIA A JANELA PRINCIPAL
root.title("Bocal Dinâmico")                    # NOMEIA A JANELA COMO BOCAL DINÂMICO
root.geometry("900x480")                        # DEFINE O TAMANHO DA JANELA
root.resizable(False,False)                     # IMPEDE QUE A JANELA SEJA REDIMENSIONADA
ctk.set_appearance_mode("light")                # DEFINE O TEMA DA JANELA PARA O TEMA CLARO
LARGURA_FIXA = 300                              # DEFINE A LARGURA PARA OS MENUS E CAMPOS DE ENTRADA
CR = 10                                         # DEFINE O RAIO DO CANTO ARREDONDADO DOS BOTÕES
ESPACAMENTO_VERTICAL = 5                        # DEFINE O ESPAÇAMENTO VERTICAL ENTRE OS WIDGETS
LARGURA_LABEL = 250                             # DEFINE A LARGURA FIXA PARA OS LABELS
LARGURA_BOTAO = 230                             # DEFINE A LARGURA FIXA PARA OS BOTÕES

# CONFIGURA O GRID PARA OS FRAMES SE EXPANDIREM DE MANEIRA UNIFORME
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)

# --------------------------------------------------------------------------------------------
# ------------------------------------ ÁREA DE CONEXÃO ---------------------------------------
# --------------------------------------------------------------------------------------------

frame_conexao = ctk.CTkFrame(   root, 
                                fg_color = "AntiqueWhite1", 
                                corner_radius = CR,
                                border_width = 1,
                                border_color = "Black")

frame_conexao.grid( row = 0, 
                   column = 0,
                   padx = 10, 
                   pady = 10, 
                   sticky = "nsew")

LabelConectXeryon_1 = ctk.CTkLabel(frame_conexao, 
                                   text = "Conexão: Motor 1 da Lente",
                                   font = ("Helvetica", 18),
                                   text_color = "Black",
                                   corner_radius = CR,
                                   width = LARGURA_LABEL)

LabelConectXeryon_1.grid(   row = 0, 
                            column = 0, 
                            padx = 10, 
                            pady = ESPACAMENTO_VERTICAL, 
                            sticky = "w")

porta_x = ctk.StringVar(value = "Selecione a Porta Serial")

PortaSerialX = ctk.CTkOptionMenu(frame_conexao, 
                                 values = PortalSerialConectadas, 
                                 variable = porta_x,
                                 font = ("Helvetica", 18),
                                 text_color = "Black",
                                 fg_color = "LightBlue1",
                                 width = LARGURA_FIXA,
                                 corner_radius = CR)

PortaSerialX.grid(  row = 0, 
                    column = 1, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL, 
                    sticky = "w")

LabelConectXeryon_2 = ctk.CTkLabel(frame_conexao, 
                                   text = "Conexão: Motor 2 da Lente",
                                   font = ("Helvetica", 18),
                                   text_color = "Black",
                                   corner_radius = CR,
                                   width = LARGURA_LABEL)

LabelConectXeryon_2.grid(   row = 1, 
                            column = 0, 
                            padx = 10, 
                            pady = ESPACAMENTO_VERTICAL, 
                            sticky = "w")

porta_y = ctk.StringVar(value = "Selecione a Porta Serial")

PortaSerialY = ctk.CTkOptionMenu(frame_conexao, 
                                 values = PortalSerialConectadas, 
                                 variable = porta_y,
                                 font = ("Helvetica", 18),
                                 text_color = "Black",
                                 fg_color = "LightBlue1",
                                 width = LARGURA_FIXA,
                                 corner_radius = CR)

PortaSerialY.grid(  row = 1, 
                    column = 1, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL, 
                    sticky = "w")

LabelConectMightyZap = ctk.CTkLabel(frame_conexao, 
                                    text = "Conexão: Bocal Dinâmico", 
                                    font = ("Helvetica", 18),
                                    text_color = "Black",
                                    corner_radius = CR,
                                    width = LARGURA_LABEL)

LabelConectMightyZap.grid(  row = 2, 
                            column = 0, 
                            padx = 10, 
                            pady = ESPACAMENTO_VERTICAL, 
                            sticky = "w")

bocal_var = ctk.StringVar(value = "Selecione a Porta Serial")

PortaSerialMightyZap = ctk.CTkOptionMenu(frame_conexao, 
                                         values = PortalSerialConectadas, 
                                         variable = bocal_var, 
                                         width = LARGURA_FIXA,
                                         font = ("Helvetica", 18),
                                         fg_color = "Navy",
                                         text_color = "White",
                                         corner_radius = CR)

PortaSerialMightyZap.grid(  row = 2, 
                            column = 1, 
                            padx = 10, 
                            pady = ESPACAMENTO_VERTICAL, 
                            sticky = "w")

btnConectBocal = ctk.CTkButton(frame_conexao, 
                               text = "Conectar Bocal Dinâmico", 
                               command = conectar_todos_motores,
                               width = LARGURA_BOTAO,
                               height = 110,
                               font = ("Helvetica", 18),
                               fg_color = "AntiqueWhite3",
                               text_color = "Black",
                               corner_radius = CR,
                               border_color = "Black",
                               border_width = 1)

btnConectBocal.grid(row = 0, 
                    column = 2, 
                    rowspan = 3, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL, 
                    sticky = "w")

# --------------------------------------------------------------------------------------------
# ------------------------------------- CONTROLE LENTE ---------------------------------------
# --------------------------------------------------------------------------------------------

frame_lente = ctk.CTkFrame( root, 
                            fg_color = "lightblue", 
                            corner_radius=CR,
                            border_color = "Black",
                            border_width = 1)

frame_lente.grid(   row = 1, 
                    column = 0, 
                    padx = 10, 
                    pady = 10, 
                    sticky = "nsew")

LabelPosLente = ctk.CTkLabel(frame_lente, 
                             text = "Posição: Lente (mm):",
                             font = ("Helvetica", 18),
                             corner_radius = CR,
                             width = LARGURA_LABEL)

LabelPosLente.grid( row = 0, 
                    column = 0, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL, 
                    sticky = "w")

entry_posicao_lente = ctk.CTkEntry(frame_lente, 
                                   width = LARGURA_FIXA,
                                   font = ("Helvetica", 18),
                                   corner_radius = CR,
                                   border_width = 1,
                                   border_color = "black")
entry_posicao_lente.grid(   row = 0, 
                            column = 1, 
                            padx = 10, 
                            pady = ESPACAMENTO_VERTICAL, 
                            sticky = "w")

LabelVeloLente = ctk.CTkLabel(frame_lente, 
                              text = "Velocidade: Lente (%):",
                              font = ("Helvetica", 18),
                              text_color = "Black",
                              corner_radius = CR,
                              width = LARGURA_LABEL)

LabelVeloLente.grid(row = 1, 
                    column = 0, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL, 
                    sticky = "w")

entry_velocidade_lente = ctk.CTkEntry(frame_lente, 
                                      width = LARGURA_FIXA,
                                      font = ("Helvetica", 18),
                                      text_color = "Black",
                                      corner_radius = CR,
                                      border_width = 1,
                                      border_color = "black")

entry_velocidade_lente.grid(row = 1, 
                            column = 1, 
                            padx = 10, 
                            pady = ESPACAMENTO_VERTICAL, 
                            sticky = "w")

btnPosLente = ctk.CTkButton(frame_lente, 
                            text = "Posicionar Lente", 
                            command = mover_Xeryon,
                            text_color = "Black",
                            fg_color = "LightBlue1",
                            font = ("Helvetica", 18),
                            height = 80,
                            width = LARGURA_BOTAO,
                            corner_radius = CR,
                            border_color = "Black",
                            border_width = 1)
btnPosLente.grid(   row = 0, 
                    column = 2, 
                    columnspan = 2, 
                    rowspan = 2, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL, 
                    sticky = "w")

velocidade_var = ctk.StringVar()

# --------------------------------------------------------------------------------------------
# ------------------------------------- CONTROLE BOCAL ---------------------------------------
# --------------------------------------------------------------------------------------------

frame_bocal = ctk.CTkFrame( root, 
                            fg_color = "steel blue", 
                            corner_radius=CR,
                            border_color = "Black",
                            border_width = 1)

frame_bocal.grid(   row = 2, 
                    column = 0, 
                    padx = 10, 
                    pady = 10, 
                    sticky = "nsew")

LabelPosBocal = ctk.CTkLabel(frame_bocal, 
                             text = "Posição: Bocal (mm):", 
                             font = ("Helvetica", 18),
                             text_color = "White",
                             corner_radius = CR,
                             width = LARGURA_LABEL)

LabelPosBocal.grid( row=0, 
                    column = 0, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL, 
                    sticky = "w")

posicao_var = ctk.StringVar()
entrada_posicao = ctk.CTkEntry(frame_bocal, 
                               textvariable = posicao_var, 
                               width = LARGURA_FIXA,
                               font = ("Helvetica", 18),
                               corner_radius = CR,
                               border_width = 1,
                               border_color = "black")

entrada_posicao.grid(   row = 0, 
                        column = 1, 
                        padx = 10, 
                        pady = ESPACAMENTO_VERTICAL, 
                        sticky = "w")

LabelVeloBocal = ctk.CTkLabel(frame_bocal, 
                              text = "Velocidade: Bocal (%):",
                              font = ("Helvetica", 18),
                              text_color = "White",
                              corner_radius = CR,
                              width = LARGURA_LABEL)
LabelVeloBocal.grid(row = 1, 
                    column = 0, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL,
                    sticky = "w")

entry_velocidade_bocal = ctk.CTkEntry(frame_bocal, 
                                      textvariable = velocidade_var, 
                                      width = LARGURA_FIXA,
                                      font = ("Helvetica", 18),
                                      corner_radius = CR,
                                      border_width = 1,
                                      border_color = "black")

entry_velocidade_bocal.grid(row = 1, 
                            column = 1, 
                            padx = 10,
                            pady = ESPACAMENTO_VERTICAL, 
                            sticky = "w")

btnPosBocal = ctk.CTkButton(frame_bocal, 
                            text = "Posicionar Bocal", 
                            command = mover_MightyZap, 
                            font = ("Helvetica", 18), 
                            fg_color = "Navy", 
                            text_color = "White",
                            height = 80,
                            width = LARGURA_BOTAO,
                            corner_radius = CR,
                            border_color = "Black",
                            border_width = 1)

btnPosBocal.grid(   row = 0, 
                    column = 2, 
                    columnspan = 2, 
                    rowspan = 2, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL, 
                    sticky = "w")

# --------------------------------------------------------------------------------------------
# ---------------------------- FEEDBACK DE POSIÇÃO ATUAL -------------------------------------
# --------------------------------------------------------------------------------------------
posicao_xeryon_var = ctk.StringVar(value=f"Lente: Motor 1 = 0.000 mm, Motor 2 = 0.000 mm")
posicao_mightyzap_var = ctk.StringVar(value=f"Bocal: Motor 1 = 0.000 mm, Motor 2 = 0.000 mm")

frame_feedback = ctk.CTkFrame(  root, 
                                fg_color = "PaleGreen1", 
                                corner_radius = CR,
                                border_color = "Black",
                                border_width = 1)

frame_feedback.grid(    row = 3, 
                        column = 0, 
                        padx = 10, 
                        pady = 10, 
                        sticky = "nsew")

LabelPosXeryon = ctk.CTkLabel(frame_feedback, 
                              textvariable = posicao_xeryon_var, 
                              font = ("Helvetica", 16),
                              width = LARGURA_LABEL)

LabelPosXeryon.grid(row = 0, 
                    column = 0, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL, 
                    sticky = "w")

LabelPosMightyZap = ctk.CTkLabel(frame_feedback, 
                                 textvariable = posicao_mightyzap_var, 
                                 font = ("Helvetica", 16),
                                 width = LARGURA_LABEL)

LabelPosMightyZap.grid( row = 1, 
                       column = 0, 
                       padx = 10, 
                       pady = ESPACAMENTO_VERTICAL, 
                       sticky = "w")

btnPosAmbos = ctk.CTkButton(frame_feedback, 
                            text = "Mover: Lente + Bocal", 
                            command = mover_todos_motores,
                            font = ("Helvetica", 20),
                            fg_color = "PaleGreen3",
                            text_color = "Black",
                            height = 80,
                            width = LARGURA_BOTAO,
                            corner_radius = CR,
                            border_color = "Black",
                            border_width = 1)

ctk.CTkLabel(frame_feedback, text="", width=200).grid(row=0, column=1, padx=10, pady=ESPACAMENTO_VERTICAL, sticky="w")

btnPosAmbos.grid(   row = 0, 
                    column = 2, 
                    columnspan = 2, 
                    rowspan = 2, 
                    padx = 10, 
                    pady = ESPACAMENTO_VERTICAL, 
                    sticky = "w")

# --------------------------------------------------------------------------------------------
# ---------------------------- POSIÇÃO DOS MOTORES NA INTERFACE ------------------------------
# --------------------------------------------------------------------------------------------

def atualizar_posicoes():
    # Atualiza a posição do Xeryon
    if axisX and axisY:
        pos_x = axisX.getEPOS() - OFFSET_XERYON_MM ####
        pos_y = axisY.getEPOS() - OFFSET_XERYON_MM
        posicao_xeryon_var.set(f"Lente: Motor 1 = {pos_x:.3f} mm, Motor 2 = {pos_y:.3f} mm")
        pos_actuator = MightyZap.PresentPosition(Actuator_ID) - OFFSET_POSICAO_MIGHTYZAP
        pos_actuator_1 = MightyZap.PresentPosition(Actuator_ID_1) - OFFSET_POSICAO_MIGHTYZAP
        pos_actuator_mm = pos_actuator / CONVERSAO_MM_PARA_POSICAO
        pos_actuator_mm_1 = pos_actuator_1 / CONVERSAO_MM_PARA_POSICAO
        posicao_mightyzap_var.set(f"Lente: Motor 1 = {pos_actuator_mm:.3f} mm, Motor 2 = {pos_actuator_mm_1:.3f} mm")
    
    # ATUALIZA A CADA 200 MS
    root.after(200, atualizar_posicoes)  

atualizar_posicoes()
root.mainloop()

# PARA A COMUNICAÇÃO DOS MOTORES XERYON QUANDO A INTERFACE FOR FECHADA
if controllerX:
    controllerX.stop()
if controllerY:
    controllerY.stop()