"""Compile a parsed syntax tree to MIDI events"""

from dataclasses import dataclass
from math import log

import mido

from fritter.lang import st


_START_OF_FILE = -1000
_CONTINUATION  = -1001
_REST          = -1002
_ERASE         = -1003
_END_OF_FILE   = -2000


class PitchProducer:
    def get(self, note: str) -> int:
        """Get the pitch of a note."""

    def modulated(self, modulator: str) -> "PitchProducer":
        """Modulate based on a string parameter."""


@dataclass
class CompilerOptions:
    pitch_producer: PitchProducer
    ppqn: int = 120
    default_velocity: int = 64
    gain_levels: list[int] = None
    swing_levels: list[float] = None
    staccato_levels: list[float] = None

    def __post_init__(self):
        self.gain_levels = self.gain_levels or [8, 16, 32]
        self.swing_levels = self.swing_levels or [3/5, 2/3, 3/4]
        self.staccato_levels = self.staccato_levels or [1/4, 1/8, 1/16]


@dataclass
class Event:
    pitch: int
    # Timing is done in relative units (1.0 = 1 quarter note)
    time: float
    span: float
    octave_shift: int
    dynamics: str

    @staticmethod
    def start_of_file() -> "Event":
        return Event(_START_OF_FILE, 0.0, 0.0, None, None)

    @staticmethod
    def end_of_file(time: float) -> "Event":
        return Event(_END_OF_FILE, time, 0.0, None, None)

    @staticmethod
    def is_normal(event: "Event") -> bool:
        # Negative numbers are used for meta-events
        return event.pitch >= 0

    def end_time(self) -> float:
        return self.time + self.span


class EventStage:
    """Compilation stage that turns a syntax tree into a flat list of "events", somewhat-abstract
    notes played."""

    def __init__(self, options: CompilerOptions):
        self.options = options

        self.time = 0.0
        self.events: list[Event] = []

        # Context stacks for the currently-produced event
        self.oct_stack = [0]
        self.dyn_stack = []
        self.rep_stack = [1]
        self.mod_stack = [options.pitch_producer]
        self.qnv_stack = [1.0]

    def _emit(self, pitch: int):
        span = self.qnv_stack[-1]

        event = Event(pitch, self.time, span, None, None)
        # Special events (continuations, rests, and erasures) don't need these
        if pitch not in [_CONTINUATION, _REST, _ERASE]:
            event.octave_shift = sum(self.oct_stack)
            event.dynamics = "".join(self.dyn_stack)
        if pitch == _ERASE:
            span *= -1

        self.events.append(event)
        self.time += span

    def _pop_after_walk(self, stack: list, top, node: st.Node):
        stack.append(top)
        self.walk(node)
        stack.pop()

    def _walk_continuation(self, _node: st.Continuation):
        self._emit(_CONTINUATION)

    def _walk_rest(self, _node: st.Rest):
        self._emit(_REST)

    def _walk_erase(self, _node: st.Erase):
        self._emit(_ERASE)

    def _walk_note(self, node: st.Note):
        producer = self.mod_stack[-1]
        self._emit(producer.get(node.value))

    def _walk_octave_shift(self, node: st.OctaveShift):
        self._pop_after_walk(self.oct_stack, node.shift, node.child)

    def _walk_dynamics(self, node: st.Dynamics):
        self._pop_after_walk(self.dyn_stack, node.dynamics, node.child)

    def _walk_span(self, node: st.Span):
        self._pop_after_walk(self.qnv_stack, self.qnv_stack[-1] * node.units, node.child)

    def _walk_repeat(self, node: st.Repeat):
        self.rep_stack.append(1)
        for _ in range(node.times):
            self.walk(node.child)
            self.rep_stack[-1] += 1
        self.rep_stack.pop()

    def _walk_tie(self, node: st.Tie):
        start_index = len(self.events)
        start_time = self.time
        self.walk(node.child)

        end_time = self.time
        span = self.qnv_stack[-1]
        factor = (end_time - start_time) / span

        for event in self.events[start_index:]:
            event.time = start_time + (event.time - start_time)/factor
            event.span /= factor

        self.time = start_time + span

    def _walk_concatenation(self, node: st.Concatenation):
        for child in node.children:
            self.walk(child)

    def _walk_parallel(self, node: st.Parallel):
        start_time = self.time
        end_time = self.time
        for child in node.children:
            self.time = start_time
            self.walk(child)
            end_time = max(end_time, self.time)

        self.time = end_time

    def _walk_branch(self, node: st.Branches):
        current_rep = self.rep_stack[-1]
        child_index = node.selectors.get(current_rep, 0)
        self.walk(node.children[child_index])

    def _walk_modulation(self, node: st.Modulation):
        producer = self.mod_stack[-1].modulated(node.modulator)
        self._pop_after_walk(self.mod_stack, producer, node.child)

    def walk(self, node: st.Node):
        walk_func = {
            st.Continuation: self._walk_continuation,
            st.Rest: self._walk_rest,
            st.Erase: self._walk_erase,
            st.Note: self._walk_note,
            st.OctaveShift: self._walk_octave_shift,
            st.Dynamics: self._walk_dynamics,
            st.Span: self._walk_span,
            st.Repeat: self._walk_repeat,
            st.Tie: self._walk_tie,
            st.Concatenation: self._walk_concatenation,
            st.Parallel: self._walk_parallel,
            st.Branches: self._walk_branch,
            st.Modulation: self._walk_modulation,
        }[type(node)]

        walk_func(node)

    def compile(self, tree: st.Node):
        self.walk(tree)

        events = self.events
        # Dummy "start-of-file" event to make iteration easier
        events.append(Event.start_of_file())
        events.sort(key=lambda event: event.time)

        # Need to modify list in-place, hence the old-school iteration
        index = 1
        while index < len(events):
            event = events[index]
            if event.pitch == _CONTINUATION:
                cont_index = index-1
                cont_time = events[cont_index].time
                while events[cont_index].time == cont_time:
                    events[cont_index].span += event.span
                    cont_index -= 1

                events.pop(index)

            elif event.pitch == _REST:
                events.pop(index)

            elif event.pitch == _ERASE:
                assert False, "TODO"

            else:
                index += 1

        return list(filter(Event.is_normal, events)) + [Event.end_of_file(self.time)]


