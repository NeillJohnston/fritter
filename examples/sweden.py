"""C418 - Sweden

Sheet music here: https://musescore.com/torbybrand/sweden-minecraft
"""

from fritter.std.session import *


set_bpm(44)

piano = Player.gm("gm_acoustic_grand_piano", "D3 major")

bass = "(2 3 4 6 5 4 1/h)-"
c1   = "(2, 4, 6)"
c2   = "(5, 8, 10)"
c3   = "(3, 5, 7)"
c4   = "(5, 7, 9)"

# Intro
piano << f"""
    ((2, 4) (5, 8) (3, 5) (5, 7).f).pp/h
    ({c1} {c2} {c3} {c4}.f).p/h
    ({c1} {c2} {c3} {c4}.f)/h
    ,
    {bass}.pp
    {bass}.p
    {bass}
"""

piano << f"""
    ~ [12 13]      ~/qe  [8 9]/e        ~/qe  [10 12]/e     ~/h
    [~ 15 13 12]/h ~/qe  [8 9]/e        ~/qe  [12 10]/e     ~/h
    ~ [12 13]      15/qe [8 9, 17 16]/e 14/qe [16 15, 10]/e 12/h
    ~ [13 12]      ~/qe  [8 9]/e        ~/qe  [10 12]/e     ~/h
    ~ [12 13]      ~/qe  [8 9]/e        ~/qe  [10 12]/e     ~/h
    ~ [12 13]      15/qe [15 16]/e      14    [17 [10 12]]  ~/h
    ,
    ({c1} ~ {c2}/qe ~/e {c3}/qe ~/e {c4}/h)*6
    ,
    {bass}*6
"""

# End
piano << f"""
    (
        (5, 8, 10)/qe.p [13 12]/e (6, #11) [9 8] (2, 7)/qe [8 9]/e (1, 6)/h
        (8, 10, 15)/qe [13 12]/e (6, #11) [9 8, ~ 16] (7, 14) [15 [8 9, 16]] (6, 13)/h
        ,
        (6.p 2+ 5 4)-/h*2
    ).p
    _/w
"""

write_midi("./sweden.mid")
