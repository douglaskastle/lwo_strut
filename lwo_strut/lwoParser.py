import struct
from collections import OrderedDict
from pprint import pprint

CMAP = {
    b"COLR" : ">fffH",
    b"DIFF" : ">fH",
    b"LUMI" : ">fH",
    b"SPEC" : ">fH",
    b"REFL" : ">fH",
    b"TRAN" : ">fH",
    b"TRNL" : ">fH",
    b"GLOS" : ">fH",
    b"SHRP" : ">fH",
    b"GVAL" : ">fH",
    b"BUMP" : ">fH",
    b"BUF1" : ">fH",
    b"RIND" : ">fH",
    b"SMAN" : ">HH",
    b"RFOP" : ">H",
    b"TROP" : ">H",
    b"SIDE" : ">H",
    b"VERS" : ">HH",
    b"NODS" : ">H",

    b"CHAN" : "4s",
    b"ENAB" : ">H",
    b"OPAC" : ">HfH",
    b"NEGA" : ">H",
    
    #b"FUNC" : ">HH",
    #b"OREF" : "string",

    b"CNTR" : ">fffH",
    b"SIZE" : ">fffH",
    b"ROTA" : ">fffH",
    b"ROID" : ">fffH",
    b"FALL" : ">HfffH",
    b"CSYS" : ">H",

    b"PROC" : ">H",
    b"PROJ" : ">H",
    b"AXIS" : ">H",
    b"IMAG" : ">H",
    b"WRAP" : ">HH",
    b"WRPW" : ">fH",
    b"WRPH" : ">fH",
    b"AAST" : ">Hf",
    b"PIXB" : ">H",
    b"STCK" : ">Hf",
    b"TAMP" : ">fH",
    b"VALU" : ">HH",

    b"CLRH" : ">fH",
    b"CLRF" : ">fH",
    b"ADTR" : ">fH",
    b"RBLR" : ">fH",
    b"ALPH" : ">fH",
    b"GLOW" : ">HfHfH",
    b"LINE" : ">HfHfffH",
    b"RIMG" : ">H",
    b"NVSK" : ">H",
    b"TIMG" : ">H",
    b"NORM" : ">ffffffff",
    
    b"TXUV" : ">H",
    b"GRST" : ">f",
    b"GREN" : ">f",
    b"GRPT" : ">H",
    b"FKEY" : ">fffff", # FIX
    b"IKEY" : ">H",
}

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
                s = "{"
                e = "}"
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

