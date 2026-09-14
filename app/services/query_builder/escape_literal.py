def escape_literal(value: str) -> str:
    """Escape single quotes for safe inclusion in a SQL string literal."""
    return value.replace("'", "''")
