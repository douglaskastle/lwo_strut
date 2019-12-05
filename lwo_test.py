#!/usr/bin/env python
import os
import pickle
from lwo_strut.lwoObject import lwoObject

def main():
    #infile = "tests/basic/src/LWO2/box/box1-uv.lwo"
    infile = "tests/basic/src/LWO2/box/box0.lwo"
    x = lwoObject(infile)
    x.read()
    
    outfile = infile + ".pickle"
    
    if not os.path.isfile(outfile):
        with open(outfile, 'wb') as f:
            pickle.dump(x, f, pickle.HIGHEST_PROTOCOL)
    
    with open(outfile, 'rb') as handle:
        b = pickle.load(handle)
    
    #x.pprint()
    #b.pprint()
    print(x == b)
    

if __name__ == '__main__':
    main()
