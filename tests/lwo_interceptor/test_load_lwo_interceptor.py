from lwo_strut.lwoObject import lwoObject
from scripts.lwo_helper import LwoFile


def test_load_lwo_interceptor():
    infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.search_paths = ["/../images"]
    x.absfilepath = False
    x.read()

    f.setup_pickle(x)
    b = f.load_pickle()
    
    x == b

    assert x == b
