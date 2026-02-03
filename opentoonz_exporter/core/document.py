"""Document Information Extraction

Functions for extracting document metadata and properties needed for OpenToonz export.
"""


def get_document_info(document) -> dict:
    """Extract essential information from a Krita document.
    
    Gathers all the metadata and properties needed for OpenToonz export
    in a structured dictionary.
    
    Args:
        document: The Krita document to analyze.
        
    Returns:
        Dictionary containing document properties for export.
    """
    start_frame = document.fullClipRangeStartTime()
    end_frame = document.fullClipRangeEndTime()
    
    return {
        'name': document.name() or 'Untitled',
        'width': document.width(),
        'height': document.height(),
        'start_frame': start_frame,
        'end_frame': end_frame,
        'duration': end_frame - start_frame + 1,
        'frame_rate': document.framesPerSecond(),
    }
