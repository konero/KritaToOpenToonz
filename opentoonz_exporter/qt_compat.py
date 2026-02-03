"""Qt Compatibility Layer

Handles compatibility between PyQt5 and PyQt6 for Krita plugins.
"""

# Try PyQt6 first (Krita 6+), fall back to PyQt5 (Krita 5)
try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
        QLabel, QPushButton, QProgressDialog, QMessageBox,
        QFileDialog, QCheckBox, QSpinBox, QLineEdit, QGroupBox,
        QApplication, QDialog, QDialogButtonBox, QComboBox
    )
    from PyQt6.QtCore import Qt, QRect, QUrl, QSettings, QStandardPaths
    from PyQt6.QtGui import QIcon, QDesktopServices
    
    PYQT_VERSION = 6

except ImportError:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
        QLabel, QPushButton, QProgressDialog, QMessageBox,
        QFileDialog, QCheckBox, QSpinBox, QLineEdit, QGroupBox,
        QApplication, QDialog, QDialogButtonBox, QComboBox
    )
    from PyQt5.QtCore import Qt, QRect, QUrl, QSettings, QStandardPaths
    from PyQt5.QtGui import QIcon, QDesktopServices
    
    PYQT_VERSION = 5


def get_window_modality():
    """Get the correct WindowModal enum value for the current Qt version."""
    return Qt.WindowModality.WindowModal
