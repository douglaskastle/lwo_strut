# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import re
import chunk
import struct
import logging
from pprint import pprint
from collections import OrderedDict

from .lwoLogger import LWOLogger

CMAP = {
#    b'FORM' : None,
    b'VERS' : ">I",
    b'NLOC' : ">II",
    b'NZOM' : ">f",
    b'NSTA' : ">H",
    b'NVER' : ">I",
    b'NNDS' : None,
    b'NSRV' : None,
    b'NRNM' : None,
    b'NNME' : None,
    b'NCRD' : ">ii",
    b'NMOD' : ">I",
    b'NDTA' : None,
    b'NPRW' : None,
    b'NCOM' : None,
    b'NPLA' : ">I",
    b'NTAG' : None,
    b'NROT' : None,
    b'NNDS' : None,
    b'NCON' : None,
    b'INME' : None,
    b'IINM' : None,
    b'IINN' : None,
    b'IONM' : None,
    b'SSHN' : None,
    b'ENUM' : ">I",
    b'SMAN' : ">f",
    b'SIDE' : ">H",
    b'NSEL' : None,

    b'CNTR' : ">fffh",
    b'SIZE' : ">fffh",
    b'ROTA' : ">fffh",
    b'FALL' : ">hfffh",
    b'OREF' : None,
    b'CSYS' : ">h",

    b'TMAP' : None,
    b'CHAN' : "4s",
    b'OPAC' : ">Hf",
    b'ENAB' : ">H",
    b'IMAG' : ">H",
    b'PROJ' : ">H",
    b'VMAP' : None,
    b'FUNC' : None,
    b'NEGA' : ">H",
    b'AXIS' : ">H",
    b'WRAP' : None,
    b'WRPW' : None,
    b'WRPH' : None,
    b'AAST' : None,
    b'PIXB' : None,
    b'VALU' : None,
    b'TAMP' : None,
    b'STCK' : None,
    b'PNAM' : None,
    b'INAM' : None,
    b'GRST' : None,
    b'GREN' : None,
    b'GRPT' : None,
    b'IKEY' : None,
    b'FKEY' : None,
    b'GVER' : None,

    b'COLR' : ">fff",
    b'DIFF' : ">f",
    b'LUMI' : ">f",
    b'SPEC' : ">f",
    b'REFL' : ">f",
    b'RBLR' : ">f",
    b'TRAN' : ">f",
    b'RIND' : ">f",
    b'TBLR' : ">f",
    b'TRNL' : ">f",
    b'GLOS' : ">f",
    b'SHRP' : ">f",
    b'SMAN' : ">f",
    b'BUMP' : ">f",
    b'BLOK' : None,
    b'VERS' : None,
    b'NODS' : None,
    b'GVAL' : None,
    b'NVSK' : None,
    b'CLRF' : None,
    b'CLRH' : None,
    b'ADTR' : None,
    #b'SIDE' : None,
    b'RFOP' : None,
    b'RIMG' : None,
    b'TIMG' : None,
    b'TROP' : None,
    b'ALPH' : None,
    b'BUF1' : None,
    b'BUF2' : None,
    b'BUF3' : None,
    b'BUF4' : None,
    b'LINE' : None,
    b'NORM' : None,
    b'RFRS' : None,
    b'VCOL' : None,
    b'RFLS' : None,
    b'CMNT' : None,
    b'FLAG' : None,
    b'RSAN' : None,
    b'LCOL' : None,
    b'LSIZ' : None,
    b'TSAN' : None,
}

def calc_read_length(x):
    z = 0
    h = re.findall(r"(\d?)(\w)", x.lower())
    for g in h:
        if '' == g[0]:
            i = 1
        else:
            i = int(g[0])
        j = g[1]
        if 'b' == j or 's' == j or 'c' == j:
            z += i*1
        elif 'h' == j:
            z += i*2
        elif 'f' == j or 'l' == j or 'i' == j:
            z += i*4
        elif 'q' == j or 'd' == j:
            z += i*8
    return z


class _lwo_base:
    def __eq__(self, x):
        if not isinstance(x, self.__class__):
            return False
        for k in self.__slots__:
            a = getattr(self, k)
            b = getattr(x, k)
            if not a == b:
                print(f"{k} mismatch:")
                print(f"\t{a} != {b}")
                return False
        return True

    @property
    def dict(self):
        d = OrderedDict()
        for k in self.__slots__:
            d[k] = getattr(self, k)
        return d

    def __repr__(self):
        return str(self.dict)


class _obj_layer(_lwo_base):
    __slots__ = (
        "name",
        "index",
        "parent_index",
        "pivot",
        "pols",
        "bones",
        "bone_names",
        "bone_rolls",
        "pnts",
        "vnorms",
        "lnorms",
        "wmaps",
        "colmaps",
        "uvmaps_vmad",
        "uvmaps_vmap",
        "morphs",
        "edge_weights",
        "surf_tags",
        "has_subds",
        "bbox",
    )

    def __init__(self):
        self.name = ""
        self.index = -1
        self.parent_index = -1
        self.pivot = [0, 0, 0]
        self.pols = []
        self.bones = []
        self.bone_names = {}
        self.bone_rolls = {}
        self.pnts = []
        self.vnorms = {}
        self.lnorms = {}
        self.wmaps = {}
        self.colmaps = {}
        self.uvmaps_vmad = {}
        self.uvmaps_vmap = {}
        self.morphs = {}
        self.edge_weights = {}
        self.surf_tags = {}
        self.has_subds = False
        self.bbox = [(0, 0, 0),(0, 0, 0)]


class _obj_surf(_lwo_base):
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