class MidiStage:
    """Compilation stage that turns events into MIDI messages."""

    def __init__(self, options: CompilerOptions):
        self.options = options

    def _ticks(self, span: float) -> int:
        return round(self.options.ppqn * span)

    def _compile_event(self, event: Event) -> list[mido.Message]:
        gain_level = 0
        stacatto_level = 0
        swing_level = 0
        swing_width = 1.0

        for d in event.dynamics:
            match d:
                case "p": gain_level -= 1
                case "f": gain_level += 1
                case "t": stacatto_level += 1
                case "s": swing_level += 1
                case "w": swing_width += 1
                # Reset
                case "0":
                    gain_level = 0
                    stacatto_level = 0
                    swing_level = 0
                    swing_width = 1.0
                case d:
                    assert False, f"Unknown dynamics flag {d}"

        velocity = self.options.default_velocity
        if gain_level < 0:
            velocity -= self.options.gain_levels[-gain_level - 1]
        elif gain_level > 0:
            velocity += self.options.gain_levels[gain_level - 1]

        swing_p = 1.0
        if swing_level > 0:
            swing_p = log(self.options.swing_levels[swing_level - 1]) / log(1/2)
        time_curve = lambda t: (
            (t - t % swing_width)
            + (((t % swing_width) / swing_width)**swing_p) * swing_width
        )

        stacatto_adj = 1.0
        if stacatto_level > 0:
            stacatto_adj = self.options.staccato_levels[stacatto_level - 1]

        start_ticks = self._ticks(time_curve(event.time))
        end_ticks = self._ticks(time_curve(event.end_time() * stacatto_adj))

        return [
            mido.Message(type="note_on", note=event.pitch + 12*event.octave_shift, velocity=velocity, time=start_ticks),
            mido.Message(type="note_off", note=event.pitch + 12*event.octave_shift, time=end_ticks),
        ]

    def compile(self, events: list[Event]) -> list[mido.Message]:
        end_of_file = events.pop()
        end_of_file_ticks = self._ticks(end_of_file.time)

        messages = sum((self._compile_event(event) for event in events), start=[])
        messages.append(mido.Message(type="note_off", note=0, velocity=0, time=end_of_file_ticks))
        messages.sort(key=lambda message: message.time)

        last_ticks = 0
        # Convert times in messages to delta times
        for message in messages:
            message.time, last_ticks = message.time - last_ticks, message.time

        return messages


def compile(tree: st.Node, options: CompilerOptions) -> list[mido.Message]:
    event_stage = EventStage(options)
    midi_stage = MidiStage(options)

    res = event_stage.compile(tree)
    res = midi_stage.compile(res)
    return res
