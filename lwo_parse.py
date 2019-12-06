#!/usr/bin/env python
from lwo_strut.lwoObject import lwoObject
from scripts.lwo_helper import LwoFile


def main():
    #     #infile = "tests/basic/src/LWO2/box/box1-uv.lwo"

    infile = "tests/basic/src/LWO2/box/box0.lwo"
    f = LwoFile(infile, create_pickle=True)
    f.check_file()

    x = lwoObject(infile)
    x.read()

    x.pprint()

    f.setup_pickle(x)
    # x.pprint()

    b = f.load_pickle()

    # x.pprint()
    # b.pprint()
    print(x == b)

#     #x.layers[0].name = "Layer 2"
#     outfile = infile + ".error0.pickle"
#     #os.unlink(outfile)
#     if not os.path.isfile(outfile):
#         with open(outfile, 'wb') as f:
#             pickle.dump(x, f, pickle.HIGHEST_PROTOCOL)
#
#     with open(outfile, 'rb') as handle:
#         b = pickle.load(handle)
#
#     #x.pprint()
#     #b.pprint()
#     print(x == b)

if __name__ == "__main__":
    main()
