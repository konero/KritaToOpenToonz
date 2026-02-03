"""OpenToonz Export Engine

Main export logic for converting Krita animations to OpenToonz scene format.
"""

import os

from .document import get_document_info
from .layer import get_animated_layers, get_static_layers, get_layer_keyframes, count_total_keyframes, is_stop_frame
from .frame_export import FrameExporter
from .utils import mkdir, sanitize_filename, int_to_str, make_unique_name, compute_content_hash


class ExportOptions:
    """Configuration options for OpenToonz export."""
    
    # Level type constants
    LEVEL_RASTER = "Raster"
    LEVEL_TOONZ_RASTER = "ToonzRaster"
    LEVEL_VECTOR = "Vector"
    
    def __init__(self):
        self.include_invisible = False
        self.include_reference = False
        self.include_static = False
        self.flatten_groups = True
        self.scene_name = ""
        self.level_type = self.LEVEL_RASTER  # For future expansion


class ExportResult:
    """Result of an export operation."""
    
    def __init__(self):
        self.success = False
        self.output_path = ""
        self.script_path = ""
        self.layer_count = 0
        self.frame_count = 0
        self.error_message = ""
        
    def __str__(self):
        if self.success:
            return (f"Export complete: {self.layer_count} layers, "
                    f"{self.frame_count} frames")
        return f"Export failed: {self.error_message}"


class LayerExportInfo:
    """Information about an exported layer for ToonzScript generation."""
    
    def __init__(self, name: str, folder_path: str, level_type: str):
        self.name = name
        self.folder_path = folder_path
        self.level_type = level_type
        self.frame_data = []  # List of (xsheet_row, frame_id) tuples
        self.file_pattern = ""  # e.g., "LayerName..png" for sequence


