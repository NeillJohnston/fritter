# Fritter

Fritter is a Python library for turning code into music (as MIDI files). It comes with a music notation language that compiles to MIDI and a "standard library" that hosts some tools for composing and support for General MIDI.

```py
from fritter.std.session import *


set_bpm(140)

guitar = Player.gm("gm_electric_guitar_jazz", "C major")
drums  = Player.gm_drums()

guitar << "((1 2 b3 4)/e 2 [b7- 1] _/w).s"
drums  << "(rc ~ ~ rc).sp/e*2"

write_midi("out.mid")

```

## Fritter Notation Language

### Basics

**Notes:** Let's start with an example - a very simple arpeggio on the notes of a C major triad. You can write absolute notes to handle this:

```
C E G
```

These can include an octave - by default this is 4, so this does the same thing:

```
C4 E4 G4
```

Writing absolute notes all the time is clunky. You can write relative to a scale, so if you set the scale to C major then this also does the same thing:

```
1 3 5
```

One more way is by using roman numerals, which always refer to the root note's relative _major_ scale. This gives you easy access to the major scale regardless of what scale you're in at the moment. Note that these are case-insensitive:

```
i iii v
```

Two "special" notes are the **rest** and **continuation**. Rests simply don't play anything, while continuations extend the last-played note(s):

```
1 ~ 2 ~
1 _ 2 _
```

These two sequences have the same length - the first sequence will play a 1, rest, then play a 2, and rest again. The second sequence will play a 1 followed by a 2, but both will last longer.

**Octave shifting:** The octave a note is played in can also be adjusted with the `+` and `-` operators.

```
1+
8
15-
```

These all play the same thing (assuming we're still using a typical major scale). 1 an octave up is equivalent to the "8th" note of the scale, which is equivalent to the 15th note an octave down.

**Modulating:** Having different ways to refer to notes isn't very useful until you start changing scales on the fly, which you can do with a modulation:

```
!C major: 1 3 5
```

As before, the root note of your modulation can be a scale degree or roman numeral:

```
!2 minor: 1 3 5
!V mixolydian: 1 3 5
```

These play different arpeggios of chords by modulating then using the same `1 3 5` pattern. Scales get the exact same treatment - you can "modulate" to a chord and play just its notes like so:

```
!2 m7: 1 2 3 4
!V 7:  1 2 3 4
```

Modulating from C, these are Dm7 and G7 respectively.

You can nest modulations, here's a weird way of playing a 2-5-1:

```
(!V major: (!V minor: ...) ...) ...
```

You can also use an octave shift in the root note of a modulation:

```
!6- minor: ...
```

**Span:** So far every note played has been a quarter-note, the default span for a note to last. With the span operator `/` you can control how long notes play:

```
1/t 2/s 3/e 4/q 5/h 6/w
```

These will play a thirty-second, sixteenth, eighth, quarter, half, and whole note in order.

You can stack note spans as much as you like:

```
1/qe
```

This will play a note for a quarter + an eighth note (equivalent to 3 eighth notes, a dotted quarter note).

**Ties:** Another way to control note duration is with a _tie_, indicated with square brackets. These will force the expression inside to take up a single quarter note:

```
[1 2]
1/e 2/e
(1 2)/e
```

These expressions are all equivalent - play a 1 and a 2 for an eighth note each. The third expression uses parentheses to group the two notes into a sequence, and then applies the span operator to everything.

Ties are the only way you can make certain rhythms that don't evenly divide by 2, like triplets:

```
[1 2 3]/h
```

This uses a two and span operator to play a triplet over the span of a half-note.

**Dynamics:** To make your compositions sound more lifelike, you can control _how_ notes are played with dynamics. There are 3 aspects that you can adjust with dynamics:
- Velocity (`.p` for quieter, `.f` for louder)
- Staccato (`.t`)
- Swing (`.s` to adjust swing amount, `.w` to adjust swing width)

Dynamics stack, so `1.pp` will play a note very softly and `1.fff` will play the same note very, very loudly.

TODO explain swing

**Repetition:** You can repeat a note or a sequence with the repeat operator `*`:

```
1*4
(1 2 3 4)*2
```

These will play the sequences `1 1 1 1` and `1 2 3 4 1 2 3 4`, respectively.

**Branching:** Within a repetition, you can play a different sequence on a certain repetition using branches:

```
(
        1
    |2: 2
    |4: 3
)*4
```

This will play the sequence `1 2 1 3`. On the first and third repetitions, the default branch is played. However, the second and fourth repetitions are specified to play different branches.

The repetition "index" is only taken from the _closest_ repetition operator. This allows you to stack repetitions more easily:

```
(~ |3: 1)*4*10
(~ |3: 1)*40
```

The first one will play `~ ~ 1 ~` 10 times, and the second one will play `~ ~ 1 ~` followed by 36 more rests, because only the 3rd repetition out of 40 is assigned to play the 1.

**Parallel:** Finally, notes can be played in parallel by separating sequences with commas:

```
(1, 3, 5)
```

This will play a simple triad chord.

```
1-/w, 3 4 5 4
```

This will play a bass note for a whole note and a simple melody on top.
