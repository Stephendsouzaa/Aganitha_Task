"""Module for handling dynamic file naming with search-based prefixes."""

import os
import re
from typing import Optional

def generate_filename(base_dir: str, search_query: str, extension: str = 'csv') -> str:
    """Generate a unique filename based on search query and existing files.

    Args:
        base_dir: Directory where the file will be created
        search_query: Search query used to generate the base filename
        extension: File extension (default: 'csv')

    Returns:
        A unique filename based on the search query
    """
    # Clean the search query to create a valid filename
    base_name = clean_search_query(search_query)
    
    # If base_name is empty after cleaning, use 'search_results' as default
    if not base_name:
        base_name = 'search_results'
    
    # Get existing files with similar names
    pattern = rf'^{re.escape(base_name)}(?:_\d+)?\.{extension}$'
    existing_files = [f for f in os.listdir(base_dir) 
                     if os.path.isfile(os.path.join(base_dir, f)) and 
                     re.match(pattern, f, re.IGNORECASE)]
    
    if not existing_files:
        return f"{base_name}.{extension}"
    
    # Find the highest number suffix
    max_num = 0
    for file in existing_files:
        match = re.search(rf'_(\d+)\.{extension}$', file)
        if match:
            num = int(match.group(1))
            max_num = max(max_num, num)
        elif file == f"{base_name}.{extension}":
            max_num = max(max_num, 0)
    
    # Generate new filename with incremented number
    return f"{base_name}_{max_num + 1}.{extension}"

def clean_search_query(query: str) -> str:
    """Clean search query to create a valid filename.

    Args:
        query: Search query to clean

    Returns:
        Cleaned string suitable for use in filename
    """
    # Remove special characters and replace spaces with underscores
    cleaned = re.sub(r'[^\w\s-]', '', query)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    
    # Limit length and remove trailing underscores
    cleaned = cleaned[:50].strip('_').lower()
    
    return cleaned