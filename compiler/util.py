from .globals import TokenType, NodeKind


def is_digit(char: str) -> bool:
    if char and len(char) == 1:
        return char in '0123456789'
    return False

def is_alphabetic(char: str) -> bool:
    if char and len(char) == 1:
        return char.upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return False

def format_token(currentToken: TokenType, tokenString: str = '', lineno: int = None) -> str:
    if tokenString and lineno is not None:
        return f'''Line {lineno}: <{currentToken.name}, "{tokenString}">'''
    if lineno is not None:
        return f'''Line {lineno}: <{currentToken.name}>'''
    return f'''<{currentToken.name}>'''

def show_token(currentToken: TokenType, tokenString: str = '', lineno: int = None) -> None:
    print(format_token(currentToken, tokenString, lineno))
    return

def IDGenerator(max_id=10**3):
    counter = 0
    while counter < max_id:
        counter += 1
        yield counter
    return None



