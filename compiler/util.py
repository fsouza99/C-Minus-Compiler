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

def show_node(node):
    if node.kind == NodeKind.FACTOR:
        print(f"""<{node.number}, {node.kind.name}, att: {node.attribute}, line {node.lineno}>\n""")
    elif node.children:
        print(f"""<{node.number}, {node.kind.name}, line {node.lineno}>""")
        for child in node.children:
            print(f"""\t<{child.number}, {child.kind.name}, line {child.lineno}>""")
        print('\n')
        for child in node.children:
            show_node(child)
    return

def show_tree(root):
    print(f"""<{root.number}, {root.kind.name}, line {root.lineno}>""")
    if root.children:
        for child in root.children:
            print(f"""\t<{child.number}, {child.kind.name}, line {child.lineno}>""")
        print('\n')
        for child in root.children:
            show_node(child)
    return None

def IDGenerator():
    counter = 0
    while counter < 10**3:
        counter += 1
        yield counter
    return