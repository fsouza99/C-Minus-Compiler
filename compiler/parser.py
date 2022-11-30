from .globals import *
from .util import *
from .scanner import *

IDGenerator = IDGenerator()

class TreeNode():

    def __init__(self, child=None, kind : NodeKind = None, lineno : int = None, attribute=None):
        self.children = []
        if child is not None:
            self.children.append(child)
        self.kind = NodeKind.UNDEFINED if kind is None else kind
        self.number = next(IDGenerator)
        self.attribute = attribute
        self.lineno = lineno
    
    def addChild(self, child):
        self.children.append(child)
        return None

class Parser():

    def __init__(self, scanner: Scanner):
        self.token = self.root = None
        self.scanner = scanner

    def match(self, token):
        if self.token == token:
            self.token = self.scanner.get_token()
            return True
        raise Exception(f"""ERROR: Syntax Error. Expected token: {self.token}. Received token: {token}. Line: {self.scanner.line_index}""")

    def reference_exp(self):
        t = TreeNode(lineno=self.scanner.line_index)
        self.match(TokenType.ID)
        if self.token == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            if self.token != TokenType.RPAREN:
                t.addChild(self.arg_list())
            self.match(TokenType.RPAREN)
            t.kind = NodeKind.CALL_EXP
            return t
        t.kind = NodeKind.VAR_REF_EXP
        if self.token == TokenType.LBRACKETS:
            self.match(TokenType.LBRACKETS)
            t.addChild(self.expression())
            self.match(TokenType.RBRACKETS)
        return t

    def expression_stmt(self):
        if self.token == TokenType.SEMI:
            self.match(TokenType.SEMI)
            t = TreeNode(lineno=self.scanner.line_index)
            t.kind = NodeKind.SEMI_STMT
            return t
        t = self.expression()
        self.match(TokenType.SEMI)
        return t

    def expression(self):
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.EXP
        if self.token == TokenType.ID:
            child = self.reference_exp()
            if child.kind == NodeKind.VAR_REF_EXP:
                if self.token == TokenType.ASSIGN:
                    self.match(TokenType.ASSIGN)
                    t.kind = NodeKind.VAR_ASSIGN
                    t.addChild(child)
                    t.addChild(self.expression())
                    return t
                t.addChild(self.simple_expression(child))
                return t
            t.addChild(child)
            return t
        t.addChild(self.simple_expression())
        return t

    def simple_expression(self, initialTerm=None):
        # simple-expression → additive-expression {relop additive-expression}
        t = TreeNode(lineno=self.scanner.line_index)
        t.addChild(self.additive_expression(initialTerm))
        t.kind = NodeKind.SIMPLE_EXP
        while self.is_token_relop():
            if self.token == TokenType.LTEQ:
                self.match(TokenType.LTEQ)
            elif self.token == TokenType.LT:
                self.match(TokenType.LT)
            elif self.token == TokenType.GT:
                self.match(TokenType.GT)
            elif self.token == TokenType.GTEQ:
                self.match(TokenType.GTEQ)
            elif self.token == TokenType.COMP:
                self.match(TokenType.COMP)
            elif self.token == TokenType.DIFF:
                self.match(TokenType.DIFF)
            t.addChild(self.additive_expression())
        return t

    def additive_expression(self, initialTerm=None):
        # additive-expression → term {mulop term}
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.ADDITIVE_EXP
        t.addChild(self.term(initialTerm))
        while self.is_token_addop():
            if self.token == TokenType.PLUS:
                self.match(TokenType.PLUS)
            elif self.token == TokenType.MINUS:
                self.match(TokenType.MINUS)
            t.addChild(self.term())
        return t

    def term(self, initialTerm=None):
        # term → factor {mulop factor}
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.TERM
        if initialTerm is None:
            t.addChild(self.factor())
        else:
            t.addChild(initialTerm)
            initialTerm.kind = NodeKind.FACTOR
        while self.is_token_mulop():
            if self.token == TokenType.TIMES:
                self.match(TokenType.TIMES)
            elif self.token == TokenType.OVER:
                self.match(TokenType.OVER)
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

    def factor(self):
        # factor → ( expression ) | var | call | NUM
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.FACTOR
        if self.token == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            t.addChild(self.expression())
            self.match(TokenType.RPAREN)
        elif self.token == TokenType.NUM:
            self.match(TokenType.NUM)
            self.attribute = TokenType.NUM
        else:
            self.match(TokenType.ID)
            self.attribute = TokenType.ID
            if self.token == TokenType.LBRACKETS:
                self.match(TokenType.LBRACKETS)
                t.addChild(self.expression())
                self.match(TokenType.RBRACKETS)
            elif self.token == TokenType.LPAREN:
                self.match(TokenType.LPAREN)
                if self.token != TokenType.RPAREN:
                    t.addChild(self.arg_list())
                self.match(TokenType.RPAREN)
        return t

    def arg_list(self):
        t = TreeNode(lineno=self.scanner.line_index)
        t.addChild(self.expression())
        t.kind = NodeKind.ARG_LIST
        while self.token == TokenType.COMMA:
            self.match(TokenType.COMMA)
            t.addChild(self.expression())
        return t

    def selection_stmt(self):
        # selection-stmt → if ( expression ) statement [else statement]
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.SELECTION_STMT
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
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.ITERATION_STMT
        self.match(TokenType.WHILE)
        self.match(TokenType.LPAREN)
        t.addChild(self.expression())
        self.match(TokenType.RPAREN)
        t.addChild(self.stmt())
        return t

    def return_stmt(self):
        self.match(TokenType.RETURN)
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.RETURN_STMT
        if self.token == TokenType.SEMI:
            self.match(TokenType.SEMI)
            return t
        t.addChild(self.expression())
        self.match(TokenType.SEMI)
        return t

    def type_specifier(self):
        if self.token == TokenType.INT:
            self.match(TokenType.INT)
            return TokenType.INT
        if self.token == TokenType.VOID:
            self.match(TokenType.VOID)
            return TokenType.VOID
        return None

    def param_list(self):
        # param-list → param {, param}
        t = TreeNode(lineno=self.scanner.line_index)
        t.addChild(self.param())
        t.kind = NodeKind.PARAM_LIST
        while self.token == TokenType.COMMA:
            self.match(TokenType.COMMA)
            t.addChild(self.param())
        return t

    def param(self):
        #  param → type-specifier ID | type-specifier ID [ ]
        t = TreeNode(lineno=self.scanner.line_index)
        type_specifier = self.type_specifier()
        t.kind = NodeKind.INT_PARAM if type_specifier == TokenType.INT else NodeKind.VOID_PARAM
        if type_specifier == TokenType.VOID:
            return t
        self.match(TokenType.ID)
        if self.token == TokenType.LBRACKETS:
            self.match(TokenType.LBRACKETS)
            self.match(TokenType.RBRACKETS)
        return t

    def local_declarations(self):
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.LOCAL_DECLARATIONS
        while self.token == TokenType.INT or self.token == TokenType.VOID:
            v = TreeNode(lineno=self.scanner.line_index)
            self.type_specifier()
            v.kind = NodeKind.VAR_DECLARATION
            self.match(TokenType.ID)
            if self.token == TokenType.LBRACKETS:
                self.match(TokenType.LBRACKETS)
                self.match(TokenType.RBRACKETS)
            self.match(TokenType.SEMI)
            t.addChild(v)
        return t

    def compound_stmt(self):
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.COMPOUND_STMT
        self.match(TokenType.LCBRACES)
        if self.token != TokenType.RCBRACES:
            if self.token == TokenType.INT or self.token == TokenType.VOID:
                t.addChild(self.local_declarations())
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
        t = TreeNode(self.stmt(), lineno=self.scanner.line_index)
        t.kind = NodeKind.STMT_LIST
        while self.token != TokenType.RCBRACES:
            t.addChild(self.stmt())
        return t

    def declaration(self):
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.DECLARATION
        type_specifier = self.type_specifier()
        self.match(TokenType.ID)
        if self.token == TokenType.SEMI:
            self.match(TokenType.SEMI)
            t.kind = NodeKind.VAR_DECLARATION
            self.match(TokenType.SEMI)
        elif self.token == TokenType.LBRACKETS:
            self.match(TokenType.LBRACKETS)
            self.match(TokenType.NUM)
            self.match(TokenType.RBRACKETS)
            t.kind = NodeKind.VAR_DECLARATION
            self.match(TokenType.SEMI)
        elif self.token == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            if self.token == TokenType.INT or self.token == TokenType.VOID:
                t.addChild(self.param_list())
            self.match(TokenType.RPAREN)
            t.addChild(self.compound_stmt())
            t.kind = NodeKind.FUN_DECLARATION
        return t

    def declaration_list(self):
        t = TreeNode(lineno=self.scanner.line_index)
        t.kind = NodeKind.DECLARATION_LIST
        while self.token != TokenType.ENDOFFILE:
            t.addChild(self.declaration())
        return t

    def parse(self):
        self.token = self.scanner.get_token()
        self.root = self.declaration_list()
        if self.token != TokenType.ENDOFFILE:
            raise Exception("ERROR: Code ends before file.")
        return self.root







