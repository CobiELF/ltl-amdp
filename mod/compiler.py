#imports
import sys
from lark import Lark, tree, Visitor, Transformer

ltl_grammar = """
    ltl : next
        | future
        | global
        | until
        | "(" ltl ")"
        | state
        | term
    
    next : "X" ltl

    future : "F" ltl

    global : "G" ltl

    until : ltl "U" ltl

    state : neg
          | con
    
    neg : "~" ltl

    con : ltl "&" ltl

    term : TERM

    TERM : "red_room" | "orange_room" | "yellow_room" | "green_room" | "blue_room" | "purple_room"
            | "landmark_1" | "landmark_2" | "landmark_3" | "landmark_4" | "landmark_5"
            | "first_floor" | "second_floor" | "third_floor" | "fourth_floor" | "fifth_floor"

        %import common.WS
        %ignore WS
"""

class LTLTransformer(Transformer):
    #TODO handle "futures" modifying "untils"
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

    def con(self, children):
        return """
        Robot.where[first] %s
        Robot.where[first] %s
        """ % (children[0], children[1])

    def future(self, children): #TODO
        pass

    def term(self, children):
        return "in %s.at" % children[0]

def make_ltl_ast(grounding):
    """
    make_ltl_ast(grounding: str) -> Tree
    parse an ltl ast from a given grounding string
    """

    parser = Lark(ltl_grammar, start='ltl', ambiguity='explicit')
    ptree = parser.parse(grounding)
    
    return ptree

def compile_tree(ptree, name="grounding"):
    #TODO maybe make this take i na grounding then just do the whole thing?

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

    #TODO stuff with goals
    
def make_png(grounding):
    parser = Lark(ltl_grammar, start='ltl', ambiguity='explicit')
    tree.pydot__tree_to_png(parser.parse(grounding), './parse.png')

if __name__ == "__main__":
    tests()
    #make_png('(~red_room) U green_room')