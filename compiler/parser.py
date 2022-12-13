from .globals import *
from .util import *
from .scanner import *
from .scope import ScopeStack

IDGenerator = IDGenerator()

class TokenError(Exception):
    def __init__(self, message):
        self.message = message


class TreeNode():

    def __init__(self, name : str = None, kind : NodeKind = NodeKind.UNDEFINED, lineno : int = None, attribute=None):
        self.children = []
        self.sibling = None
        self.kind = kind
        self.number = next(IDGenerator)
        self.attribute = attribute
        self.lineno = lineno
        self.name = name

    def to_string(self, spaces):
        text = ' ' * spaces + f"""<ID: {self.number}, kind: {self.kind}"""
        if self.attribute is not None:
            text += f""", att: {self.attribute}"""
        if self.name:
            text += f""", name: {self.name}"""
        return text + f""", line: {self.lineno}>"""
    
    def add_child(self, child):
        self.children.append(child)
        return None


class Parser():

    def __init__(self, scanner: Scanner):
        self.token = self.root = None
        self.scanner = scanner
        self.tokenBackup = (None, None)
        self.scopeStack = ScopeStack()
        self.scopeStack.add_symbols(['input', 'output'])
        self.nodeCount = 0

    def new_node(self, name : str = None, kind : NodeKind = None, attribute=None):
        node = TreeNode(name=self.scanner.tokenString, kind=kind, lineno=self.scanner.lineIndex, attribute=attribute)
        self.nodeCount += 1
        return node

    def match(self, token):
        if self.token == token:
            self.tokenStringBackup = self.scanner.tokenString, self.scanner.lineIndex
            self.token = self.scanner.get_token()
            if self.token == TokenType.ERROR:
                raise TokenError(f"""ERROR: Token Error. Symbol "{self.scanner.tokenString.strip()}" at line {self.scanner.lineIndex} does not represent anything.""")
            return True
        raise SyntaxError(f"""ERROR: Syntax Error. Expected token {token} at line {self.scanner.lineIndex}, but got {self.token}.""")

    def declare_symbol(self, node, currentScopeOnly=False):
        if self.scopeStack.check_symbol(node.name, currentScopeOnly):
            raise SyntaxError(f"""ERROR: Scope Error. Symbol "{node.name}" at line {node.lineno} has already been declared.""")
        else:
            self.scopeStack.add_symbol(node.name)
        return None

    def assert_symbol(self):
        if not self.scopeStack.check_symbol(self.tokenStringBackup[0]):
            raise SyntaxError(f"""ERROR: Scope Error. Symbol "{self.tokenStringBackup[0]}" at line {self.tokenStringBackup[1]} isn't global and also has not been locally declarated.""")
        return None

    def reference_exp(self):
        t = self.new_node()
        self.match(TokenType.ID)
        self.assert_symbol()
        t.attribute = TokenType.ID.name
        if self.token == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            if self.token != TokenType.RPAREN:
                t.add_child(self.arg_list())
            self.match(TokenType.RPAREN)
            t.kind = NodeKind.CALL
            return t
        t.kind = NodeKind.VAR_REF
        if self.token == TokenType.LBRACKETS:
            self.match(TokenType.LBRACKETS)
            t.add_child(self.expression())
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
        if self.token == TokenType.LT:
            self.match(TokenType.LT)
            return TokenType.LT
        elif self.token == TokenType.LTEQ:
            self.match(TokenType.LTEQ)
            return TokenType.LTEQ
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
                    t.add_child(self.expression())
                    return t
                return self.simple_expression(t)
            return t
        return self.simple_expression()

    def simple_expression(self, baseNode=None):
        # simple-expression → additive-expression {relop additive-expression}
        t = self.additive_expression(baseNode)
        while self.is_token_relop():
            p = self.new_node(kind=NodeKind.RELOP)
            p.add_child(t)
            p.attribute = self.match_relop()
            p.add_child(self.additive_expression())
            t = p
        return t

    def additive_expression(self, baseNode=None):
        # additive-expression → term {mulop term}
        t = self.term(baseNode)
        while self.is_token_addop():
            p = self.new_node(kind=NodeKind.ADDOP)
            p.add_child(t)
            p.attribute = self.match_addop()
            p.add_child(self.term())
            t = p
        return t

    def term(self, baseNode=None):
        # term → factor {mulop factor}
        if baseNode is None:
            t = self.factor()
        else:
            t = baseNode
        while self.is_token_mulop():
            p = self.new_node(kind=NodeKind.MULOP)
            p.add_child(t)
            p.attribute = self.match_mulop()
            t = p
            t.add_child(self.factor())
        return t

    def is_token_relop(self):
        return self.token == TokenType.LT or \
            self.token == TokenType.LTEQ or \
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
                self.token == TokenType.RPAREN or \
                self.token == TokenType.RCBRACES

    def factor(self):
        # factor → ( expression ) | var | call | NUM
        if self.token == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            t = self.expression()
            self.match(TokenType.RPAREN)
        elif self.token == TokenType.NUM:
            self.match(TokenType.NUM)
            t = self.new_node(kind=NodeKind.NUM)
            t.attribute = self.tokenStringBackup[0]
            t.name = TokenType.NUM.name
        elif self.token == TokenType.ID:
            self.match(TokenType.ID)
            t = self.new_node(kind=NodeKind.VAR_REF)
            t.attribute = TokenType.ID.name
            t.name = self.tokenStringBackup[0]
            self.assert_symbol()
            if self.token == TokenType.LBRACKETS:
                self.match(TokenType.LBRACKETS)
                t.add_child(self.expression())
                self.match(TokenType.RBRACKETS)
            elif self.token == TokenType.LPAREN:
                self.match(TokenType.LPAREN)
                if self.token != TokenType.RPAREN:
                    t.add_child(self.arg_list())
                self.match(TokenType.RPAREN)
        else:
            raise SyntaxError(f"""ERROR: Syntax Error at line {self.scanner.lineIndex}.""")
        return t

    def arg_list(self):
        t = self.new_node(kind=NodeKind.ARG_LIST)
        t.add_child(self.expression())
        while self.token == TokenType.COMMA:
            self.match(TokenType.COMMA)
            t.add_child(self.expression())
        return t

    def selection_stmt(self):
        # selection-stmt → if ( expression ) statement [else statement]
        t = self.new_node(kind=NodeKind.SELECTION_STMT)
        self.match(TokenType.IF)
        self.match(TokenType.LPAREN)
        t.add_child(self.expression())
        self.match(TokenType.RPAREN)
        t.add_child(self.stmt())
        if self.token == TokenType.ELSE:
            self.match(TokenType.ELSE)
            t.add_child(self.stmt())
        return t

    def iteration_stmt(self):
        # while ( expression ) statement
        t = self.new_node(kind=NodeKind.ITERATION_STMT)
        self.match(TokenType.WHILE)
        self.match(TokenType.LPAREN)
        t.add_child(self.expression())
        self.match(TokenType.RPAREN)
        t.add_child(self.stmt())
        return t

    def return_stmt(self):
        t = self.new_node(kind=NodeKind.RETURN_STMT)
        self.match(TokenType.RETURN)
        if self.token == TokenType.SEMI:
            self.match(TokenType.SEMI)
            return t
        t.add_child(self.expression())
        self.match(TokenType.SEMI)
        return t

    def match_type_specifier(self):
        if self.token == TokenType.INT:
            self.match(TokenType.INT)
            return TokenType.INT
        if self.token == TokenType.VOID:
            self.match(TokenType.VOID)
            return TokenType.VOID
        return None

    def param_list(self):
        # param-list → param {, param}
        t = self.new_node(kind=NodeKind.PARAM_LIST)
        param = self.param()
        t.add_child(param)
        self.scopeStack.add_promise(param.name)
        while self.token == TokenType.COMMA:
            self.match(TokenType.COMMA)
            param = self.param()
            t.add_child(param)
            self.scopeStack.add_promise(param.name)
        return t

    def param(self):
        #  param → type-specifier ID | type-specifier ID [ ]
        t = self.new_node(kind=NodeKind.PARAM)
        t.attribute = self.match_type_specifier()
        if t.attribute == TokenType.VOID:
            return t
        self.match(TokenType.ID)
        t.name = self.tokenStringBackup[0]
        if self.token == TokenType.LBRACKETS:
            self.match(TokenType.LBRACKETS)
            self.match(TokenType.RBRACKETS)
        return t

    def local_declarations(self):
        if self.token == TokenType.INT or self.token == TokenType.VOID:
            t = self.new_node(kind=NodeKind.VAR_DECLARATION)
            t.attribute = self.match_type_specifier()
            self.match(TokenType.ID)
            t.name = self.tokenStringBackup[0]
            self.declare_symbol(t, currentScopeOnly=True)
            if self.token == TokenType.LBRACKETS:
                self.match(TokenType.LBRACKETS)
                self.match(TokenType.RBRACKETS)
            self.match(TokenType.SEMI)
            t.sibling = self.local_declarations()
            return t
        return None

    def compound_stmt(self):
        self.scopeStack.push_scope()
        t = self.new_node(kind=NodeKind.COMPOUND_STMT)
        self.match(TokenType.LCBRACES)
        if self.token != TokenType.RCBRACES:
            if self.token == TokenType.INT or self.token == TokenType.VOID:
                t.add_child(self.local_declarations())
            if self.token != TokenType.RCBRACES:
                t.add_child(self.stmt_list())
        self.match(TokenType.RCBRACES)
        self.scopeStack.pop_scope()
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

    def declaration(self):
        t = self.new_node()
        t.attribute = self.match_type_specifier()
        self.match(TokenType.ID)
        t.name = self.tokenStringBackup[0]
        self.declare_symbol(t)
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
                t.add_child(self.param_list())
            self.match(TokenType.RPAREN)
            t.add_child(self.compound_stmt())
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







