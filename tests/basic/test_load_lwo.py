import os
import pickle
from lwo_strut.lwoObject import lwoObject

def test_load_lwo_box0_pass():
    infile = "tests/basic/src/LWO2/box/box0.lwo"
    x = lwoObject(infile)
    x.read()
    
    outfile = infile + ".pickle"
    
    with open(outfile, 'rb') as handle:
        b = pickle.load(handle)
    
    assert x == b
    
def test_load_lwo_box0_fail():
    infile = "tests/basic/src/LWO2/box/box0.lwo"
    x = lwoObject(infile)
    x.read()
    
    outfile = infile + ".error0.pickle"
    
    with open(outfile, 'rb') as handle:
        b = pickle.load(handle)
    
    assert not x == b
