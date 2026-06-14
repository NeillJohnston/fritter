from fritter.session.note_producers import ScaleProducer


def test_scale_producer_get():
    c0_minor = ScaleProducer.from_name("C0 minor")

    assert c0_minor.get("1").abs_pitch() == 0
    assert c0_minor.get("3").abs_pitch() == 3
    assert c0_minor.get("5").abs_pitch() == 7
    assert c0_minor.get("9").abs_pitch() == 14

    assert c0_minor.get("I").abs_pitch()    == 0
    assert c0_minor.get("biii").abs_pitch() == 3
    assert c0_minor.get("V").abs_pitch()    == 7
    assert c0_minor.get("ii+").abs_pitch()  == 14

    assert c0_minor.get("D1").abs_pitch() == 14


def test_scale_producer_modulate():
    c0_minor = ScaleProducer.from_name("C0 minor")

    eb0_major = c0_minor.modulate("3 major")
    assert eb0_major.get("1").abs_pitch() == 3
    assert eb0_major.get("3").abs_pitch() == 7
    assert eb0_major.get("5").abs_pitch() == 10

    e0_major = c0_minor.modulate("iii major")
    assert e0_major.get("1").abs_pitch() == 4
    assert e0_major.get("3").abs_pitch() == 8
    assert e0_major.get("5").abs_pitch() == 11

    e1_major = c0_minor.modulate("E1 major")
    assert e1_major.get("1").abs_pitch() == 16
    assert e1_major.get("3").abs_pitch() == 20
    assert e1_major.get("5").abs_pitch() == 23
