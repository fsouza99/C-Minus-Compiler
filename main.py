from compiler.scanner import Scanner
from compiler.parser import Parser
from compiler.print import TreePrinter
from sys import argv

import os

OUT_DIR = os.path.join(os.getcwd(), 'examples')

def start():
    if len(argv) == 2:
        source = argv[1]
    else:
        source = input('Enter a cm file [filename.cm]: ')
        # source = 'parity (error).cm'
        # source = 'factorial (error).cm'
        # source = 'euclids-gcd (error).cm'
        # source = 'selection-sort (error).cm'
    try:
        path = os.path.join(OUT_DIR, source)
        source_file = open(path, 'r')
    except Exception:
        print('ERROR: File not found.')
        return
    trace_file = open(os.path.join(OUT_DIR, source[:-3]) + '.trace', 'w')
    scanner = Scanner(source_file=source_file, trace_file=trace_file, verbose=False)
    parser = Parser(scanner)
    try:
        parser.parse()
        # TreePrinter.show_tree(parser.root)
        TreePrinter.save_tree(parser.root, filename=os.path.join(OUT_DIR, source[:-3])+'.tree')
        print(f"""Number of created nodes: {parser.nodeCount}.""")
    except Exception as exc:
        # raise exc
        print(exc)
    finally:
        source_file.close()
        trace_file.close()
    return None

if __name__ == "__main__":
    start()





