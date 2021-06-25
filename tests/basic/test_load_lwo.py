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

