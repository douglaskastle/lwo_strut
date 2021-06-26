import struct
import chunk
from .LWO2 import LWO2
from .lwoBase import _lwo_base

CMAP = {
    b'FORM' : None,
    b'VERS' : ">Q",
    b'NLOC' : "fff",
    b'NODS' : "fff",
}

class _obj_surf3(_lwo_base):
    __slots__ = (
        "name",
        "source_name",
        "colr",
        "diff",
        "lumi",
        "spec",
        "refl",
        "rblr",
        "tran",
        "rind",
        "tblr",
        "trnl",
        "glos",
        "shrp",
        "bump",
        "strs",
        "smooth",
        "textures",
    )

    def __init__(self):
        self.name = "Default"
        self.version = "Default"
        self.source_name = ""
        self.colr = [1.0, 1.0, 1.0]
        self.diff = 1.0  # Diffuse
        self.lumi = 0.0  # Luminosity
        self.spec = 0.0  # Specular
        self.refl = 0.0  # Reflectivity
        self.rblr = 0.0  # Reflection Bluring
        self.tran = 0.0  # Transparency (the opposite of Blender's Alpha value)
        self.rind = 1.0  # RT Transparency IOR
        self.tblr = 0.0  # Refraction Bluring
        self.trnl = 0.0  # Translucency
        self.glos = 0.4  # Glossiness
        self.shrp = 0.0  # Diffuse Sharpness
        self.bump = 1.0  # Bump
        self.strs = 0.0  # Smooth Threshold
        self.smooth = False  # Surface Smoothing
        self.textures = {}  # Textures list

    def lwoprint(self):  # debug: no cover
        print(f"SURFACE")
        print(f"Surface Name:       {self.name}")
        print(
            f"Color:              {int(self.colr[0]*256)} {int(self.colr[1]*256)} {int(self.colr[2]*256)}"
        )
        print(f"Luminosity:         {self.lumi*100:>8.1f}%")
        print(f"Diffuse:            {self.diff*100:>8.1f}%")
        print(f"Specular:           {self.spec*100:>8.1f}%")
        print(f"Glossiness:         {self.glos*100:>8.1f}%")
        print(f"Reflection:         {self.refl*100:>8.1f}%")
        print(f"Transparency:       {self.tran*100:>8.1f}%")
        print(f"Refraction Index:   {self.rind:>8.1f}")
        print(f"Translucency:       {self.trnl*100:>8.1f}%")
        print(f"Bump:               {self.bump*100:>8.1f}%")
        print(f"Smoothing:          {self.smooth:>8}")
        print(f"Smooth Threshold:   {self.strs*100:>8.1f}%")
        print(f"Reflection Bluring: {self.rblr*100:>8.1f}%")
        print(f"Refraction Bluring: {self.tblr*100:>8.1f}%")
        print(f"Diffuse Sharpness:  {self.shrp*100:>8.1f}%")
        print()
        for textures_type in self.textures.keys():
            print(textures_type)
            for texture in self.textures[textures_type]:
                texture.lwoprint(indent=1)
class Block:
    def __init__(self, name=None):
        self.name = name
        self.start = 0
        self.length = 0
        self.form = False
        self.values = None
        self.bytes = None

#class LWO3(LWOBase):
class LWO3(LWO2):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_types = [b"LWO3"]
        
    def read_block(self):
        
        (name, ) = self.unpack("4s")
        b = Block()
        b.bytes = self.sbytes
        #b.start = self.offset
        #b.length = self.bytes[self.offset:]

        if not CMAP[name] is None:
            #print(CMAP[name], self.calc_read_length(CMAP[name]))
            b.values = self.unpack(CMAP[name])
            b.name = name
        else:
            b.form = True
            (form_length, ) = self.unpack(">I")
            #self.debug(f"length {form_length}")
            b.start = self.offset
        
            (subname, ) = self.unpack("4s")
            #print(subname)
            b.name = subname
            b.length = form_length
            #b.bytes = self.sbytes[self.offset:self.offset+form_length+4]
        
        return b
    
    def read_surf(self):
        """Read the object's surface data."""
        self.sbytes = self.bytes2()
        if len(self.surfs) == 0:
            self.info("Reading Object Surfaces")

        self.offset += 8
        
        name = self.read_lwostring()

        surf = _obj_surf3()
        if not 0 == len(name):
            surf.name = name
        self.debug(f"Surf {surf.name}")

        s_name = self.read_lwostring()
        #self.debug(f"Surf {s_name}")
        
        block = self.read_block()
       
        print(block.name, block.values, block.bytes)
       
        block = self.read_block()
       
        print(block.name, block.values, block.bytes[block.start:block.start+block.length])

        exit()

        i = 0
        while self.offset < len(self.sbytes):
            #self.debug(f"Surf offset {self.offset} {len(self.sbytes)}")
            block = self.read_block()
            
            print(block.name, block.values, block.bytes)
            
            if 3 == i:
                exit()

