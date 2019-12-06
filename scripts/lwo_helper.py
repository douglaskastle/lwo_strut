import os
import pickle
import re
import zipfile
import pathlib

class LwoFile(object):
    
    def __init__(self, infile, delimit="/src/", create_pickle=False):
        self.infile = infile
        self.delimit = delimit
        self.zdel_dir = []
        self.create_pickle = create_pickle

        if re.search(self.delimit, self.infile):
            head, name = self.infile.split(self.delimit)
        else:
            name = os.path.basename(self.infile)
    
    def check_file(self):
        edit_infile = self.infile
        #edit_infile = re.sub("\\\\", "/", edit_infile)
        x = []
        if not os.path.exists(self.infile):
            elem = edit_infile.split("/")
            for i in range(len(elem)):
                self.zpath = "/".join(elem[0:i])
                self.zfile = "/".join(elem[0:i+1]) + ".zip"
                x.append(self.zfile)
                if os.path.exists(self.zfile):
                    print(f"ZIP file found {self.zfile}")
                    break
                self.zfile = None
            
            if not None == self.zfile:
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
        self.picklefile = self.infile + ".pickle"
        self.picklefile = re.sub("src", "pickle", self.picklefile)
        head, tail = os.path.split(os.path.realpath(self.picklefile))
        pathlib.Path(head).mkdir(parents=True, exist_ok=True)
    
        if not os.path.isfile(self.picklefile) and self.create_pickle:
            with open(self.picklefile, 'wb') as f:
                pickle.dump(x, f, pickle.HIGHEST_PROTOCOL)
    
    def load_pickle(self):
        with open(self.picklefile, 'rb') as f:
            return pickle.load(f)
