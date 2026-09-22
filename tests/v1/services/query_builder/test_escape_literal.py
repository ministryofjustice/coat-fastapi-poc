from app.services.query_builder.escape_literal import escape_literal

def test_escape_literal_replaces_single_quote_with_double():
    """A single quote in the middle of a string is doubled"""
    assert escape_literal("O'Brien") == "O''Brien"

