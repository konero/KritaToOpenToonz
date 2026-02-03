"""Layer Operations for OpenToonz Export

Functions for working with Krita layers during animation export.
"""

# Supported layer types for animation export
ANIMATED_LAYER_TYPES = ["paintlayer"]

# Reference layer color label (grey = 8)
REFERENCE_LAYER_COLOR = 8

# Light Table layer markers
LIGHT_TABLE_PREFIX = "LT_"
LIGHT_TABLE_NAME = "Light Table"


def get_animated_layers(
    document,
    include_invisible: bool = False,
    include_reference: bool = False,
    flatten_groups: bool = False
) -> list:
    """Get all exportable animated layers from a document.
    
    When flatten_groups is False, recursively finds all animated paint layers.
    When flatten_groups is True, includes groups that contain animated children
    (as flattened composites) and does not recurse into them.
    
    Args:
        document: The Krita document.
        include_invisible: Whether to include hidden layers.
        include_reference: Whether to include reference layers (grey color label).
        flatten_groups: Whether to export groups as flattened images.
        
    Returns:
        List of animated layer nodes suitable for export.
    """
    layers = []
    
    def collect_layers(node):
        for child in node.childNodes():
            # Skip invisible layers unless requested
            if not include_invisible and not child.visible():
                continue
            
            # Skip reference layers unless requested
            if not include_reference and is_reference_layer(child):
                continue
            
            # Skip Light Table layers
            layer_name = child.name()
            if layer_name.startswith(LIGHT_TABLE_PREFIX) or layer_name == LIGHT_TABLE_NAME:
                continue
            
            layer_type = child.type()
            
            if layer_type == 'grouplayer':
                if flatten_groups:
                    # Check if this group contains animated content
                    if group_has_animated_content(child):
                        layers.append(child)
                    # Don't recurse into groups we're flattening
                else:
                    # Recurse into groups to find individual paint layers
                    collect_layers(child)
            elif layer_type in ANIMATED_LAYER_TYPES:
                if child.animated():
                    layers.append(child)
    
    collect_layers(document.rootNode())
    # Reverse so Krita's top layer (front) maps to highest OpenToonz column (front)
    return list(reversed(layers))


def get_static_layers(
    document,
    include_invisible: bool = False,
    include_reference: bool = False
) -> list:
    """Get all exportable non-animated (static) layers from a document.
    
    Static layers are paint layers without animation keyframes, useful for
    backgrounds, layouts, peg bars, or safety margins.
    
    Args:
        document: The Krita document.
        include_invisible: Whether to include hidden layers.
        include_reference: Whether to include reference layers (grey color label).
        
    Returns:
        List of static paint layer nodes suitable for export.
    """
    layers = []
    
    def collect_layers(node):
        for child in node.childNodes():
            # Skip invisible layers unless requested
            if not include_invisible and not child.visible():
                continue
            
            # Skip reference layers unless requested
            if not include_reference and is_reference_layer(child):
                continue
            
            # Skip Light Table layers
            layer_name = child.name()
            if layer_name.startswith(LIGHT_TABLE_PREFIX) or layer_name == LIGHT_TABLE_NAME:
                continue
            
            layer_type = child.type()
            
            if layer_type == 'grouplayer':
                # Recurse into groups to find static paint layers
                collect_layers(child)
            elif layer_type in ANIMATED_LAYER_TYPES:
                # Only include non-animated paint layers
                if not child.animated():
                    layers.append(child)
    
    collect_layers(document.rootNode())
    # Reverse so Krita's top layer (front) maps to highest OpenToonz column (front)
    return list(reversed(layers))


def group_has_animated_content(group) -> bool:
    """Check if a group layer contains any animated children.
    
    Recursively checks all descendants for animation keyframes.
    
    Args:
        group: The group layer node to check.
        
    Returns:
        True if the group contains animated content.
    """
    for child in group.childNodes():
        if child.type() in ANIMATED_LAYER_TYPES:
            if child.animated():
                return True
        elif child.type() == 'grouplayer':
            if group_has_animated_content(child):
                return True
    return False


def get_group_keyframes(group, start_frame: int, end_frame: int) -> list:
    """Get all keyframe indices for any animated layer within a group.
    
    Since groups don't have their own keyframes, we collect keyframes
    from all animated children and return a unified list.
    
    Args:
        group: The group layer.
        start_frame: First frame to check.
        end_frame: Last frame to check (inclusive).
        
    Returns:
        Sorted list of unique frame numbers that have keyframes in any child.
    """
    keyframe_set = set()
    
    def collect_keyframes(node):
        for child in node.childNodes():
            if child.type() in ANIMATED_LAYER_TYPES and child.animated():
                for frame in range(start_frame, end_frame + 1):
                    if child.hasKeyframeAtTime(frame):
                        keyframe_set.add(frame)
            elif child.type() == 'grouplayer':
                collect_keyframes(child)
    
    collect_keyframes(group)
    return sorted(keyframe_set)


def is_reference_layer(layer) -> bool:
    """Check if a layer is marked as a reference layer by its color label.
    
    Reference layers use the grey color label (index 8) to indicate they
    are animation guides that should typically be excluded from export.
    
    Args:
        layer: The Krita layer node.
        
    Returns:
        True if the layer has the reference layer color label.
    """
    return layer.colorLabel() == REFERENCE_LAYER_COLOR


def get_layer_keyframes(layer, start_frame: int, end_frame: int) -> list:
    """Get all keyframe indices for a layer within a frame range.
    
    For group layers, collects keyframes from all animated children.
    
    Args:
        layer: The animated layer or group layer.
        start_frame: First frame to check.
        end_frame: Last frame to check (inclusive).
        
    Returns:
        List of frame numbers that have keyframes.
    """
    # For groups, delegate to the specialized function
    if layer.type() == 'grouplayer':
        return get_group_keyframes(layer, start_frame, end_frame)
    
    keyframes = []
    for frame in range(start_frame, end_frame + 1):
        if layer.hasKeyframeAtTime(frame):
            keyframes.append(frame)
    return keyframes


def count_total_keyframes(layers: list, start_frame: int, end_frame: int) -> int:
    """Count total keyframes across all layers for progress reporting.
    
    Args:
        layers: List of animated layers.
        start_frame: First frame to check.
        end_frame: Last frame to check (inclusive).
        
    Returns:
        Total number of keyframes across all layers.
    """
    total = 0
    for layer in layers:
        total += len(get_layer_keyframes(layer, start_frame, end_frame))
    return total


def is_stop_frame(layer) -> bool:
    """Check if the current frame is a stop frame (fully transparent).
    
    Stop frames are blank keyframes used to end a hold in traditional animation.
    
    Args:
        layer: The layer to check at its current time.
        
    Returns:
        True if the frame is fully transparent (stop frame).
    """
    # Get a small sample of pixel data to check for content
    # We check the entire layer bounds
    bounds = layer.bounds()
    if bounds.isEmpty():
        return True
    
    # If bounds are empty, it's a stop frame
    return bounds.width() == 0 or bounds.height() == 0
