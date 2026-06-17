import re

from parsy import seq, regex

from fritter.lang.compiler import PitchProducer
from fritter.theory import Degree, Note, Scale
from fritter.std.scales import NAMED_SCALES


NUMERALS = {
    "iii": 3,
    "ii": 2,
    "iv": 4,
    "i": 1,
    "vii": 7,
    "vi": 6,
    "v": 5,
}

num        = regex(r"\d+").map(int)
letter     = regex(r"[A-G]")
roman      = regex("|".join(NUMERALS), re.IGNORECASE).map(lambda s: NUMERALS[s.lower()])
alter      = regex(r"[b#]*").map(lambda s: s.count("#") - s.count("b"))
abs_octave = num.optional().map(lambda n: n if n is not None else 4)
rel_octave = regex(r"[\-+]*").map(lambda s: s.count("+") - s.count("-"))

abs_note   = seq(letter, alter, abs_octave).combine(Note)
maj_note   = seq(alter, roman, rel_octave)
scale_note = seq(alter, num, rel_octave)


class ScalePitchProducer(PitchProducer):
    scale: Scale

    def __init__(self, scale: Scale, bias: int = 12):
        self.scale = scale
        self.bias = bias

    @staticmethod
    def from_name(scale_name: str, bias: int = 12) -> "ScalePitchProducer":
        root, name = scale_name.split()
        root = abs_note.parse(root)

        degrees = NAMED_SCALES[name]
        octave_span = 1 + degrees[-1].semitones() // 12
        return ScalePitchProducer(Scale(root, degrees, octave_span), bias)

    def _maj_note(self, alter: int, degree: int, shift: int) -> Note:
        return Degree(degree, alter).of(self.scale.root).shifted(shift)

    def _scale_note(self, alter: int, degree: int, shift: int) -> Note:
        return self.scale.get(degree).altered(alter).shifted(shift)

    def _get_note(self, note: str) -> Note:
        return (
            abs_note
            | maj_note.combine(self._maj_note)
            | scale_note.combine(self._scale_note)
        ).parse(note)

    def get(self, note: str) -> int:
        note = self._get_note(note)
        return note.abs_pitch() + self.bias

    def modulated(self, modulator: str) -> "ScalePitchProducer":
        root, name = modulator.split()

        root = self._get_note(root)
        degrees = NAMED_SCALES[name]
        octave_span = 1 + degrees[-1].semitones() // 12
        return ScalePitchProducer(Scale(root, degrees, octave_span), self.bias)


class MappingPitchProducer(PitchProducer):
    mapping: dict[str, int]

    def __init__(self, mapping: dict[str, int]):
        self.mapping = mapping

    def get(self, note: str) -> int:
        return self.mapping[note]

    def modulated(self, _modulator: str) -> "MappingPitchProducer":
        assert False, "Not implemented"
