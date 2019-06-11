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
        | TERM
    
    next: "X" ltl

    future: "F" ltl

    global: "G" ltl

    until: ltl "U" ltl

    state : neg
          | con
    
    neg: "~" ltl

    con: ltl "&" ltl

    TERM : "red_room" | "orange_room" | "yellow_room" | "green_room" | "blue_room" | "purple_room"
            | "landmark_1" | "landmark_2" | "landmark_3" | "landmark_4" | "landmark_5"
            | "first_floor" | "second_floor" | "third_floor" | "fourth_floor" | "fifth_floor"

        %import common.WS
        %ignore WS
"""

ltl_grammar_ez = """
    ltl : next
        | future
        | global
        | until
        | "(" ltl ")"
        | state
        | TERM
    
    next: "X" TERM

    future: "F" TERM

    global: "G" TERM

    until: TERM "U" TERM

    state : neg
          | con
    
    neg: "~" TERM

    con: TERM "&" TERM

    TERM : "red_room" | "orange_room" | "yellow_room" | "green_room" | "blue_room" | "purple_room"
            | "landmark_1" | "landmark_2" | "landmark_3" | "landmark_4" | "landmark_5"
            | "first_floor" | "second_floor" | "third_floor" | "fourth_floor" | "fifth_floor"

        %import common.WS
        %ignore WS
"""   

class LarkTransformer(Transformer):
    def until(self, ptree):
        print("""
    some u:Time | {
        all t:u^prev-u | Robot.where[t] in %s.at
        Robot.where[u] in %s.at
    }""" % (ptree[0], ptree[1]))

    def term(self, ptree):
        print("in %s.at" % ptree[0])

    def neg(self, ptree):
        pass

def make_ltl_ast(grounding):
    """
    make_ltl_ast(grounding: str) -> Tree
    parse an ltl ast from a given grounding string
    """

    parser = Lark(ltl_grammar_ez, start='ltl', ambiguity='explicit')
    ptree = parser.parse(grounding)
    
    return ptree

def compile(ptree, name="grounding"):
    print("pred %s {" % (name))
    LarkTransformer().transform(ptree)
    print("}")

def tests():
    """
    LTL Goals:
    1) ~ red_room U green_room
    2) F red_room U green_room
    3) F green_room U green_room
    4) ~ red_room U green_room
    5) F red_room & green_room
    6) ~ green_room & green_room
    """

    goal0 = make_ltl_ast("red_room U green_room")
    print(goal0)
    compile(goal0)
    #goal1 = make_ltl_ast("(~red_room) U green_room") # 1

def make_png(grounding):
    parser = Lark(ltl_grammar, start='ltl', ambiguity='explicit')
    tree.pydot__tree_to_png(parser.parse(grounding), './parse.png')

if __name__ == "__main__":
    tests()
    #make_png('(~red_room) U green_room')