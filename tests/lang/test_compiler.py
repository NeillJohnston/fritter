from fritter.lang.grammar import parse
from fritter.lang.compiler import CompilerOptions, Event, EventStage, PitchProducer


# For testing, a pitch producer that produces notes multiplied by a number
class TestPitchProducer(PitchProducer):
    def __init__(self, k: int):
        self.k = k

    def get(self, note: str):
        return self.k * int(note)

    def modulated(self, modulator: str):
        return TestPitchProducer(self.k * int(modulator))


def events_compile(text: str):
    producer = TestPitchProducer(1)
    return EventStage(CompilerOptions(producer)).compile(parse(text))[:-1]  # Remove the EOF event


def validate_sequences(text1: str, text2: str):
    # Validate that two sequences of text are interpreted to the same events
    assert events_compile(text1) == events_compile(text2)


def test_simple_sequence():
    # Check that events come out as expected for a mix of simple cases
    events = events_compile("1+.a/h*2 _ ~ [2 3]")
    assert events == [
        # Ensure that modulation and simple operators applied
        Event(1, 0.0, 2.0, 1, "a"),
        # Ensure that the repetition + continuation on the last repetition applied
        Event(1, 2.0, 3.0, 1, "a"),
        # Ensure that the rest after the 1 and the tie on 2 and 3 applied
        Event(2, 6.0, 0.5, 0, ""),
        Event(3, 6.5, 0.5, 0, ""),
    ]


def test_nested_dynamics():
    # Check that dynamics stack properly and apply outside-in
    validate_sequences("(1.a (2.b (3.c 4.d).e).f).g", "1.ga 2.gfb 3.gfec 4.gfed")


def test_nested_octave_shifts():
    # Check that octave shifts stack properly
    validate_sequences("(1+ (2+ 3)-)+", "1++ 2+ 3")


def test_operator_ordering():
    # Check that re-ordering operators on a single atom doesn't affect their outcome
    validate_sequences("1 + .a /h *2", "1 *2 .a + /h")


def test_nested_ties():
    # Check that ties reassign spans and times properly
    validate_sequences("[1 [2 [3 4]]] 5", "1/e 2/s 3/t 4/t 5")


def test_simple_parallel():
    # Check that simple parallelization works
    events = events_compile("(1, 2 3, 4) 5")
    assert events == [
        Event(1, 0.0, 1.0, 0, ""),
        Event(2, 0.0, 1.0, 0, ""),
        # Ensures that events are properly sorted by start time
        Event(4, 0.0, 1.0, 0, ""),
        Event(3, 1.0, 1.0, 0, ""),
        # Ensure that the length of the parallel sequence is equal to the length of its longest sequence
        Event(5, 2.0, 1.0, 0, ""),
    ]


def test_nested_branches():
    # Check that branches+repeats properly nest (outer repetition should have no affect on inner)
    validate_sequences("(1 |3: (2 |3: 3)*3)*3", "1 1 2 2 3")


def test_nested_modulation():
    # Check that modulation stacks properly
    events = events_compile("!2: 1 (!3: 1) !5: 1")
    assert events == [
        Event(2, 0.0, 1.0, 0, ""),
        Event(6, 1.0, 1.0, 0, ""),
        Event(5, 2.0, 1.0, 0, ""),
    ]
