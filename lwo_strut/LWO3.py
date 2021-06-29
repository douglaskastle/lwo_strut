from .LWO2 import LWO2
from .lwoBase import LWOBlock, CMAP, _lwo_base, _obj_node, _obj_nodeRoot, _obj_nodeserver, _obj_nodeName, _obj_nodeTag

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
        "nodes",
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
        self.angle = 0.0  # Surface Smoothing
        self.smooth = False  # Surface Smoothing
        self.side = 0
        self.textures = {}
        self.nodes = []

class LWO3(LWO2):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_types = [b"LWO3"]
        
    def read_block(self):
        b = LWOBlock()
        
        (name, ) = self.unpack("4s")
        (length, ) = self.unpack(">I")
        b.length = length
        b.skip = self.offset+b.length
        if b'FORM' == name:
            (subname, ) = self.unpack("4s")
            b.length -= 4
            b.name = subname
        else:
            b.name = name
            if not CMAP[name] is None:
                b.values = self.unpack(CMAP[name])
            
        return b

    def read_clip(self):
        """Read texture clip path"""
        (c_id, ) = self.unpack(">I")
        
        b = self.read_block()
        self.offset += 8
        orig_path = self.read_lwostring()
        self.clips[c_id] = orig_path
        self.offset = b.skip
    
    def read_shader_data(self, length):
        return
        b = self.read_block()
        print(b.name)
        b = self.read_block()
        print(b.name)
        b = self.read_block()
        print(b.name)
        b = self.read_block()
        print(b.name)
        b = self.read_block()
        print(b.name)
        b = self.read_block()
        print(b.name)
#         b = self.read_block()
#         print(b.name)
        return
        
        slength = self.offset + length
        while self.offset < slength:
            b = self.read_block()
            
            if b"ATTR" == b.name:
                pass
                self.debug(f"Unimplemented: {b.name}")    
#             elif b"SSHD" == b.name:
#                 self.read_shader_data(b.length)
            else:  # pragma: no cover 
                self.error(f"Unsupported Block: {b.name}")    
            self.offset = b.skip
    
    def read_shader(self, length):
        slength = self.offset + length
        while self.offset < slength:
            b = self.read_block()
            
            if b"SSHN" == b.name:
                s = self.read_lwostring()
            elif b"SSHD" == b.name:
                self.read_shader_data(b.length)
            else:  # pragma: no cover 
                self.error(f"Unsupported Block: {b.name}")    
            self.offset = b.skip
   
    def read_surf(self):
        """Read the object's surface data."""
        if len(self.surfs) == 0:
            self.info("Reading Object Surfaces")

        name = self.read_lwostring()

        surf = _obj_surf3()
        if not 0 == len(name):
            surf.name = name

        s_name = self.read_lwostring()
        
        nodes = []
        while self.offset < len(self.bytes):
            b = self.read_block()
            if b"VERS" == b.name:
                pass
                #(surf.version, ) = b.values
            elif b"NODS" == b.name:
                n = self.read_nodes(b.length)
                nodes.append(n)
            elif b"SSHA" == b.name:
                self.read_shader(b.length)
            elif b"SMAN" == b.name:
                surf.angle = b.values[0]
                if surf.angle > 0.0:
                    surf.smooth = True
            elif b"SIDE" == b.name:
                self.side = b.values[0]
            else:  # pragma: no cover 
                self.error(f"Unsupported Block: {b.name}")    
                print(b.name, b.length)
            
            self.offset = b.skip
        
        surf.nodes = nodes 
        
        #print(len(surf.nodes), surf.nodes) 
        self.surfs[surf.name] = surf

#     def mapping_tags(self):
#         if b"FORM" == self.chunkname:
#             (tag_type,) = self.unpack("4s")
#             if tag_type == b"SURF":
#                 self.read_surf()
#             elif tag_type == b"CLIP":
#                 self.offset += 4
#                 self.read_clip()
#             else:
#                 self.error(f"Unsupported tag_type: {tag_type}")
#                 self.rootchunk.skip()
#         elif b"OTAG" == self.chunkname:
#             #print(self.bytes[self.offset:])
#             self.debug(f"Unimplemented Chunk: {self.chunkname}")  
#             (otag_type,) = self.unpack("4s")
#             s = self.read_lwostring()
#             self.debug(f"{otag_type} {s}")  
#             self.rootchunk.skip()
#         
#         super().mapping_tags()


#     def read_lwo(self):
#         self.f = open(self.filename, "rb")
#         try:
#             header, chunk_size, chunk_name = struct.unpack(">4s1L4s", self.f.read(12))
#         except:
#             self.error(f"Error parsing file header! Filename {self.filename}")
#             self.f.close()
#             return
# 
#         if not chunk_name in self.file_types:
#             raise Exception(
#                 f"Incorrect file type: {chunk_name} not in {self.file_types}"
#             )
#         self.file_type = chunk_name
# 
#         self.info(f"Importing LWO: {self.filename}")
#         self.info(f"{self.file_type.decode('ascii')} Format")
# 
#         while True:
#             try:
#                 self.rootchunk = chunk.Chunk(self.f)
#             except EOFError:
#                 break
#             self.parse_tags()
#         del self.f
