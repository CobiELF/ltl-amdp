#imports
import sys
from lark import Lark, tree, Visitor, Transformer

class LTLTransformer(Transformer):
    
    def ltl(self, children):
        return children[0]

    def state (self, children):
        return children[0]

    def neg(self, children):
        return "not " + children[0]
    
    def until(self, children):
        return """
        some u:Time | {
            all t:u.^prev-u | Robot.where[t] %s
            Robot.where[u] %s
        }""" % (children[0], children[1])

    def glob(self, children):
        return children[0]

    def con(self, children):
        return "Robot.where[first] %s \n Robot.where[first] %s" % (children[0], children[1])

    def future(self, children): #TODO
        if "u:Time" not in children[0]:
            return ("some u:Time | { \n some t:u.^prev-u | %s" % children[0]).replace("first", "u", 1)

        if "all t:u" in children[0]:
            return children[0].replace("all t", "some t")

    def term(self, children):
        return "in %s.at" % children[0]

def make_ltl_ast(grounding):
    """
    make_ltl_ast(grounding: str) -> Tree
    parse an ltl ast from a given grounding string
    """

    try:
        parser = Lark(open('mod/ltl.lark').read(), start='ltl', ambiguity='explicit')
    except FileNotFoundError:
        parser = Lark(open('./ltl.lark').read(), start='ltl', ambiguity='explicit')
    ptree = parser.parse(grounding)
    
    return ptree

def compile_tree(ptree, name="grounding"):
    print("pred %s {" % name)
    print(LTLTransformer().transform(ptree))
    print("}")

def tests():
    """
    LTL Goals:
    1) ~ red_room U green_room
    2) F red_room U green_room
    3) F green_room U green_room
    4) ~ red_room & green_room
    5) F red_room & green_room
    6) ~ green_room & green_room
    """

    goal1 = make_ltl_ast("(~red_room) U green_room")
    goal2 = make_ltl_ast("F (red_room U green_room)")
    goal3 = make_ltl_ast("F (green_room U green_room)")
    goal4 = make_ltl_ast("(~ red_room) & green_room")
    goal5 = make_ltl_ast("F (red_room & green_room)")
    goal6 = make_ltl_ast("(~ green_room) & green_room")

    for tree in [goal1, goal2, goal3, goal4, goal5, goal6]:
        compile_tree(tree)
    
def make_png(grounding):
    parser = Lark(open('mod/ltl.lark'), start='ltl', ambiguity='explicit')
    tree.pydot__tree_to_png(parser.parse(grounding), './parse.png')

if __name__ == "__main__":
    pass
    #tests()
    #make_png('(~red_room) U green_room')