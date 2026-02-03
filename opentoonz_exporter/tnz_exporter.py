"""OpenToonz Scene Exporter

Handles the creation of OpenToonz scene files (.tnz) by exporting
frames, generating ToonzScript, and executing it via OpenToonz command line.
"""

import os
import subprocess

from .toonz_script import generate_blank_scene_script, generate_scene_with_levels_script
from .core.exporter import OpenToonzExportEngine, ExportOptions, ExportResult


class TNZExporter:
    """Exports Krita documents to OpenToonz scene format.
    
    This works by:
    1. Exporting animation frames as PNG sequences
    2. Generating a ToonzScript that loads the levels and sets timing
    3. Running the script through OpenToonz command-line
    """
    
    def __init__(self, opentoonz_path: str = ""):
        """Initialize the exporter.
        
        Args:
            opentoonz_path: Path to the OpenToonz executable.
        """
        self._opentoonz_path = opentoonz_path
    
    @property
    def opentoonz_path(self) -> str:
        """Get the OpenToonz executable path."""
        return self._opentoonz_path
    
    @opentoonz_path.setter
    def opentoonz_path(self, value: str):
        """Set the OpenToonz executable path."""
        self._opentoonz_path = value
    
    def validate_opentoonz_path(self) -> bool:
        """Check if the OpenToonz path is valid.
        
        Returns:
            True if the path exists and appears to be OpenToonz.
        """
        if not self._opentoonz_path:
            return False
        
        if not os.path.isfile(self._opentoonz_path):
            return False
        
        # Basic check - filename should contain "opentoonz" (case insensitive)
        filename = os.path.basename(self._opentoonz_path).lower()
        return "opentoonz" in filename or "toonz" in filename
    
    def export_blank_scene(self, output_path: str) -> dict:
        """Export a blank OpenToonz scene to the specified path.
        
        Args:
            output_path: Full path to the output .tnz file.
            
        Returns:
            Dict with 'success' bool, 'message' str.
        """
        if not self._opentoonz_path:
            raise ValueError("OpenToonz executable path is not set.")
        
        if not self.validate_opentoonz_path():
            raise ValueError(f"Invalid OpenToonz path: {self._opentoonz_path}")
        
        # Generate the ToonzScript
        script_content = generate_blank_scene_script(output_path)
        
        # Create and run script
        return self._write_and_run_script(script_content, output_path)
    
    def export_scene(self, document, export_base_path: str, scene_name: str,
                     options: ExportOptions = None,
                     on_progress=None, on_cancelled=None) -> dict:
        """Export a Krita document to OpenToonz scene format.
        
        Creates a folder structure:
        - export_base_path/scene_name/
          - scene_name.tnz
          - Layer1/Layer1.0001.png, etc.
          - Layer2/Layer2.0001.png, etc.
        
        Args:
            document: The Krita document to export.
            export_base_path: Base directory for export.
            scene_name: Name for the scene (used for folder and .tnz file).
            options: Export configuration options (ExportOptions or None).
            on_progress: Optional callback (current, total, message).
            on_cancelled: Optional callback that returns True if cancelled.
            
        Returns:
            Dict with 'success' bool, 'message' str, and export details.
        """
        if not self._opentoonz_path:
            raise ValueError("OpenToonz executable path is not set.")
        
        if not self.validate_opentoonz_path():
            raise ValueError(f"Invalid OpenToonz path: {self._opentoonz_path}")
        
        # Set up export options
        if options is None:
            options = ExportOptions()
        options.scene_name = scene_name
        
        # Create and run the export engine
        engine = OpenToonzExportEngine(document, export_base_path, options)
        engine.on_progress = on_progress
        engine.on_cancelled = on_cancelled
        
        # Export frames
        result = engine.export()
        
        if not result.success:
            return {
                'success': False,
                'message': result.error_message
            }
        
        # Get layer information for script generation
        layer_infos = engine.get_layer_infos()
        
        if not layer_infos:
            return {
                'success': False,
                'message': 'No layers were exported'
            }
        
        # Generate ToonzScript with levels and timing
        output_tnz_path = result.output_path
        script_content = generate_scene_with_levels_script(output_tnz_path, layer_infos)
        
        # Write and run the script
        script_result = self._write_and_run_script(script_content, output_tnz_path)
        
        if script_result['success']:
            script_result['layer_count'] = result.layer_count
            script_result['frame_count'] = result.frame_count
        
        return script_result
    
    def _write_and_run_script(self, script_content: str, output_tnz_path: str) -> dict:
        """Write a ToonzScript to disk and execute it.
        
        Args:
            script_content: The ToonzScript code.
            output_tnz_path: Path to the expected .tnz output (for verification).
            
        Returns:
            Dict with 'success' bool and 'message' str.
        """
        # Create script file next to the output
        output_dir = os.path.dirname(output_tnz_path)
        script_filename = "_krita_export_temp.toonzscript"
        script_path = os.path.join(output_dir, script_filename)
        
        try:
            # Write the script file
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Run OpenToonz with the script
            result = self._run_opentoonz_script(script_path, output_tnz_path)
            
            return result
            
        finally:
            # Clean up the temporary script file
            if os.path.exists(script_path):
                try:
                    os.remove(script_path)
                except:
                    pass  # Ignore cleanup errors
    
    def _run_opentoonz_script(self, script_path: str, output_tnz_path: str = "") -> dict:
        """Run a ToonzScript file through OpenToonz.
        
        Args:
            script_path: Path to the .toonzscript file.
            output_tnz_path: Path to the expected output file (for verification).
            
        Returns:
            Dict with 'success' bool and 'message' str.
        """
        try:
            # Build the command
            cmd = [self._opentoonz_path, script_path]
            
            # Run the command with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout for larger exports
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Combine stdout and stderr for checking
            all_output = (result.stdout or "") + (result.stderr or "")
            
            # OpenToonz quirk: it may return exit code 1 even on success
            # Check for our success message or verify the output file was created
            script_succeeded = "Scene created successfully!" in all_output
            file_created = output_tnz_path and os.path.exists(output_tnz_path)
            
            if script_succeeded or file_created:
                return {
                    'success': True,
                    'message': 'Scene created successfully!',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                error_msg = all_output or "Unknown error - no output from OpenToonz"
                return {
                    'success': False,
                    'message': f'OpenToonz script execution failed:\n{error_msg}',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'OpenToonz script execution timed out (120 seconds).'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'message': f'Could not find OpenToonz executable: {self._opentoonz_path}'
            }
        except PermissionError:
            return {
                'success': False,
                'message': f'Permission denied when trying to run OpenToonz: {self._opentoonz_path}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error running OpenToonz: {str(e)}'
            }
    
    def get_script_preview(self, output_path: str, layer_infos: list = None) -> str:
        """Get a preview of the ToonzScript that would be generated.
        
        Args:
            output_path: The output .tnz path.
            layer_infos: Optional layer info for full scene preview.
            
        Returns:
            The ToonzScript code as a string.
        """
        if layer_infos:
            return generate_scene_with_levels_script(output_path, layer_infos)
        return generate_blank_scene_script(output_path)
