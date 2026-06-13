from parsy import *  # TODO replace glob import

from fritter.lang import st


r"""
Rough formal definition of the language:

expression    ::= modulations
modulations   ::= branches? (Modulator branches)*
branches      ::= parallel (branch_selectors parallel)*
parallel      ::= concatenation ("," concatenation)*
concatenation ::= atom+

atom  ::= (group | tie | Cont | Rest | Erase | Note) operator*
group ::= "(" expression ")"
tie   ::= "[" expression "]"
Cont  ::= "_"
Rest  ::= "~"
Erase ::= "<~"
Note  ::= /[\w#]+/

operator ::= Octave | Dynamics | Span | Repeat
Octave   ::= ("-" | "+")+
Dynamics ::= "." /\w+/
Span     ::= "/" /[tseqhw]+/
Repeat   ::= "*" /\d+/
"""


SPAN_UNITS_MAP = {
    "w": 4.0,
    "h": 2.0,
    "q": 1.0,
    "e": 0.5,
    "s": 0.25,
    "t": 0.125,
}


def construct_atom(atom: st.Node, operators: list[st.Node]):
    for partial in operators:
        partial.child = atom
        atom = partial
    return atom


def construct_branches(head: st.Node, tail: list[tuple[list[int], st.Node]]) -> st.Node:
    if len(tail) == 0: return head

    tail_selector_lists, tail_nodes = zip(*tail)
    return st.Branches(
        [head] + list(tail_nodes),
        {selector: index+1 for index, selector_list in enumerate(tail_selector_lists) for selector in selector_list}
    )


def construct_mod(modulator: str | None, node: st.Node) -> st.Node:
    if modulator is None: return node

    return st.Modulation(node, modulator)


# Lexemes are tokens with optional whitespace
space = regex(r"\s*")
lexeme = lambda parser: parser << space
strlex = lambda pattern: lexeme(string(pattern))

# Small pieces and forward declarations
num   = lexeme(regex(r"\d+"))

expression  = forward_declaration()
group = forward_declaration()
tie   = forward_declaration()

# Operators
Octave   = lexeme(regex(r"[\-+]+").map(lambda s: s.count("+") - s.count("-")))
Dynamics = lexeme(regex(r"\.(\w+)", group=1))
Span     = lexeme(regex(r"/([tseqhw]+)", group=1).map(lambda s: sum(SPAN_UNITS_MAP[c] for c in s)))
Repeat   = lexeme(regex(r"\*(\d+)", group=1).map(int))
# Parsers for operators will partially construct their nodes, for easy construction later
partial_op = lambda func: (lambda operand: func(None, operand))
postfix    = (
    Octave.map(partial_op(st.OctaveShift))
    | Dynamics.map(partial_op(st.Dynamics))
    | Span.map(partial_op(st.Span))
    | Repeat.map(partial_op(st.Repeat))
)

# Atoms
group .become(strlex("(") >> expression << strlex(")"))
tie   .become(strlex("[") >> expression.map(st.Tie) << strlex("]"))

argless = lambda func: (lambda *_args: func())

Cont      = strlex("_").map(argless(st.Continuation))
Rest      = strlex("~").map(argless(st.Rest))
Erase     = strlex("<~").map(argless(st.Erase))
Note      = lexeme(regex(r"[\w#]+")).map(st.Note)
generator = ...
atom      = seq(group | tie | Cont | Rest | Erase | Note, postfix.many()).combine(construct_atom)

# Structures
selector_list = strlex("|") >> num.sep_by(strlex(",")).map(lambda ns: list(map(int, ns))) << strlex(":")
modulator     = strlex("!") >> regex(r"[\w#]+") << strlex(":")

prune = lambda func: (lambda terms: terms[0] if len(terms) == 1 else func(terms))

concatenation = atom.at_least(1).map(prune(st.Concatenation))
parallel      = concatenation.sep_by(strlex(",")).map(prune(st.Parallel))
branches      = seq(parallel, seq(selector_list, parallel).many()).combine(construct_branches)
modulations   = seq(
    seq(modulator.optional(), branches).combine(construct_mod),
    seq(modulator, branches).combine(construct_mod).many()
).combine(lambda head, tail: [head] + tail).map(prune(st.Concatenation))

expression.become(modulations)


# print(mod_term.parse(""))
print(expression.parse("!mod: a b, c d |3,4: e f, g h"))
#print(expr.parse("1---+.abc/qhw"))
