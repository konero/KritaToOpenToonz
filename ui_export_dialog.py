"""Export to OpenToonz Dialog

Modal dialog for exporting to OpenToonz scene format.
"""

import os
import sys
import krita

from .qt_compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QProgressDialog, QMessageBox,
    QFileDialog, QCheckBox, QSpinBox, QGroupBox, QLineEdit,
    QApplication, get_window_modality, QUrl, QDesktopServices,
    QDialog, QDialogButtonBox, QComboBox, QSettings, QStandardPaths
)
from .config import (
    VERSION, PLUGIN_NAME, PLUGIN_ID,
    get_opentoonz_default_paths, get_opentoonz_executable_filter,
    SETTINGS_OPENTOONZ_PATH, SETTINGS_EXPORT_PATH,
    SETTINGS_FLATTEN_GROUPS, SETTINGS_INCLUDE_INVISIBLE,
    SETTINGS_INCLUDE_REFERENCE, SETTINGS_INCLUDE_STATIC
)
from .tnz_exporter import TNZExporter
from .core.exporter import ExportOptions


def get_default_export_path() -> str:
    """Get the default export path based on the operating system.
    
    Returns the user's Documents folder on all platforms.
    
    Returns:
        Path to the default export directory.
    """
    docs_path = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DocumentsLocation
    )
    
    if docs_path and os.path.isdir(docs_path):
        return docs_path
    
    # Fallback to home directory if Documents doesn't exist
    return os.path.expanduser("~")


def find_opentoonz_executable() -> str:
    """Try to find OpenToonz executable in default locations.
    
    Returns:
        Path to OpenToonz executable if found, empty string otherwise.
    """
    for path in get_opentoonz_default_paths():
        expanded_path = os.path.expanduser(path)
        if os.path.isfile(expanded_path):
            return expanded_path
    return ""


