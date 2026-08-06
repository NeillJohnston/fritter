"""This Will Destroy You - They Move on Tracks of Never-Ending Light"""


from fritter.std import *


P = Player.gm("gm_acoustic_grand_piano", f"Db2 major")

set_bpm(60)

P << """
(
    (!ii+:  1/w, [5 b3] _/hq)
    (!vi:   1/w, [b3+ 5] _/hq)
    (!bVII: 1/w, [2+ 5] _/hq)
    (!ii+:  1/h, [b3+ 5] _/q)
    (
        (!I+: 1/h, [3+ 5] _/q)
    |2: (!I+:  1, [3+ 5])
        (!IV+: 1, [3+ 5])
    )
)*2
"""

P << """
(!bVII: 1/w, [3+ 5] _/hq)
(!vi:   1/h, [b3+ 5] _/q)
(!I+:   1/h, [3+ 5] _/q)
"""

P << """
(
    (!ii+: 1.f/w, [b3+ 5.p]/e*8)
    (!v:   1.f/w, [b3+ 5.p]+/e*8)
    (!I+:  1.f/w, [3+ 5.p]/e*8)*2

    (!bVII: 1.f/w, [3+ 5.p]/e*8)
    (!ii+:  1.f/w, [b3+ 5.p]/e*8)
    (
        (!I+: 1.f/w, [3+ 5.p]/e*8)*2
    |2: (!I+: 1.f/w, [3+ 5.p]/e*8)
        (!vi: 1.f/h, [b3+ 5.p]/e*8)
    )
)*2
"""

P << """
(
    (!bVII: 1.f/hq, [3+ 5.p]/e*6)
    (!v:    1.f/q,  [b3+ 5.p].f+/e*2)
    (!IV+:  1.f/h,  [3+ 5.p]/e*4)
    (!ii+:  1.f/q,  [b3+ 5.p].f/e*2)
    (!I+:   1.f/w,  [3+ 5.p]/e*8)
)*2
"""

P << """
(
    (1.f/w, [3+ 5.p]/e*8)

    (1-.f/w, [3+ 5.p]/e*8)
    (1-.f/w, [3+ 5.p].p/e*8)
    (1-.f/w, [3+ 5.p].pp/e*8)
    (1-.f/w, [3+ 5.p].ppp/e*8)*3
    (1-.f/w, [3+ 5.p].p/e*8)
    (1-.f/w, [3+ 5.p]/e*8)
)+
"""

P << """
(
    (1-/w.ff, [(3+ |6,7: 4+) 5.p]/e*8)
    (1-/w.f,  [5+ 1]/e*8)
    (4-/w.ff, [(3+ |6,7: 4+) 5.p]/e*8)
    (1-/w.f,  [(3+ |1: 4+) 5.p]/e*8)
)+*4
"""

P << """
(
    ([6, 10] [5, 9] [4, 8]/hq, ~/e 1+ 1+ 1+/he)
    ([8, 12]/q [4, 8]/hq, ~/qe 1+/he)
    ([8, 12]/q [5, 9]/w, ~/qe 1+/hqe)
)*6
"""

write_midi("they_move_on_tracks_of_never_ending_light.mid")
