from compiler.scanner import Scanner
from compiler.parser import Parser
from compiler.util import show_tree
from sys import argv

WORK_FOLDER = 'examples'

def start():
    if len(argv) == 2:
        source = argv[1]
    else:
        # source = input('Enter a cm file [filename.cm]: ')
        source = 'tiny.cm'
    try:
        source_file = open(WORK_FOLDER + '\\' + source, 'r')
    except Exception:
        print('ERROR: File not found.')
        return
    trace_file = open(WORK_FOLDER + '\\' + source[:-3] + '.trace', 'w')
    scanner = Scanner(source_file=source_file, trace_file=trace_file, verbose=False)
    parser = Parser(scanner)
    parser.parse()
    source_file.close()
    trace_file.close()
    show_tree(parser.root)
    return

if __name__ == "__main__":
    start()





