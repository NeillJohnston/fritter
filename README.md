# Fritter

Fritter is a Python library for turning code into music (as MIDI files). It comes with a music notation language that compiles to MIDI and a "standard library" that hosts some tools for composing and support for General MIDI.

```py
from fritter.std.session import *

guitar = Player.gm("gm_electric_guitar_jazz", scale="D major", channel=0)
drums  = Player.gm_drums()

guitar.play("")
```

## Fritter Notation Language

**Notes:** Notes are not intrinsic to the language, and you can easily create your own `PitchProducer` to decide how note values should get translated to MIDI pitches. But you'll 
