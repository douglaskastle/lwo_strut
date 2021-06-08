#!/usr/bin/env python
import logging
from glob import glob
from pprint import pprint
from lwo_strut.lwoObject import lwoObject
#from lwo_strut.lwoObjectOld import lwoObject
from scripts.lwo_helper import LwoFile


def main():
#     #infile = "../NASA-3D-Resources/3D Models/Aquarius (A)/Aquarius-2010-Composite.lwo"
#     #infile = "../NASA-3D-Resources/3D Models/Atmosphere-Space Transition Region Explorer/Astre-main3.lwo"
#     #infile = "../NASA-3D-Resources/3D Models/Aura/Aura_2013-2.lwo"
#     infile = "../NASA-3D-Resources/3D Models/Gamma Ray Observatory - Composite/GRO-Composite.lwo"
#     f = LwoFile(infile, create_pickle=True)
#     f.check_file()
    
    infiles = glob("../NASA-3D-Resources/**/*.[Ll][Ww][Oo]", recursive=True)
    
    #infiles = infiles[:3]
    #print(infiles)
    #exit()
    #infiles = ["/home/gomez/project/NASA-3D-Resources/3D Models/RADARsat-Composite/RADARsat-Composite.lwo",]
    
    for infile in infiles:
        print(infile)
        try:
            x = lwoObject(infile, logging.DEBUG)
            x.read()
        except:
            print(infile)
            raise

        y = x.elements
    
        f = LwoFile(infile, create_pickle=False)
        f.check_file()
        f.setup_pickle(y)

        b = f.load_pickle()
        if b is None:
            return
    
        #print(y == b)
        if not y == b:
            for k in y.keys():
                if not y[k] == b[k]:
                    print(f'{k}')
#                     pprint(y[k])
#                     pprint(b[k])
#             raise
        #exit()
    


if __name__ == "__main__":
    main()
