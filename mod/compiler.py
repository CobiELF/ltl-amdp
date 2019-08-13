#imports
import sys
from lark import Lark, tree, Visitor, Transformer

class LTLTransformer(Transformer):
    
    def ltl(self, children):
        return children[0]

    def neg(self, children):
        return "not " + children[0]
    
    def until(self, children): #TODO consider special cases
        return "some u:Time | {\n\tall p:u.^prev-u | %s\n\t%s}" % (children[0].replace("[t]", "[p]"), children[1].replace("[t]", "[u]"))

    def glob(self, children):
        return ("all g:Time | %s" % children[0].replace("[t]", "[g]"))

    def con(self, children):
        return "(%s) and (%s)" % (children[0], children[1])

    def future(self, children):
        return ("some f:Time | %s" % children[0].replace("[t]", "[f]"))

    def term(self, children):
        return "Robot.where[t] in %s.at" % children[0]

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

def simple_tests():
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
    
def big_tests():
    simple = [
        "G (landmark_1)",
        "F (landmark_1)",
        "landmark_1 U landmark_2",
        "F (landmark_1) & G (landmark_2)",
        "G (landmark_2) & F (landmark_1)",
        "~ (landmark_1) U landmark_2",
        "F (landmark_3 & F (first_floor))",
        "G (landmark_3 & G (first_floor))",
        "first_floor U ~yellow_room",
        "~ (landmark_1) U G (first_floor)"
    ]

    for grounding in simple:
        print(grounding)
        compile_tree(make_ltl_ast(grounding))
        print()

def target_test(n):
    fp = open("ALL_TAR", "r")

    lineno=0
    for line in fp:
        if lineno > n:
            break
        else:
            print(line)
            compile_tree(make_ltl_ast(line))
            print()

    fp.close()

def test_grounding(grounding):
    print("Grounding: %s" % grounding)
    compile_tree(make_ltl_ast(grounding))
    print()

def make_png(grounding):
    try:
        parser = Lark(open('mod/ltl.lark').read(), start='ltl', ambiguity='explicit')
    except FileNotFoundError:
        parser = Lark(open('./ltl.lark').read(), start='ltl', ambiguity='explicit')
    tree.pydot__tree_to_png(parser.parse(grounding), './parse.png')

if __name__ == "__main__":
    test_grounding("G (landmark_1) U yellow_room")
    test_grounding("F (yellow_room) U (landmark_1)")