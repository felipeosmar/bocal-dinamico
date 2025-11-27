# Bocal Dinâmico

Sistema de controle de motores para posicionamento preciso de bocal, com interface gráfica desenvolvida em Python.

## Descrição

Este projeto implementa uma interface gráfica para controlar 3 atuadores lineares MightyZap para o bocal dinâmico.

## Requisitos

### Hardware
- 3x Atuadores MightyZap (IDs 0, 1 e 2)
- Porta serial disponível para comunicação

### Software
- Python 3.10+
- Bibliotecas Python:
  - `customtkinter` - Interface gráfica moderna
  - `pyserial` - Comunicação serial
  - `PythonLibMightyZap_FC` - Biblioteca de controle dos atuadores MightyZap (incluída em `lib/`)

## Instalação

```bash
pip install customtkinter pyserial
```

> **Nota**: A biblioteca `PythonLibMightyZap_FC` já está incluída no diretório `lib/`.

## Configuração

### Parâmetros dos Motores MightyZap (Bocal)

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| IDs dos Motores | 0, 1, 2 | Identificadores dos 3 motores |
| Limite Superior | +1.01 mm | Posição máxima do bocal |
| Limite Inferior | -2.01 mm | Posição mínima do bocal |
| Offset | 7.0 mm | Posição inicial/referência |
| Velocidade Máxima | 1024 | Unidades internas |

> **Nota**: Os parâmetros podem ser ajustados no arquivo `src/config.py`.

## Uso

### Executando a aplicação

```bash
python main.py
```

### Interface Gráfica

A interface é dividida em três seções:

1. **Área de Conexão**
   - Seleção da porta serial
   - Botão para conectar aos 3 motores

2. **Controle do Bocal**
   - Campo para posição desejada (mm)
   - Campo para velocidade (%)
   - Botão para posicionar o bocal

3. **Feedback de Posição**
   - Exibição em tempo real das posições dos 3 motores

### Fluxo de Operação

1. Selecione a porta serial correta
2. Clique em "Conectar Bocal Dinâmico" - os 3 motores serão inicializados e zerados
3. Digite a posição e velocidade desejadas
4. Clique em "Posicionar Bocal" para mover os motores

## Estrutura do Projeto

```
bocal-dinamico/
├── main.py                          # Ponto de entrada da aplicação
├── README.md
│
├── lib/                             # Bibliotecas dos fabricantes
│   └── PythonLibMightyZap_FC.py     # Biblioteca MightyZap
│
└── src/                             # Código fonte modular
    ├── __init__.py
    ├── config.py                    # Configurações e constantes
    ├── serial_utils.py              # Utilitários de comunicação serial
    ├── mightyzap_controller.py      # Controlador dos 3 motores MightyZap
    │
    └── gui/                         # Interface gráfica
        ├── __init__.py
        ├── alerts.py                # Diálogos e alertas
        ├── frames.py                # Frames da interface
        └── main_window.py           # Janela principal
```

## Arquitetura

O projeto segue o princípio de **Responsabilidade Única (SRP)** e está organizado em módulos:

| Módulo | Responsabilidade |
|--------|------------------|
| `config.py` | Centraliza todas as configurações e constantes |
| `serial_utils.py` | Detecção e validação de portas seriais |
| `mightyzap_controller.py` | Encapsula a lógica de controle dos 3 motores |
| `gui/alerts.py` | Gerencia diálogos e mensagens ao usuário |
| `gui/frames.py` | Define os componentes visuais (frames) |
| `gui/main_window.py` | Coordena a interface e o controlador |

## Alertas e Segurança

O sistema implementa verificações de fim de curso:
- Alerta exibido ao tentar ultrapassar os limites do bocal
- Os comandos são bloqueados quando os limites são atingidos

## Licença

Este projeto é de uso interno. Consulte o responsável pelo projeto para informações sobre licenciamento.
