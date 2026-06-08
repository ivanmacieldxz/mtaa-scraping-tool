import os
from pathlib import Path
from scraper import extract_info
from content_processor import save_markdown_from_html

from PySide6.QtCore import QObject, QThread, Signal
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


class ScrapeWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, url: str, output_dir: str):
        super().__init__()
        self.url = url
        self.output_dir = output_dir

    def run(self):
        try:
            html = extract_info(self.url)
            filepath, title = save_markdown_from_html(html, output_dir=self.output_dir)
            message = f"Guardado como: {filepath}\nTítulo: {title}"
            self.finished.emit(message)
        except Exception as err:
            self.error.emit(str(err))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MTAA Scraping Tool")
        self.setMinimumSize(700, 460)
        self._default_output_dir = str(Path.home() / "mtaa-scraping-tool" / "output")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/articulo")

        self.output_dir_input = QLineEdit(self._default_output_dir)
        self.output_dir_input.setPlaceholderText("Directorio de salida")

        self.browse_button = QPushButton("Seleccionar carpeta")
        self.browse_button.clicked.connect(self.choose_output_dir)

        self.scrape_button = QPushButton("Extraer y guardar Markdown")
        self.scrape_button.clicked.connect(self.start_scraping)

        self.status_message = QLabel("Listo.")
        self.status_message.setWordWrap(True)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("El registro de la extracción aparecerá aquí...")

        self.setup_ui()

        self.thread = None
        self.worker = None

    def setup_ui(self):
        url_layout = QVBoxLayout()
        url_layout.addWidget(QLabel("URL de la página"))
        url_layout.addWidget(self.url_input)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Directorio de salida"))
        dir_layout.addWidget(self.output_dir_input)
        dir_layout.addWidget(self.browse_button)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.scrape_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(url_layout)
        main_layout.addLayout(dir_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel("Registro"))
        main_layout.addWidget(self.log_output)
        main_layout.addWidget(self.status_message)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def choose_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida", self.output_dir_input.text())
        if folder:
            self.output_dir_input.setText(folder)

    def append_log(self, text: str):
        self.log_output.append(text)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def start_scraping(self):
        url = self.url_input.text().strip()
        output_dir = self.output_dir_input.text().strip() or self._default_output_dir

        if not url:
            QMessageBox.warning(self, "URL requerida", "Por favor ingresa una URL válida.")
            return

        if not output_dir:
            QMessageBox.warning(self, "Directorio requerido", "Por favor selecciona un directorio de salida.")
            return

        os.makedirs(output_dir, exist_ok=True)
        self.set_controls_enabled(False)
        self.status_message.setText("Extrayendo contenido, por favor espera...")
        self.append_log(f"Iniciando extracción para: {url}")

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

    def set_controls_enabled(self, enabled: bool):
        self.url_input.setEnabled(enabled)
        self.output_dir_input.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.scrape_button.setEnabled(enabled)

    def on_scrape_success(self, message: str):
        self.append_log(f"✔ {message}")
        self.status_message.setText("Extracción completada.")
        QMessageBox.information(self, "Éxito", message)
        self.set_controls_enabled(True)

    def on_scrape_error(self, error_text: str):
        self.append_log(f"✕ Error: {error_text}")
        self.status_message.setText("Ocurrió un error durante la extracción.")
        QMessageBox.critical(self, "Error", f"Error procesando el contenido:\n{error_text}")
        self.set_controls_enabled(True)


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
