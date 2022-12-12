from .globals import *
from .util import *
from .scanner import *

IDGenerator = IDGenerator()
GLOBAL_SCOPE_KEY = 'GLOBAL'
BUILTIN_FUNCTIONS = ['input', 'output']


class TreeNode():

    def __init__(self, name : str = None, kind : NodeKind = NodeKind.UNDEFINED, lineno : int = None, attribute=None):
        self.children = []
        self.sibling = None
        self.kind = kind
        self.number = next(IDGenerator)
        self.attribute = attribute
        self.lineno = lineno
        self.name = name

    def toString(self, spaces):
        text = ' ' * spaces + f"""<ID: {self.number}, kind: {self.kind}"""
        if self.attribute is not None:
            text += f""", att: {self.attribute}"""
        if self.name:
            text += f""", name: {self.name}"""
        return text + f""", line: {self.lineno}>"""
    
    def addChild(self, child):
        self.children.append(child)
        return None


class SyntaxError(Exception):
    def __init__(self, message):
        self.message = message

class TokenError(Exception):
    def __init__(self, message):
        self.message = message

class Parser():

    def __init__(self, scanner: Scanner):
        self.token = self.root = None
        self.scanner = scanner
        self.symbols = {GLOBAL_SCOPE_KEY:BUILTIN_FUNCTIONS}
        self.tokenBackup = (None, None)
        self.currentScope = GLOBAL_SCOPE_KEY
        self.nodeCount = 0

    def getNewNode(self, name : str = None, kind : NodeKind = None, attribute=None):
        node = TreeNode(name=self.scanner.tokenString, kind=kind, lineno=self.scanner.line_index, attribute=attribute)
        self.nodeCount += 1
        return node

    def match(self, token):
        if self.token == token:
            self.tokenStringBackup = self.scanner.tokenString, self.scanner.line_index
            self.token = self.scanner.get_token()
            if self.token == TokenType.ERROR:
                raise TokenError(f"""ERROR: Token Error.\nSymbol {self.scanner.tokenString} at line {self.scanner.line_index} does not represent anything.""")
            return True
        raise SyntaxError(f"""ERROR: Syntax Error.\nExpected token {token} at line {self.scanner.line_index}, but got {self.token}.""")

    def reference_exp(self):
        t = self.getNewNode()
        self.match(TokenType.ID)
        if not self.check_symbol(self.tokenStringBackup[0]):
            raise SyntaxError(f"""ERROR: Reference Error.\nSymbol "{self.tokenStringBackup[0]}" at line {self.tokenStringBackup[1]} has not been declared.""")
        if self.token == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            if self.token != TokenType.RPAREN:
                t.addChild(self.arg_list())
            self.match(TokenType.RPAREN)
            t.kind = NodeKind.CALL
            t.attribute = TokenType.ID.name
            return t
        t.kind = NodeKind.VAR_REF
        t.attribute = TokenType.ID.name
        if self.token == TokenType.LBRACKETS:
            self.match(TokenType.LBRACKETS)
            t.addChild(self.expression())
            self.match(TokenType.RBRACKETS)
        return t

    def expression_stmt(self):
        if self.token == TokenType.SEMI:
            self.match(TokenType.SEMI)
            return None
        t = self.expression()
        self.match(TokenType.SEMI)
        return t

    def match_relop(self):
        if self.token == TokenType.LTEQ:
            self.match(TokenType.LTEQ)
            return TokenType.LTEQ
        elif self.token == TokenType.LT:
            self.match(TokenType.LT)
            return TokenType.LT
        elif self.token == TokenType.GT:
            self.match(TokenType.GT)
            return TokenType.GT
        elif self.token == TokenType.GTEQ:
            self.match(TokenType.GTEQ)
            return TokenType.GTEQ
        elif self.token == TokenType.COMP:
            self.match(TokenType.COMP)
            return TokenType.COMP
        elif self.token == TokenType.DIFF:
            self.match(TokenType.DIFF)
            return TokenType.DIFF
        return None

    def match_mulop(self):
        if self.token == TokenType.TIMES:
            self.match(TokenType.TIMES)
            return TokenType.TIMES
        elif self.token == TokenType.OVER:
            self.match(TokenType.OVER)
            return TokenType.OVER
        return None

    def match_addop(self):
        if self.token == TokenType.PLUS:
            self.match(TokenType.PLUS)
            return TokenType.PLUS
        elif self.token == TokenType.MINUS:
            self.match(TokenType.MINUS)
            return TokenType.MINUS
        return None

    def expression(self):
        if self.token == TokenType.ID:
            t = self.reference_exp()
            if not self.is_token_delimiter() and t.kind == NodeKind.VAR_REF:
                if self.token == TokenType.ASSIGN:
                    self.match(TokenType.ASSIGN)
                    t.kind = NodeKind.ASSIGN
                    t.addChild(self.expression())
                    return t
                p = self.getNewNode()
                p.addChild(t)
                while self.is_token_relop():
                    p.attribute = self.match_relop()
                    p.addChild(self.additive_expression())
                    p.kind = NodeKind.RELOP
                while self.is_token_addop():
                    p.attribute = self.match_addop()
                    p.addChild(self.term())
                    p.kind = NodeKind.ADDOP
                while self.is_token_mulop():
                    p.attribute = self.match_mulop()
                    p.addChild(self.factor())
                    p.kind = NodeKind.MULOP
                t = p
            return t
        return self.simple_expression()

    def simple_expression(self):
        # simple-expression → additive-expression {relop additive-expression}
        t = self.additive_expression()
        while self.is_token_relop():
            p = self.getNewNode(kind=NodeKind.RELOP)
            p.addChild(t)
            p.attribute = self.match_relop()
            p.addChild(self.additive_expression())
            t = p
        return t

    def additive_expression(self):
        # additive-expression → term {mulop term}
        t = self.term()
        while self.is_token_addop():
            p = self.getNewNode(kind=NodeKind.ADDOP)
            p.addChild(t)
            p.attribute = self.match_addop()
            p.addChild(self.term())
            t = p
        return t

    def term(self):
        # term → factor {mulop factor}
        t = self.factor()
        while self.is_token_mulop():
            p = self.getNewNode(kind=NodeKind.MULOP)
            p.addChild(t)
            p.attribute = self.match_mulop()
            t = p
            t.addChild(self.factor())
        return t

    def is_token_relop(self):
        return self.token == TokenType.LTEQ or \
            self.token == TokenType.LT or \
            self.token == TokenType.GT or \
            self.token == TokenType.GTEQ or \
            self.token == TokenType.COMP or \
            self.token == TokenType.DIFF

    def is_token_addop(self):
        return self.token == TokenType.PLUS or self.token == TokenType.MINUS

    def is_token_mulop(self):
        return self.token == TokenType.TIMES or self.token == TokenType.OVER

    def is_token_delimiter(self):
        return  self.token == TokenType.COMMA or \
                self.token == TokenType.SEMI or \
                self.token == TokenType.RBRACKETS or \
                self.token == TokenType.RPAREN

    def factor(self):
        # factor → ( expression ) | var | call | NUM
        if self.token == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            t = self.expression()
            self.match(TokenType.RPAREN)
        elif self.token == TokenType.NUM:
            self.match(TokenType.NUM)
            t = self.getNewNode(kind=NodeKind.NUM)
            t.attribute = self.tokenStringBackup[0]
            t.name = TokenType.NUM.name
        elif self.token == TokenType.ID:
            self.match(TokenType.ID)
            t = self.getNewNode(kind=NodeKind.VAR_REF)
            t.attribute = TokenType.ID.name
            t.name = self.tokenStringBackup[0]
            if not self.check_symbol(self.tokenStringBackup[0]):
                raise SyntaxError(f"""ERROR: Reference Error.\nSymbol "{self.tokenStringBackup[0]}" at line {self.tokenStringBackup[1]} has not been declared.""")
            if self.token == TokenType.LBRACKETS:
                self.match(TokenType.LBRACKETS)
                t.addChild(self.expression())
                self.match(TokenType.RBRACKETS)
            elif self.token == TokenType.LPAREN:
                self.match(TokenType.LPAREN)
                if self.token != TokenType.RPAREN:
                    t.addChild(self.arg_list())
                self.match(TokenType.RPAREN)
        else:
            raise SyntaxError(f"""ERROR: Syntax Error at line {self.scanner.line_index}.""")
        return t

    def arg_list(self):
        t = self.getNewNode(kind=NodeKind.ARG_LIST)
        t.addChild(self.expression())
        while self.token == TokenType.COMMA:
            self.match(TokenType.COMMA)
            t.addChild(self.expression())
        return t

    def selection_stmt(self):
        # selection-stmt → if ( expression ) statement [else statement]
        t = self.getNewNode(kind=NodeKind.SELECTION_STMT)
        self.match(TokenType.IF)
        self.match(TokenType.LPAREN)
        t.addChild(self.expression())
        self.match(TokenType.RPAREN)
        t.addChild(self.stmt())
        if self.token == TokenType.ELSE:
            self.match(TokenType.ELSE)
            t.addChild(self.stmt())
        return t

    def iteration_stmt(self):
        # while ( expression ) statement
        t = self.getNewNode(kind=NodeKind.ITERATION_STMT)
        self.match(TokenType.WHILE)
        self.match(TokenType.LPAREN)
        t.addChild(self.expression())
        self.match(TokenType.RPAREN)
        t.addChild(self.stmt())
        return t

    def return_stmt(self):
        t = self.getNewNode(kind=NodeKind.RETURN_STMT)
        self.match(TokenType.RETURN)
        if self.token == TokenType.SEMI:
            self.match(TokenType.SEMI)
            return t
        t.addChild(self.expression())
        self.match(TokenType.SEMI)
        return t

    def match_type(self):
        if self.token == TokenType.INT:
            self.match(TokenType.INT)
            return TokenType.INT
        if self.token == TokenType.VOID:
            self.match(TokenType.VOID)
            return TokenType.VOID
        return None

    def param_list(self):
        # param-list → param {, param}
        t = self.getNewNode(kind=NodeKind.PARAM_LIST)
        t.addChild(self.param())
        while self.token == TokenType.COMMA:
            self.match(TokenType.COMMA)
            t.addChild(self.param())
        return t

    def param(self):
        #  param → type-specifier ID | type-specifier ID [ ]
        t = self.getNewNode(kind=NodeKind.PARAM)
        t.attribute = self.match_type()
        if t.attribute == TokenType.VOID:
            return t
        self.match(TokenType.ID)
        t.name = self.tokenStringBackup[0]
        self.declare_symbol()
        if self.token == TokenType.LBRACKETS:
            self.match(TokenType.LBRACKETS)
            self.match(TokenType.RBRACKETS)
        return t

    def local_declarations(self):
        if self.token == TokenType.INT or self.token == TokenType.VOID:
            t = self.getNewNode(kind=NodeKind.VAR_DECLARATION)
            t.attribute = self.match_type()
            self.match(TokenType.ID)
            t.name = self.tokenStringBackup[0]
            self.declare_symbol()
            if self.token == TokenType.LBRACKETS:
                self.match(TokenType.LBRACKETS)
                self.match(TokenType.RBRACKETS)
            self.match(TokenType.SEMI)
            t.sibling = self.local_declarations()
            return t
        return None

    def compound_stmt(self):
        t = self.getNewNode(kind=NodeKind.COMPOUND_STMT)
        self.match(TokenType.LCBRACES)
        if self.token != TokenType.RCBRACES:
            if self.token == TokenType.INT or self.token == TokenType.VOID:
                t.addChild(self.local_declarations())
            if self.token != TokenType.RCBRACES:
                t.addChild(self.stmt_list())
        self.match(TokenType.RCBRACES)
        return t

    def stmt(self):
        # statement → expression-stmt | compound-stmt | selection-stmt | iteration-stmt | return-stmt
        if self.token == TokenType.LCBRACES:
            return self.compound_stmt()
        if self.token == TokenType.IF:
            return self.selection_stmt()
        if self.token == TokenType.WHILE:
            return self.iteration_stmt()
        if self.token == TokenType.RETURN:
            return self.return_stmt()
        return self.expression_stmt()

    def stmt_list(self):
        if self.token != TokenType.RCBRACES:
            t = self.stmt()
            t.sibling = self.stmt_list()
            return t
        return None

    def declare_symbol(self, scope=GLOBAL_SCOPE_KEY):
        stack = self.symbols.get(scope, [])
        stack.append(self.tokenStringBackup[0])
        self.symbols[scope] = stack
        return

    def check_symbol(self, symbol, scope=GLOBAL_SCOPE_KEY):
        return symbol in self.symbols[scope]

    def declaration(self):
        t = self.getNewNode()
        t.attribute = self.match_type()
        self.match(TokenType.ID)
        t.name = self.tokenStringBackup[0]
        self.declare_symbol()
        if self.token == TokenType.SEMI:
            self.match(TokenType.SEMI)
            t.kind = NodeKind.VAR_DECLARATION
        elif self.token == TokenType.LBRACKETS:
            self.match(TokenType.LBRACKETS)
            self.match(TokenType.NUM)
            self.match(TokenType.RBRACKETS)
            self.match(TokenType.SEMI)
            t.kind = NodeKind.VAR_DECLARATION
        elif self.token == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            if self.token == TokenType.INT or self.token == TokenType.VOID:
                t.addChild(self.param_list())
            self.match(TokenType.RPAREN)
            t.addChild(self.compound_stmt())
            t.kind = NodeKind.FUN_DECLARATION
        return t

    def declaration_list(self):
        t = self.declaration()
        p = t
        while self.token != TokenType.ENDOFFILE:
            p.sibling = self.declaration()
            p = p.sibling
        return t

    def parse(self):
        self.token = self.scanner.get_token()
        self.root = self.declaration_list()
        if self.token != TokenType.ENDOFFILE:
            raise SyntaxError("ERROR: Code ends before file.")
        return self.root







