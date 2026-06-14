from fritter.theory import Degree


# (d)iminished, (m)inor, (M)ajor, (S)harp
U1  = Degree( 1,  0)
m2  = Degree( 2, -1)
M2  = Degree( 2,  0)
m3  = Degree( 3, -1)
M3  = Degree( 3,  0)
P4  = Degree( 4,  0)
S4  = Degree( 4,  1)
d5  = Degree( 5, -1)
P5  = Degree( 5,  0)
S5  = Degree( 5,  1)
m6  = Degree( 6, -1)
M6  = Degree( 6,  0)
d7  = Degree( 7, -2)
m7  = Degree( 7, -1)
M7  = Degree( 7,  0)
m9  = Degree( 9, -1)
M9  = Degree( 9,  0)
M11 = Degree(11,  0)
S11 = Degree(11,  1)
m13 = Degree(13, -1)
M13 = Degree(13,  0)

UEXT = "upper_extension"


CHORD_TREE = {
    M2: {
        P5: {  # Suspended 2nd
            None: ("sus2", "sus2"),
            m6: {
                None: ("b6sus2", "b6sus2"),
                UEXT: ("b6sus2_{}", "b6sus2_{}"),
            },
            M6: {
                None: ("maj6sus2", "6sus2"),
                UEXT: ("maj6sus2_{}", "6sus2_{}"),
            },
            m7: {
                None: ("7sus2", "7sus2"),
                UEXT: ("{}sus2", "{}sus2"),
            },
            M7: {
                None: ("maj7sus2", "M7sus2"),
                UEXT: ("maj{}sus2", "M{}sus2"),
            },
        },
    },

    m3: {
        d5: {  # Diminished
            None: ("dim", "o"),
            d7: {
                None: ("dim7", "o7"),
                UEXT: ("dim{}", "o{}"),
            },
            m7: {
                None: ("min7b5", "m7b5"),
                UEXT: ("min{}b5", "m{}b5"),
            },
        },

        P5: {  # Minor
            None: ("min", "m"),
            m6: {
                None: ("minb6", "mb6"),
                UEXT: ("minb6_{}", "mb6_{}"),
            },
            M6: {
                None: ("min6", "m6"),
                UEXT: ("min6_{}", "m6_{}"),
            },
            m7: {
                None: ("min7", "m7"),
                UEXT: ("min{}", "m{}"),
            },
            M7: {
                None: ("minmaj7", "mM7"),
                UEXT: ("minmaj{}", "mM{}"),
            },
        },
    },

    M3: {
        P5: {  # Major
            None: ("maj", "M"),
            m6: {
                None: ("majb6", "b6"),
                # UEXT: ("majb6_{}", "b6_{}"),
            },
            M6: {
                None: ("maj6", "6"),
                UEXT: ("maj6_{}", "6_{}"),
            },
            m7: {  # Dominant
                None: ("majb7", "7"),
                UEXT: ("maj{}b7", "{}"),
            },
            M7: {
                None: ("maj7", "M7"),
                UEXT: ("maj{}", "M{}"),
            },
        },

        S5: {  # Augmented
            None: ("aug", "+"),
            M6: {
                None: ("aug6", "+6"),
                UEXT: ("aug6_{}", "+6_{}"),
            },
            m7: {  # Augmented dominant
                None: ("aug7", "+7"),
                UEXT: ("aug{}", "+{}"),
            },
            M7: {
                None: ("augmaj7", "+M7"),
                UEXT: ("augmaj{}", "+M{}"),
            },
        },
    },

    P4: {
        P5: {  # Suspended 4th
            None: ("sus4", "sus"),
            m6: {
                None: ("b6sus4", "b6sus"),
                UEXT: ("b6sus4_{}", "b6sus_{}"),
            },
            M6: {
                None: ("maj6sus4", "6sus"),
                UEXT: ("maj6sus4_{}", "6sus_{}"),
            },
            m7: {
                None: ("7sus4", "7sus"),
                UEXT: ("{}sus4", "{}sus"),
            },
            M7: {
                None: ("maj7sus4", "M7sus"),
                UEXT: ("maj{}sus4", "M{}sus"),
            },
        }
    },
}

ADDITIONS = {
    "addb2": m2,
    "add2": M2,
    "add4": P4,
    "add#4": S4,
    "addb6": m6,
    "add6": M6,
    "addb9": m9,
    "add9": M9,
    "add11": M11,
    "add#11": S11,
    "addb13": m13,
    "add13": M13,
}


def _alterations(long: str, short: str, degrees: list[Degree]):
    for name, add in ADDITIONS.items():
        if add not in degrees:
            yield (f"{long}{name}", degrees + [add])
            yield (f"{short}{name}", degrees + [add])


def _build_chords(tree: dict, degrees: list[Degree] = [U1]):
    for degree, node in tree.items():
        if degree is None:
            long, short = node
            yield (long, degrees)
            yield (short, degrees)

            yield from _alterations(long, short, degrees)

        elif degree == UEXT:
            long, short = node
            for name, uext in [("9", [M9]), ("11", [M9, M11]), ("13", [M9, M11, M13])]:
                yield (long.format(name), degrees + uext)
                yield (short.format(name), degrees + uext)

                yield from _alterations(long.format(name), short.format(name), degrees + uext)

        else:
            yield from _build_chords(node, degrees + [degree])


SCALE_DATA = {
    "chromatic": [U1, m2, M2, m3, M3, P4, S4, P5, m6, M6, m7, M7],
    # Diatonic modes
    "lydian":     [U1, M2, M3, S4, P5, M6, M7], # major #4
    "ionian":     [U1, M2, M3, P4, P5, M6, M7],
    "mixolydian": [U1, M2, M3, P4, P5, M6, m7], # major b7
    "dorian":     [U1, M2, m3, P4, P5, M6, m7], # minor #6
    "aeolian":    [U1, M2, m3, P4, P5, m6, m7],
    "phrygian":   [U1, m2, m3, P4, P5, m6, m7], # minor b2
    "locrian":    [U1, m2, m3, P4, d5, m6, m7], # minor b2, b5
    # Pentatonic scales
    "pentatonic":       [U1, M2, M3, P5, M6],
    "minor_pentatonic": [U1, m3, P4, P5, m7],
}


SCALE_NICKNAMES = {
    "ionian": ["major"],
    "aeolian": ["minor"],
}


NAMED_SCALES = {}

for (name, degrees) in _build_chords(CHORD_TREE):
    NAMED_SCALES[name] = degrees
for (name, degrees) in SCALE_DATA.items():
    NAMED_SCALES[name] = degrees
for (name, nicknames) in SCALE_NICKNAMES.items():
    for nickname in nicknames:
        NAMED_SCALES[nickname] = NAMED_SCALES[name]
