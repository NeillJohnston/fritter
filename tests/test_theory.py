from fritter.theory import Note, Degree


def test_note_repr():
    assert str(Note("C", 0, 4)) == "C4"
    assert str(Note("A", -1, 0)) == "Ab0"
    assert str(Note("A", 1, 0)) == "A#0"


def test_degree_of():
    # Check that the degree algorithm works
    m7 = Degree(7, -1)
    M7 = Degree(7,  0)
    M9 = Degree(9,  0)

    C4 = Note("C", 0, 4)
    assert m7.of(C4) == Note("B", -1, 4)
    assert M7.of(C4) == Note("B",  0, 4)
    assert M9.of(C4) == Note("D",  0, 5)

    F4 = Note("F", 0, 4)
    assert m7.of(F4) == Note("E", -1, 5)
    assert M7.of(F4) == Note("E",  0, 5)
    assert M9.of(F4) == Note("G",  0, 5)
