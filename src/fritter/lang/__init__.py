import mido

from fritter.lang.grammar import parse
from fritter.lang.compiler import CompilerOptions, compile as _compile


def compile(text: str, options: CompilerOptions) -> list[mido.Message]:
    """Compile Fritter text to a list of MIDI messages.

    Note that the MIDI channel needs to be set for each message after the fact.
    """

    return _compile(parse(text), options)
