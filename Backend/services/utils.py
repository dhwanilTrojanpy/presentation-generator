def load_text_file(file_path: str) -> str:
    """
    Reads a text file and returns its content as a string.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: The contents of the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")