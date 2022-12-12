from enum import Enum

class TokenType(Enum):
    # reserved words

    IF = 0
    ELSE = 1
    INT = 2
    RETURN = 3
    VOID = 4
    WHILE = 5

    # special symbols

    PLUS = 6
    MINUS = 7
    TIMES = 8
    OVER = 9
    LT = 10
    LTEQ = 11
    GT = 12
    GTEQ = 13
    COMP = 14
    DIFF = 15
    ASSIGN = 16
    SEMI = 17
    COMMA = 18
    LPAREN = 19
    RPAREN = 20
    LBRACKETS = 21
    RBRACKETS = 22
    LCBRACES = 23
    RCBRACES = 24

    # others

    NUM = 25
    ID = 26
    ENDOFFILE = 27
    ERROR = 28


class NodeKind(Enum):

    ADDOP = 0
    ARGS = 1
    ARG_LIST = 2
    ASSIGN = 3
    CALL = 4
    COMPOUND_STMT = 5
    FUN_DECLARATION = 6
    ITERATION_STMT = 7
    MULOP = 8
    NUM = 9
    PARAM = 10
    PARAM_LIST = 11
    RELOP = 12
    RETURN_STMT = 13
    SELECTION_STMT = 14
    UNDEFINED = 15
    VAR_DECLARATION = 16
    VAR_REF = 17





