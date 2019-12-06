#!/usr/bin/env python
import os
import re
from lwo_strut.lwoObject import lwoObject
from scripts.lwo_helper import LwoFile


def main():
    infiles = [
        "tests/basic/src/LWO2/box/box0.lwo",
        "tests/basic/src/LWO2/box/box6-hidden.lwo",
        "tests/basic/src/LWO/box/box3-uv-layers.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo",
    ]
    for infile in infiles:
        f = LwoFile(infile, create_pickle=True)
        f.check_file()
    
        x = lwoObject(infile)
        x.search_paths = ["/../images"]
        x.absfilepath = False
        x.read()
    
        #print(f.picklefile)
        os.unlink(f.picklefile)
        f.setup_pickle(x)
    
        b = f.load_pickle()
    
        print(x == b)


    infile = "tests/basic/src/LWO2/box/box0.lwo"
    f = LwoFile(infile, create_pickle=True)
    f.check_file()

    x = lwoObject(infile)
    x.read()
    
    print(f.picklefile)
    f.picklefile = re.sub(".lwo.pickle", ".lwo.error0.pickle", f.picklefile)
    print(f.picklefile)

    x.layers[0].name = "Layer 2"
    os.unlink(f.picklefile)
    f.setup_pickle(x)
    
    b = f.load_pickle()
    
    print(x == b)


if __name__ == "__main__":
    main()
