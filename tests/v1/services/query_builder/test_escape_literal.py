from app.services.query_builder.escape_literal import escape_literal

def test_escape_literal_replaces_single_quote_with_double():
    """A single quote in the middle of a string is doubled"""
    assert escape_literal("O'Brien") == "O''Brien"

def test_escape_literal_returns_unchanged_if_no_special_characters():
    """Returns unchanged string if no special characters"""
    assert escape_literal("example string") == "example string"

def test_escape_literal_replaces_multiple_single_quotes_with_double():
    """Multiple single quotes are each doubled independently"""
    assert escape_literal("It's '1' = 1") == "It''s ''1'' = 1"

def test_escape_literal_doubles_adjacent_single_quotes():
    """Adjacent single quotes are each doubled independently"""
    assert escape_literal("''") == "''''"

def test_escape_literal_returns_empty_string_given_an_empty_input():
    """Tests returns an empty string if input is empty"""
    assert escape_literal("") == ""