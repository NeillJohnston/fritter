"""Music theory-related objects."""

from dataclasses import dataclass


LETTERS = "CDEFGAB"

LETTER_PITCHES = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]


@dataclass
class Note:
    letter: str
    alter: int
    octave: int

    def __repr__(self):
        alter_dir = "b" if self.alter < 0 else "#"
        return f"{self.letter}{alter_dir * abs(self.alter)}{self.octave}"

    def shift(self, octaves: int) -> "Note":
        return Note(self.letter, self.alter, self.octave + octaves)

    def abs_pitch(self) -> int:
        # Pitch centered on C0 = 0
        return LETTER_PITCHES[self.letter] + self.alter + 12*self.octave

    def midi_pitch(self) -> int:
        # Pitch centered on C4 = 60
        return LETTER_PITCHES[self.letter] + self.alter + 12*(self.octave + 1)


@dataclass
class Degree:
    steps: int
    alter: int

    def of(self, root: Note) -> Note:
        letter = LETTERS[(LETTERS.index(root.letter) + self.steps - 1) % 7]
        octave = root.octave + (LETTERS.index(root.letter) + self.steps - 1) // 7
        alter = (root.abs_pitch() + self.semitones()) - (LETTER_PITCHES[letter] + 12*octave)

        return Note(
            letter,
            alter,
            octave,
        )

    def semitones(self) -> int:
        return (
            MAJOR_STEPS[(self.steps - 1) % 7]
            + 12*((self.steps - 1) // 7)
            + self.alter
        )


@dataclass
class Scale:
    root: Note
    degrees: list[Degree]
    octave_span: int

    def get(self, degree: int) -> Note:
        index = (degree - 1) % len(self.degrees)
        octaves = (degree - 1) // len(self.degrees)

        return self.degrees[index].of(self.root).shift(self.octave_span * octaves)