class OpenToonzExportEngine:
    """Core export engine for OpenToonz animation export.
    
    Exports Krita animation layers as PNG sequences and generates
    ToonzScript to create the OpenToonz scene with proper timing.
    """
    
    def __init__(self, document, export_path: str, options: ExportOptions = None):
        """Initialize the export engine.
        
        Args:
            document: The Krita document to export.
            export_path: Base directory where exports will be saved.
            options: Export configuration options.
        """
        self.document = document
        self.export_path = export_path
        self.options = options if options is not None else ExportOptions()
        
        # Callbacks for progress reporting
        self.on_progress = None  # Callable: (current, total, message) -> None
        self.on_cancelled = None  # Callable: () -> bool
        
        # Export state
        self._result = ExportResult()
        self._layer_infos = []  # List of LayerExportInfo
    
    def export(self) -> ExportResult:
        """Execute the export operation.
        
        Creates:
        - SceneName/
          - SceneName.tnz (created by OpenToonz via script)
          - LayerName1/LayerName1.0001.png, etc.
          - LayerName2/LayerName2.0001.png, etc.
          - _export_scene.toonzscript (temp script file)
        
        Returns:
            ExportResult with details of the operation.
        """
        try:
            self._run_export()
        except Exception as e:
            self._result.success = False
            self._result.error_message = str(e)
        
        return self._result
    
    def get_layer_infos(self) -> list:
        """Get the layer export information after export.
        
        Returns:
            List of LayerExportInfo objects.
        """
        return self._layer_infos
    
    def _report_progress(self, current: int, total: int, message: str):
        """Report progress if callback is set."""
        if self.on_progress:
            self.on_progress(current, total, message)
    
    def _is_cancelled(self) -> bool:
        """Check if export was cancelled."""
        return self.on_cancelled and self.on_cancelled()
    
    def _run_export(self):
        """Internal export implementation."""
        # Gather document info
        doc_info = get_document_info(self.document)
        
        # Determine scene name
        scene_name = self.options.scene_name
        if not scene_name:
            scene_name = sanitize_filename(doc_info['name'])
        if not scene_name:
            scene_name = "Untitled"
        
        # Create main export folder: export_path/SceneName/
        scene_folder = os.path.join(self.export_path, scene_name)
        mkdir(scene_folder)
        
        # Get exportable animated layers
        animated_layers = get_animated_layers(
            self.document,
            self.options.include_invisible,
            self.options.include_reference,
            self.options.flatten_groups
        )
        
        # Get static layers if requested
        static_layers = []
        if self.options.include_static:
            static_layers = get_static_layers(
                self.document,
                self.options.include_invisible,
                self.options.include_reference
            )
        
        if not animated_layers and not static_layers:
            self._result.error_message = "No layers found to export. Check that layers have animation keyframes or enable 'Include non-animated layers' option."
            return
        
        # Determine frame range
        start_frame = doc_info['start_frame']
        end_frame = doc_info['end_frame']
        duration = doc_info['duration']
        
        # Count total work for progress reporting
        total_keyframes = count_total_keyframes(animated_layers, start_frame, end_frame)
        
        # Initialize the frame exporter
        frame_exporter = FrameExporter(self.document)
        
        # Process each animated layer
        processed = 0
        used_layer_names = set()
        
        for col_index, layer in enumerate(animated_layers):
            # Generate unique layer name
            base_name = sanitize_filename(layer.name())
            layer_name = make_unique_name(base_name, used_layer_names)
            
            # Create layer folder: SceneName/LayerName/
            layer_folder = os.path.join(scene_folder, layer_name)
            mkdir(layer_folder)
            
            # Create layer info for script generation
            layer_info = LayerExportInfo(
                name=layer_name,
                folder_path=layer_folder,
                level_type=self.options.level_type
            )
            # OpenToonz uses ".." for frame number placeholder in sequences
            layer_info.file_pattern = f"{layer_name}..png"
            
            # Get keyframes for this layer
            keyframes = get_layer_keyframes(layer, start_frame, end_frame)
            
            # For deduplication: map content hash -> frame_id
            # This handles clone keyframes (exposures) by reusing the same frame
            hash_to_frame_id = {}
            
            # Track which frame image each xsheet row should show
            current_frame_id = None
            frame_counter = 0
            
            for frame in range(start_frame, end_frame + 1):
                # Check for cancellation
                if self._is_cancelled():
                    self._result.error_message = "Export cancelled by user"
                    return
                
                # Calculate xsheet row (0-indexed)
                xsheet_row = frame - start_frame
                
                # Check if this frame has a keyframe
                if frame in keyframes:
                    # Report progress
                    processed += 1
                    self._report_progress(
                        processed,
                        total_keyframes,
                        f"Exporting {layer_name} - frame {frame}..."
                    )
                    
                    # Set document to this frame
                    self.document.setCurrentTime(frame)
                    self.document.waitForDone()
                    
                    # Check for stop frame (blank keyframe)
                    if is_stop_frame(layer):
                        current_frame_id = None  # Clear - no cell
                        continue
                    
                    # Get pixel data for content deduplication
                    pixel_data = layer.projectionPixelData(
                        0, 0, doc_info['width'], doc_info['height']
                    )
                    content_hash = compute_content_hash(pixel_data)
                    
                    # Check if we've already exported this exact content
                    if content_hash in hash_to_frame_id:
                        # Reuse existing frame_id (clone keyframe / exposure)
                        current_frame_id = hash_to_frame_id[content_hash]
                    else:
                        # New unique content - export it
                        frame_counter += 1
                        frame_id = frame_counter  # 1-based frame IDs
                        
                        # Filename: LayerName.0001.png
                        filename = f"{layer_name}.{int_to_str(frame_id)}.png"
                        filepath = os.path.join(layer_folder, filename)
                        
                        success = frame_exporter.export_frame(layer, frame, filepath)
                        
                        if not success:
                            self._result.error_message = f"Failed to export frame {frame} of {layer_name}"
                            return
                        
                        # Record hash for future deduplication
                        hash_to_frame_id[content_hash] = frame_id
                        current_frame_id = frame_id
                        self._result.frame_count += 1
                
                # Add frame data for xsheet (even if held from previous keyframe)
                if current_frame_id is not None:
                    layer_info.frame_data.append((xsheet_row, current_frame_id))
            
            self._layer_infos.append(layer_info)
        
        # Process static layers (held from first to last frame)
        for layer in static_layers:
            # Check for cancellation
            if self._is_cancelled():
                self._result.error_message = "Export cancelled by user"
                return
            
            # Generate unique layer name
            base_name = sanitize_filename(layer.name())
            layer_name = make_unique_name(base_name, used_layer_names)
            
            # Report progress
            self._report_progress(
                processed + 1,
                total_keyframes + len(static_layers),
                f"Exporting static layer {layer_name}..."
            )
            processed += 1
            
            # Create layer folder
            layer_folder = os.path.join(scene_folder, layer_name)
            mkdir(layer_folder)
            
            # Create layer info for script generation
            layer_info = LayerExportInfo(
                name=layer_name,
                folder_path=layer_folder,
                level_type=self.options.level_type
            )
            layer_info.file_pattern = f"{layer_name}..png"
            
            # Export the single static frame
            filename = f"{layer_name}.{int_to_str(1)}.png"
            filepath = os.path.join(layer_folder, filename)
            
            # Set to start frame for export
            self.document.setCurrentTime(start_frame)
            self.document.waitForDone()
            
            success = frame_exporter.export_frame(layer, start_frame, filepath)
            
            if not success:
                self._result.error_message = f"Failed to export static layer {layer_name}"
                return
            
            self._result.frame_count += 1
            
            # Hold frame 1 for the entire duration
            for frame in range(start_frame, end_frame + 1):
                xsheet_row = frame - start_frame
                layer_info.frame_data.append((xsheet_row, 1))  # Always frame 1
            
            self._layer_infos.append(layer_info)
        
        # Store scene info for script generation
        self._result.success = True
        self._result.output_path = os.path.join(scene_folder, f"{scene_name}.tnz")
        self._result.layer_count = len(animated_layers) + len(static_layers)
