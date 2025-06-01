import sys
import time
import random
import string
import pyautogui
import keyboard # Mantido para a tecla de parada global

try:
    import pyperclip
    PYPERCLIP_DISPONIVEL = True
    print("Pyperclip importado com sucesso.")
except ImportError:
    PYPERCLIP_DISPONIVEL = False
    print("Pyperclip não encontrado. Caracteres especiais podem não ser digitados corretamente.")
    print("Para instalar: pip install pyperclip")

# --- Configurações Globais ---
TECLA_DE_PARADA = 'esc'
# simulacao_em_andamento será uma variável de instância (self.simulacao_em_andamento)

# --- Configurações para Erros (mantidas globais) ---
CHANCE_DE_ERRO_UM_CHAR = 0.03
CHANCE_DE_ERRO_BLOCO = 0.015
TAMANHOS_BLOCO_ERRO = [3, 4, 5]
POSSIVEIS_CHARS_ERRO = string.ascii_lowercase
ASCII_SIMPLES_PARA_TYPEWRITE = string.ascii_letters + string.digits + string.punctuation + ' \n\t'


# --- Funções Auxiliares de Simulação (mantidas globais, pois não dependem do estado da GUI diretamente) ---
#     Elas serão chamadas por métodos da classe SimuladorApp.

def digitar_caractere_com_clipboard(char_para_digitar):
    """Digita um caractere usando o clipboard se necessário (para caracteres especiais)."""
    if not PYPERCLIP_DISPONIVEL:
        pyautogui.typewrite(char_para_digitar)
        return
    try:
        clipboard_original = pyperclip.paste()
        pyperclip.copy(char_para_digitar)
        # Pequena pausa para garantir que o clipboard foi atualizado e a aplicação alvo está pronta
        time.sleep(0.05) 
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.05) # Pausa após colar
        pyperclip.copy(clipboard_original) # Restaura o clipboard original
    except Exception as e:
        print(f"DEBUG: Erro ao usar pyperclip para '{char_para_digitar}': {e}. Tentando typewrite.")
        pyautogui.typewrite(char_para_digitar)

def calcular_delay(modo_velocidade, tipo_de_pausa="normal_char"):
    """Calcula os delays para a digitação, variando conforme o modo e o tipo de pausa."""
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
    return 0.05  # Fallback

def calcular_delay_palavra(modo_velocidade):
    """Calcula o delay após digitar um espaço (fim de palavra)."""
    if modo_velocidade == "Normal": return random.uniform(0.1, 0.3)
    elif modo_velocidade == "Time-Lapse": return random.uniform(0.005, 0.02)
    return 0.1


from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QTextEdit, QRadioButton, QPushButton,
                               QMessageBox, QButtonGroup, QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QScreen # Para centralizar a janela


class SimuladorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.simulacao_em_andamento = False
        self.setWindowTitle("Simulador de Digitação Realista - PySide6")
        self.init_ui()
        self.apply_styles()
        self._center_window()

    def init_ui(self):
        """Configura a interface gráfica do usuário."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20) # Margens externas
        main_layout.setSpacing(15) # Espaçamento entre seções

        # --- Seção de Entrada de Texto ---
        self.label_texto = QLabel("Cole o texto para simulação abaixo:")
        main_layout.addWidget(self.label_texto)

        self.campo_texto = QTextEdit()
        self.campo_texto.setPlaceholderText("Digite ou cole seu texto aqui...")
        self.campo_texto.setMinimumHeight(150) # Altura mínima para o campo de texto
        self.campo_texto.setText("""Olá, este é um texto de exemplo para testar erros em bloco.
Atenção para a simulação de digitação mais complexa.
O sistema tentará, às vezes, digitar um bloco de 3, 4 ou 5 caracteres errados,
e depois apagá-los antes de continuar com o texto correto.

Vamos ver como a palavra "sequência" será digitada, ou "paralelepípedo".
Números: 1234567890. Símbolos: !@#$%^&*()_+=-[]{};':",./<>?`~

