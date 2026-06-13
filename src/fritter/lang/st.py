"""Fritter lang syntax tree."""

from dataclasses import dataclass


class Node:
    pass


@dataclass
class Empty(Node): pass


@dataclass
class Continuation(Node): pass


@dataclass
class Rest(Node): pass


@dataclass
class Erase(Node): pass


@dataclass
class Note(Node):
    value: str


@dataclass
class OctaveShift(Node):
    child: Node
    shift: int


@dataclass
class Dynamics(Node):
    child: Node
    dynamics: str


@dataclass
class Span(Node):
    child: Node
    units: int


@dataclass
class Repeat(Node):
    child: Node
    times: int


@dataclass
class Tie(Node):
    child: Node


@dataclass
class Concatenation(Node):
    children: list[Node]


@dataclass
class Parallel(Node):
    children: list[Node]


@dataclass
class Branches(Node):
    children: list[Node]
    selectors: dict[int, int]  # Map from repetition number to child index


@dataclass
class Modulation(Node):
    child: Node
    modulator: str
