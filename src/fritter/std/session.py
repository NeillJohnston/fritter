import subprocess
from dataclasses import dataclass
from tempfile import NamedTemporaryFile

import mido

from fritter.lang.compiler import PitchProducer
from fritter.lang import CompilerOptions, compile
from fritter.std.pitch_producers import ScalePitchProducer, MappingPitchProducer
from fritter.std import gm


GLOBAL_TRACKS = {}
GLOBAL_RES = 480
GLOBAL_BPM = 120


def global_ppqn():
    # TODO this is definitely wrong
    return GLOBAL_RES / GLOBAL_BPM * 120


@dataclass
class Player:
    midi_channel: int
    midi_patch: int
    pitch_producer: PitchProducer
    macros: dict[str, str] = None

    def __post_init__(self):
        self.macros = self.macros or {}

    @staticmethod
    def gm(gm_instrument_name: str, scale_name: str, midi_channel: int = None) -> "Player":
        global GLOBAL_TRACKS

        if midi_channel is None:
            midi_channel = len(GLOBAL_TRACKS)

        return Player(
            midi_channel,
            gm.PROGRAM_MAP[gm_instrument_name],
            ScalePitchProducer.from_name(scale_name),
            {},
        )

    @staticmethod
    def gm_drums(midi_channel: int = None) -> "Player":
        if midi_channel is None:
            midi_channel = gm.PERCUSSION_CHANNEL

        return Player(
            midi_channel,
            0,
            MappingPitchProducer(gm.PERCUSSION_MAP),
            {},
        )

    def __post_init__(self):
        global GLOBAL_TRACKS

        track = mido.MidiTrack()
        track.append(
            mido.Message("program_change", channel=self.midi_channel, program=self.midi_patch, time=0)
        )
        GLOBAL_TRACKS[self.midi_channel] = track

    def play(self, text: str) -> "Player":
        global GLOBAL_TRACKS

        for search, replace in self.macros.items():
            text = text.replace(search, replace)

        options = CompilerOptions(
            pitch_producer=self.pitch_producer,
            ppqn=global_ppqn(),
        )
        messages = compile(text, options)
        for message in messages:
            message.channel = self.midi_channel
        GLOBAL_TRACKS[self.midi_channel] += messages

        return self

    def with_macros(self, macros: dict[str, str]) -> "Player":
        return Player(
            self.midi_channel,
            self.midi_patch,
            self.pitch_producer,
            self.macros | macros
        )

    def __and__(self, macros: dict[str, str]):
        return self.with_macros(macros)

    def __lshift__(self, text: str):
        return self.play(text)

    def __lt__(self, text: str):
        """Convenience that lets you "comment out" sections by just deleting a <."""
        return self


def set_bpm(bpm: int):
    global GLOBAL_BPM
    GLOBAL_BPM = bpm


def write_midi(filename: str = None, file = None):
    midi = mido.MidiFile(
        ticks_per_beat=GLOBAL_RES,
        tracks=list(GLOBAL_TRACKS.values())
    )
    midi.save(filename=filename, file=file)


def play_midi(sf2: str):
    with NamedTemporaryFile() as tmp:
        write_midi(tmp.name)
        tmp.seek(0)
        subprocess.run(["fluidsynth", "-iq", sf2, tmp.name])


def render_midi(sf2: str, filename: str):
    with NamedTemporaryFile() as tmp:
        write_midi(tmp.name)
        tmp.seek(0)
        subprocess.run(["fluidsynth", "-iq", sf2, tmp.name, "-g", "1", "-F", filename])
