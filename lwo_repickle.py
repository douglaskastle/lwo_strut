#!/usr/bin/env python
import os
import re
from lwo_strut.lwoObject import lwoObject
from scripts.lwo_helper import LwoFile


def main():
    infiles = [ 
        "tests/basic/src/LWO2/box/box6-hidden.lwo",
        "tests/basic/src/LWO2/box/colors1.lwo",
        "tests/basic/src/LWO2/box/colors0.lwo",
        "tests/basic/src/LWO2/box/box9.lwo",
        "tests/basic/src/LWO2/box/box8.lwo",
        "tests/basic/src/LWO2/box/box7.lwo",
        "tests/basic/src/LWO2/box/box6.lwo",
        "tests/basic/src/LWO2/box/box5-ngon.lwo",
        "tests/basic/src/LWO2/box/box4-uv-layers.lwo",
        "tests/basic/src/LWO2/box/box3-uv-layers.lwo",
        "tests/basic/src/LWO2/box/box2-uv.lwo",
        "tests/basic/src/LWO2/box/box11.lwo",
        "tests/basic/src/LWO2/box/box10.lwo",
        "tests/basic/src/LWO2/box/box1.lwo",
        "tests/basic/src/LWO2/box/box1-uv.lwo",
        "tests/basic/src/LWO2/box/box0.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo",
        "tests/lwo_interceptor/src/LWO3/Federation - Interceptor/objects/interceptor_hull.lwo",
    ]
    for infile in infiles:
        f = LwoFile(infile, create_pickle=True)
        f.check_file()
    
        x = lwoObject(infile)
        x.ch.search_paths = ["../images"]
        #x.ch.recursive = True
        x.absfilepath = False
        x.read()
        x.resolve_clips()
        x.validate_lwo()
    
        #print(f.picklefile)
        f.rm_pickle()
        
        f.setup_pickle(x.elements)
    
        b = f.load_pickle()
    
    infiles = [ 
        "tests/basic/src/LWO3/box/box0.lwo",
        "tests/basic/src/LWO3/box/box1.lwo",
        "tests/basic/src/LWO3/box/box2-uv.lwo",
        "tests/basic/src/LWO3/box/box3-uv-layers.lwo",
    ]
    for infile in infiles:
        f = LwoFile(infile, create_pickle=True)
        f.check_file()
    
        x = lwoObject(infile)
        x.ch.search_paths = ["."]
        x.ch.recursive = True
        x.absfilepath = False
        x.read()
        x.resolve_clips()
        x.validate_lwo()
    
        #print(f.picklefile)
        f.rm_pickle()
        
        f.setup_pickle(x.elements)
    
        b = f.load_pickle()
    
        #print(x == b)
    infiles = [
        "tests/bulk/ELC2.lwo",
        "tests/bulk/Violator.lwo",
        "tests/bulk/tcs-p-ani-layers.lwo",
        "tests/bulk/uss-defiant.lwo",
        "tests/bulk/arrow.lwo",
    ]
    for infile in infiles:
        f = LwoFile(infile, create_pickle=True)
        f.check_file()
    
        x = lwoObject(infile)
        x.ch.search_paths = ["../images"]
        x.absfilepath = False
        x.read()
    
        #print(f.picklefile)
        f.rm_pickle()
        
        f.setup_pickle(x.elements)
    
        b = f.load_pickle()


    infile = "tests/basic/src/LWO2/box/box0.lwo"
    f = LwoFile(infile, create_pickle=True)
    f.check_file()
    
    f.picklefile = re.sub(".lwo.pickle", ".lwo.error0.pickle", f.picklefile)

    x.layers[0].name = "Layer 2"
    f.rm_pickle()
    f.setup_pickle(x.elements)


if __name__ == "__main__":
    main()
