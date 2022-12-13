class ScopeStack():

    class Scope():

        def __init__(self):
            self.symbols = []

        def check_symbol(self, symbol):
            return symbol in self.symbols

        def add_symbol(self, symbol):
            self.symbols.append(symbol)
            return None

        def add_symbols(self, symbols):
            for symbol in symbols:
                self.symbols.append(symbols)
            return None

    def __init__(self):
        self.stack = [self.Scope()]
        self.promiseSymbols = None
        self.topIndex = 0

    def push_scope(self):
        self.stack.append(self.Scope())
        self.topIndex += 1
        if self.promiseSymbols is not None:
            self.add_symbols(self.promiseSymbols)
            self.promiseSymbols = None
        return None

    def pop_scope(self):
        aux = self.stack.pop(-1)
        self.topIndex -= 1
        return aux

    def add_symbol(self, symbol):
        self.stack[-1].add_symbol(symbol)
        return None

    def add_symbols(self, symbols):
        for symbol in symbols:
            self.stack[-1].add_symbol(symbol)
        return None

    def add_promise(self, symbol):
        if self.promiseSymbols is None:
            self.promiseSymbols = []
        self.promiseSymbols.append(symbol)
        return None

    def check_symbol(self, symbol, currentScopeOnly=False):
        if currentScopeOnly:
            return self.stack[-1].check_symbol(symbol)
        for i in range(self.topIndex, -1, -1):
            if self.stack[i].check_symbol(symbol):
                return True
        return False