#             #(subchunk_name, ) = self.unpack("4s")
#             self.debug(f"Surf {subchunk_name}")
#             
#             if b"FORM" == subchunk_name:
#                 print(self.sbytes[self.offset:])
#                 #if 
#             
#             el
            
#             if b"VERS" == block.name:
#                 (surf.version, ) = self.unpack(">Q")
#             elif b"NODS" == subchunk_name:
#                 pass
#             elif b"NROT" == subchunk_name:
#                 pass
#             elif b"NLOC" == subchunk_name:
#                 self.unpack("fff")
#                 pass
#             elif b"NZOM" == subchunk_name:
#                 self.unpack("ff")
#                 pass
#             elif b"NSTA" == subchunk_name:
#                 self.unpack("f")
#                 self.unpack("h")
#                 pass
#             elif b"NVER" == subchunk_name:
#                 self.unpack("f")
#                 self.unpack("f")
#                 pass
#             elif b"NNDS" == subchunk_name:
#                 pass
#             elif b"NSRV" == subchunk_name:
#                 (length, ) = self.unpack(">I")
#                # yy = self.read_lwostring(length)
#                 s = self.read_lwostring()
#                 self.debug(f"Surf {subchunk_name} {s}")
#             elif b"NTAG" == subchunk_name:
#                 pass
#             elif b"NRNM" == subchunk_name:
#                 (length, ) = self.unpack(">I")
#                 s = self.read_lwostring()
#                 self.debug(f"Surf {subchunk_name} {s}")
#             elif b"NNME" == subchunk_name:
#                 (length, ) = self.unpack(">I")
#                 s = self.read_lwostring()
#                 self.debug(f"Surf {subchunk_name} {s}")
#             elif b"NCRD" == subchunk_name:
#                 self.unpack("fff")
#             elif b"NMOD" == subchunk_name:
#                 self.unpack("ff")
#             elif b"NDTA" == subchunk_name:
#                 pass
#             elif b"NPRW" == subchunk_name:
#                 (length, ) = self.unpack(">I")
#                 self.debug(f"Surf length {length}")
#                 self.offset += length
#                 #self.unpack("h")
#             elif b"NCOM" == subchunk_name:
#                 pass
#                 (length, ) = self.unpack(">I")
#                 self.debug(f"Surf length {length}")
#                 self.offset += length
#             elif b"NPLA" == subchunk_name:
#                 self.unpack("ff")
#             elif b"SATR" == subchunk_name:
#                 pass
#             elif b"META" == subchunk_name:
#                 pass
#             elif b"ENUM" == subchunk_name:
#                 pass
# #             elif b"" == subchunk_name:
# #                 pass
# #                 #self.debug(f"Unimplemented SubChunk: {subchunk_name}")  # pragma: no cover 
#             else:
#                 self.error(f"Unsupported SubBlock: {subchunk_name}")  # pragma: no cover     
            
            
            i += 1
        self.surfs[surf.name] = surf

    def read_lwo(self):
        self.f = open(self.filename, "rb")
        try:
            header, chunk_size, chunk_name = struct.unpack(">4s1L4s", self.f.read(12))
        except:
            self.error(f"Error parsing file header! Filename {self.filename}")
            self.f.close()
            return

        if not chunk_name in self.file_types:
            raise Exception(
                f"Incorrect file type: {chunk_name} not in {self.file_types}"
            )
        self.file_type = chunk_name

        self.info(f"Importing LWO: {self.filename}")
        self.info(f"{self.file_type.decode('ascii')} Format")

        while True:
            try:
                self.rootchunk = chunk.Chunk(self.f)
                print(self.rootchunk.chunkname)
            except EOFError:
                break
            #self.parse_tags()
        del self.f

#         self.chunks = []
#         while True:
#             try:
#                  self.chunks.append(chunk.Chunk(self.f))
#             except EOFError:
#                 break
#         del self.f
#         
#         for self.rootchunk in self.chunks:
#             self.debug(self.rootchunk)
#             #self.rootchunk = rootchunk
#             print(self.rootchunk.chunkname)
#             self.parse_tags()
#             #exit()
