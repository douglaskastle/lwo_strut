import struct
#import array
from collections import OrderedDict
from pprint import pprint

class SurfT(object):
    COLR = b"COLR"
    DIFF = b"DIFF"
    LUMI = b"LUMI"
    SPEC = b"SPEC"
    REFL = b"REFL"
    TRAN = b"TRAN"
    TRNL = b"TRNL"
    GLOS = b"GLOS"
    GVAL = b"GVAL"
    SHRP = b"SHRP"
    BUMP = b"BUMP"
    BUF1 = b"BUF1"
    SIDE = b"SIDE"
    SMAN = b"SMAN"
    VERS = b"VERS"

    RFOP = b"RFOP"
    RIMG = b"RIMG"
    RSAN = b"RSAN"
    RBLR = b"RBLR"
    RIND = b"RIND"
    TROP = b"TROP"
    TIMG = b"TIMG"
    TBLR = b"TBLR"

    CLRS = b"CLRS"
    CLRF = b"CLRF"
    ADTR = b"ADTR"
    GLOW = b"GLOW"
    LINE = b"LINE"
    ALPH = b"ALPH"

    VCOL = b"VCOL"
    NORM = b"NORM"
    BLOK = b"BLOK"
    __slots__=()


class ReadT(object):
    FORM = ">4sL4s"
    TAG  = "4s"
    TAGU2= ">4sH"
    LAYR = ">HH"
    LWID = ">4s"
    VEC4 = ">4f"
    VEC3 = ">3f"
    COL3 = ">3f"
    ANG4 = ">f"
    F4   = ">f"
    U4   = ">I"
    U2   = ">H"
    U2U2 = ">HH"
    UV   = ">ff"
    OPAC = ">Hf"
    ISEQ = ">BBhHhh"
    __slots__=()

CMAP = {
    SurfT.COLR : ">fffH",
    SurfT.DIFF : ">fH",
    SurfT.LUMI : ">fH",
    SurfT.SPEC : ">fH",
    SurfT.REFL : ">fH",
    SurfT.TRAN : ">fH",
    SurfT.TRNL : ">fH",
    SurfT.GLOS : ">fH",
    SurfT.GVAL : ">fH",
    SurfT.BUMP : ">fH",
    SurfT.BUF1 : ">fH",
    SurfT.RIND : ">fH",
    SurfT.SMAN : ">HH",
    SurfT.RFOP : ">H",
    SurfT.TROP : ">H",
    SurfT.SIDE : ">H",
#    SurfT.BLOK : ReadT.LWID,
    SurfT.VERS : ">HH",
    b"NODS" : ReadT.U2,

    b"CHAN" : "4s",
    b"ENAB" : ReadT.U2,
    b"OPAC" : ">HfH",
    b"AXIS" : ReadT.U2,
    b"NEGA" : ReadT.U2,
    
    b"VALU" : ">HH",
    #b"FUNC" : ">HH",

    b"CNTR" : ">fffH",
    b"SIZE" : ">fffH",
    b"ROTA" : ">fffH",
    b"OREF" : "string",      # Possibily text
    b"ROID" : ">fffH",
    b"FALL" : ">HfffH",
    b"CSYS" : ReadT.U2,

    b"PROC" : ">H",
    b"PROJ" : ">H",
    b"IMAG" : ">H",
    b"WRAP" : ">HH",
    b"WRPW" : ">fH",
    b"WRPH" : ">fH",
    b"AAST" : ">Hf",
    b"PIXB" : ">H",
}
# class ArrayLite(array.array):
#     pass
#     
#     def __init__(self, *args):
#         super(array.array, self).__init__(*args)
class lwopprint(object):
    
    def __init__(self, d):
        self.indent = "    "
        self.d = d
        
        self.pprint()

    def retStrInt(self, d, level):
        lines = []
        lines.append(f"{self.indent*level}{d},")
        return(lines)
        
    def retStrArray(self, d, level):
        lines = []
        i = 0
        for j in d:
            if i < 4 or i > len(d)-2:
                if isinstance(j, dict):
                    lines.extend(self.retStrDict(j, level+1))
                else:
                    lines.append(f"{self.indent*level}{j},")
            elif i == 4:
                lines.append(f"{self.indent*level}...,")
            i += 1
        return(lines)
    
    def retStrDict(self, d, level):
        lines = []
        i = 0
        for j in d.keys():
            if isinstance(d[j], dict):
                s = "{{"
                e = "}}"
            else:
                s = "["
                e = "]"
            
            lines.append(f"{self.indent*level}{j}: {s}")
#             if isinstance(d[j], dict):
#             el
            if b'PTAG' == j:
                continue
            
            if isinstance(d[j], dict):
                lines.extend(self.retStrDict(d[j], level+1))
            elif None == d[j]:
                lines.append("None")
            elif isinstance(d[j], int):
                lines.extend(self.retStrInt(d[j], level+1))
            else:
                lines.extend(self.retStrArray(d[j], level+1))
                #print(d[j])
                #lines.extend(str(d[j]))
