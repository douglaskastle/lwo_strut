from .LWO2 import LWO2
from .lwoBase import _lwo_base

CMAP = {
    b'FORM' : None,
    b'VERS' : ">Q",
    b'NLOC' : ">III",
    b'NODS' : None,
    b'NZOM' : ">If",
    b'NSTA' : ">IH",
    b'NVER' : ">II",
    b'NNDS' : ">I",
    b'NSRV' : ">I",
    b'NRNM' : ">I",
    b'NNME' : ">I",
    b'NCRD' : ">I",
    b'NMOD' : ">I",
    b'NDTA' : ">I",
    b'NPRW' : ">I",
    b'NCOM' : ">I",
    b'NPLA' : ">I",
    b'INME' : ">I",
    b'IINM' : ">I",
    b'IINN' : ">I",
    b'IONM' : ">I",
    b'SSHN' : ">I",
    b'ENUM' : ">II",
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
        self.smooth = False  # Surface Smoothing
        self.textures = {}
        self.nodes = []

#     def lwoprint(self):  # debug: no cover
#         print(f"SURFACE")
#         print(f"Surface Name:       {self.name}")
#         print(
#             f"Color:              {int(self.colr[0]*256)} {int(self.colr[1]*256)} {int(self.colr[2]*256)}"
#         )
#         print(f"Luminosity:         {self.lumi*100:>8.1f}%")
#         print(f"Diffuse:            {self.diff*100:>8.1f}%")
#         print(f"Specular:           {self.spec*100:>8.1f}%")
#         print(f"Glossiness:         {self.glos*100:>8.1f}%")
#         print(f"Reflection:         {self.refl*100:>8.1f}%")
#         print(f"Transparency:       {self.tran*100:>8.1f}%")
#         print(f"Refraction Index:   {self.rind:>8.1f}")
#         print(f"Translucency:       {self.trnl*100:>8.1f}%")
#         print(f"Bump:               {self.bump*100:>8.1f}%")
#         print(f"Smoothing:          {self.smooth:>8}")
#         print(f"Smooth Threshold:   {self.strs*100:>8.1f}%")
#         print(f"Reflection Bluring: {self.rblr*100:>8.1f}%")
#         print(f"Refraction Bluring: {self.tblr*100:>8.1f}%")
#         print(f"Diffuse Sharpness:  {self.shrp*100:>8.1f}%")
#         print()
#         for textures_type in self.textures.keys():
#             print(textures_type)
#             for texture in self.textures[textures_type]:
#                 texture.lwoprint(indent=1)

class _obj_nodeTag3(_lwo_base):

    __slots__ = (
        "name",
        "realname", 
        "coords",
        "mode",
        "preview",
        "comment",
        "placement",
    )
    def __init__(self):
        self.name = "Default"
        self.realname = "Default"
        self.coords = (0, 0)
        self.mode = 0
        self.preview = "Default"
        self.comment = "Default"
        self.placement = 0
    
    def __str__(self):
        return f"\n{self.name}\n{self.realname}\n{self.coords}\n{self.mode}\n{self.preview}\n{self.comment}\n{self.placement}"
    
class _obj_nodeRoot3(_lwo_base):

    __slots__ = (
        "loc",
        "zoom", 
        "disabled",
    )
    def __init__(self):
        self.loc = (0, 0)
        self.zoom = 0.0
        self.disabled = False
    
    def __str__(self):
        return f"\n{self.loc}\n{self.zoom}\n{self.disabled}"
    
class _obj_nodeName3(_lwo_base):

    __slots__ = (
        "name",
        "inputname", 
        "inputnodename",
        "inputoutputname",
    )
    def __init__(self):
        self.name = "Default"
        self.inputname = "Default"
        self.inputnodename = "Default"
        self.inputoutputname = "Default"
    
    def __str__(self):
        return f"\n{self.name}\n{self.inputname}\n{self.inputnodename}\n{self.inputoutputname}"
    
class _obj_nodeserver3(_lwo_base):

    __slots__ = (
        "name",
        "tag", 
    )
    def __init__(self):
        self.name = 0
        self.tag = None
    
    def __str__(self):
        return f"\n{self.name}\n{self.tag}"
    
class _obj_node3(_lwo_base):

    __slots__ = (
        "version",
        "root", 
        "server",
        "connections",
    )
    def __init__(self):
        self.version = 0
        self.root = None
        self.server = None
        self.connections = None
    
    def __str__(self):
        return f"\n{self.version}\n{self.root}\n{self.server}\n{self.connections}"
    

class Block:
    def __init__(self, name=None):
        self.name = name
        self.length = 0
        self.form = False
        self.values = None
        self.skip = 0
        self.skip1 = 0

# class LWOBlock:
#     def __init__(self, name, length, offset):
#         self.name = name
#         self.length = length
#         self.offset = offset
#         self.skip = self.offset + length

class LWO3(LWO2):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_types = [b"LWO3"]
        
    def read_block(self):
        
        (name, ) = self.unpack("4s")
        
        b = Block()

        if not CMAP[name] is None:
            b.values = self.unpack(CMAP[name])
            b.name = name
            b.skip = self.offset
            b.skip1 = self.offset + b.values[0]
        else:
            b.form = True
            (form_length, ) = self.unpack(">I")
            b.length = form_length
            b.skip = self.offset+b.length
            b.skip1 = b.skip
        
            (subname, ) = self.unpack("4s")
            b.length -= 4
            b.name = subname
            
        return b
    
    def read_node_root(self, length):
        t = _obj_nodeRoot3()
        slength = self.offset + length
        while self.offset < slength:
            b = self.read_block()
            if b"NLOC" == b.name: # Location
                t.loc = b.values[1:]
            elif b"NZOM" == b.name: # Zoom 
                t.zoom = b.values[1]
            elif b"NSTA" == b.name: # Disabled
                t.disabled = bool(b.values[1])
            else:  # pragma: no cover 
                self.error(f"Unsupported Block: {b.name}")    
            self.offset = b.skip
        return t
    
    def read_node_tags(self, length):
        t = _obj_nodeTag3()
        slength = self.offset + length
        while self.offset < slength:
            b = self.read_block()
            if b"NRNM" == b.name: # RealName
                t.realname = self.read_lwostring()
            elif b"NNME" == b.name: # Name
                t.name = self.read_lwostring()
            elif b"NCRD" == b.name: # Coordinates
                #print(b.values)
                t.coords = self.unpack(">hh")
            elif b"NMOD" == b.name: # Mode
                (t.mode, ) = self.unpack(">I")
            elif b"NDTA" == b.name: # Data
                pass
            elif b"NPRW" == b.name: # Preview
                t.preview = self.read_lwostring()
            elif b"NCOM" == b.name: # Comment
                t.comment = self.read_lwostring()
            elif b"NPLA" == b.name: # Placement
                (t.placement, ) = self.unpack(">I")
            else:  # pragma: no cover 
                self.error(f"Unsupported Block: {b.name}")    
            self.offset = b.skip1
        
        return t
    
    def read_node_setup(self, length):
        t = _obj_nodeserver3()
        slength = self.offset + length
        
        while self.offset < slength:
            b = self.read_block()
            if b"NSRV" == b.name: # Server
                t.name= self.read_lwostring()
            elif b"NTAG" == b.name: # Node Tags
                t.tag = self.read_node_tags(b.length)
            else:  # pragma: no cover 
                self.error(f"Unsupported Block: {b.name}")    
            self.offset = b.skip1
        return t
    
    def read_node_connections(self, length):
        t = _obj_nodeName3()
        slength = self.offset + length
        while self.offset < slength:
            b = self.read_block()
            s = self.read_lwostring()
            
            if b"INME" == b.name: # NodeName 
                t.name = s
            elif b"IINM" == b.name: # InputName
                t.inputname = s
            elif b"IINN" == b.name: # InputNodeName
                t.inputnodename = s
            elif b"IONM" == b.name: # InputOutputName
                t.inputoutputname = s
            else:  # pragma: no cover 
                self.error(f"Unsupported Block: {b.name}")    
            self.offset = b.skip1
        return t
    
    def read_nodes(self, length):
        n = _obj_node3()
        slength = self.offset + length
        while self.offset < slength:
            b = self.read_block()
            if b"NVER" == b.name:
                n.version = b.values[1]
            elif b"NROT" == b.name:
                n.root = self.read_node_root(b.length)
            elif b"NNDS" == b.name:
                n.server = self.read_node_setup(b.length)
            elif b"NCON" == b.name:
                n.connections = self.read_node_connections(b.length)
            else:  # pragma: no cover 
                self.error(f"Unsupported Block: {b.name}")    
            self.offset = b.skip
        return n
    
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
            self.offset = b.skip1
   
    def read_surf(self):
        """Read the object's surface data."""
        if len(self.surfs) == 0:
            self.info("Reading Object Surfaces")

        self.offset += 8
        
        name = self.read_lwostring()

        surf = _obj_surf3()
        if not 0 == len(name):
            surf.name = name
        #self.debug(f"Surf {surf.name}")

        s_name = self.read_lwostring()
        
        nodes = []
        while self.offset < len(self.bytes):
            b = self.read_block()
            if b"VERS" == b.name:
                (surf.version, ) = b.values
            elif b"NODS" == b.name:
                n = self.read_nodes(b.length)
                nodes.append(n)
            elif b"SSHA" == b.name:
                self.read_shader(b.length)
            else:  # pragma: no cover 
                self.error(f"Unsupported Block: {b.name}")    
                print(b.name, b.length)
            
            self.offset = b.skip
        
        surf.nodes = nodes 
        
        #print(len(surf.nodes), surf.nodes) 
        self.surfs[surf.name] = surf

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
