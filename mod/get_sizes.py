import sys
import csv
from lark import Lark, tree, Token

def tree_size(tree):
    if isinstance(tree, Token):
        return 0
    else:
        if tree.data == "ltl":
            return sum([tree_size(child) for child in tree.children])
        else:
            return sum([1 + tree_size(child) for child in tree.children])


if __name__ == "__main__":
    with open("mod/ALL.tsv", "r") as tsvfile: # might cause wd problems
        fp = open("mod/ALL_w_sizes.tsv", "w")
        tsvreader = csv.reader(tsvfile, delimiter='\t')
        parser = Lark(open('mod/ltl.lark').read(), start='ltl', ambiguity='explicit')
        for row in tsvreader:
            size = tree_size(parser.parse(row[0]))
            fp.write(row[0] + "\t" + row[1] + "\t" + str(size) + "\n")
        fp.close()
