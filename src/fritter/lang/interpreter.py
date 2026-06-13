"""Syntax tree interpreter. Produces a list of "events" which can be translated to MIDI."""

from dataclasses import dataclass

from fritter.lang import st


_NOTE_START_OF_FILE = "<sof>"
_NOTE_CONTINUATION = "<continuation>"
_NOTE_REST = "<rest>"
_NOTE_ERASE = "<erase>"


@dataclass
class Event:
    note: str
    # Timing is done in relative units (1.0 = 1 quarter note)
    time: float
    span: float
    modulations: list[str]
    octave_shift: int
    dynamics: str


class FritterInterpreter:
    def __init__(self):
        self.time = 0.0
        self.events: list[Event] = []

        # Context stacks for the currently-produced event
        self.oct_stack = [0]
        self.dyn_stack = []
        self.rep_stack = [1]
        self.mod_stack = []
        self.qnv_stack = [1.0]

    def _emit(self, note: str):
        span = self.qnv_stack[-1]

        event = Event(note, self.time, span, None, None, None)
        # Special events (continuations, rests, and erasures) don't need these
        if note not in [_NOTE_CONTINUATION, _NOTE_REST, _NOTE_ERASE]:
            event.modulations = self.mod_stack[::]
            event.octave_shift = sum(self.oct_stack)
            event.dynamics = "".join(self.dyn_stack)
        if note == _NOTE_ERASE:
            span *= -1

        self.events.append(event)
        self.time += span

    def _pop_after_walk(self, stack: list, top, node: st.Node):
        stack.append(top)
        self.walk(node)
        stack.pop()

    def _walk_continuation(self, _node: st.Continuation):
        self._emit(_NOTE_CONTINUATION)

    def _walk_rest(self, _node: st.Rest):
        self._emit(_NOTE_REST)

    def _walk_erase(self, _node: st.Erase):
        self._emit(_NOTE_ERASE)

    def _walk_note(self, node: st.Note):
        self._emit(node.value)

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
        self._pop_after_walk(self.mod_stack, node.modulator, node.child)

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

    def interpret(self, tree: st.Node):
        self.walk(tree)

        events = self.events
        # Dummy "start-of-file" event to make iteration easier
        events.append(Event(_NOTE_START_OF_FILE, -1e9, 0.0, None, None, None))
        events.sort(key=lambda event: event.time)

        # Need to modify list in-place, hence the old-school iteration
        index = 1
        while index < len(events):
            event = events[index]
            if event.note == _NOTE_CONTINUATION:
                cont_index = index-1
                cont_time = events[cont_index].time
                while events[cont_index].time == cont_time:
                    events[cont_index].span += event.span
                    cont_index -= 1

                events.pop(index)

            elif event.note == _NOTE_REST:
                events.pop(index)

            elif event.note == _NOTE_ERASE:
                assert False, "TODO"

            else:
                index += 1

        return list(filter(lambda event: event.span > 0, events))


def interpret(tree: st.Node) -> list[Event]:
    return FritterInterpreter().interpret(tree)
