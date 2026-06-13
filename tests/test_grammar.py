from fritter.lang.grammar import expression
from fritter.lang import st


def test_binop_precedence():
    tree = expression.parse("x y !mod: a b, c d |1,2: e f, g h")
    assert tree == st.Concatenation([
        st.Concatenation([
            st.Note("x"),
            st.Note("y"),
        ]),
        st.Modulation(
            st.Branches(
                [
                    st.Parallel([
                        st.Concatenation([
                            st.Note("a"),
                            st.Note("b"),
                        ]),
                        st.Concatenation([
                            st.Note("c"),
                            st.Note("d"),
                        ]),
                    ]),
                    st.Parallel([
                        st.Concatenation([
                            st.Note("e"),
                            st.Note("f"),
                        ]),
                        st.Concatenation([
                            st.Note("g"),
                            st.Note("h"),
                        ]),
                    ]),
                ],
                { 1: 1, 2: 1 }
            ),
            "mod"
        )
    ])
