from fritter.lang.grammar import parse_fritter
from fritter.lang import st


def test_binop_precedence():
    tree = parse_fritter("mod; a b, c d |3,4: e f, g h")
    assert tree == st.Modulation(
        st.Branch(
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
            { 3: 1, 4: 1 }
        ),
        "mod",
    )
