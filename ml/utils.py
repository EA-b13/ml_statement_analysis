def parse_numeric(value):
    """
    Convert a string (or numeric value) to a float.
    This function removes commas and whitespace.
    If conversion fails, it returns 0.0.
    """
    if value is None:
        return 0.0
    try:
        # Convert to string, remove commas, and strip spaces.
        return float(str(value).replace(',', '').strip())
    except Exception:
        return 0.0