"""Frame Export Handler

Handles the export of individual animation frames to PNG files.
Uses Krita's native document export for proper color management.
"""

import krita


class FrameExporter:
    """Exports individual layer frames using temporary documents.
    
    Creates isolated temporary documents for each frame export to ensure
    clean output with proper color profile handling.
    """
    
    def __init__(self, source_document):
        """Initialize with the source document to export from.
        
        Args:
            source_document: The Krita document containing layers to export.
        """
        self.source = source_document
        self.krita_instance = krita.Krita.instance()
        
        # Cache document properties for creating matching temp documents
        self._width = source_document.width()
        self._height = source_document.height()
        self._color_model = source_document.colorModel()
        self._color_depth = source_document.colorDepth()
        self._color_profile = source_document.colorProfile()
        self._resolution = source_document.resolution()
    
    def export_frame(self, layer, frame_number: int, output_path: str) -> bool:
        """Export a single frame from a layer to a PNG file.
        
        Creates a temporary document matching the source document's properties,
        transfers the pixel data, and exports using Krita's native export.
        
        Args:
            layer: The Krita layer node to export from.
            frame_number: Which frame to export.
            output_path: Full path for the output PNG file.
            
        Returns:
            True if export succeeded, False otherwise.
        """
        # Move to the target frame and wait for render
        self.source.setCurrentTime(frame_number)
        self.source.waitForDone()
        
        # Get pixel data from the layer at full document size
        pixel_data = layer.projectionPixelData(0, 0, self._width, self._height)
        
        if not pixel_data:
            return False
        
        # Build a temporary document for clean export
        temp_doc = self._create_temp_document()
        if temp_doc is None:
            return False
        
        try:
            # Enable batch mode to suppress export dialogs
            temp_doc.setBatchmode(True)
            
            # Transfer pixels to temp document
            self._transfer_pixels(temp_doc, pixel_data)
            
            # Export using Krita's native PNG export
            export_config = self._build_png_config()
            success = temp_doc.exportImage(output_path, export_config)
            
            return success
            
        finally:
            # Always clean up the temp document
            temp_doc.close()
    
    def _create_temp_document(self):
        """Create a temporary document matching source document properties.
        
        Returns:
            A new Krita document, or None if creation failed.
        """
        return self.krita_instance.createDocument(
            self._width,
            self._height,
            "opentoonz_export_temp",
            self._color_model,
            self._color_depth,
            self._color_profile,
            self._resolution
        )
    
    def _transfer_pixels(self, temp_doc, pixel_data: bytes) -> None:
        """Transfer pixel data into the temporary document.
        
        Args:
            temp_doc: The temporary document to receive pixels.
            pixel_data: Raw pixel bytes from the source layer.
        """
        # Get the paint layer in the temp document (created by default)
        root = temp_doc.rootNode()
        children = root.childNodes()
        
        if children:
            target_layer = children[0]
            target_layer.setPixelData(pixel_data, 0, 0, self._width, self._height)
        
        # Ensure the document is fully updated
        temp_doc.refreshProjection()
        temp_doc.waitForDone()
    
    def _build_png_config(self) -> 'InfoObject':
        """Build PNG export configuration.
        
        Returns:
            InfoObject configured for PNG export with alpha.
        """
        config = krita.InfoObject()
        config.setProperty("alpha", True)
        config.setProperty("compression", 6)
        config.setProperty("indexed", False)
        config.setProperty("interlaced", False)
        return config
