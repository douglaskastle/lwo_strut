#!/usr/bin/env python
from glob import glob
from lwo_strut.lwoParser import lwoParser


def main():
    #infile = "../NASA-3D-Resources/3D Models/Aquarius (A)/Aquarius-2010-Composite.lwo"
    #infile = "../NASA-3D-Resources/3D Models/Atmosphere-Space Transition Region Explorer/Astre-main3.lwo"
    #infile = "../NASA-3D-Resources/3D Models/Aura/Aura_2013-2.lwo"
    infile = "../NASA-3D-Resources/3D Models/Gamma Ray Observatory - Composite/GRO-Composite.lwo"
    x = lwoParser(infile)
    #exit()
    
    infiles = glob("../NASA-3D-Resources/*/*/*.lwo")
    #print(infiles)
    for infile in infiles:
        print(infile)
        try:
            x = lwoParser(infile)
        except:
            print(infile)
            raise
        #exit()
#     infile = "tests/basic/src/LWO2/box/box0.lwo"
#     f = LwoFile(infile, create_pickle=True)
#     f.check_file()
# 
#     x = lwoObject(infile)
#     x.read()
# 
#     #x.pprint()
# 
#     f.setup_pickle(x)
#     # x.pprint()
# 
#     b = f.load_pickle()
# 
#     # x.pprint()
#     # b.pprint()
#     print(x == b)

if __name__ == "__main__":
    main()
