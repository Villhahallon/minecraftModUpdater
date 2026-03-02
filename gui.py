import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QComboBox,
)
from PySide6.QtCore import QObject, QThread, Signal, QUrl, Qt
from PySide6.QtGui import QDesktopServices, QTextCursor

from core.config import Config
from core.updater import run_updater
  
class UpdaterWorker(QObject):
    log = Signal(str)
    finished = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            self.log.emit("Starting Updater...")
            results = run_updater(self.config)

            for line in results:
                self.log.emit(line)
            self.log.emit("Done ✨")
        except Exception as e:
            self.log.emit(f"Error: {e}")
        finally:
            self.finished.emit()
            

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minecraft Mod Updater")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        #minecraft version
        mc_laylout = QHBoxLayout()
        mc_laylout.addWidget(QLabel("Minecraft Version:"))
        self.mc_input = QLineEdit("1.21.11")
        mc_laylout.addWidget(self.mc_input)
        layout.addLayout(mc_laylout)

        #loader
        loader_layout = QHBoxLayout()
        loader_layout.addWidget(QLabel("Loader:"))
        self.loader_combo = QComboBox()
        self.loader_combo.addItems(["fabric", "forge", "quilt"])
        loader_layout.addWidget(self.loader_combo)
        layout.addLayout(loader_layout)

        #mod file picker
        mods_layout = QHBoxLayout()
        self.mods_path = QLineEdit("mods.txt")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.pick_mods_file)
        mods_layout.addWidget(QLabel("Mods file:"))
        mods_layout.addWidget(self.mods_path)
        mods_layout.addWidget(browse_btn)
        layout.addLayout(mods_layout)
        
        #run button
        self.run_button = QPushButton("Run updater")
        self.run_button.clicked.connect(self.run_updater)
        layout.addWidget(self.run_button)

        #output log
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.max_log_lines = 1000
        layout.addWidget(self.output)

        # Open mods folder button
        self.open_folder_btn = QPushButton("Open mods folder")
        self.open_folder_btn.clicked.connect(self.open_mods_folder)
        layout.addWidget(self.open_folder_btn)

    def pick_mods_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select mods.txt", "", "Text files (*.txt)")
        if path:
            self.mods_path.setText(path)

    def log(self, text: str):
        # Append new line
        self.output.append(text)
        # Trim old lines to avoid unbounded memory growth
        doc = self.output.document()
        # Remove oldest blocks while above limit
        while doc.blockCount() > self.max_log_lines:
            cursor = QTextCursor(doc)
            cursor.movePosition(QTextCursor.Start)
            cursor.select(QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            # remove the following newline
            cursor.deleteChar()

    def open_mods_folder(self):
        config = Config(
            minecraft_version=self.mc_input.text(),
            loader=self.loader_combo.currentText(),
            base_dir=Path("mods"),
            mods_file=Path(self.mods_path.text())
        )
        folder = config.mods_dir
        folder.mkdir(parents=True, exist_ok=True)

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(folder.resolve()))
        )

    def on_finished(self):
        self.run_button.setEnabled(True)
        self.open_folder_btn.setEnabled(True)

    def run_updater(self):
        self.output.clear()
        self.run_button.setEnabled(False)
        self.open_folder_btn.setEnabled(False)
    
        config = Config(
            minecraft_version=self.mc_input.text(),
            loader=self.loader_combo.currentText(),
            base_dir=Path("mods"),
            mods_file=Path(self.mods_path.text())
        )
       
        self.updater_thread = QThread()
        self.worker = UpdaterWorker(config)
            
        self.worker.moveToThread(self.updater_thread)

        #signals
        self.updater_thread.started.connect(self.worker.run)
        # ensure cross-thread log signals are queued to avoid direct cross-thread UI access
        self.worker.log.connect(self.log, Qt.QueuedConnection)
        self.worker.finished.connect(self.updater_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.updater_thread.deleteLater)
        self.updater_thread.finished.connect(self.on_finished)

        self.updater_thread.start()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 