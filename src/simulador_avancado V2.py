import sys
import time
import random
import string
import pyautogui
import keyboard

try:
    import pyperclip
    PYPERCLIP_DISPONIVEL = True
    print("Pyperclip importado com sucesso.")
except ImportError:
    PYPERCLIP_DISPONIVEL = False
    print("Pyperclip não encontrado...")
    print("Para instalar: pip install pyperclip")

TECLA_DE_PARADA = 'esc'
CHANCE_DE_ERRO_UM_CHAR = 0.03
CHANCE_DE_ERRO_BLOCO = 0.015
TAMANHOS_BLOCO_ERRO = [3, 4, 5]
POSSIVEIS_CHARS_ERRO = string.ascii_lowercase
ASCII_SIMPLES_PARA_TYPEWRITE = string.ascii_letters + string.digits + string.punctuation + ' \n\t'

def digitar_caractere_com_clipboard(char_para_digitar):
    if not PYPERCLIP_DISPONIVEL:
        pyautogui.typewrite(char_para_digitar)
        return
    try:
        clipboard_original = pyperclip.paste()
        pyperclip.copy(char_para_digitar)
        time.sleep(0.05)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.05)
        pyperclip.copy(clipboard_original)
    except Exception as e:
        print(f"DEBUG: Erro ao usar pyperclip para '{char_para_digitar}': {e}. Tentando typewrite.")
        pyautogui.typewrite(char_para_digitar)

def calcular_delay(modo_velocidade, tipo_de_pausa="normal_char"):
    fator_timelapse_erro = 0.2
    if modo_velocidade == "Normal":
        if tipo_de_pausa == "normal_char": return random.uniform(0.05, 0.18)
        elif tipo_de_pausa == "percepcao_erro_um_char": return random.uniform(0.3, 0.7)
        elif tipo_de_pausa == "pos_backspace_um_char": return random.uniform(0.15, 0.4)
        elif tipo_de_pausa == "correcao_char_um_char": return random.uniform(0.07, 0.18)
        elif tipo_de_pausa == "char_errado_bloco": return random.uniform(0.04, 0.12)
        elif tipo_de_pausa == "percepcao_erro_bloco": return random.uniform(0.5, 1.2)
        elif tipo_de_pausa == "entre_backspaces_bloco": return random.uniform(0.05, 0.15)
        elif tipo_de_pausa == "pos_correcao_bloco": return random.uniform(0.2, 0.6)
    else:  # Time-Lapse
        if tipo_de_pausa == "normal_char": return random.uniform(0.001, 0.01)
        elif tipo_de_pausa == "percepcao_erro_um_char": return random.uniform(0.03, 0.07) * fator_timelapse_erro
        elif tipo_de_pausa == "pos_backspace_um_char": return random.uniform(0.02, 0.05) * fator_timelapse_erro
        elif tipo_de_pausa == "correcao_char_um_char": return random.uniform(0.005, 0.015) * fator_timelapse_erro
        elif tipo_de_pausa == "char_errado_bloco": return random.uniform(0.002, 0.01)
        elif tipo_de_pausa == "percepcao_erro_bloco": return random.uniform(0.05, 0.12) * fator_timelapse_erro
        elif tipo_de_pausa == "entre_backspaces_bloco": return random.uniform(0.005, 0.015)
        elif tipo_de_pausa == "pos_correcao_bloco": return random.uniform(0.02, 0.06) * fator_timelapse_erro
    return 0.05

def calcular_delay_palavra(modo_velocidade):
    if modo_velocidade == "Normal": return random.uniform(0.1, 0.3)
    elif modo_velocidade == "Time-Lapse": return random.uniform(0.005, 0.02)
    return 0.1

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QTextEdit, QRadioButton, QPushButton,
                               QMessageBox, QButtonGroup, QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QFont, QScreen, QPixmap

class SimuladorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.simulacao_em_andamento = False
        self.setWindowTitle("Simulador de Digitação Avançado")
        self.setObjectName("MainWindow")
        self.init_ui()
        self.apply_styles() # Aplicar estilos DEPOIS que todos os objectNames estiverem definidos
        self._center_window()

    def _create_header(self):
        header_widget = QWidget()
        header_widget.setObjectName("HeaderWidget")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(10)

        logo_label_placeholder = QLabel("HT")
        logo_label_placeholder.setObjectName("LogoLabel")
        # A fonte será definida via QSS

        app_title_label = QLabel("| Simulador de Digitação Realista")
        app_title_label.setObjectName("AppTitleLabel")
        # A fonte será definida via QSS

        header_layout.addWidget(logo_label_placeholder)
        header_layout.addSpacerItem(QSpacerItem(5, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)) # Espaço reduzido
        header_layout.addWidget(app_title_label)
        header_layout.addStretch()
        return header_widget

    def _create_footer(self):
        footer_widget = QWidget()
        footer_widget.setObjectName("FooterWidget")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(15, 8, 15, 8)

        copyright_label = QLabel("© 2025 Henrique Torquato. Todos os direitos reservados.")
        copyright_label.setObjectName("CopyrightLabel")
        
        version_label = QLabel("Versão 2.1.0") # Incrementando a versão pela mudança de fonte
        version_label.setObjectName("VersionLabel")

        footer_layout.addWidget(copyright_label)
        footer_layout.addStretch()
        footer_layout.addWidget(version_label)
        return footer_widget

    def init_ui(self):
        overall_layout = QVBoxLayout(self)
        overall_layout.setContentsMargins(0, 0, 0, 0)
        overall_layout.setSpacing(0)

        header = self._create_header()
        overall_layout.addWidget(header)

        content_widget = QWidget()
        content_widget.setObjectName("ContentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 20, 25, 25)
        content_layout.setSpacing(18)

        self.label_texto = QLabel("Cole o texto para simulação abaixo:")
        self.label_texto.setObjectName("LabelTextoPrincipal") # Adicionando objectName
        content_layout.addWidget(self.label_texto)

        self.campo_texto = QTextEdit()
        self.campo_texto.setPlaceholderText("Digite ou cole seu texto aqui...")
        self.campo_texto.setMinimumHeight(180)
        self.campo_texto.setText("Testando as novas fontes estilo Apple...\nSF Pro, Helvetica Neue, Arial...\nO visual deve estar mais refinado agora.\n12345 !@#$%.")
        content_layout.addWidget(self.campo_texto)
        
        content_layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self.label_velocidade = QLabel("Modo de Velocidade:")
        self.label_velocidade.setObjectName("LabelVelocidadePrincipal") # Adicionando objectName
        content_layout.addWidget(self.label_velocidade)

        opcoes_velocidade_layout = QHBoxLayout()
        self.modo_velocidade_group = QButtonGroup(self)
        self.radio_normal = QRadioButton("Normal")
        self.radio_normal.setChecked(True)
        self.modo_velocidade_group.addButton(self.radio_normal)
        opcoes_velocidade_layout.addWidget(self.radio_normal)
        self.radio_timelapse = QRadioButton("Time-Lapse")
        self.modo_velocidade_group.addButton(self.radio_timelapse)
        opcoes_velocidade_layout.addWidget(self.radio_timelapse)
        opcoes_velocidade_layout.addStretch()
        content_layout.addLayout(opcoes_velocidade_layout)
        
        content_layout.addStretch(1) 

        self.status_label = QLabel("") 
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.status_label)

        self.botao_iniciar = QPushButton("Iniciar Simulação")
        self.botao_iniciar.clicked.connect(self.ao_iniciar_simulacao)
        self.botao_iniciar.setMinimumHeight(45)
        content_layout.addWidget(self.botao_iniciar)
        
        overall_layout.addWidget(content_widget)
        overall_layout.setStretchFactor(content_widget, 1)

        footer = self._create_footer()
        overall_layout.addWidget(footer)
        
        self.setLayout(overall_layout)
        self.setMinimumSize(600, 550)

    def apply_styles(self):
        # Definição da pilha de fontes preferida
        apple_font_stack = "'SF Pro Display', 'Helvetica Neue', Helvetica, Arial, sans-serif"

        qss = f"""
            QWidget {{ /* Fonte base para toda a aplicação */
                font-family: Arial, sans-serif; /* Fallback bem genérico */
                font-size: 10pt;
            }}

            #MainWindow {{ }}

            #HeaderWidget {{
                background-color: #FFFFFF;
                border-bottom: 1px solid #E0E0E0; /* Borda inferior sutil cinza claro */
            }}
            #LogoLabel {{
                font-family: {apple_font_stack};
                color: #1D1D1F; /* Cor escura da Apple para texto */
                font-size: 18pt; /* Aumentado para destaque */
                font-weight: 600; /* Semi-bold */
                padding: 5px 0px 5px 5px;
            }}
            #AppTitleLabel {{
                font-family: {apple_font_stack};
                color: #515154; /* Cinza Apple para texto secundário */
                font-size: 11pt; /* Aumentado */
                font-weight: 400; /* Regular */
                padding-top: 2px; /* Alinhamento visual com o logo */
            }}

            #ContentWidget {{
                background-color: #FFFFFF;
            }}
            /* Estilo para labels principais no corpo */
            #LabelTextoPrincipal, #LabelVelocidadePrincipal {{
                font-family: {apple_font_stack};
                color: #1D1D1F; 
                font-size: 11pt; /* Aumentado */
                font-weight: 500; /* Medium */
                padding-bottom: 4px;
            }}
             /* Estilo para labels gerais (não principais) dentro do ContentWidget, se houver */
            #ContentWidget QLabel {{
                font-family: {apple_font_stack}; /* Aplica também aos labels não nomeados dentro do content */
                color: #333333;
                font-size: 10pt;
            }}

            QTextEdit {{
                font-family: {apple_font_stack};
                background-color: #FFFFFF; 
                border: 1px solid #D2D2D7; /* Cinza Apple para bordas de campos */
                border-radius: 8px; 
                padding: 10px; 
                font-size: 10pt;
                color: #1D1D1F;
            }}
            QRadioButton {{
                font-family: {apple_font_stack};
                font-size: 10pt;
                color: #1D1D1F;
                spacing: 7px; 
            }}
            QRadioButton::indicator {{
                width: 16px; 
                height: 16px;
            }}
            QRadioButton::indicator:unchecked {{
                border: 1.5px solid #AEAEB2; /* Cinza Apple para indicadores */
                border-radius: 8px;
                background-color: #FFFFFF;
            }}
            QRadioButton::indicator:checked {{
                border: 1.5px solid #007AFF; /* Azul Apple para selecionado */
                border-radius: 8px;
                background-color: #007AFF; 
            }}
            QRadioButton::indicator:checked::after {{
                content: ""; display: block;
                width: 8px; height: 8px;
                margin: 3px; /* (16 - 1.5*2 - 8)/2 */
                border-radius: 4px;
                background-color: white;
            }}

            QPushButton {{
                font-family: {apple_font_stack};
                background-color: #262626; 
                color: white;
                border: none;
                border-radius: 8px; 
                padding: 12px 18px; 
                font-size: 11pt;
                font-weight: 500; /* Medium */
            }}
            QPushButton:hover {{
                background-color: #404040; 
            }}
            QPushButton:pressed {{
                background-color: #7F7F7F; 
            }}

            #FooterWidget {{
                background-color: #FFFFFF; 
                border-top: 1px solid #E0E0E0; /* Borda sutil para separar do conteúdo branco */
            }}
            #CopyrightLabel, #VersionLabel {{
                font-family: {apple_font_stack};
                color: #8A8A8E; /* Cinza Apple para texto de rodapé */
                font-size: 8pt;
            }}
            #StatusLabel {{ 
                font-family: {apple_font_stack};
                color: #8A8A8E; 
                font-size: 9pt;
                padding-bottom: 5px;
            }}
        """
        self.setStyleSheet(qss)

    def _center_window(self):
        try:
            screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
            self.setGeometry(
                (screen_geometry.width() - self.width()) // 2,
                (screen_geometry.height() - self.height()) // 2,
                self.width(),
                self.height()
            )
        except Exception as e:
            print(f"Não foi possível centralizar a janela: {e}")

    @Slot() 
    def ao_iniciar_simulacao(self):
        if self.simulacao_em_andamento:
            QMessageBox.warning(self, "Atenção", "Uma simulação já está em andamento.")
            return

        texto_input = self.campo_texto.toPlainText().strip()
        if not texto_input:
            QMessageBox.critical(self, "Erro", "O campo de texto está vazio.")
            return

        modo_selecionado = "Normal" if self.radio_normal.isChecked() else "Time-Lapse"
        self.hide() 
        
        self.status_label.setText(f"Simulação em modo {modo_selecionado} iniciando...")
        QApplication.processEvents() 

        print(f"\nIniciando simulação em modo: {modo_selecionado}")
        print(f"Você tem 5 segundos para posicionar o cursor...")
        for i in range(5, 0, -1):
            if keyboard.is_pressed(TECLA_DE_PARADA): 
                print(f"\n--- Simulação interrompida ANTES de iniciar.")
                self.show()
                self.status_label.setText("Simulação cancelada.")
                return
            print(f"{i}...")
            time.sleep(1)
        print("Iniciando digitação!")

        try:
            self.executar_simulacao_logica(texto_input, modo_selecionado)
            if hasattr(self, '_simulacao_concluida_sem_interrupcao') and self._simulacao_concluida_sem_interrupcao:
                 self.status_label.setText("Simulação concluída!")
            elif not self.simulacao_em_andamento : # Se foi interrompida
                 self.status_label.setText("Simulação interrompida pelo usuário.")
            # Se simulacao_em_andamento ainda for True aqui, significa que o loop terminou
            # mas a flag não foi explicitamente setada para False por interrupção.
            # A lógica de `executar_simulacao_logica` deve garantir o estado correto.

        except pyautogui.FailSafeException:
            QMessageBox.critical(self, "Fail-Safe Ativado!", "Simulação interrompida (mouse no canto superior esquerdo).")
            print("--- PYAUTOGUI FAIL-SAFE TRIGGERED ---")
            self.status_label.setText("Fail-Safe Ativado!")
        except Exception as e:
            QMessageBox.critical(self, "Erro na Simulação", f"Ocorreu um erro inesperado: {e}")
            print(f"Erro detalhado na simulação: {e}")
            self.status_label.setText("Erro na simulação.")
            import traceback
            traceback.print_exc()
        finally:
            self.simulacao_em_andamento = False 
            self.show()

    def checar_parada_logica(self):
        if keyboard.is_pressed(TECLA_DE_PARADA):
            print(f"\n--- Tecla '{TECLA_DE_PARADA}' pressionada. Interrompendo simulação. ---")
            self.simulacao_em_andamento = False
            self._simulacao_concluida_sem_interrupcao = False # Adicionado para clareza no status
            return True
        return False

    def digitar_sequencia_logica(self, sequencia, modo_velocidade, tipo_delay_char="normal_char"):
        for char_item in sequencia:
            if not self.simulacao_em_andamento: return False
            delay_char_atual = calcular_delay(modo_velocidade, tipo_delay_char)
            if char_item in ASCII_SIMPLES_PARA_TYPEWRITE:
                pyautogui.typewrite(char_item)
            else:
                digitar_caractere_com_clipboard(char_item)
            time.sleep(delay_char_atual)
            if self.checar_parada_logica(): return False
        return True

    def executar_simulacao_logica(self, texto_completo, modo_velocidade):
        self.simulacao_em_andamento = True
        self._simulacao_concluida_sem_interrupcao = True # Assume que vai concluir

        texto_completo = texto_completo.replace('\r\n', '\n').replace('\r', '\n')
        for char_idx, char_correto in enumerate(texto_completo):
            if not self.simulacao_em_andamento:
                self._simulacao_concluida_sem_interrupcao = False
                break
            # ... (lógica de erro e digitação como antes, chamando self.checar_parada_logica) ...
            # Exemplo de como tratar o retorno de checar_parada_logica dentro do loop:
            if char_correto.strip() and random.random() < CHANCE_DE_ERRO_BLOCO:
                tamanho_bloco = random.choice(TAMANHOS_BLOCO_ERRO)
                bloco_errado = [random.choice(POSSIVEIS_CHARS_ERRO) for _ in range(tamanho_bloco)]
                if char_correto.isupper() and bloco_errado[0].isalpha():
                    bloco_errado[0] = bloco_errado[0].upper()
                if not self.digitar_sequencia_logica(bloco_errado, modo_velocidade, "char_errado_bloco"): self._simulacao_concluida_sem_interrupcao = False; break
                time.sleep(calcular_delay(modo_velocidade, "percepcao_erro_bloco"))
                if self.checar_parada_logica(): self._simulacao_concluida_sem_interrupcao = False; break
                for _ in range(tamanho_bloco):
                    if not self.simulacao_em_andamento: self._simulacao_concluida_sem_interrupcao = False; break
                    pyautogui.press('backspace')
                    time.sleep(calcular_delay(modo_velocidade, "entre_backspaces_bloco"))
                    if self.checar_parada_logica(): self._simulacao_concluida_sem_interrupcao = False; break
                if not self.simulacao_em_andamento: self._simulacao_concluida_sem_interrupcao = False; break
                time.sleep(calcular_delay(modo_velocidade, "pos_correcao_bloco"))
                if self.checar_parada_logica(): self._simulacao_concluida_sem_interrupcao = False; break

            elif char_correto.strip() and random.random() < CHANCE_DE_ERRO_UM_CHAR:
                char_errado = random.choice(POSSIVEIS_CHARS_ERRO)
                while char_errado == char_correto.lower() and len(POSSIVEIS_CHARS_ERRO) > 1: char_errado = random.choice(POSSIVEIS_CHARS_ERRO)
                if char_correto.isupper() and char_errado.isalpha(): char_errado = char_errado.upper()
                
                if char_errado in ASCII_SIMPLES_PARA_TYPEWRITE: pyautogui.typewrite(char_errado)
                else: digitar_caractere_com_clipboard(char_errado)
                time.sleep(calcular_delay(modo_velocidade, "normal_char"))
                if self.checar_parada_logica(): self._simulacao_concluida_sem_interrupcao = False; break
                
                time.sleep(calcular_delay(modo_velocidade, "percepcao_erro_um_char"))
                if self.checar_parada_logica(): self._simulacao_concluida_sem_interrupcao = False; break
                pyautogui.press('backspace')
                time.sleep(calcular_delay(modo_velocidade, "pos_backspace_um_char"))
                if self.checar_parada_logica(): self._simulacao_concluida_sem_interrupcao = False; break
                
                if char_correto in ASCII_SIMPLES_PARA_TYPEWRITE: pyautogui.typewrite(char_correto)
                else: digitar_caractere_com_clipboard(char_correto)
                time.sleep(calcular_delay(modo_velocidade, "correcao_char_um_char"))
                if self.checar_parada_logica(): self._simulacao_concluida_sem_interrupcao = False; break
                continue
            
            if char_correto in ASCII_SIMPLES_PARA_TYPEWRITE: pyautogui.typewrite(char_correto)
            else: digitar_caractere_com_clipboard(char_correto)
            time.sleep(calcular_delay(modo_velocidade, "normal_char"))
            if self.checar_parada_logica(): self._simulacao_concluida_sem_interrupcao = False; break
            
            if char_correto == ' ': time.sleep(calcular_delay_palavra(modo_velocidade))
            elif char_correto == '\n' or (char_correto == '.' and char_idx + 1 < len(texto_completo) and texto_completo[char_idx+1] == ' '):
                if modo_velocidade == "Normal": time.sleep(random.uniform(0.3, 0.7))
                else: time.sleep(random.uniform(0.02, 0.06))
            if self.checar_parada_logica(): self._simulacao_concluida_sem_interrupcao = False; break
        
        if self.simulacao_em_andamento and self._simulacao_concluida_sem_interrupcao:
            print("\n--- Simulação de digitação concluída! ---")
        # A flag self.simulacao_em_andamento será resetada no finally de ao_iniciar_simulacao

    def closeEvent(self, event):
        if self.simulacao_em_andamento:
            resposta = QMessageBox.question(self, "Sair?",
                                            "A simulação está em andamento. Deseja interrompê-la e sair?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                            QMessageBox.StandardButton.No)
            if resposta == QMessageBox.StandardButton.Yes:
                self.simulacao_em_andamento = False
                self._simulacao_concluida_sem_interrupcao = False
                try: keyboard.press_and_release(TECLA_DE_PARADA)
                except Exception as e: print(f"Erro ao simular tecla no fechamento: {e}")
                time.sleep(0.1) 
                event.accept() 
            else:
                event.ignore() 
        else:
            event.accept()

if __name__ == "__main__":
    pyautogui.FAILSAFE = True  
    pyautogui.PAUSE = 0.0      

    app = QApplication(sys.argv)
    window = SimuladorApp()
    window.show()
    sys.exit(app.exec())