class _surf_position(_lwo_base):
    __slots__ = (
        "cntr",
        "size",
        "rota",
        "fall",
        "oref",
        "csys",
    )

    def __init__(self):
        self.cntr = (0.0, 0.0, 0.0, 0)
        self.size = (0.0, 0.0, 0.0, 0)
        self.rota = (0.0, 0.0, 0.0, 0)
        self.fall = (0, 0.0, 0.0, 0.0, 0)
        self.oref = ""
        self.csys = 0


class _surf_texture(_lwo_base):
    __slots__ = (
        "opac",
        "opactype",
        "enab",
        "clipid",
        "projection",
        "axis",
        "position",
        "enab",
        "uvname",
        "channel",
        "type",
        "func",
        "image",
        "nega",
    )

    def __init__(self):
        self.clipid = 1
        self.rev = 9
        self.opac = 1.0
        self.opactype = 0
        self.enab = True
        self.projection = 5
        self.axis = 0
        self.position = _surf_position()
        self.uvname = "UVMap"
        self.channel = "COLR"
        self.type = "IMAP"
        self.func = None
        self.image = None
        self.nega = None

    def lwoprint(self, indent=0):  # debug: no cover
        print(f"TEXTURE")
        print(f"ClipID:         {self.clipid}")
        print(f"Opacity:        {self.opac*100:.1f}%")
        print(f"Opacity Type:   {self.opactype}")
        print(f"Enabled:        {self.enab}")
        print(f"Projection:     {self.projection}")
        print(f"Axis:           {self.axis}")
        print(f"UVname:         {self.uvname}")
        print(f"Channel:        {self.channel}")
        print(f"Type:           {self.type}")
        print(f"Function:       {self.func}")
        print(f"Image:          {self.image}")
        print()

class _obj_nodeTag(_lwo_base):

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
    
class _obj_nodeRoot(_lwo_base):

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
    
class _obj_nodeName(_lwo_base):

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
    
class _obj_nodeserver(_lwo_base):

    __slots__ = (
        "name",
        "tag", 
    )
    def __init__(self):
        self.name = 0
        self.tag = None
    
    def __str__(self):
        return f"\n{self.name}\n{self.tag}"
    
class _obj_node(_lwo_base):

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

class LWOBlock:
    def __init__(self):
        self.name = None
        self.length = 0
        #self.offset = 0
        self.skip = 0
        
        self.values = None
        #self.skip1 = 0

class LWOBase:
    def __init__(self, filename=None, loglevel=logging.INFO):
        self.filename = filename
        self.file_types = []
        self.file_type = []
        self.layers = []
        self.surfs = {}
        self.materials = {}
        self.tags = []
        self.clips = {}
        self.images = []
        
        self.pnt_count = 0
        
        self.rootchunk = None
        self.seek = 0

        self.pnt_count = 0

        self.l = LWOLogger("LWO", loglevel)
        self.offset = 0

#     def read_bytes(self):
#         self.offset = 0
#         return self.rootchunk.read()
        
    def debug(self, msg):
         self.l.debug(msg)
        
    def info(self, msg):
        self.l.info(msg)

    def warning(self, msg):
        self.l.warning(msg)

    def error(self, msg):
        if self.l.level < logging.INFO:
            raise Exception(f"{self.filename} {msg}")
        else:
            self.l.error(msg)
 
    def unpack(self, x):
        read_length = calc_read_length(x)
        y = struct.unpack(x, self.bytes[self.offset : self.offset + read_length])
        self.offset += read_length
        return y
    
    def read_block(self):
        b = LWOBlock()
        
        (name,) = self.unpack("4s")
        (length,) = self.unpack(">H")
        b.length = length
        b.skip = self.offset + b.length
        b.name = name
        if not CMAP[name] is None:
            b.values = self.unpack(CMAP[name])
        return b
    
    def read_lwostring(self, length=None):
        """Parse a zero-padded string."""
        
        if length is None:
            raw_name = self.bytes[self.offset:]
            i = raw_name.find(b"\0")
            name_len = i + 1
            if name_len % 2 == 1:  # Test for oddness.
                name_len += 1

            if i > 0:
                # Some plugins put non-text strings in the tags chunk.
                name = raw_name[0:i].decode("utf-8", "ignore")
            else:
                name = ""
        else:
            name_len = length
            name = self.bytes[self.offset:self.offset+name_len-1].decode("utf-8", "ignore")
        self.offset += name_len
        self.chunkname  = name
        self.chunklength = name_len
        return self.chunkname

    def read_tags(self):
        """Read the object's Tags chunk."""
        while self.offset < len(self.bytes):
            tag = self.read_lwostring()
            self.tags.append(tag)

    def read_pnts(self):
        """Read the layer's points."""
        self.info(f"    Reading Layer ({self.layers[-1].name }) Points")
        while self.offset < len(self.bytes):
            #pnts = struct.unpack(">fff", self.bytes[offset : offset + 12])
            pnts = self.unpack(">fff")
            # Re-order the points so that the mesh has the right pitch,
            # the pivot already has the correct order.
            pnts = [
                pnts[0] - self.layers[-1].pivot[0],
                pnts[2] - self.layers[-1].pivot[1],
                pnts[1] - self.layers[-1].pivot[2],
            ]
            self.pnt_count += 1
            self.layers[-1].pnts.append(pnts)

    def parse_tags(self):
        self.chunkname = self.rootchunk.chunkname
        #self.bytes = self.read_bytes()
        self.bytes = self.rootchunk.read()
        self.offset = 0
        self.mapping_tags()

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
            except EOFError:
                break
            self.parse_tags()
        del self.f
