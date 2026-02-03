"""OpenToonz Exporter Configuration

Version and constants for the OpenToonz Exporter plugin.
"""

import sys

VERSION = "0.2.0"
PLUGIN_ID = "opentoonz_exporter"
PLUGIN_NAME = "Export Animation to OpenToonz Scene"

# Settings keys
SETTINGS_OPENTOONZ_PATH = "opentoonz_path"
SETTINGS_EXPORT_PATH = "export_path"
# Persistent option keys
SETTINGS_FLATTEN_GROUPS = "flatten_groups"
SETTINGS_INCLUDE_INVISIBLE = "include_invisible"
SETTINGS_INCLUDE_REFERENCE = "include_reference"
SETTINGS_INCLUDE_STATIC = "include_static"


def get_opentoonz_default_paths():
    """Get default paths to search for OpenToonz executable based on OS.
    
    Returns:
        List of potential paths to OpenToonz executable.
    """
    if sys.platform == "win32":
        return [
            r"C:\Program Files\OpenToonz\OpenToonz.exe",
            r"C:\Program Files (x86)\OpenToonz\OpenToonz.exe",
            r"C:\OpenToonz\OpenToonz.exe",
        ]
    elif sys.platform == "darwin":
        return [
            "/Applications/OpenToonz/OpenToonz.app/Contents/MacOS/OpenToonz",
            "/Applications/OpenToonz.app/Contents/MacOS/OpenToonz",
            "~/Applications/OpenToonz.app/Contents/MacOS/OpenToonz",
        ]
    else:  # Linux and others
        return [
            "/usr/bin/opentoonz",
            "/usr/local/bin/opentoonz",
            "/opt/opentoonz/bin/opentoonz",
            "~/.local/bin/opentoonz",
        ]


def get_opentoonz_executable_filter():
    """Get file filter for OpenToonz executable based on OS.
    
    Returns:
        File filter string for QFileDialog.
    """
    if sys.platform == "win32":
        return "OpenToonz Executable (OpenToonz.exe);;All Executables (*.exe);;All Files (*)"
    elif sys.platform == "darwin":
        return "OpenToonz Application (OpenToonz);;All Files (*)"
    else:
        return "OpenToonz Executable (opentoonz);;All Files (*)"