#             elif i == 4:
#                 lines.append(f"{self.indent*level}...,")
            i += 1
            lines.append(f"{self.indent*level}{e}")
        return lines
        
    def pprint(self):
        #pprint(self.d)
        print()
        lines = self.retStrDict(self.d, 0)
        print("\n".join(lines))

class LWOParser(object):
    
    def __init__(self, filename):
        self.filename = filename
        
        self.d = OrderedDict()
       
        self.f = open(self.filename, "rb")
        
        self.read_chunks()
                
        self.f.close()
        del self.f
        
        #pprint(self.d)
        lwopprint(self.d)
        #x.pprint()
     
    def read_vx2(self):
        """Read a variable-length index."""
        pointdata = self.f.read(4)
        if pointdata[0] != 255:
            index = pointdata[0] * 256 + pointdata[1]
            self.f.seek(self.f.tell()-2)
        else:
            index = pointdata[1] * 65536 + pointdata[2] * 256 + pointdata[3]
        return index

    def read_lwostring(self):
        name = ""
        j = 0
        while True:
            i = self.f.read(1)
            j += 1
            if i == b"\0":
                break
            name += i.decode("utf-8", "ignore")
        
        if j % 2 == 1:
            self.f.read(1)
        return name
    
    def read_tags(self):
        x = []
        while self.f.tell() < self.endbyte:
            x.append(self.read_lwostring())
        return x
    
    def read_layr(self):
        x = OrderedDict()
        x['index'], x['flags'] = struct.unpack(">HH", self.f.read(4))
        x['pivot'] = struct.unpack(">fff", self.f.read(12))
        x['layr_name'] = self.read_lwostring()
        x['parent_index'] = -1
        if self.f.tell() == self.endbyte + 2:
            (x['parent_index'],) = struct.unpack(">h", self.f.read(2))
        
        return x
        
#         new_layr = _obj_layer()
#         new_layr.index = x['index']
#         # Swap Y and Z to match Blender's pitch.
#         new_layr.pivot = [x['pivot'][0], x['pivot'][2], x['pivot'][1]]
#         new_layr.parent_index = x['parent_index']
#         if x['flags'] > 0 :
#             new_layr.hidden = True
#         if x['layr_name']:
#             new_layr.name = x['layr_name']
#         else:
#             new_layr.name = "Layer %d" % (new_layr.index + 1)
#         return new_layr
    
    def read_pnts(self):
        pnts = []
        #x = 0
        #pnts2 = ArrayLite()
        while self.f.tell() < self.endbyte:
            pnts.append(struct.unpack(">fff", self.f.read(12)))
        return(pnts)

    def read_pols(self):
        pols = []
        (type, ) = struct.unpack(">4s", self.f.read(4))
        
        while self.f.tell() < self.endbyte:
           face_pnt = self.read_vx2()
           pols.append(face_pnt)

        return pols
    
    def read_ptag(self):
        x = OrderedDict()
        (type, ) = struct.unpack(">4s", self.f.read(4))
        x[type] = {}
        while self.f.tell() < self.endbyte:
            part = self.read_vx2()
            (smgp, ) = struct.unpack(">H", self.f.read(2))
            x[type][part] = smgp
        return(x)
    
    def read_clip(self):
        #name = self.read_lwostring()
        (index, ) = struct.unpack(">I", self.f.read(4))
        print(index)
        (type, _) = struct.unpack(">4sH", self.f.read(6))
        print(type)
        #clip = self.read_lwostring()
        #print(clip)
        if b"STIL" == type:
            clip = self.read_lwostring()
        else:
            raise
        print(clip)
        #exit()
        #return x

    def read_tmap(self, endbyte=None):
        x = OrderedDict()
        while self.f.tell() < endbyte:
            (type, ) = struct.unpack(">4s", self.f.read(4))
            (subchunk_len, ) = struct.unpack(">H", self.f.read(2))
            if b'OREF' == type:
                x[type] = self.read_lwostring()
            else:              
                index = CMAP[type]
                x[type] = struct.unpack(index, self.f.read(subchunk_len))
        return x

    def read_texture(self, endbyte=None):
        x = OrderedDict()
        while self.f.tell() < endbyte:
            (type, ) = struct.unpack(">4s", self.f.read(4))
            (subchunk_len, ) = struct.unpack(">H", self.f.read(2))
            if b'TMAP' == type:
                x[type] = self.read_tmap(self.f.tell()+subchunk_len)
            elif b'FUNC' == type:
                x[type] = self.read_lwostring()
                remlength = (subchunk_len - len(x[type])) & 0xfffffffe
                if x[type] == "Fractal Noise":
                    self.f.read(remlength)
                elif x[type] == "turbNoise":
                    self.f.read(remlength)
                else:
                    raise Exception(f"{type} {x[type]} {subchunk_len} {remlength}")
            elif b'VALU' == type:
                self.f.read(subchunk_len)
                x[type] = "FIX"
            else:              
                index = CMAP[type]
                x[type] = struct.unpack(index, self.f.read(subchunk_len))
        
        return x
    
    def read_blok(self, endbyte):
        x = OrderedDict()
        (type, ) = struct.unpack(">4s", self.f.read(4))
        (chunk_len, ) = struct.unpack(">1L", self.f.read(4))
        if b"PROC" == type or b"IMAP" == type:
            x[type] = self.read_texture(endbyte)
        else:
            raise
            
        return x

    def read_nods(self, endbyte):
        x = OrderedDict()
        while self.f.tell() < endbyte:
            (type, ) = struct.unpack(">4s", self.f.read(4))
            #print(type)
            if b"NROT" == type:
                (x, ) = struct.unpack(">H", self.f.read(2))
                print(x)
            elif b"NLOC" == type:
                self.f.read(10)
            elif b"NZOM" == type:
                self.f.read(6)
            elif b"NSTA" == type:
                self.f.read(4)
            elif b"NVER" == type:
                self.f.read(6)
            elif b"NNDS" == type:
                self.f.read(2)
            elif b"NTAG" == type:
                self.f.read(2)
            elif b"NCRD" == type:
                self.f.read(10)
            elif b"NMOD" == type:
                self.f.read(6)
            elif b"NDTA" == type:
                self.f.read(2)
            elif b"NPRW" == type:
                self.f.read(4)
            elif b"NCOM" == type:
                self.f.read(4)
            elif b"NCON" == type:
                self.f.read(2)
            elif b"NSRV" == type or b"NRNM" == type or b"NNME" == type:
                self.f.read(2)
                x = self.read_lwostring()
                print(x)

            
        #exit()

    def read_surf(self):
        x = {}
        name = self.read_lwostring()
        source = self.read_lwostring()
        print(name, source)
        
        while self.f.tell() < self.endbyte:
            (type, ) = struct.unpack(">4s", self.f.read(4))
            (subchunk_len, ) = struct.unpack(">H", self.f.read(2))
            print(type, subchunk_len)
            
            endbyte = self.f.tell()+subchunk_len
            if b"NODS" == type:
                s = self.f.tell()
                x[type] = self.read_nods(endbyte)
                #print(self.f.tell()+subchunk_len)
                #self.f.seek(s+subchunk_len)
            elif b"BLOK" == type:
                x[type] = self.read_blok(endbyte)
            else:
                index = CMAP[type]
                x[type] = struct.unpack(index, self.f.read(subchunk_len))
            
        return x
    
    def read_chunks(self, parent=None):
        """Read the data in chunks."""
        
        x = None
        (chunk_name, chunk_len) = struct.unpack(">4s1L", self.f.read(8))
