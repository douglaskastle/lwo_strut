from lwo_strut.lwoObject import lwoObject
from scripts.lwo_helper import LwoFile

def test_load_lwo_box0_pass():
    infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo"
    f = LwoFile(infile)
    f.check_file()

    x = lwoObject(infile)
    x.search_paths = ["/../images"]
    x.read()
    
    f.setup_pickle(x)
    b = f.load_pickle()
    
    assert x == b
# from lwo_helper import load_lwo
# 
# def test_load_lwo0():
#     infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo"
#     load_lwo(infile)
