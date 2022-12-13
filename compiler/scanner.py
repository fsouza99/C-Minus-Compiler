from .globals import *
from .util import *


class State(Enum):
    START = 0
    INNUM = 1
    INID = 2
    INASSIGN = 3
    INDIFF = 4
    INLT = 5
    INGT = 6
    INOVER = 7
    INMULTI = 8
    INCOMMENT = 9
    INCOMMENTEND = 10
    DONE = 11


RESERVED_WORDS = {
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'int': TokenType.INT,
    'return': TokenType.RETURN,
    'void': TokenType.VOID,
    'while': TokenType.WHILE
}


class Scanner():

    def __init__(self, sourceFile, traceFile=None, verbose=None):
        self.text = sourceFile.read()
        self.EOF = len(self.text)
        self.traceFile = traceFile
        self.lineIndex = 1
        self.tokenString = None
        self._pointer = 0
        self.verbose = traceFile is not None if verbose is None else verbose
        
    def check_reserve(self, tokenString: str):
        return RESERVED_WORDS.get(tokenString, TokenType.ID)

    def get_next_char(self):
        if self._pointer >= self.EOF:
            return None
        char = self.text[self._pointer]
        if char == '\n':
            self.lineIndex += 1
        self._pointer += 1
        return char

    def move_cursor_back(self):
        self._pointer -= 1
        if self.text[self._pointer] == '\n':
            self.lineIndex -= 1
        return

    def save_token(self, currentToken: TokenType, tokenString: str = ''):
        self.traceFile.write(format_token(currentToken, tokenString, self.lineIndex)+"\n")

    def get_token(self):

        self.tokenString = ''
        state = State.START
        while state != State.DONE:
            char = self.get_next_char()
            save = True
            if state == State.START:
                if is_digit(char):
                    state = State.INNUM
                elif is_alphabetic(char):
                    state = State.INID
                else:
                    save = False
                    if char == '=':
                        state = State.INASSIGN
                    elif char == '!':
                        state = State.INDIFF
                    elif char == '>':
                        state = State.INGT
                    elif char == '<':
                        state = State.INLT
                    elif char == '/':
                        state = State.INOVER
                    elif char == ' ' or char == '\t' or char == '\n' or char == '\r':
                        continue
                    else:
                        state = State.DONE
                        if char == '+':
                            currentToken = TokenType.PLUS
                        elif char == '-':
                            currentToken = TokenType.MINUS
                        elif char == '*':
                            currentToken = TokenType.TIMES
                        elif char == '[':
                            currentToken = TokenType.LBRACKETS
                        elif char == ']':
                            currentToken = TokenType.RBRACKETS
                        elif char == '(':
                            currentToken = TokenType.LPAREN
                        elif char == ')':
                            currentToken = TokenType.RPAREN
                        elif char == '{':
                            currentToken = TokenType.LCBRACES
                        elif char == '}':
                            currentToken = TokenType.RCBRACES
                        elif char == ',':
                            currentToken = TokenType.COMMA
                        elif char == ';':
                            currentToken = TokenType.SEMI
                        elif char is None:
                            currentToken = TokenType.ENDOFFILE
                        else:
                            currentToken = TokenType.ERROR
                            save = True
            elif state == State.INID:
                if not is_alphabetic(char):
                    save = False
                    state = State.DONE
                    currentToken = TokenType.ID
                    if char is not None:
                        self.move_cursor_back()
            elif state == State.INNUM:
                if not is_digit(char):
                    save = False
                    state = State.DONE
                    currentToken = TokenType.NUM
                    if char is not None:
                        self.move_cursor_back()
            elif state == State.INASSIGN:
                save = False
                if char == '=':
                    currentToken = TokenType.COMP
                else:
                    currentToken = TokenType.ASSIGN
                    if char is not None:
                        self.move_cursor_back()
                state = State.DONE
            elif state == State.INOVER:
                save = False
                if char == '*':
                    state = State.INCOMMENT
                else:
                    currentToken = TokenType.OVER
                    state = State.DONE
                    if char is not None:
                        self.move_cursor_back()
            elif state == State.INDIFF:
                if char == '=':
                    save = False
                    currentToken = TokenType.DIFF
                else:
                    currentToken = TokenType.ERROR
                    if char is None:
                        save = False
                    else:
                        self.move_cursor_back()
                        self.tokenString = '!'
                state = State.DONE
            elif state == State.INLT:
                save = False
                if char == '=':
                    currentToken = TokenType.LTEQ
                else:
                    currentToken = TokenType.LT
                    if char is not None:
                        self.move_cursor_back()
                state = State.DONE
            elif state == State.INGT:
                save = False
                if char == '=':
                    currentToken = TokenType.GTEQ
                else:
                    currentToken = TokenType.GT
                    if char is not None:
                        self.move_cursor_back()
                state = State.DONE
            elif state == State.INCOMMENT:
                save = False
                if char == '*':
                    state = State.INCOMMENTEND
                elif char is None:
                    state = State.START
            elif state == State.INCOMMENTEND:
                save = False
                if char == '/':
                    state = State.START
                elif char != '*':
                    state = State.INCOMMENT
                elif char is None:
                    state = State.START
            if save:
                self.tokenString += char
            if state == State.DONE and currentToken == TokenType.ID:
                currentToken = self.check_reserve(self.tokenString)
        if self.traceFile:
            if self.tokenString in RESERVED_WORDS.keys():
                self.tokenString = None
            self.save_token(currentToken, self.tokenString)
        if self.verbose:
            show_token(currentToken, self.tokenString, self.lineIndex)
        return currentToken
