from fritter.std.pitch_producers import ScalePitchProducer


def test_scale_producer_get():
    c0_minor = ScalePitchProducer.from_name("C0 minor", bias=0)

    assert c0_minor.get("1") == 0
    assert c0_minor.get("3") == 3
    assert c0_minor.get("5") == 7
    assert c0_minor.get("9") == 14

    assert c0_minor.get("I")    == 0
    assert c0_minor.get("biii") == 3
    assert c0_minor.get("V")    == 7
    assert c0_minor.get("ii+")  == 14

    assert c0_minor.get("D1") == 14


def test_scale_producer_modulate():
    c0_minor = ScalePitchProducer.from_name("C0 minor", bias=0)

    eb0_major = c0_minor.modulated("3 major")
    assert eb0_major.get("1") == 3
    assert eb0_major.get("3") == 7
    assert eb0_major.get("5") == 10

    e0_major = c0_minor.modulated("iii major")
    assert e0_major.get("1") == 4
    assert e0_major.get("3") == 8
    assert e0_major.get("5") == 11

    e1_major = c0_minor.modulated("E1 major")
    assert e1_major.get("1") == 16
    assert e1_major.get("3") == 20
    assert e1_major.get("5") == 23
