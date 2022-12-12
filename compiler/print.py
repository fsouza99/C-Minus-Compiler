from .globals import TokenType, NodeKind

class TreePrinter():

    spaces = 0
    spaceUnit = 4

    def addIdentation():
        TreePrinter.spaces += TreePrinter.spaceUnit

    def removeIdentation():
        TreePrinter.spaces -= TreePrinter.spaceUnit

    def show_node(node):
        print(node.toString(TreePrinter.spaces))
        return None

    def show_tree(root):
        p = root
        while p is not None:
            TreePrinter.show_node(p)
            TreePrinter.addIdentation()
            for child in p.children:
                TreePrinter.show_tree(child)
            p = p.sibling
            TreePrinter.removeIdentation()
        return None

    def save_node(node, file):
        file.write(node.toString(TreePrinter.spaces) + '\n')
        return None    

    def expand(node, file):
        p = node
        while p is not None:
            TreePrinter.save_node(p, file)
            TreePrinter.addIdentation()
            for child in p.children:
                TreePrinter.expand(child, file)
            p = p.sibling
            TreePrinter.removeIdentation()
        return None

    def save_tree(root, filename='output.tree'):
        with open(filename, 'w') as file:
            TreePrinter.expand(root, file)
        return None






