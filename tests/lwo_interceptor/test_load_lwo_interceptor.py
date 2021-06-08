from lwo_strut.lwoObject import lwoObject
from scripts.lwo_helper import LwoFile


def test_load_lwo_interceptor():
    infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.ch.search_paths = ["../images"]
    x.absfilepath = False
    x.read()
    x.resolve_clips()
    x.validate_lwo()
    
    y = x.elements    

    f.setup_pickle(y)
    b = f.load_pickle()

    assert y == b
