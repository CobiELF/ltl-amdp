#imports
import sys
from lark import Lark, tree, Visitor, Transformer

def until_replace(child, isLeft):
    # TODO make this work for children on both sides, and with global
    if isLeft:
        if "some" in child: #F
            childvar = child[child.index("[")+1]
            child = child.replace(childvar, "p") #change previous variable to p

            separatorloc = child.index("|") + 2
            return "some u:Time | {\n\tsome p:u.^prev-u | %s\n\t" % child[separatorloc:]

        if "all" in child: #G
            childvar = child[child.index("[")+1]
            child = child.replace(childvar, "p") #change previous variable to p

            separatorloc = child.index("|") + 2
            return "some u:Time | {\n\tall p:u.^prev-u | %s\n\t" % child[separatorloc:]
        else:
            return "some u:Time | {\n\tall p:u.^prev-u | %s\n\t" % child

    if not isLeft and "all" in child:
        return child.replace("Time", "u.^next")

    else:
        return child.replace("[t]", "[p]")

class LTLTransformer(Transformer): #this actually does the transformation from ast to alloy string
    
    def ltl(self, children):
        return children[0]

    def neg(self, children):
        return "not " + children[0]
    
    def until(self, children): #TODO consider special cases
        #return "some u:Time | {\n\tall p:u.^prev-u | %s\n\t%s}" % (children[0].replace("[t]", "[p]"), children[1].replace("[t]", "[u]"))
        #return "some u:Time | {\n\tall p:u.^prev-u | %s\n\t%s}" % (until_replace(children[0]), children[1].replace("[t]", "[u]"))
        return until_replace(children[0], True) + until_replace(children[1], False) +"\n\t}"

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
    Examples given in alloy part of the project.
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
    """
    Bigger, more comprehensive unit testing.
    """
    simple = [ #one operator, one term OR strict forms found commonly in target files
        "G (landmark_1)",
        "F (landmark_1)",
        "landmark_1 U landmark_2",
        "F (landmark_1) & G (landmark_2)",
        "G (landmark_2) & F (landmark_1)",
        "~ (landmark_1) U landmark_2",
        "F (landmark_3 & F (first_floor))",
        "G (landmark_3 & G (first_floor))"
    ]

    wonky = [ # statements that don't translate correctly from LTL to alloy
        "G (landmark_1) U yellow_room",
        "F (yellow_room) U landmark_1"
    ]

    pass #return tests that you want

def target_test(n): #tests from target file
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

def test_grounding(grounding): # wrapper function for making the AST and compiling i
    print("Grounding: %s" % grounding)
    compile_tree(make_ltl_ast(grounding))
    print()

def make_png(grounding): # make a visual png of the AST for a given grounding. requires pydot package.
    try:
        parser = Lark(open('mod/ltl.lark').read(), start='ltl', ambiguity='explicit')
    except FileNotFoundError:
        parser = Lark(open('./ltl.lark').read(), start='ltl', ambiguity='explicit')
    tree.pydot__tree_to_png(parser.parse(grounding), './parse.png')

if __name__ == "__main__":
    test_grounding("F (yellow_room) U F (landmark_1)")