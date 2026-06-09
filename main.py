import os
from pathlib import Path
from scraper import extract_info
from content_processor import save_markdown_from_html

from PySide6.QtCore import QObject, QThread, QUrl, Qt, Signal
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
)

try:
    from qt_material import apply_stylesheet
except ImportError:
    apply_stylesheet = None


class StyledButton(QPushButton):
    """Button following Material 3 guidelines."""
    def __init__(self, text: str, primary: bool = False):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setMinimumWidth(100)
        font = QFont()
        font.setPointSize(10)
        font.setWeight(QFont.Medium)
        self.setFont(font)
        
        if primary:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #80c784;
                    color: #000000;
                    border: none;
                    border-radius: 8px;
                    font-weight: 500;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #81c784;
                }
                QPushButton:pressed {
                    background-color: #7cb342;
                }
                QPushButton:disabled {
                    background-color: #404040;
                    color: #666666;
                }
                """
            )
        else:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #424242;
                    border-radius: 8px;
                    font-weight: 500;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                    border: 1px solid #616161;
                }
                QPushButton:pressed {
                    background-color: #1d1d1d;
                }
                QPushButton:disabled {
                    background-color: #1a1a1a;
                    color: #666666;
                    border: 1px solid #333333;
                }
                """
            )


class StyledLineEdit(QLineEdit):
    """Text input following Material 3 guidelines."""
    def __init__(self, placeholder: str = ""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(48)
        self.setStyleSheet(
            """
            QLineEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #424242;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #80c784;
                background-color: #1e1e1e;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
            """
        )


class StyledTextEdit(QTextEdit):
    """Text area following Material 3 guidelines."""
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            """
            QTextEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #424242;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                font-family: "Courier New", monospace;
            }
            QTextEdit:focus {
                border: 2px solid #80c784;
            }
            """
        )


