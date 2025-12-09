def tokenize(source: str):
    """Turn the source string into a simple list of tokens."""
    tokens = []
    current = ""
    # Iterates over each character in the source string to build tokens based on whitespace and brackets
    for ch in source:
        if ch.isspace():
            if current:
                tokens.append(current)
                current = ""
        elif ch in "[]":
            if current:
                tokens.append(current)
                current = ""
            tokens.append(ch)
        else:
            current += ch
    # Add the last token if the source didn't end with whitespace
    if current:
        tokens.append(current)
    return tokens
