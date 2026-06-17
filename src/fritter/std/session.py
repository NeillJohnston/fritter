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

    @staticmethod
    def gm(gm_instrument_name: str, scale_name: str, midi_channel: int = None) -> "Player":
        global GLOBAL_TRACKS

        if midi_channel is None:
            midi_channel = len(GLOBAL_TRACKS)

        return Player(
            midi_channel,
            gm.PROGRAM_MAP[gm_instrument_name],
            ScalePitchProducer.from_name(scale_name),
        )

    @staticmethod
    def gm_drums(midi_channel: int = None) -> "Player":
        if midi_channel is None:
            midi_channel = gm.PERCUSSION_CHANNEL

        return Player(
            midi_channel,
            0,
            MappingPitchProducer(gm.PERCUSSION_MAP),
        )

    def __post_init__(self):
        global GLOBAL_TRACKS

        track = mido.MidiTrack()
        track.append(
            mido.Message("program_change", channel=self.midi_channel, program=self.midi_patch, time=0)
        )
        GLOBAL_TRACKS[self.midi_channel] = track

    def play(self, text: str):
        global GLOBAL_TRACKS

        options = CompilerOptions(
            pitch_producer=self.pitch_producer,
            ppqn=global_ppqn(),
        )
        messages = compile(text, options)
        for message in messages:
            message.channel = self.midi_channel
        GLOBAL_TRACKS[self.midi_channel] += messages

    def __lshift__(self, text: str):
        self.play(text)


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
