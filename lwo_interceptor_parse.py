#!/usr/bin/env python
import logging
from lwo_strut.lwoObject import lwoObject
from scripts.lwo_helper import LwoFile
from pprint import pprint

def main():
    infiles = [
        "tests/basic/src/LWO2/box/box0.lwo",
        "tests/basic/src/LWO2/box/box6-hidden.lwo",
        "tests/basic/src/LWO/box/box3-uv-layers.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo",
    ]
    infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo"
    infile = infiles[2]
    f = LwoFile(infile, create_pickle=True)
    f.check_file()

    x = lwoObject(infile, logging.DEBUG)
    x.ch.search_paths = ["../images"]
    x.absfilepath = False
    x.read()
    x.resolve_clips()
    x.validate_lwo()
    
    y = x.elements
    
    f.setup_pickle(y)

    b = f.load_pickle()
    
    print(y == b)
    
    #print(x)


if __name__ == "__main__":
    main()
