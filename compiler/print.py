from .globals import TokenType, NodeKind

class TreePrinter():

    spaces = 0
    spaceUnit = 4

    def grow_identation():
        TreePrinter.spaces += TreePrinter.spaceUnit

    def shrink_identation():
        TreePrinter.spaces -= TreePrinter.spaceUnit

    def show_node(node):
        print(node.to_string(TreePrinter.spaces))
        return None

    def show_tree(root):
        p = root
        while p is not None:
            TreePrinter.show_node(p)
            TreePrinter.grow_identation()
            for child in p.children:
                TreePrinter.show_tree(child)
            p = p.sibling
            TreePrinter.shrink_identation()
        return None

    def save_node(node, file):
        file.write(node.to_string(TreePrinter.spaces) + '\n')
        return None    

    def print_expand(node, file):
        p = node
        while p is not None:
            TreePrinter.save_node(p, file)
            TreePrinter.grow_identation()
            for child in p.children:
                TreePrinter.print_expand(child, file)
            p = p.sibling
            TreePrinter.shrink_identation()
        return None

    def save_tree(root, filename='output.tree'):
        with open(filename, 'w') as file:
            TreePrinter.print_expand(root, file)
        return None






