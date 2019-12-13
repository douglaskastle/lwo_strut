#!/usr/bin/env python
from lwo_strut.lwoObject import lwoObject
from scripts.lwo_helper import LwoFile
from pprint import pprint

def main():
    infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo"
    f = LwoFile(infile, create_pickle=True)
    f.check_file()

    x = lwoObject(infile)
    x.search_paths = ["/../images"]
    x.absfilepath = False
    x.read()

    f.setup_pickle(x)

    b = f.load_pickle()
    
    #pprint(x.tags)
    print(x.tags)
    print(b.tags)

    print(x == b)
    #print(x)


if __name__ == "__main__":
    main()
