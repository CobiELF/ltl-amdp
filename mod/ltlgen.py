import random
from lark import Lark, tree, Visitor, Transformer

#TERMS = ["red_room" , "orange_room" , "yellow_room" , "green_room" , "blue_room" , "purple_room", "landmark_1" , "landmark_2" , "landmark_3" , "landmark_4" , "landmark_5", "first_floor" , "second_floor" , "third_floor" , "fourth_floor" , "fifth_floor"]
TERMS = ["red_room", "first_floor", "landmark_1", "green_room"]
NLS = ["the red room", "the first floor", "landmark one", "the green room"]

def add_unop(exprs, op):
    return [op + " ( " + expr + " )" for expr in exprs]

def add_binop_head(exprs, op):
    binop_exprs = []
    for term in TERMS:
        for expr in exprs:
            binop_exprs.append("( " + term + " ) " + op + " ( " + expr + " )")
    return binop_exprs

def add_binop_tail(exprs, op):
    binop_exprs = []
    for term in TERMS:
        for expr in exprs:
            binop_exprs.append("( " + expr + " ) " + op + " ( " + term + " ) ")
    return binop_exprs

def add_binop(lefts, op, rights):
    binop_exprs = []
    for left in lefts:
        for right in rights:
            binop_exprs.append("( " + left + " ) " + op + " ( " + right + " )")
    return binop_exprs

class LTLTransformer(Transformer):

    def ltl(self, children):
        return children[0]

    def neg(self, children):
        return "do not " + children[0]

    def until(self, children):
        return children[0] + " until " + children[1]
    
    def glob(self, children):
        return "always " + children[0]

    def con(self, children):
        return children[0] + " and " + children[1]

    def future(self, children):
        return "go to " + children[0]

    def term(self, children):
        nls = {}
        for i in range(len(TERMS)):
            nls[TERMS[i]] = NLS[i]
        return nls[children[0]]

if __name__ == "__main__":

    # 1ops (~,F,G,U,&)
    # ~ does not make sense without time quantification inside/outside
    F = add_unop(TERMS, "F")
    G = add_unop(TERMS, "G")
    U = add_binop(TERMS, "U", TERMS)
    # & does not make sense without time quantification inside/outside

    # 2ops (~~,~F,~G,~U,~&)
    # assume nots are distributed in so dont worry about applying

    # 2ops (F~,FF,FG,FU,F&)
    FN = add_unop(add_unop(TERMS, "~"), "F")
    # FF does not make sense
    FG = add_unop(G, "F")
    # FU does not make sense
    FA = add_unop(add_binop(TERMS, "&", TERMS), "F")

    # 2ops (G~,GF,GG,GU,G&)
    GN = add_unop(add_unop(TERMS, "~"), "G")
    # GF does not make sense
    # GG does not make sense
    # GU does not make sense
    GA = add_unop(add_binop(TERMS, "&", TERMS), "G")

    # 2ops (U~,UF,UG,UU,U&)
    UN = add_binop(add_unop(TERMS, "~"), "U", TERMS) # "a UNTIL not b" does not seem useful
    # UF does not make sense
    # UG does not make sense
    UU = add_binop(U, "U", TERMS)
    UA = add_binop(add_binop(TERMS, "&", TERMS), "U", TERMS) + add_binop(TERMS, "U", add_binop(TERMS, "&", TERMS))

    # 2ops (&~,&F,&G,&U,&&)
    # nots dont make sense without time
    # &F does not make sense, need time on both sides
    # need time on both sides
    # need time on both sides
    # need time on both sides
    # AA does not make sense

    # 3ops (~~?,~F?,~G?,~U?,~&?)
    # assume nots are distributed in so dont worry about applying

    # 3ops (F~?,FF?,FG?,FU?,F&?)
    # no ~? set
    # FF? does not make sense
    FGN = add_unop(GN, "F")
    # FU? does not make sense
    FAA = add_unop(add_binop(TERMS, "&", add_binop(TERMS, "&", TERMS)), "F")
    FAN = add_unop(add_binop(TERMS, "&", add_unop(TERMS, "~")), "F")

    # 3ops (G~?,GF?,GG?,GU?,G&?)
    GNA = add_unop(add_binop(add_unop(TERMS, "~"), "&", TERMS), "G")
    # GF? does not make sense
    # GG? does not make sense
    # GU? does not make sense
    GAA = add_unop(add_binop(add_binop(TERMS, "&", TERMS), "&", TERMS), "G")

    # 3ops (U~?,UF?,UG?,UU?,U&?)
    # no ~? set
    # UF? does not make sense
    # UG? does not make sense
    UUU = add_binop(UU, "U", TERMS) + add_binop(TERMS, "U", UU)
    UUN = add_binop(UN, "U", TERMS) + add_binop(TERMS, "U", UN)
    UUA = add_binop(UA, "U", TERMS) + add_binop(TERMS, "U", UA)
    UAA = add_binop(add_binop(TERMS, "&", TERMS), "U", add_binop(TERMS, "&", TERMS))
    UNN = add_binop(add_unop(TERMS, "~"), "U", add_unop(TERMS, "~"))
    UAN = add_binop(add_binop(TERMS, "&", TERMS), "U", add_unop(TERMS, "~"))
    UNA = add_binop(add_unop(TERMS, "~"), "U", add_binop(TERMS, "&", TERMS))

    # 3ops (&~?,&F?,&G?,&U?,&&)
    # nots dont make sense without time
    AFF = add_binop(F, "&", F)
    AFG = add_binop(F, "&", G)
    AGF = add_binop(G, "&", F)
    # conjoined untils dont make sense 
    # AA does not make sense

    one_op = F + G + U
    two_op = FN + FG + FA + GN + GA + UN + UU + UA
    three_op = FGN + FAA + FAN + GNA + GAA + UUU + UUN + UUA + UAA + UNN + UAN + UNA + AFF + AFG + AGF
    # print(sum([len(x) for x in [F + G, U]]))
    # print(sum([len(x) for x in [FN, FG, FA, GN, GA, UN, UU, UA]]))
    # print(sum([len(x) for x in [FGN, FAA, FAN, GNA, GAA, UUU, UUN, UUA, UAA, UNN, UAN, UNA, AFF, AFG, AGF]]))

    ops = [one_op, two_op, three_op]
    for fname in ["ltl-nl_1op.tsv", "ltl-nl_2op.tsv", "ltl-nl_3op.tsv"]:
        with open(fname, "w") as fp:
            parser = Lark(open('mod/ltl.lark').read(), start='ltl', ambiguity='explicit')
            for expr in ops[int(fname[7])-1]: # don't @ me
                fp.write(expr + "\t" + LTLTransformer().transform(parser.parse(expr)) + "\n")
            print("%s OPS PROCESSED" % fname[7])