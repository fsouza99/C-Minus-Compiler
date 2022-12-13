from compiler.scanner import Scanner
from compiler.parser import Parser
from compiler.print import TreePrinter
from sys import argv

import os

OUT_DIR = os.path.join(os.getcwd(), 'examples')
CM_DIR = os.path.join(OUT_DIR, 'cms')
TRACE_DIR = os.path.join(OUT_DIR, 'traces')
TREE_DIR = os.path.join(OUT_DIR, 'trees')

def start():
    if len(argv) == 2:
        source = argv[1]
    else:
        source = input('Enter a cm file [filename.cm]: ')
    try:
        path = os.path.join(CM_DIR, source)
        sourceFile = open(path, 'r')
    except Exception:
        print('ERROR: File not found.')
        return
    traceFile = open(os.path.join(TRACE_DIR, source[:-3]) + '.trace', 'w')
    scanner = Scanner(sourceFile=sourceFile, traceFile=traceFile, verbose=False)
    parser = Parser(scanner)
    try:
        parser.parse()
        # TreePrinter.show_tree(parser.root)
        TreePrinter.save_tree(parser.root, filename=os.path.join(TREE_DIR, source[:-3])+'.tree')
        print(f"""Number of created nodes: {parser.nodeCount}.""")
    except Exception as exc:
        print(exc)
    finally:
        sourceFile.close()
        traceFile.close()
    return None

if __name__ == "__main__":
    start()





