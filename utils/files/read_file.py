import os

def read_file(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Read the content of a file and return it as a string.
    
    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)
        
    Returns:
        The content of the file as a string
    """
    try:
        # Check if the path is absolute or relative
        if not os.path.isabs(file_path):
            # Handle relative paths by joining with the current directory
            file_path = os.path.join(os.getcwd(), file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Open and read the file
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
            
        return content
    
    except Exception as e:
        # Log the error and re-raise
        print(f"Error reading file {file_path}: {str(e)}")
        raise
