import sys
from lwo_strut.lwoObject import lwoObject
from scripts.lwo_helper import LwoFile


def test_load_lwo_box0_pass():
    infile = "tests/basic/src/LWO2/box/box0.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.read()
    y = x.elements

    assert f.test_pickle(y)


def test_load_lwo_box0_fail():
    infile = "tests/basic/src/LWO2/box/box0.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.read()
    y = x.elements

    f.picklefile = "tests/basic/pickle/LWO2/box/box0.lwo.error0.pickle"

    if sys.version_info[1] <= 7:
        return
    assert not f.test_pickle(y, full=False)

def test_load_lwo_box3():
    infile = "tests/basic/src/LWO/box/box3-uv-layers.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.read()
    y = x.elements

    assert f.test_pickle(y)

def test_load_lwo_box6():
    infile = "tests/basic/src/LWO2/box/box6-hidden.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.read()
    y = x.elements

    assert f.test_pickle(y)

def test_load_lwo3_box0():
    infile = "tests/basic/src/LWO3/box/box0.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.read()
    y = x.elements

    assert f.test_pickle(y)

def test_load_lwo3_box1():
    infile = "tests/basic/src/LWO3/box/box1.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.read()
    y = x.elements

    assert f.test_pickle(y)

def test_load_lwo3_box2():
    infile = "tests/basic/src/LWO3/box/box2-uv.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.read()
    x.ch.search_paths = ["."]
    x.ch.recursive = True
    x.absfilepath = False
    x.resolve_clips()
    x.validate_lwo()
    y = x.elements

    assert f.test_pickle(y)

def test_load_lwo3_box3():
    infile = "tests/basic/src/LWO3/box/box3-uv-layers.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.read()
    x.ch.search_paths = ["."]
    x.ch.recursive = True
    x.absfilepath = False
    x.resolve_clips()
    x.validate_lwo()
    y = x.elements

    assert f.test_pickle(y)

def test_bulk_lwo0():
    infiles = [
        "tests/basic/src/LWO2/box/colors1.lwo",
        "tests/basic/src/LWO2/box/colors0.lwo",
        "tests/basic/src/LWO2/box/box11.lwo",
        "tests/basic/src/LWO2/box/box10.lwo",
        "tests/basic/src/LWO2/box/box9.lwo",
        "tests/basic/src/LWO2/box/box8.lwo",
        "tests/basic/src/LWO2/box/box7.lwo",
        "tests/basic/src/LWO2/box/box6.lwo",
        "tests/basic/src/LWO2/box/box6-hidden.lwo",
        "tests/basic/src/LWO2/box/box5-ngon.lwo",
        "tests/basic/src/LWO2/box/box4-uv-layers.lwo",
        "tests/basic/src/LWO2/box/box3-uv-layers.lwo",
        "tests/basic/src/LWO2/box/box2-uv.lwo",
        "tests/basic/src/LWO2/box/box1.lwo",
        "tests/basic/src/LWO2/box/box1-uv.lwo",
        "tests/basic/src/LWO2/box/box0.lwo",
    ]
    for infile in infiles:
        f = LwoFile(infile)
        f.check_file()

        x = lwoObject(infile)
        x.ch.search_paths = ["../images"]
        x.absfilepath = False
        x.read()
        x.resolve_clips()
        x.validate_lwo()
        y = x.elements

        assert f.test_pickle(y)

