# lexer.py

def tokenize(source: str):
    """Turn the source string into a simple list of tokens."""
    tokens = []
    current = ""
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
    if current:
        tokens.append(current)
    return tokens
