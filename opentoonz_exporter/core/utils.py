"""Utility Functions for OpenToonz Export

General-purpose helper functions used throughout the exporter.
"""

import os
import re
import hashlib


def mkdir(directory: str) -> None:
    """Create a directory if it doesn't exist.
    
    Args:
        directory: Path to the directory to create.
        
    Raises:
        OSError: If directory creation fails for reasons other than existence.
    """
    if os.path.exists(directory):
        return
    try:
        os.makedirs(directory)
    except OSError as e:
        raise e


def int_to_str(value: int, num_digits: int = 4) -> str:
    """Convert an integer to a zero-padded string.
    
    Args:
        value: The integer to convert.
        num_digits: Minimum number of digits (default 4).
        
    Returns:
        Zero-padded string representation.
    """
    return str(value).zfill(num_digits)


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use as a filename.
    
    Replaces spaces with underscores and removes characters that are
    problematic in filenames across different operating systems.
    
    Args:
        name: The original name to sanitize.
        
    Returns:
        A filesystem-safe version of the name.
    """
    # Replace spaces with underscores
    sanitized = name.replace(" ", "_")
    # Remove characters that are problematic in filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '', sanitized)
    # Strip leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    return sanitized if sanitized else "unnamed"


def make_unique_name(name: str, used_names: set) -> str:
    """Generate a unique name by appending a numeric suffix if necessary.
    
    If the name is already in used_names, appends _1, _2, etc. until unique.
    The unique name is automatically added to used_names.
    
    Args:
        name: The desired name.
        used_names: Set of already-used names.
        
    Returns:
        A unique version of the name.
    """
    if name not in used_names:
        used_names.add(name)
        return name
    
    counter = 1
    while f"{name}_{counter}" in used_names:
        counter += 1
    
    unique_name = f"{name}_{counter}"
    used_names.add(unique_name)
    return unique_name


def compute_content_hash(pixel_data: bytes) -> str:
    """Compute a hash of pixel data for content deduplication.
    
    Used to detect clone keyframes (exposures) that share the same content,
    allowing us to export only one copy and reference it multiple times.
    
    Args:
        pixel_data: Raw pixel data from a layer.
        
    Returns:
        Hexadecimal hash string.
    """
    return hashlib.md5(pixel_data).hexdigest()