class lwoParser(object):
    
    def __init__(self, filename, debug=False):
        self.filename = filename
        self.debug = debug
        
        self.d = OrderedDict()
       
        self.f = open(self.filename, "rb")
        
        self.f.seek(8)
        (lwo_type, ) = struct.unpack(">4s", self.f.read(4))
        print(lwo_type)
        if not b'LWO2' == lwo_type:
            print(f"Type {lwo_type} not supported yet")
            return
            exit()
        self.f.seek(0)
        
        self.read_chunks()
                
        self.f.close()
        del self.f
        
        #pprint(self.d)
        lwopprint(self.d)
        #x.pprint()
     
    def read_vx(self):
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
        if (self.f.tell() + 2) == self.endbyte:
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
           face_pnt = self.read_vx()
           pols.append(face_pnt)

        return pols
    
    def read_ptag(self):
        x = OrderedDict()
        (type, ) = struct.unpack(">4s", self.f.read(4))
        x[type] = {}
        while self.f.tell() < self.endbyte:
            part = self.read_vx()
            (smgp, ) = struct.unpack(">H", self.f.read(2))
            x[type][part] = smgp
        return(x)
    
    def read_clip(self):
        x = OrderedDict()
        y = OrderedDict()
        (index, ) = struct.unpack(">I", self.f.read(4))
        (type, ) = struct.unpack(">4s", self.f.read(4))
        (subchunk_len, ) = struct.unpack(">H", self.f.read(2))
        endbyte = self.f.tell()+subchunk_len

        if b"STIL" == type:
            y[type] = self.read_lwostring()
        else:
            if self.debug:
                raise Exception(f"Unknown identifier {type}")
        x[index] = y
        #pprint(x)

        if not self.f.tell() == endbyte and self.debug:
            raise Exception(f"not self.f.tell() == endbyte")
        #exit()
        return x

    def read_tmap(self, endbyte=None):
        x = OrderedDict()
        while self.f.tell() < endbyte:
            (type, ) = struct.unpack(">4s", self.f.read(4))
            (subchunk_len, ) = struct.unpack(">H", self.f.read(2))
            if b'OREF' == type:
                x[type] = self.read_lwostring()
            else:              
                if not type in CMAP.keys():
                    if self.debug:
                        raise Exception(f"Unknown identifier {type}")
                    self.f.read(subchunk_len)
                else:
                    index = CMAP[type]
                    x[type] = struct.unpack(index, self.f.read(subchunk_len))
        return x

    def read_uvmap(self):
        x = OrderedDict()
        name = self.read_lwostring()
        while self.f.tell() < self.endbyte:
            pnt_id = self.read_vx()
            pos = struct.unpack(">ff", self.f.read(8))
            x[pnt_id] = (pos[0], pos[1])

        return x, name
    
    def read_vmap(self, endbyte=None):
        x = OrderedDict()
        while self.f.tell() < endbyte:
            (type, ) = struct.unpack(">4s", self.f.read(4))
            (subchunk_len, ) = struct.unpack(">H", self.f.read(2))
            if b'TXUV' == type:
                y, name = self.read_uvmap()
                if not type in x.keys():
                    x[type] = {}
                x[type][name] = y
            elif b'PICK' == type: # "../NASA-3D-Resources/3D Models/James Webb Space Telescope (2016)/JWST-2016-Composite.lwo"
                self.f.seek(self.endbyte)
            elif b'MBAL' == type: # "../NASA-3D-Resources/3D Models/Laser Interferometer Space Antenna/Lisa-2006.lwo"
                self.f.seek(self.endbyte)
            else:              
                if self.debug:
                    raise Exception(f"Unknown identifier {type}")
        return x
        

    def read_texture(self, endbyte=None):
        x = OrderedDict()
        while self.f.tell() < endbyte:
            (type, ) = struct.unpack(">4s", self.f.read(4))
            (subchunk_len, ) = struct.unpack(">H", self.f.read(2))
            if b'TMAP' == type:
                x[type] = self.read_tmap(self.f.tell()+subchunk_len)
            elif b'VMAP' == type:
                x[type] = self.read_lwostring()
            elif b'PNAM' == type:
                x[type] = self.read_lwostring()
            elif b'INAM' == type:
                x[type] = self.read_lwostring()
            elif b'FUNC' == type:
                x[type] = self.read_lwostring()
                if len(x[type]) % 2 == 0:
                    rem = len(x[type]) + 2
                else:
                    rem = len(x[type]) + 1
                remlength = subchunk_len - rem
                
                if x[type] == "Fractal Noise":
                    self.f.read(remlength)
                elif x[type] == "turbNoise":
                    self.f.read(remlength)
                elif x[type] == "Crumple": # "../NASA-3D-Resources/3D Models/Aqua (C)/Aqua-Composite-Full.lwo"
                    self.f.read(remlength)
                elif x[type] == "Grid": # "../NASA-3D-Resources/3D Models/Aqua (C)/Aqua-Composite-Full.lwo"
                    self.f.read(remlength)
                elif x[type] == "Underwater": # "../NASA-3D-Resources/3D Models/Argo/Argo.lwo
                    self.f.read(remlength)
                elif x[type] == "Dots": # "../NASA-3D-Resources/3D Models/MMS (2014)/MMS-2014-composite.lwo
                    self.f.read(remlength)
                elif x[type] == "Edge_Transparency": # "../NASA-3D-Resources/3D Models/ISS (High Res)/Objects/Modules/cupola/cupola_open.lwo"
                    self.f.read(remlength)
                elif x[type] == "LW_FastFresnel": # "../NASA-3D-Resources/3D Models/ISS (High Res)/Objects/Modules/cupola/cupola_open.lwo"
                    self.f.read(remlength)
                elif x[type] == "Turbulence": # "../NASA-3D-Resources/3D Models/Wind-field Infrared Explorer (WIRE)/WIREcomposite2.lwo"
                    self.f.read(remlength)
                else:
                    if self.debug:
                        raise Exception(f"{type} {x[type]} {subchunk_len} {remlength}")
                    else:
                        self.f.read(remlength)
            elif b'VALU' == type:
                self.f.read(subchunk_len)
                x[type] = "FIX"
            else:              
                if b'OPAC' == type and not subchunk_len == 8: # "../NASA-3D-Resources/3D Models/Aquarius (A)/Aquarius-2010-Composite.lwo"
                    self.f.seek(endbyte)
                    break
                 
                if not type in CMAP.keys():
                    if self.debug:
                        raise Exception(f"Unknown identifier {type} {subchunk_len}")
                    self.f.read(subchunk_len)
                else:
                    index = CMAP[type]
                    x[type] = struct.unpack(index, self.f.read(subchunk_len))
                
        return x
    
    def read_blok(self, endbyte):
        x = OrderedDict()
        (type, ) = struct.unpack(">4s", self.f.read(4))
        (chunk_len, ) = struct.unpack(">1L", self.f.read(4))
        if b"PROC" == type or b"IMAP" == type \
        or b"SHDR" == type or b"GRAD" == type:
            x[type] = self.read_texture(endbyte)
        else:
            if self.debug:
                raise Exception(f"Unknown identifier {type}")
            
        return x

    def read_nods(self, endbyte):
        x = OrderedDict()
        while self.f.tell() < endbyte:
            (type, ) = struct.unpack(">4s", self.f.read(4))
            print(type)
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
            elif b"OMDE" == type:
                self.f.read(6)
            elif b"OMAX" == type:
                self.f.read(2)
            elif b"VPRM" == type:
                self.f.read(10)
            elif b"VPVL" == type:
                self.f.read(8)
            elif b"NSRV" == type or b"NRNM" == type or b"NNME" == type:
                self.f.read(2)
                x = self.read_lwostring()
                print(x)

            
        #exit()

    def read_surf(self):
        x = {}
        name = self.read_lwostring()
        source = self.read_lwostring()
        #print(name, source)
        
        while self.f.tell() < self.endbyte:
            (type, ) = struct.unpack(">4s", self.f.read(4))
            (subchunk_len, ) = struct.unpack(">H", self.f.read(2))
            #print(type, subchunk_len)
            
            endbyte = self.f.tell()+subchunk_len
            if b"NODS" == type:
                s = self.f.tell()
                #x[type] = self.read_nods(endbyte)
                #print(self.f.tell()+subchunk_len)
                self.f.seek(s+subchunk_len)
            elif b"ENVL" == type: # "../NASA-3D-Resources/3D Models/Aquarius (A)/Aquarius-2010-Composite.lwo"
                s = self.f.tell()
                #x[type] = self.read_nods(endbyte)
                self.f.seek(s+subchunk_len)
            elif b"BLOK" == type:
                x[type] = self.read_blok(endbyte)
                #pprint(x[type])
            else:
                if not type in CMAP.keys():
                    if self.debug:
                        raise Exception(f"Unknown identifier {type}")
                    self.f.read(subchunk_len)
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
        
        #print(chunk_name, chunk_len)
        
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
            x = self.read_vmap(self.endbyte)
            #self.f.seek(self.endbyte)
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
        elif b'LAYR' == chunk_name or b'PTAG' == chunk_name \
          or b'SURF' == chunk_name or b'CLIP' == chunk_name \
          or b'VMAP' == chunk_name:
            if not chunk_name in d.keys():
                d[chunk_name] = []
            d[chunk_name].append(x)
        else:
            d[chunk_name] = x
        
        if not self.f.tell() == self.endbyte:
            raise Exception(f"not {self.f.tell()} == {self.endbyte}")

        return chunk_name, x