Aproveite o simulador!""")
        main_layout.addWidget(self.campo_texto)

        # --- Seção de Opções de Velocidade ---
        self.label_velocidade = QLabel("Modo de Velocidade:")
        main_layout.addWidget(self.label_velocidade)

        opcoes_velocidade_layout = QHBoxLayout()
        self.modo_velocidade_group = QButtonGroup(self) # Para garantir exclusividade

        self.radio_normal = QRadioButton("Normal")
        self.radio_normal.setChecked(True) # Opção padrão
        self.modo_velocidade_group.addButton(self.radio_normal)
        opcoes_velocidade_layout.addWidget(self.radio_normal)

        self.radio_timelapse = QRadioButton("Time-Lapse")
        self.modo_velocidade_group.addButton(self.radio_timelapse)
        opcoes_velocidade_layout.addWidget(self.radio_timelapse)
        
        opcoes_velocidade_layout.addStretch() # Empurra os radios para a esquerda
        main_layout.addLayout(opcoes_velocidade_layout)

        # --- Seção de Botão e Status ---
        # Espaçador para empurrar o botão para baixo
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.status_label = QLabel("") # Para feedback futuro, se necessário na GUI
        self.status_label.setObjectName("StatusLabel") # Para estilização específica
        main_layout.addWidget(self.status_label)
        
        self.botao_iniciar = QPushButton("Iniciar Simulação")
        self.botao_iniciar.clicked.connect(self.ao_iniciar_simulacao)
        self.botao_iniciar.setMinimumHeight(40) # Altura mínima para o botão
        main_layout.addWidget(self.botao_iniciar)
        
        self.setLayout(main_layout)
        self.setMinimumSize(550, 450) # Tamanho mínimo da janela

    def apply_styles(self):
        """Aplica os estilos QSS para um visual moderno."""
        font_geral = QFont("Arial", 10)
        font_label_titulo = QFont("Arial", 10) # Pode ser um pouco maior ou bold se quiser
        font_botao = QFont("Arial", 11, QFont.Weight.Bold)

        self.setFont(font_geral)

        qss = """
            QWidget {
                background-color: #F8F9FA; /* Fundo geral da janela (cinza bem claro) */
            }
            QLabel {
                color: #212529; /* Cor de texto escura para labels */
                padding-bottom: 2px; /* Pequeno espaço abaixo do label */
            }
            QTextEdit {
                background-color: #FFFFFF; /* Fundo branco para o campo de texto */
                border: 1px solid #CED4DA; /* Borda cinza clara */
                border-radius: 8px; /* Cantos arredondados */
                padding: 8px; /* Espaçamento interno */
                font-size: 10pt;
            }
            QRadioButton {
                font-size: 10pt;
                spacing: 5px; /* Espaço entre o botão e o texto */
                color: #212529;
            }
            QRadioButton::indicator {
                width: 16px; /* Tamanho do indicador do radio button */
                height: 16px;
            }
            QPushButton {
                background-color: #007BFF; /* Azul primário */
                color: white;
                border: none;
                border-radius: 8px; /* Cantos arredondados */
                padding: 10px 15px; /* Espaçamento interno (vertical, horizontal) */
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3; /* Azul mais escuro no hover */
            }
            QPushButton:pressed {
                background-color: #004085; /* Azul ainda mais escuro ao pressionar */
            }
            #StatusLabel { /* Estilo para o status label, se usado */
                color: #6C757D; /* Cinza para texto de status */
                font-size: 9pt;
            }
        """
        self.setStyleSheet(qss)
        self.label_texto.setFont(font_label_titulo)
        self.label_velocidade.setFont(font_label_titulo)
        # self.botao_iniciar.setFont(font_botao) # O QSS já define a fonte do botão

    def _center_window(self):
        """Centraliza a janela na tela."""
        try:
            screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
            window_geometry = self.geometry()
            x = (screen_geometry.width() - window_geometry.width()) // 2
            y = (screen_geometry.height() - window_geometry.height()) // 2
            self.move(x, y)
        except Exception as e:
            print(f"Não foi possível centralizar a janela: {e}")


    # --- Métodos da Lógica de Simulação Adaptados ---
    @Slot() # Indica que é um slot para sinais do Qt
    def ao_iniciar_simulacao(self):
        """Chamado quando o botão 'Iniciar Simulação' é clicado."""
        if self.simulacao_em_andamento:
            QMessageBox.warning(self, "Atenção", "Uma simulação já está em andamento.")
            return

        texto_input = self.campo_texto.toPlainText().strip()
        if not texto_input:
            QMessageBox.critical(self, "Erro", "O campo de texto está vazio.")
            return

        modo_selecionado = "Normal" if self.radio_normal.isChecked() else "Time-Lapse"

        self.hide() # Esconde a janela da GUI

        # Feedback no console (mantido do original)
        print(f"\nIniciando simulação em modo: {modo_selecionado}")
        print(f"Você tem 5 segundos para posicionar o cursor no local desejado...")
        print(f"Pressione '{TECLA_DE_PARADA}' (Esc) a qualquer momento para parar.")
        if not PYPERCLIP_DISPONIVEL:
            print("AVISO: Pyperclip não está instalado. Caracteres acentuados podem falhar.")
        else:
            print("INFO: Pyperclip está disponível, será usado para caracteres especiais.")
        print(f"ATENÇÃO: Verifique se o layout do seu teclado no SO está correto (Ex: Português Brasil ABNT2).")

        # Contagem regressiva no console
        for i in range(5, 0, -1):
            if keyboard.is_pressed(TECLA_DE_PARADA): # Checagem preliminar
                print(f"\n--- Tecla '{TECLA_DE_PARADA}' pressionada. Interrompendo simulação ANTES de iniciar.")
                self.show()
                return
            print(f"{i}...")
            time.sleep(1)
        
        print("Iniciando digitação!")

        try:
            self.executar_simulacao_logica(texto_input, modo_selecionado)
        except pyautogui.FailSafeException:
            QMessageBox.critical(self, "Fail-Safe Ativado!",
                                 "Simulação interrompida (mouse no canto superior esquerdo).")
            print("--- PYAUTOGUI FAIL-SAFE TRIGGERED ---")
        except Exception as e:
            QMessageBox.critical(self, "Erro na Simulação",
                                 f"Ocorreu um erro inesperado: {e}")
            print(f"Erro detalhado na simulação: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.simulacao_em_andamento = False # Garante que resetamos o estado
            self.show() # Mostra a janela da GUI novamente
            self.status_label.setText("") # Limpa o status label

    def checar_parada_logica(self):
        """Verifica se a tecla de parada foi pressionada."""
        if keyboard.is_pressed(TECLA_DE_PARADA):
            print(f"\n--- Tecla '{TECLA_DE_PARADA}' pressionada. Interrompendo simulação. ---")
            self.simulacao_em_andamento = False
            return True
        return False

    def digitar_sequencia_logica(self, sequencia, modo_velocidade, tipo_delay_char="normal_char"):
        """Digita uma sequência de caracteres, um por um, com delay."""
        for char_item in sequencia:
            if not self.simulacao_em_andamento: return False # Checa antes de cada char
            delay_char_atual = calcular_delay(modo_velocidade, tipo_delay_char)
            if char_item in ASCII_SIMPLES_PARA_TYPEWRITE:
                pyautogui.typewrite(char_item)
            else:
                digitar_caractere_com_clipboard(char_item)
            time.sleep(delay_char_atual)
            if self.checar_parada_logica(): return False
        return True

    def executar_simulacao_logica(self, texto_completo, modo_velocidade):
        """Executa a lógica principal da simulação de digitação."""
        self.simulacao_em_andamento = True
        texto_completo = texto_completo.replace('\r\n', '\n').replace('\r', '\n')

        for char_idx, char_correto in enumerate(texto_completo):
            if not self.simulacao_em_andamento: break

            # Chance de erro em bloco
            if char_correto.strip() and random.random() < CHANCE_DE_ERRO_BLOCO:
                tamanho_bloco = random.choice(TAMANHOS_BLOCO_ERRO)
                print(f"DEBUG: Simulando ERRO EM BLOCO de {tamanho_bloco} caracteres antes de '{char_correto}'")
                bloco_errado = [random.choice(POSSIVEIS_CHARS_ERRO) for _ in range(tamanho_bloco)]
                if char_correto.isupper() and bloco_errado[0].isalpha():
                    bloco_errado[0] = bloco_errado[0].upper()
                
                if not self.digitar_sequencia_logica(bloco_errado, modo_velocidade, "char_errado_bloco"): break
                if self.checar_parada_logica(): break
                time.sleep(calcular_delay(modo_velocidade, "percepcao_erro_bloco"))
                if self.checar_parada_logica(): break
                
                print(f"DEBUG: Apagando bloco de {tamanho_bloco} caracteres...")
                for _ in range(tamanho_bloco):
                    if not self.simulacao_em_andamento: break
                    pyautogui.press('backspace')
                    time.sleep(calcular_delay(modo_velocidade, "entre_backspaces_bloco"))
                    if self.checar_parada_logica(): break
                if not self.simulacao_em_andamento: break
                
                time.sleep(calcular_delay(modo_velocidade, "pos_correcao_bloco"))
                if self.checar_parada_logica(): break

            # Chance de erro de um caractere
            elif char_correto.strip() and random.random() < CHANCE_DE_ERRO_UM_CHAR:
                print(f"DEBUG: Simulando ERRO DE UM CHAR para '{char_correto}'")
                char_errado = random.choice(POSSIVEIS_CHARS_ERRO)
                while char_errado == char_correto.lower() and len(POSSIVEIS_CHARS_ERRO) > 1:
                    char_errado = random.choice(POSSIVEIS_CHARS_ERRO)
                if char_correto.isupper() and char_errado.isalpha():
                    char_errado = char_errado.upper()

                delay_digitacao_errado = calcular_delay(modo_velocidade, "normal_char")
                if char_errado in ASCII_SIMPLES_PARA_TYPEWRITE: pyautogui.typewrite(char_errado)
                else: digitar_caractere_com_clipboard(char_errado)
                time.sleep(delay_digitacao_errado)
                if self.checar_parada_logica(): break

                time.sleep(calcular_delay(modo_velocidade, "percepcao_erro_um_char"))
                if self.checar_parada_logica(): break
                
                pyautogui.press('backspace')
                time.sleep(calcular_delay(modo_velocidade, "pos_backspace_um_char"))
                if self.checar_parada_logica(): break

                delay_digitacao_correto = calcular_delay(modo_velocidade, "correcao_char_um_char")
                if char_correto in ASCII_SIMPLES_PARA_TYPEWRITE: pyautogui.typewrite(char_correto)
                else: digitar_caractere_com_clipboard(char_correto)
                time.sleep(delay_digitacao_correto)
                if self.checar_parada_logica(): break
                continue # Pula a digitação normal do char_correto

            # Digitação normal do char_correto
            delay_normal_char = calcular_delay(modo_velocidade, "normal_char")
            if char_correto in ASCII_SIMPLES_PARA_TYPEWRITE:
                pyautogui.typewrite(char_correto)
            else:
                digitar_caractere_com_clipboard(char_correto)
            time.sleep(delay_normal_char)
            if self.checar_parada_logica(): break

            # Pausas adicionais
            if char_correto == ' ':
                time.sleep(calcular_delay_palavra(modo_velocidade))
            elif char_correto == '\n' or \
                 (char_correto == '.' and char_idx + 1 < len(texto_completo) and texto_completo[char_idx+1] == ' '):
                if modo_velocidade == "Normal": time.sleep(random.uniform(0.3, 0.7))
                else: time.sleep(random.uniform(0.02, 0.06))
            if self.checar_parada_logica(): break

        if self.simulacao_em_andamento:
            print("\n--- Simulação de digitação concluída! ---")
        else:
            # A mensagem de interrupção já foi impressa por checar_parada_logica
            pass
        self.simulacao_em_andamento = False


    def closeEvent(self, event):
        """Chamado quando o usuário tenta fechar a janela."""
        if self.simulacao_em_andamento:
            resposta = QMessageBox.question(self, "Sair?",
                                            "A simulação parece estar em andamento. Deseja interrompê-la e sair?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                            QMessageBox.StandardButton.No)
            if resposta == QMessageBox.StandardButton.Yes:
                self.simulacao_em_andamento = False
                try:
                    # Tenta pressionar ESC para garantir que a thread do keyboard listener (se houver)
                    # ou a lógica de pyautogui.PAUSE seja afetada.
                    keyboard.press_and_release(TECLA_DE_PARADA)
                except Exception as e:
                    print(f"Erro ao tentar simular tecla de parada no fechamento: {e}")
                time.sleep(0.1) # Pequena pausa para processamento
                event.accept() # Fecha a janela
            else:
                event.ignore() # Não fecha a janela
        else:
            event.accept()


if __name__ == "__main__":
    pyautogui.FAILSAFE = True  # Essencial para segurança com pyautogui
    pyautogui.PAUSE = 0.0      # Pyautogui não fará pausas automáticas entre as chamadas

    app = QApplication(sys.argv)
    window = SimuladorApp()
    window.show()
    sys.exit(app.exec())