class ScrapeWorker(QObject):
    finished = Signal(str, str)
    error = Signal(str)

    def __init__(self, url: str, output_dir: str):
        super().__init__()
        self.url = url
        self.output_dir = output_dir

    def run(self):
        try:
            html = extract_info(self.url)
            filepath, title = save_markdown_from_html(html, output_dir=self.output_dir, url=self.url)
            message = f"Guardado como: {filepath}\nTítulo: {title}"
            self.finished.emit(message, filepath)
        except Exception as err:
            self.error.emit(str(err))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MTAA Scraping Tool")
        self.setMinimumSize(750, 600)
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #121212;
            }
            """
        )
        self._default_output_dir = str(Path.home() / "mtaa-scraping-tool" / "output")

        self.url_input = StyledLineEdit("https://example.com/articulo")
        self.output_dir_input = StyledLineEdit(self._default_output_dir)

        self.browse_button = StyledButton("Seleccionar carpeta")
        self.browse_button.clicked.connect(self.choose_output_dir)

        self.scrape_button = StyledButton("Extraer Markdown", primary=True)
        self.scrape_button.clicked.connect(self.start_scraping)
        self.scrape_button.setMinimumHeight(44)

        self.open_file_button = StyledButton("Abrir archivo")
        self.open_file_button.setEnabled(False)
        self.open_file_button.clicked.connect(self.open_last_file)
        self.open_file_button.setMinimumHeight(44)

        self.status_message = QLabel("Listo")
        self.status_message.setWordWrap(True)
        self.status_message.setStyleSheet(
            """
            QLabel {
                color: #b0bec5;
                font-size: 13px;
                font-weight: 500;
            }
            """
        )

        self.log_output = StyledTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("El registro aparecerá aquí...")
        self.log_output.setMinimumHeight(200)

        self.setup_ui()

        self.thread = None
        self.worker = None
        self.last_output_file = None

    def setup_ui(self):
        """Build UI with original layout and Material 3 styling."""
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # URL input section
        url_layout = QVBoxLayout()
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(6)
        url_label = QLabel("URL de la página")
        url_label.setStyleSheet("color: #e0e0e0; font-weight: 500; font-size: 12px;")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)

        # Output directory section
        dir_layout = QHBoxLayout()
        dir_layout.setContentsMargins(0, 0, 0, 0)
        dir_layout.setSpacing(8)
        
        dir_input_layout = QVBoxLayout()
        dir_input_layout.setContentsMargins(0, 0, 0, 0)
        dir_input_layout.setSpacing(6)
        dir_label = QLabel("Directorio de salida")
        dir_label.setStyleSheet("color: #e0e0e0; font-weight: 500; font-size: 12px;")
        dir_input_layout.addWidget(dir_label)
        dir_input_layout.addWidget(self.output_dir_input)
        
        dir_layout.addLayout(dir_input_layout)
        dir_layout.addWidget(self.browse_button, alignment=Qt.AlignBottom)
        main_layout.addLayout(dir_layout)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        button_layout.addStretch()
        button_layout.addWidget(self.scrape_button)
        button_layout.addWidget(self.open_file_button)
        main_layout.addLayout(button_layout)

        # Log section
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(6)
        log_label = QLabel("Registro")
        log_label.setStyleSheet("color: #e0e0e0; font-weight: 500; font-size: 12px;")
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_output)
        main_layout.addLayout(log_layout)

        # Status message
        main_layout.addWidget(self.status_message)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def choose_output_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de salida", self.output_dir_input.text()
        )
        if folder:
            self.output_dir_input.setText(folder)

    def show_warning(self, title: str, message: str):
        """Show styled warning dialog."""
        msg_box = QMessageBox(QMessageBox.Warning, title, message, QMessageBox.Ok, self)
        self._apply_dialog_style(msg_box)
        msg_box.exec()

    def show_information(self, title: str, message: str):
        """Show styled information dialog."""
        msg_box = QMessageBox(QMessageBox.Information, title, message, QMessageBox.Ok, self)
        self._apply_dialog_style(msg_box)
        msg_box.exec()

    def show_critical(self, title: str, message: str):
        """Show styled critical dialog."""
        msg_box = QMessageBox(QMessageBox.Critical, title, message, QMessageBox.Ok, self)
        self._apply_dialog_style(msg_box)
        msg_box.exec()

    def _apply_dialog_style(self, dialog: QMessageBox):
        """Apply Material 3 styling to dialog."""
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(150)
        dialog.setStyleSheet(
            """
            QMessageBox {
                background-color: #1e1e1e;
            }
            QMessageBox QLabel {
                color: #e0e0e0;
            }
            QMessageBox QPushButton {
                background-color: #80c784;
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 500;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #81c784;
            }
            QMessageBox QPushButton:pressed {
                background-color: #7cb342;
            }
            """
        )

    def append_log(self, text: str):
        self.log_output.append(text)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def start_scraping(self):
        url = self.url_input.text().strip()
        output_dir = self.output_dir_input.text().strip() or self._default_output_dir

        if not url:
            self.show_warning("URL requerida", "Por favor ingresa una URL válida.")
            return

        if not output_dir:
            self.show_warning(
                "Directorio requerido", "Por favor selecciona un directorio de salida."
            )
            return

        os.makedirs(output_dir, exist_ok=True)
        self.set_controls_enabled(False)
        self.status_message.setText("⏳ Extrayendo contenido, por favor espera...")
        self.append_log(f"→ Iniciando extracción para: {url}")

        self.thread = QThread()
        self.worker = ScrapeWorker(url, output_dir)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_scrape_success)
        self.worker.error.connect(self.on_scrape_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.last_output_file = None
        self.open_file_button.setEnabled(False)

    def set_controls_enabled(self, enabled: bool):
        self.url_input.setEnabled(enabled)
        self.output_dir_input.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.scrape_button.setEnabled(enabled)

    def on_scrape_success(self, message: str, filepath: str):
        self.last_output_file = filepath
        self.append_log(f"✓ {message}")
        self.status_message.setText("✓ Extracción completada")
        self.status_message.setStyleSheet("color: #80c784; font-size: 13px; font-weight: 500;")
        self.open_file_button.setEnabled(True)
        self.show_information("Éxito", message)
        self.set_controls_enabled(True)

    def on_scrape_error(self, error_text: str):
        self.append_log(f"✗ Error: {error_text}")
        self.status_message.setText("✗ Error durante la extracción")
        self.status_message.setStyleSheet("color: #ef5350; font-size: 13px; font-weight: 500;")
        self.show_critical("Error", f"Error procesando el contenido:\n{error_text}")
        self.set_controls_enabled(True)

    def open_last_file(self):
        if not self.last_output_file:
            self.show_warning(
                "Archivo no disponible", "No hay un archivo generado para abrir."
            )
            return

        if not os.path.exists(self.last_output_file):
            self.show_warning(
                "Archivo no encontrado", "El archivo generado ya no existe."
            )
            self.open_file_button.setEnabled(False)
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(self.last_output_file))


def main():
    app = QApplication([])
    if apply_stylesheet is not None:
        try:
            apply_stylesheet(app, theme="dark_teal.xml")
        except Exception:
            pass

    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()