#         try:
#             (chunk_name, chunk_len) = struct.unpack(">4s1L", self.f.read(8))
#         except:
#             print(self.f.tell())
#             #pprint(self.lwo)
#             exit()
        
        print(chunk_name, chunk_len)
        
        self.startbyte = self.f.tell()
        self.endbyte = self.startbyte + chunk_len
        endbyte = self.endbyte 
        if b'FORM' == chunk_name:
            (lwo_type, ) = struct.unpack(">4s", self.f.read(4))
            x = [chunk_len, lwo_type]
        elif b'TAGS' == chunk_name:
            x = self.read_tags()
        elif b'LAYR' == chunk_name:
            x = self.read_layr()
        elif b'PNTS' == chunk_name:
            x = self.read_pnts()
        elif b'BBOX' == chunk_name:
            x = OrderedDict()
            x['min'] = struct.unpack(">fff", self.f.read(12))
            x['max'] = struct.unpack(">fff", self.f.read(12))
        elif b'VMAP' == chunk_name:
            pass
            self.f.seek(self.endbyte)
        elif b'POLS' == chunk_name:
            x = self.read_pols()
        elif b'PTAG' == chunk_name:
            x = self.read_ptag()
        elif b'SURF' == chunk_name:
            x = self.read_surf()
            self.f.seek(self.endbyte)
        elif b'CLIP' == chunk_name:
            x = self.read_clip()
            self.f.seek(self.endbyte)
        else:
            self.f.seek(self.endbyte)

        
        if None == parent:
            self.d[chunk_name] = OrderedDict()
            self.d[chunk_name][b"OPTS"] = x
            d = self.d[chunk_name]
        else:
            d = parent
            
        if b'FORM' == chunk_name:
            while self.f.tell() < endbyte:
                self.read_chunks(self.d[chunk_name])
                #print(self.f.tell(), endbyte)
        elif b'LAYR' == chunk_name or b'PTAG' == chunk_name\
          or b'SURF' == chunk_name:
            if not chunk_name in d.keys():
                d[chunk_name] = []
            d[chunk_name].append(x)
        else:
            d[chunk_name] = x
        
        if not self.f.tell() == self.endbyte:
            raise Exception(f"{self.f.tell()} != {self.endbyte}")

        return chunk_name, x
