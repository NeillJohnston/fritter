from arpeggio import OneOrMore, Optional, ParserPython, PTNodeVisitor, RegExMatch, StrMatch, ZeroOrMore, EOF, visit_parse_tree

from fritter.lang import st


SPAN_UNITS_MAP = {
    "w": 4.0,
    "h": 2.0,
    "q": 1.0,
    "e": 0.5,
    "s": 0.25,
    "t": 0.125,
}


class QStrMatch(StrMatch):
    """Quiet string match."""
    suppress = True


# Operators
def Octave():   return RegExMatch(r"[\-+]+")
def Dynamics(): return QStrMatch("."), RegExMatch(r"\w+")
def Span():     return QStrMatch("/"), RegExMatch(r"\w+")
def Repeat():   return QStrMatch("*"), RegExMatch(r"\d+")
def postfix(): return [Octave, Dynamics, Span, Repeat]

# Atoms
def Cont():  return "_"
def Rest():  return "~"
def Erase(): return "<~"
def Note():  return RegExMatch(r"[\w#]+")
def generator(): return QStrMatch("<"), QStrMatch(">")  # TODO
def atom():      return [group, tie, Cont, Rest, Erase, Note], ZeroOrMore(postfix)

# Sequence construction
def group(): return QStrMatch("("), expression, QStrMatch(")")
def tie():   return QStrMatch("["), expression, QStrMatch("]")

def Num():       return RegExMatch(r"\d+")
def choice():    return QStrMatch("|"), OneOrMore(Num, sep=QStrMatch(",")), QStrMatch(":")
def Modulator(): return RegExMatch(r"[\w#]+"), QStrMatch(";")

def cat(): return ZeroOrMore(atom)
def par(): return OneOrMore(cat, sep=QStrMatch(","))
def bra(): return OneOrMore(par, sep=choice)
def mod(): return Optional(Modulator), bra

expression = mod

# Grammar root
def fritter(): return expression, EOF


class FritterVisitor(PTNodeVisitor):
    # Operators

    def visit_Octave(self, node, _children):
        shift = node.value.count("+") - node.value.count("-")
        return st.OctaveShift(None, shift)

    def visit_Dynamics(self, node, _children):
        return st.Dynamics(None, node.value)

    def visit_Span(self, node, _children):
        units = 0.0
        for c in node.value:
            # TODO error handling
            units += SPAN_UNITS_MAP[c]
        return st.Span(None, node.value)

    def visit_Repeat(self, node, _children):
        return st.Repeat(None, int(node.value))

    # Atoms

    def visit_Cont(self, _node, _children):
        return st.Continuation()

    def visit_Rest(self, _node, _children):
        return st.Rest()

    def visit_Erase(self, _node, _children):
        return st.Erase()

    def visit_Note(self, node, _children):
        return st.Note(node.value)

    def visit_atom(self, _node, children):
        atom = children[0]
        for operator in children.postfix:
            operator.child = atom
            atom = operator

        return atom

    # Sequence construction

    def visit_group(self, _node, children):
        return children

    def visit_tie(self, _node, children):
        return st.Tie(children[0])

    def visit_choice(self, _node, children):
        return list(map(int, children))

    def visit_cat(self, _node, children):
        if len(children) == 1: return children[0]

        return st.Concatenation(children)

    def visit_par(self, _node, children):
        if len(children) == 1: return children[0]

        return st.Parallel(children)

    def visit_bra(self, _node, children):
        if not children.choice: return children.par[0]

        return st.Branch(
            children.par,
            {
                num: index + 1
                for index, nums in enumerate(children.choice)
                for num in nums
            }
        )

    def visit_mod(self, _node, children):
        child = children.bra[0]
        if not children.Modulator: return child

        return st.Modulation(child, children.Modulator[0])


def parse_fritter(text: str) -> ...:
    parser = ParserPython(fritter, memoization=True)
    parse_tree = parser.parse(text)

    visitor = FritterVisitor()
    return visit_parse_tree(parse_tree, visitor)
