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

    ADDITIVE_EXP = 0
    ARGS = 1
    ARG_LIST = 2
    CALL_EXP = 3
    COMPOUND_STMT = 4
    DECLARATION = 5
    DECLARATION_LIST = 6
    EXP = 7
    EXP_STMT = 8
    FACTOR = 9
    FUN_DECLARATION = 10
    INT_PARAM = 11
    ITERATION_STMT = 12
    LOCAL_DECLARATIONS = 13
    PARAM_LIST = 14
    RETURN_STMT = 15
    SELECTION_STMT = 16
    SEMI_STMT = 17
    SIMPLE_EXP = 18
    STMT = 19
    STMT_LIST = 20
    TERM = 21
    UNDEFINED = 22
    VAR_ASSIGN = 23
    VAR_DECLARATION = 24
    VAR_REF_EXP = 25
    VOID_PARAM = 26


