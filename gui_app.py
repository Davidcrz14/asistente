import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QPalette, QColor, QFont
import qtawesome as qta
from main import procesar_comando_con_ia, ejecutar_comando
import speech_recognition as sr

class MicrophoneButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(qta.icon('fa5s.microphone', color='white'))
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border-radius: 30px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
            }
        """)
        self.setFixedSize(80, 80)

class LiveTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.setFont(QFont("Arial", 12))

class SpeechRecognitionThread(QThread):
    text_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, recognizer, microphone):
        super().__init__()
        self.recognizer = recognizer
        self.microphone = microphone
        self.is_listening = False

    def run(self):
        self.is_listening = True
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio, language="es-ES")
                    self.text_received.emit(text)
                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    self.error_occurred.emit(f"Error en el servicio de reconocimiento de voz: {e}")
                except Exception as e:
                    self.error_occurred.emit(f"Error inesperado: {e}")

    def stop(self):
        self.is_listening = False

class MainWindow(QMainWindow):
    update_live_text = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asistente de Voz")
        self.setGeometry(100, 100, 500, 600)

        self.set_dark_palette()

        self.live_text_edit = LiveTextEdit()
        self.response_text_edit = QTextEdit()
        self.response_text_edit.setReadOnly(True)
        self.response_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #34495e;
                color: #bdc3c7;
                border: 2px solid #2c3e50;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.response_text_edit.setFont(QFont("Arial", 10))
        self.mic_button = MicrophoneButton()
        self.status_label = QLabel("Presiona el botón para hablar")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #bdc3c7; font-size: 14px;")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Comando en vivo:"))
        layout.addWidget(self.live_text_edit)
        layout.addWidget(QLabel("Respuesta:"))
        layout.addWidget(self.response_text_edit)
        layout.addWidget(self.status_label)
        layout.addWidget(self.mic_button, alignment=Qt.AlignmentFlag.AlignCenter)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.mic_button.clicked.connect(self.toggle_listening)
        self.update_live_text.connect(self.live_text_edit.setText)

        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.speech_thread = SpeechRecognitionThread(self.recognizer, self.microphone)
        self.speech_thread.text_received.connect(self.on_text_received)
        self.speech_thread.error_occurred.connect(self.on_error)

        self.live_text = ""

    def set_dark_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1a1a1a"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#ecf0f1"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#2c3e50"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#34495e"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ecf0f1"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ecf0f1"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#ecf0f1"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#34495e"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ecf0f1"))
        palette.setColor(QPalette.ColorRole.BrightText, QColor("#e74c3c"))
        palette.setColor(QPalette.ColorRole.Link, QColor("#3498db"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#3498db"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ecf0f1"))
        self.setPalette(palette)

    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.is_listening = True
        self.mic_button.setIcon(qta.icon('fa5s.stop', color='white'))
        self.status_label.setText("Escuchando... Di tu comando.")
        self.live_text = ""
        self.update_live_text.emit("")
        self.animate_button()
        self.speech_thread.start()

    def stop_listening(self):
        self.is_listening = False
        self.mic_button.setIcon(qta.icon('fa5s.microphone', color='white'))
        self.status_label.setText("Procesando comando...")
        if hasattr(self, 'button_animation'):
            self.button_animation.stop()
        self.speech_thread.stop()
        self.speech_thread.wait()
        QTimer.singleShot(100, self.process_command)  # Añadimos un pequeño retraso

    def on_text_received(self, text):
        self.live_text += text + " "
        self.update_live_text.emit(self.live_text)

    def on_error(self, error_message):
        self.status_label.setText(error_message)

    def process_command(self):
        if self.live_text.strip():  # Verificamos que el texto no esté vacío después de quitar espacios
            comando_procesado = procesar_comando_con_ia(self.live_text)
            respuesta = ejecutar_comando(comando_procesado, self.live_text)
            self.response_text_edit.append(f"Comando: {self.live_text}\nRespuesta: {respuesta}\n")
            self.status_label.setText("Comando procesado. Listo para el siguiente.")
        else:
            self.status_label.setText("No se detectó ningún comando. Intenta de nuevo.")
        self.live_text = ""  # Limpiamos el texto después de procesarlo
        self.update_live_text.emit("")  # Actualizamos el widget de texto en vivo

    def animate_button(self):
        animation = QPropertyAnimation(self.mic_button, b"geometry")
        animation.setDuration(1000)
        animation.setLoopCount(-1)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        start = self.mic_button.geometry()
        end = start.adjusted(-5, -5, 5, 5)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.start()
        self.button_animation = animation

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
