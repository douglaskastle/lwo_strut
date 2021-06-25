import os
import sys
import pickle
import re
import zipfile
import pathlib


class LwoFile(object):
    def __init__(self, infile, create_pickle=False):
        self.infile = infile
        self.zdel_dir = []
        self.create_pickle = create_pickle
        self.picklefile = self.infile + ".pickle"
        self.picklefile = re.sub("src", "pickle", self.picklefile)
        self.pickle = None

    def check_file(self):
        edit_infile = self.infile
        x = []
        if not os.path.exists(self.infile):
            elem = edit_infile.split("/")
            for i in range(len(elem)):
                self.zpath = "/".join(elem[0:i])
                self.zfile = "/".join(elem[0:i + 1]) + ".zip"
                x.append(self.zfile)
                if os.path.exists(self.zfile):
                    print(f"ZIP file found {self.zfile}")
                    break
                self.zfile = None

            if None is not self.zfile:
                zf = zipfile.ZipFile(self.zfile, "r")
                zf.extractall(self.zpath)
                self.zfiles = zf.namelist()
                zf.close()
                zdir = os.path.join(self.zpath, self.zfiles[0].split("/")[0])
                if not os.path.isdir(zdir):
                    raise Exception(zdir)
                self.zdel_dir.append(zdir)

        if not os.path.exists(self.infile):
            raise Exception(f"Infile or zip file not found {self.infile} {x}")

    def setup_pickle(self, x):
        head, tail = os.path.split(os.path.realpath(self.picklefile))
        pathlib.Path(head).mkdir(parents=True, exist_ok=True)

        if not os.path.isfile(self.picklefile) or  self.create_pickle:
            with open(self.picklefile, "wb") as f:
                pickle.dump(x, f, pickle.HIGHEST_PROTOCOL)

    def load_pickle(self):
        print(self.picklefile)
        with open(self.picklefile, "rb") as f:
            try:
                self.pickle = pickle.load(f)
            except ValueError as e:
                # 3.8 pickle is different from 3.7, don't care if the pickle fails
                if sys.version_info[1] <= 7:
                    self.pickle = None
                else:
                    raise Exception(e)
            return self.pickle
     
    def rm_pickle(self):
        if os.path.isfile(self.picklefile):
            os.unlink(self.picklefile)
    
    def test_pickle(self, x, full=True):
        if self.pickle is None:
            self.load_pickle()
            
        if self.pickle is None:
            return True
        
        if full:
            for k in self.pickle:
                if not len(self.pickle[k]) == len(x[k]):
                    raise Exception(f"Number of {k} not matching:\n{len(self.pickle[k])}\n{len(x[k])}")
                if not self.pickle[k] == x[k]:
                    for j in self.pickle[k]:
                        if not self.pickle[k][j] == x[k][j]:
                            raise Exception(f"{k} not matching:\n\t{j}\n\t\t{self.pickle[k][j]}\n\t\t{x[k][j]}")
                    #raise Exception(f"{k} not matching:\n{self.pickle[k]}\n{x[k]}")
            
        return self.pickle == x
        #return True
         
