from fritter.lang.grammar import expression
from fritter.lang import st


def test_operators():
    tree = expression.parse("x ++ .abc /qe *4")
    assert tree == st.Repeat(
        st.Span(
            st.Dynamics(
                st.OctaveShift(
                    st.Note("x"),
                    2,
                ),
                "abc",
            ),
            1.5,
        ),
        4,
    )


def test_nesting_basic():
    tree = expression.parse("a ((b c) (d e)) ([f g] [h i]) j")
    print(tree)
    assert tree == st.Concatenation([
        st.Note("a"),
        st.Concatenation([
            st.Concatenation([
                st.Note("b"),
                st.Note("c"),
            ]),
            st.Concatenation([
                st.Note("d"),
                st.Note("e"),
            ]),
        ]),
        st.Concatenation([
            st.Tie(
                st.Concatenation([
                    st.Note("f"),
                    st.Note("g"),
                ]),
            ),
            st.Tie(
                st.Concatenation([
                    st.Note("h"),
                    st.Note("i"),
                ]),
            ),
        ]),
        st.Note("j"),
    ])


def test_binop_precedence():
    tree = expression.parse("a b !mod: c d, e f |1,2: g h, i j !mod2: k l")
    assert tree == st.Concatenation([
        st.Concatenation([
            st.Note("a"),
            st.Note("b"),
        ]),
        st.Modulation(
            st.Branches(
                [
                    st.Parallel([
                        st.Concatenation([
                            st.Note("c"),
                            st.Note("d"),
                        ]),
                        st.Concatenation([
                            st.Note("e"),
                            st.Note("f"),
                        ]),
                    ]),
                    st.Parallel([
                        st.Concatenation([
                            st.Note("g"),
                            st.Note("h"),
                        ]),
                        st.Concatenation([
                            st.Note("i"),
                            st.Note("j"),
                        ]),
                    ]),
                ],
                { 1: 1, 2: 1 },
            ),
            "mod",
        ),
        st.Modulation(
            st.Concatenation([
                st.Note("k"),
                st.Note("l"),
            ]),
            "mod2",
        ),
    ])