class OpenToonzExportDialog(QDialog):
    """Modal dialog for exporting to OpenToonz scene format.
    
    Provides options for specifying the OpenToonz path and output location.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Export Animation to OpenToonz Scene - v{VERSION}")
        self.setMinimumWidth(550)
        
        self._document = krita.Krita.instance().activeDocument()
        self._settings = QSettings("krita", PLUGIN_ID)
        
        # Load saved paths or use defaults
        self._opentoonz_path = self._settings.value(
            SETTINGS_OPENTOONZ_PATH, 
            find_opentoonz_executable()
        )
        self._export_path = self._settings.value(
            SETTINGS_EXPORT_PATH, 
            get_default_export_path()
        )
        
        self._setup_ui()
        self._connect_signals()
        self._load_initial_paths()
    
    def _setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # Header description
        header_label = QLabel(
            "<b>Export Animation to OpenToonz Scene</b><br>"
            "Exports your Krita animation layers as PNG sequences and creates "
            "an OpenToonz scene file (.tnz) with proper timing."
        )
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        # Tabs for Export and Settings
        from PyQt5.QtWidgets import QTabWidget, QWidget
        tab_widget = QTabWidget()

        # --- Export Tab ---
        export_tab = QWidget()
        export_layout = QVBoxLayout(export_tab)
        export_layout.setContentsMargins(8, 8, 8, 8)
        export_layout.setSpacing(10)

        # Output Location Group
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(8, 8, 8, 8)
        output_layout.setSpacing(6)

        output_label = QLabel("Export location (a subfolder will be created with scene name):")
        output_layout.addWidget(output_label)

        output_row = QHBoxLayout()
        self._output_path_edit = QLineEdit()
        self._output_path_edit.setPlaceholderText("Select output location...")
        self._output_path_edit.setToolTip(
            "Base directory for export.\n"
            "A subfolder with the scene name will be created here."
        )
        output_row.addWidget(self._output_path_edit)

        self._browse_output_button = QPushButton("Browse...")
        output_row.addWidget(self._browse_output_button)
        output_layout.addLayout(output_row)

        filename_row = QHBoxLayout()
        filename_row.addWidget(QLabel("Scene name:"))
        self._filename_edit = QLineEdit()
        self._filename_edit.setPlaceholderText("scene_name")
        self._filename_edit.setToolTip(
            "Name for the scene and export folder.\n"
            "Creates: [location]/[name]/[name].tnz"
        )
        filename_row.addWidget(self._filename_edit)
        output_layout.addLayout(filename_row)

        output_group.setLayout(output_layout)
        export_layout.addWidget(output_group)

        # Export Options Group
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout()
        options_layout.setContentsMargins(8, 8, 8, 8)
        options_layout.setSpacing(6)

        self._flatten_groups_checkbox = QCheckBox("Flatten animated groups")
        self._flatten_groups_checkbox.setChecked(True)
        self._flatten_groups_checkbox.setToolTip(
            "Merge group layers into a single flattened image.\n"
            "Useful when a group contains separate line/color layers\n"
            "that should be combined for the final export."
        )
        options_layout.addWidget(self._flatten_groups_checkbox)

        self._invisible_checkbox = QCheckBox("Include invisible layers")
        self._invisible_checkbox.setChecked(False)
        self._invisible_checkbox.setToolTip(
            "Export animated layers that are currently hidden in the document."
        )
        options_layout.addWidget(self._invisible_checkbox)

        self._reference_checkbox = QCheckBox("Include reference layers (grey)")
        self._reference_checkbox.setChecked(False)
        self._reference_checkbox.setToolTip(
            "Export layers marked with a grey color label.\n"
            "These are typically used as animation reference guides."
        )
        options_layout.addWidget(self._reference_checkbox)

        self._static_checkbox = QCheckBox("Include non-animated layers")
        self._static_checkbox.setChecked(False)
        self._static_checkbox.setToolTip(
            "Export layers without animation keyframes.\n"
            "These will appear as a single held frame from start to end.\n"
            "Useful for backgrounds, layouts, peg bars, or safety margins."
        )
        options_layout.addWidget(self._static_checkbox)

        options_group.setLayout(options_layout)
        export_layout.addWidget(options_group)

        export_layout.addStretch()
        tab_widget.addTab(export_tab, "Export")

        # --- Settings Tab ---
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setContentsMargins(12, 12, 12, 12)
        settings_layout.setSpacing(10)

        toonz_group = QGroupBox("OpenToonz Configuration")
        toonz_layout = QVBoxLayout()
        toonz_layout.setContentsMargins(8, 8, 8, 8)
        toonz_layout.setSpacing(6)

        toonz_label = QLabel("Path to OpenToonz executable:")
        toonz_layout.addWidget(toonz_label)

        toonz_row = QHBoxLayout()
        self._opentoonz_path_edit = QLineEdit()
        self._opentoonz_path_edit.setPlaceholderText(self._get_opentoonz_placeholder())
        self._opentoonz_path_edit.setToolTip(
            "Path to the OpenToonz executable.\n"
            "This is needed to locate OpenToonz tools and verify compatibility."
        )
        toonz_row.addWidget(self._opentoonz_path_edit)

        self._browse_toonz_button = QPushButton("Browse...")
        toonz_row.addWidget(self._browse_toonz_button)
        toonz_layout.addLayout(toonz_row)

        os_info = self._get_os_info_text()
        os_label = QLabel(os_info)
        os_label.setStyleSheet("color: gray; font-size: 10px;")
        os_label.setWordWrap(True)
        toonz_layout.addWidget(os_label)

        toonz_group.setLayout(toonz_layout)
        settings_layout.addWidget(toonz_group)
        settings_layout.addStretch()
        tab_widget.addTab(settings_tab, "Settings")

        layout.addWidget(tab_widget)

        # === Dialog Buttons ===
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self._ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_button.setText("Export")

        button_box.accepted.connect(self._on_export)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
    
    def _get_opentoonz_placeholder(self) -> str:
        """Get placeholder text for OpenToonz path based on OS."""
        if sys.platform == "win32":
            return "C:\\Program Files\\OpenToonz\\OpenToonz.exe"
        elif sys.platform == "darwin":
            return "/Applications/OpenToonz.app/Contents/MacOS/OpenToonz"
        else:
            return "/usr/bin/opentoonz"
    
    def _get_os_info_text(self) -> str:
        """Get informational text about the current OS."""
        if sys.platform == "win32":
            return "Detected OS: Windows. Looking for OpenToonz.exe"
        elif sys.platform == "darwin":
            return "Detected OS: macOS. Looking for OpenToonz.app"
        else:
            return f"Detected OS: {sys.platform}. Looking for opentoonz binary"
    
    def _connect_signals(self):
        """Connect UI signals to slots."""
        self._browse_toonz_button.clicked.connect(self._browse_opentoonz)
        self._browse_output_button.clicked.connect(self._browse_output)
    
    def _load_initial_paths(self):
        """Load saved paths into the UI."""
        if self._opentoonz_path:
            self._opentoonz_path_edit.setText(self._opentoonz_path)
        
        if self._export_path:
            self._output_path_edit.setText(self._export_path)
        
        # Set default filename from document name
        if self._document:
            doc_name = self._document.name()
            if doc_name:
                # Remove extension if present
                if '.' in doc_name:
                    doc_name = os.path.splitext(doc_name)[0]
                self._filename_edit.setText(doc_name)
            else:
                self._filename_edit.setText("untitled_scene")
        else:
            self._filename_edit.setText("new_scene")

        # Load persisted option states (handle string/boolean variants)
        def _read_bool(key, default):
            val = self._settings.value(key, default)
            if isinstance(val, str):
                return val.lower() in ("1", "true", "yes", "on")
            return bool(val)

        try:
            self._flatten_groups_checkbox.setChecked(
                _read_bool(SETTINGS_FLATTEN_GROUPS, self._flatten_groups_checkbox.isChecked())
            )
            self._invisible_checkbox.setChecked(
                _read_bool(SETTINGS_INCLUDE_INVISIBLE, self._invisible_checkbox.isChecked())
            )
            self._reference_checkbox.setChecked(
                _read_bool(SETTINGS_INCLUDE_REFERENCE, self._reference_checkbox.isChecked())
            )
            self._static_checkbox.setChecked(
                _read_bool(SETTINGS_INCLUDE_STATIC, self._static_checkbox.isChecked())
            )
        except Exception:
            # If settings are missing or of unexpected type, ignore and keep defaults
            pass
    
    def _browse_opentoonz(self):
        """Open file dialog to select OpenToonz executable."""
        start_dir = ""
        current_path = self._opentoonz_path_edit.text()
        if current_path and os.path.exists(os.path.dirname(current_path)):
            start_dir = os.path.dirname(current_path)
        elif sys.platform == "win32":
            start_dir = "C:\\Program Files"
        elif sys.platform == "darwin":
            start_dir = "/Applications"
        else:
            start_dir = "/usr"
        
        file_filter = get_opentoonz_executable_filter()
        
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select OpenToonz Executable",
            start_dir,
            file_filter
        )
        
        if path:
            self._opentoonz_path_edit.setText(path)
    
    def _browse_output(self):
        """Open file dialog to select output directory."""
        start_dir = self._output_path_edit.text() or get_default_export_path()
        
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            start_dir
        )
        
        if path:
            self._output_path_edit.setText(path)
    
    def _validate_inputs(self) -> bool:
        """Validate user inputs before export.
        
        Returns:
            True if all inputs are valid, False otherwise.
        """
        # OpenToonz path is required for script execution
        opentoonz_path = self._opentoonz_path_edit.text().strip()
        if not opentoonz_path:
            QMessageBox.warning(
                self,
                "Missing OpenToonz Path",
                "Please specify the path to OpenToonz executable.\n\n"
                "This is required to generate the scene file."
            )
            return False
        
        if not os.path.isfile(opentoonz_path):
            QMessageBox.warning(
                self,
                "Invalid OpenToonz Path",
                f"The OpenToonz executable was not found:\n{opentoonz_path}"
            )
            return False
        
        output_path = self._output_path_edit.text().strip()
        if not output_path:
            QMessageBox.warning(
                self,
                "Missing Output Path",
                "Please specify an output directory for the scene file."
            )
            return False
        
        if not os.path.isdir(output_path):
            QMessageBox.warning(
                self,
                "Invalid Output Path",
                f"The output directory does not exist:\n{output_path}"
            )
            return False
        
        filename = self._filename_edit.text().strip()
        if not filename:
            QMessageBox.warning(
                self,
                "Missing Filename",
                "Please specify a filename for the scene."
            )
            return False
        
        # Check for invalid characters in filename
        invalid_chars = '<>:"/\\|?*'
        if any(c in filename for c in invalid_chars):
            QMessageBox.warning(
                self,
                "Invalid Filename",
                f"Filename cannot contain these characters: {invalid_chars}"
            )
            return False
        
        return True
    
    def _save_settings(self):
        """Save current settings for next time."""
        opentoonz_path = self._opentoonz_path_edit.text().strip()
        if opentoonz_path:
            self._settings.setValue(SETTINGS_OPENTOONZ_PATH, opentoonz_path)
        
        output_path = self._output_path_edit.text().strip()
        if output_path:
            self._settings.setValue(SETTINGS_EXPORT_PATH, output_path)
        # Save export option states
        try:
            self._settings.setValue(SETTINGS_FLATTEN_GROUPS, int(self._flatten_groups_checkbox.isChecked()))
            self._settings.setValue(SETTINGS_INCLUDE_INVISIBLE, int(self._invisible_checkbox.isChecked()))
            self._settings.setValue(SETTINGS_INCLUDE_REFERENCE, int(self._reference_checkbox.isChecked()))
            self._settings.setValue(SETTINGS_INCLUDE_STATIC, int(self._static_checkbox.isChecked()))
        except Exception:
            pass
    
    def _on_export(self):
        """Handle export button click."""
        if not self._validate_inputs():
            return
        
        if not self._document:
            QMessageBox.warning(
                self,
                "No Document",
                "No active document to export. Please open an animation first."
            )
            return
        
        self._save_settings()
        
        opentoonz_path = self._opentoonz_path_edit.text().strip()
        output_path = self._output_path_edit.text().strip()
        scene_name = self._filename_edit.text().strip()
        
        # Remove .tnz extension if user added it (we add it automatically)
        if scene_name.endswith('.tnz'):
            scene_name = scene_name[:-4]
        
        # The actual output will be: output_path/scene_name/scene_name.tnz
        scene_folder = os.path.normpath(os.path.join(output_path, scene_name))
        full_tnz_path = os.path.join(scene_folder, f"{scene_name}.tnz")
        
        # Check if scene folder already exists
        if os.path.exists(scene_folder):
            reply = QMessageBox.question(
                self,
                "Folder Exists",
                f"The export folder already exists:\n{scene_folder}\n\n"
                "Existing files may be overwritten. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Create progress dialog
        progress = QProgressDialog(
            "Exporting animation...",
            "Cancel",
            0, 100,
            self
        )
        progress.setWindowModality(get_window_modality())
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
        cancelled = False
        
        def on_progress(current, total, message):
            if total > 0:
                progress.setValue(int(current / total * 100))
            progress.setLabelText(message)
            QApplication.processEvents()
        
        def on_cancelled():
            nonlocal cancelled
            cancelled = progress.wasCanceled()
            return cancelled
        
        try:
            # Build export options from UI state
            options = ExportOptions()
            options.include_invisible = self._invisible_checkbox.isChecked()
            options.include_reference = self._reference_checkbox.isChecked()
            options.include_static = self._static_checkbox.isChecked()
            options.flatten_groups = self._flatten_groups_checkbox.isChecked()
            
            # Create the exporter with the OpenToonz path
            exporter = TNZExporter(opentoonz_path)
            
            # Run the full export (frames + scene creation)
            progress.setLabelText("Exporting frames...")
            result = exporter.export_scene(
                self._document,
                output_path,
                scene_name,
                options=options,
                on_progress=on_progress,
                on_cancelled=on_cancelled
            )
            
            progress.close()
            
            if cancelled:
                QMessageBox.information(
                    self,
                    "Export Cancelled",
                    "Export was cancelled by user."
                )
                return
            
            if result['success']:
                layer_count = result.get('layer_count', 0)
                frame_count = result.get('frame_count', 0)
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"OpenToonz scene exported successfully!\n\n"
                    f"Location: {full_tnz_path}\n"
                    f"Layers: {layer_count}\n"
                    f"Frames exported: {frame_count}"
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to create scene:\n{result['message']}"
                )
            
        except ValueError as e:
            progress.close()
            QMessageBox.critical(
                self,
                "Configuration Error",
                str(e)
            )
        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export scene:\n{str(e)}"
            )
