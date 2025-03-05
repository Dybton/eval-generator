import os
import json

def save_file(path: str, filename: str, content, encoding="utf-8", indent=None):
    """
    Save content to a file at the specified path
    
    Args:
        path: Directory path to save to
        filename: Name of the file
        content: Data to save (string, dict, list etc)
        encoding: File encoding (default utf-8)
        indent: JSON indentation level (default None)
    """
    
    
    # Create directory if it doesn't exist
    os.makedirs(path, exist_ok=True)
    
    full_path = os.path.join(path, filename)
    
    # Handle different content types
    if isinstance(content, (dict, list)):
        with open(full_path, 'w', encoding=encoding) as f:
            json.dump(content, f, indent=indent)
    else:
        with open(full_path, 'w', encoding=encoding) as f:
            f.write(str(content))
            
    return full_path