"""Export Animation to OpenToonz Scene

A Krita plugin for exporting animations to OpenToonz scene format (.tnz).
"""

import os
from krita import Krita, Extension

from .config import PLUGIN_ID, PLUGIN_NAME
from .qt_compat import QIcon


def _get_plugin_icon():
    """Get the plugin icon based on the current theme."""
    try:
        from .qt_compat import QApplication
        
        # Determine if using dark or light theme
        palette = QApplication.palette()
        bg_lightness = palette.window().color().lightness()
        is_dark = bg_lightness < 128
        theme = "dark" if is_dark else "light"
        
        # Build path to icon
        plugin_dir = os.path.dirname(__file__)
        icon_path = os.path.join(plugin_dir, "icons", f"opentoonz-export-{theme}.svg")
        
        if os.path.exists(icon_path):
            return QIcon(icon_path)
    except Exception:
        pass
    
    return None


class OpenToonzExporterExtension(Extension):
    """Extension that adds OpenToonz export to Krita's Tools menu."""
    
    def __init__(self, parent):
        super().__init__(parent)
    
    def setup(self):
        """Called once on Krita startup."""
        pass
    
    def createActions(self, window):
        """Create menu actions for the plugin.
        
        Args:
            window: The Krita main window.
        """
        action = window.createAction(
            PLUGIN_ID,
            "Export Animationto OpenToonz Scene...",
            "tools/scripts"
        )
        action.triggered.connect(self._show_export_dialog)
        
        # Set custom icon for toolbar display
        icon = _get_plugin_icon()
        if icon:
            action.setIcon(icon)
    
    def _show_export_dialog(self):
        """Open the export dialog."""
        from .ui_export_dialog import OpenToonzExportDialog
        
        main_window = None
        try:
            main_window = Krita.instance().activeWindow().qwindow()
        except:
            pass
        
        dialog = OpenToonzExportDialog(main_window)
        dialog.exec()


# Register the extension with Krita
Krita.instance().addExtension(OpenToonzExporterExtension(Krita.instance()))
