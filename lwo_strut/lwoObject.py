import os
import struct
import chunk
import re
from glob import glob
from pprint import pprint
from collections import OrderedDict


class lwoNoImageFoundException(Exception):
    pass


class _lwo_base(object):
    def __eq__(self, x):
        if not isinstance(x, self.__class__):
            return False
        
#         raise Exception(len(self.__slots__), len(x.__slots__))
#         if not len(self.__slots__) == len(x.__slots__):
#             print("Different number of __slots__")
#             return False
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
    SurfT.LUMI : ReadT.F4,
    SurfT.SPEC : ReadT.F4,
    SurfT.REFL : ReadT.F4,
    SurfT.TRAN : ReadT.F4,
    SurfT.TRNL : ReadT.F4,
    SurfT.GLOS : ReadT.F4,
    SurfT.GVAL : ReadT.F4,
    SurfT.BUMP : ReadT.F4,
    SurfT.BUF1 : ReadT.F4,
    SurfT.SMAN : ReadT.U2,
    SurfT.RFOP : ">HH",
    SurfT.TROP : ">HH",
    SurfT.SIDE : ">H",
    SurfT.BLOK : ReadT.LWID,
    SurfT.RIND : None,
    SurfT.VERS : ">HH",
    b"NODS" : ReadT.U2,

    b"CHAN" : ReadT.U2,
    b"ENAB" : ReadT.U2,
    b"OPAC" : ReadT.OPAC,
    b"AXIS" : ReadT.U2,
    b"NEGA" : ReadT.U2,
    
    b"VALU" : ReadT.U2,

    b"CNTR" : ">fffH",
    b"SIZE" : ">fffH",
    b"ROTA" : ">fffH",
    b"OREF" : "string",      # Possibily text
    b"ROID" : ">fffH",
    b"FALL" : ">HfffH",
    b"CSYS" : ReadT.U2,

    b"PROC" : ">H",
}

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
        "hidden",
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
        self.hidden = False


class _obj_surf(_lwo_base):
    __slots__ = (
        "bl_mat",
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
        "rfop",
        "trop",
        "side",
        "smooth",
        "textures",
        "textures_5",
    )

    def __init__(self):
        self.bl_mat = None
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
        self.rfop = 0    # Reflection Options
        self.trop = 0    # Transparency Options
        self.side = 0    # Polygon Sidedness
        self.smooth = False  # Surface Smoothing
        self.textures = {}  # Textures list
        self.textures_5 = []  # Textures list for LWOB

    def lwoprint(self):
        print(f"SURFACE")
        print(f"Surface Name:       {self.name}")
        print(f"Color:              {int(self.colr[0]*256)} {int(self.colr[1]*256)} {int(self.colr[2]*256)}")
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


class _surf_texture(_lwo_base):
    __slots__ = (
        "opac",
        "opactype",
        "enab",
        "clipid",
        "projection",
        "enab",
        "uvname",
        "channel",
        "type",
        "func",
        "clip",
        "nega",
    )

    def __init__(self):
        self.clipid = 1
        self.opac = 1.0
        self.opactype = 0
        self.enab = True
        self.projection = 5
        self.uvname = "UVMap"
        self.channel = "COLR"
        self.type = "IMAP"
        self.func = None
        self.clip = None
        self.nega = None

    def lwoprint(self, indent=0):
        print(f"TEXTURE")
        print(f"ClipID:         {self.clipid}")
        print(f"Opacity:        {self.opac*100:.1f}%")
        print(f"Opacity Type:   {self.opactype}")
        print(f"Enabled:        {self.enab}")
        print(f"Projection:     {self.projection}")
        print(f"UVname:         {self.uvname}")
        print(f"Channel:        {self.channel}")
        print(f"Type:           {self.type}")
        print(f"Function:       {self.func}")
        print(f"Clip:           {self.clip}")
        print()


class _surf_texture_5(_lwo_base):
    __slots__ = ("path", "X", "Y", "Z")

    def __init__(self):
        self.path = ""
        self.X = False
        self.Y = False
        self.Z = False

class LWO2(object):
    
    def __init__(self):
        self.type = "LWO2"
        self.layers = []
        self.surfs = {}
        self.tags = []
        self.clips = {}

    def unimplemented(self, name=None):
        pass
        #raise Exception(f"Unimplemented chunk {name}")
    
    def read_lwostring(self, raw_name):
        """Parse a zero-padded string."""

        i = raw_name.find(b"\0")
        name_len = i + 1
        if name_len % 2 == 1:  # Test for oddness.
            name_len += 1

        if i > 0:
            # Some plugins put non-text strings in the tags chunk.
            name = raw_name[0:i].decode("utf-8", "ignore")
        else:
            name = ""

        return name, name_len

    def read_vx(self, pointdata):
        """Read a variable-length index."""
        if pointdata[0] != 255:
            index = pointdata[0] * 256 + pointdata[1]
            size = 2
        else:
            index = pointdata[1] * 65536 + pointdata[2] * 256 + pointdata[3]
            size = 4

        return index, size

    def read_tags(self, tag_bytes):
        """Read the object's Tags chunk."""
        offset = 0
        chunk_len = len(tag_bytes)

        while offset < chunk_len:
            tag, tag_len = self.read_lwostring(tag_bytes[offset:])
            offset += tag_len
            #lwo.tags.append(tag)
            self.tags.append(tag)

    def read_pnts(self, pnt_bytes):
        """Read the layer's points."""
        print(f"\tReading Layer ({self.layers[-1].name }) Points")
        offset = 0
        chunk_len = len(pnt_bytes)

        while offset < chunk_len:
            pnts = struct.unpack(">fff", pnt_bytes[offset:offset + 12])
            offset += 12
            # Re-order the points so that the mesh has the right pitch,
            # the pivot already has the correct order.
            pnts = [
                pnts[0] - self.layers[-1].pivot[0],
                pnts[2] - self.layers[-1].pivot[1],
                pnts[1] - self.layers[-1].pivot[2],
            ]
            self.layers[-1].pnts.append(pnts)

    def read_morph(self, morph_bytes, is_abs):
        """Read an endomorph's relative or absolute displacement values."""
        chunk_len = len(morph_bytes)
        offset = 2
        name, name_len = self.read_lwostring(morph_bytes[offset:])
        offset += name_len
        deltas = []
    
        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(morph_bytes[offset:offset + 4])
            offset += pnt_id_len
            pos = struct.unpack(">fff", morph_bytes[offset:offset + 12])
            offset += 12
            pnt = self.layers[-1].pnts[pnt_id]
    
            if is_abs:
                deltas.append([pnt_id, pos[0], pos[2], pos[1]])
            else:
                # Swap the Y and Z to match Blender's pitch.
                deltas.append([pnt_id, pnt[0] + pos[0], pnt[1] + pos[2], pnt[2] + pos[1]])
    
            self.layers[-1].morphs[name] = deltas

    def read_weightmap(self, weight_bytes):
        """Read a weight map's values."""
        chunk_len = len(weight_bytes)
        offset = 2
        name, name_len = self.read_lwostring(weight_bytes[offset:])
        offset += name_len
        weights = []

        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(weight_bytes[offset:offset + 4])
            offset += pnt_id_len
            (value,) = struct.unpack(">f", weight_bytes[offset:offset + 4])
            offset += 4
            weights.append([pnt_id, value])

        self.layers[-1].wmaps[name] = weights
        
    def read_colmap(self, col_bytes):
        """Read the RGB or RGBA color map."""
        chunk_len = len(col_bytes)
        (dia,) = struct.unpack(">H", col_bytes[0:2])
        offset = 2
        name, name_len = self.read_lwostring(col_bytes[offset:])
        offset += name_len
        colors = {}
    
        if dia == 3:
            while offset < chunk_len:
                pnt_id, pnt_id_len = self.read_vx(col_bytes[offset:offset + 4])
                offset += pnt_id_len
                col = struct.unpack(">fff", col_bytes[offset:offset + 12])
                offset += 12
                colors[pnt_id] = (col[0], col[1], col[2])
        elif dia == 4:
            while offset < chunk_len:
                pnt_id, pnt_id_len = self.read_vx(col_bytes[offset:offset + 4])
                offset += pnt_id_len
                col = struct.unpack(">ffff", col_bytes[offset:offset + 16])
                offset += 16
                colors[pnt_id] = (col[0], col[1], col[2])
    
        if name in self.layers[-1].colmaps:
            if "PointMap" in self.layers[-1].colmaps[name]:
                self.layers[-1].colmaps[name]["PointMap"].update(colors)
            else:
                self.layers[-1].colmaps[name]["PointMap"] = colors
        else:
            self.layers[-1].colmaps[name] = dict(PointMap=colors)
    
    
    def read_normmap(self, norm_bytes):
        """Read vertex normal maps."""
        chunk_len = len(norm_bytes)
        offset = 2
        name, name_len = self.read_lwostring(norm_bytes[offset:])
        offset += name_len
        vnorms = {}
    
        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(norm_bytes[offset:offset + 4])
            offset += pnt_id_len
            norm = struct.unpack(">fff", norm_bytes[offset:offset + 12])
            offset += 12
            vnorms[pnt_id] = [norm[0], norm[2], norm[1]]
    
        self.layers[-1].vnorms = vnorms
    
    def read_color_vmad(self, col_bytes, last_pols_count):
        """Read the Discontinuous (per-polygon) RGB values."""
        chunk_len = len(col_bytes)
        (dia,) = struct.unpack(">H", col_bytes[0:2])
        offset = 2
        name, name_len = self.read_lwostring(col_bytes[offset:])
        offset += name_len
        colors = {}
        abs_pid = len(self.layers[-1].pols) - last_pols_count
    
        if dia == 3:
            while offset < chunk_len:
                pnt_id, pnt_id_len = self.read_vx(col_bytes[offset:offset + 4])
                offset += pnt_id_len
                pol_id, pol_id_len = self.read_vx(col_bytes[offset:offset + 4])
                offset += pol_id_len
    
                # The PolyID in a VMAD can be relative, this offsets it.
                pol_id += abs_pid
                col = struct.unpack(">fff", col_bytes[offset:offset + 12])
                offset += 12
                if pol_id in colors:
                    colors[pol_id][pnt_id] = (col[0], col[1], col[2])
                else:
                    colors[pol_id] = dict({pnt_id: (col[0], col[1], col[2])})
        elif dia == 4:
            while offset < chunk_len:
                pnt_id, pnt_id_len = self.read_vx(col_bytes[offset:offset + 4])
                offset += pnt_id_len
                pol_id, pol_id_len = self.read_vx(col_bytes[offset:offset + 4])
                offset += pol_id_len
    
                pol_id += abs_pid
                col = struct.unpack(">ffff", col_bytes[offset:offset + 16])
                offset += 16
                if pol_id in colors:
                    colors[pol_id][pnt_id] = (col[0], col[1], col[2])
                else:
                    colors[pol_id] = dict({pnt_id: (col[0], col[1], col[2])})
    
        if name in self.layers[-1].colmaps:
            if "FaceMap" in self.layers[-1].colmaps[name]:
                self.layers[-1].colmaps[name]["FaceMap"].update(colors)
            else:
                self.layers[-1].colmaps[name]["FaceMap"] = colors
        else:
            self.layers[-1].colmaps[name] = dict(FaceMap=colors)
    
    
    def read_uvmap(self, uv_bytes):
        """Read the simple UV coord values."""
        chunk_len = len(uv_bytes)
        offset = 2
        name, name_len = self.read_lwostring(uv_bytes[offset:])
        offset += name_len
        uv_coords = {}
    
        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(uv_bytes[offset:offset + 4])
            offset += pnt_id_len
            pos = struct.unpack(">ff", uv_bytes[offset:offset + 8])
            offset += 8
            uv_coords[pnt_id] = (pos[0], pos[1])
    
        if name in self.layers[-1].uvmaps_vmap:
            if "PointMap" in self.layers[-1].uvmaps_vmap[name]:
                self.layers[-1].uvmaps_vmap[name]["PointMap"].update(uv_coords)
            else:
                self.layers[-1].uvmaps_vmap[name]["PointMap"] = uv_coords
        else:
            self.layers[-1].uvmaps_vmap[name] = dict(PointMap=uv_coords)
    
    
    def read_uv_vmad(self, uv_bytes, last_pols_count):
        """Read the Discontinuous (per-polygon) uv values."""
        chunk_len = len(uv_bytes)
        offset = 2
        name, name_len = self.read_lwostring(uv_bytes[offset:])
        offset += name_len
        uv_coords = {}
        abs_pid = len(self.layers[-1].pols) - last_pols_count
    
        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(uv_bytes[offset:offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = self.read_vx(uv_bytes[offset:offset + 4])
            offset += pol_id_len
    
            pol_id += abs_pid
            pos = struct.unpack(">ff", uv_bytes[offset:offset + 8])
            offset += 8
            if pol_id in uv_coords:
                uv_coords[pol_id][pnt_id] = (pos[0], pos[1])
            else:
                uv_coords[pol_id] = dict({pnt_id: (pos[0], pos[1])})
    
        if name in self.layers[-1].uvmaps_vmad:
            if "FaceMap" in self.layers[-1].uvmaps_vmad[name]:
                self.layers[-1].uvmaps_vmad[name]["FaceMap"].update(uv_coords)
            else:
                self.layers[-1].uvmaps_vmad[name]["FaceMap"] = uv_coords
        else:
            self.layers[-1].uvmaps_vmad[name] = dict(FaceMap=uv_coords)
    
    
    def read_weight_vmad(self, ew_bytes):
        """Read the VMAD Weight values."""
        chunk_len = len(ew_bytes)
        offset = 2
        name, name_len = self.read_lwostring(ew_bytes[offset:])
        if name != "Edge Weight":
            return  # We just want the Catmull-Clark edge weights
    
        offset += name_len
        # Some info: LW stores a face's points in a clock-wize order (with the
        # normal pointing at you). This gives edges a 'direction' which is used
        # when it comes to storing CC edge weight values. The weight is given
        # to the point preceding the edge that the weight belongs to.
        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(ew_bytes[offset:offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = self.read_vx(ew_bytes[offset:offset + 4])
            offset += pol_id_len
            (weight,) = struct.unpack(">f", ew_bytes[offset:offset + 4])
            offset += 4
    
            face_pnts = self.layers[-1].pols[pol_id]
            try:
                # Find the point's location in the polygon's point list
                first_idx = face_pnts.index(pnt_id)
            except:
                continue
    
            # Then get the next point in the list, or wrap around to the first
            if first_idx == len(face_pnts) - 1:
                second_pnt = face_pnts[0]
            else:
                second_pnt = face_pnts[first_idx + 1]
    
            self.layers[-1].edge_weights["{0} {1}".format(second_pnt, pnt_id)] = weight
    
    
    def read_normal_vmad(self, norm_bytes):
        """Read the VMAD Split Vertex Normals"""
        chunk_len = len(norm_bytes)
        offset = 2
        name, name_len = self.read_lwostring(norm_bytes[offset:])
        lnorms = {}
        offset += name_len
    
        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(norm_bytes[offset:offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = self.read_vx(norm_bytes[offset:offset + 4])
            offset += pol_id_len
            norm = struct.unpack(">fff", norm_bytes[offset:offset + 12])
            offset += 12
            if not (pol_id in lnorms.keys()):
                lnorms[pol_id] = []
            lnorms[pol_id].append([pnt_id, norm[0], norm[2], norm[1]])
    
        print(f"LENGTH {len(lnorms.keys())}")
        self.layers[-1].lnorms = lnorms

    def read_bones(self, bone_bytes):
        """Read the layer's skelegons."""
        # print(f"\tReading Layer ({object_layers[-1].name}) Bones")
        offset = 0
        bones_count = len(bone_bytes)
    
        while offset < bones_count:
            (pnts_count,) = struct.unpack(">H", bone_bytes[offset:offset + 2])
            offset += 2
            all_bone_pnts = []
            for j in range(pnts_count):
                bone_pnt, data_size = self.read_vx(bone_bytes[offset:offset + 4])
                offset += data_size
                all_bone_pnts.append(bone_pnt)
    
            self.layers[-1].bones.append(all_bone_pnts)
    
    
    def read_bone_tags(self, tag_bytes, type):
        """Read the bone name or roll tags."""
        offset = 0
        chunk_len = len(tag_bytes)
    
        if type == "BONE":
            bone_dict = self.layers[-1].bone_names
        elif type == "BNUP":
            bone_dict = self.layers[-1].bone_rolls
        else:
            return
    
        while offset < chunk_len:
            pid, pid_len = self.read_vx(tag_bytes[offset:offset + 4])
            offset += pid_len
            (tid,) = struct.unpack(">H", tag_bytes[offset:offset + 2])
            offset += 2
            bone_dict[pid] = self.tags[tid]
    
    
    def read_surf_tags(self, tag_bytes, last_pols_count):
        """Read the list of PolyIDs and tag indexes."""
        print(f"\tReading Layer ({self.layers[-1].name}) Surface Assignments")
        offset = 0
        chunk_len = len(tag_bytes)
    
        # Read in the PolyID/Surface Index pairs.
        abs_pid = len(self.layers[-1].pols) - last_pols_count
        while offset < chunk_len:
            pid, pid_len = self.read_vx(tag_bytes[offset:offset + 4])
            offset += pid_len
            (sid,) = struct.unpack(">H", tag_bytes[offset:offset + 2])
            offset += 2
            if sid not in self.layers[-1].surf_tags:
                self.layers[-1].surf_tags[sid] = []
            self.layers[-1].surf_tags[sid].append(pid + abs_pid)

    def read_layr(self, layr_bytes):
        """Read the object's layer data."""
        new_layr = _obj_layer()
        new_layr.index, flags = struct.unpack(">HH", layr_bytes[0:4])
    
        if flags > 0 :
            new_layr.hidden = True
            #raise Exception
#         if flags > 0 and not load_hidden:
#             return False
    
        print("Reading Object Layer")
        offset = 4
        pivot = struct.unpack(">fff", layr_bytes[offset:offset + 12])
        # Swap Y and Z to match Blender's pitch.
        new_layr.pivot = [pivot[0], pivot[2], pivot[1]]
        offset += 12
        layr_name, name_len = self.read_lwostring(layr_bytes[offset:])
        offset += name_len
    
        if layr_name:
            new_layr.name = layr_name
        else:
            new_layr.name = "Layer %d" % (new_layr.index + 1)
    
        if len(layr_bytes) == offset + 2:
            (new_layr.parent_index,) = struct.unpack(">h", layr_bytes[offset:offset + 2])
    
        self.layers.append(new_layr)
        return True

    def read_pols(self, pol_bytes):
        """Read the layer's polygons, each one is just a list of point indexes."""
        print(f"\tReading Layer ({self.layers[-1].name}) Polygons")
        offset = 0
        pols_count = len(pol_bytes)
        old_pols_count = len(self.layers[-1].pols)
    
        while offset < pols_count:
            (pnts_count,) = struct.unpack(">H", pol_bytes[offset:offset + 2])
            offset += 2
            all_face_pnts =[]
            for j in range(pnts_count):
                face_pnt, data_size = self.read_vx(pol_bytes[offset:offset + 4])
                offset += data_size
                all_face_pnts.append(face_pnt)
            all_face_pnts.reverse()  # correct normals
    
            self.layers[-1].pols.append(all_face_pnts)
    
        return len(self.layers[-1].pols) - old_pols_count
    
    
    def read_clip(self, clip_bytes):
        """Read texture clip path"""
        c_id = struct.unpack(">L", clip_bytes[0:4])[0]
        orig_path, path_len = self.read_lwostring(clip_bytes[10:])
        self.clips[c_id] = {"orig_path": orig_path, "new_path": None}


    def read_surf(self, surf_bytes):
        """Read the object's surface data."""
        if len(self.surfs) == 0:
            print("Reading Object Surfaces")
    
        surf = _obj_surf()
        name, name_len = self.read_lwostring(surf_bytes)
        if len(name) != 0:
            surf.name = name
    
        # We have to read this, but we won't use it...yet.
        s_name, s_name_len = self.read_lwostring(surf_bytes[name_len:])
        offset = name_len + s_name_len
        block_size = len(surf_bytes)
        #print(name, name_len, offset, block_size, s_name, s_name_len)
        while offset < block_size:
            (subchunk_name,) = struct.unpack("4s", surf_bytes[offset:offset + 4])
            offset += 4
            (subchunk_len,) = struct.unpack(">H", surf_bytes[offset:offset + 2])
            offset += 2
    
            index = CMAP[subchunk_name]
            #print(offset, block_size, subchunk_name, subchunk_len)
            # Now test which subchunk it is.
            if subchunk_name == b"COLR":
                surf.colr = struct.unpack(">fff", surf_bytes[offset:offset + 12])
                # Don't bother with any envelopes for now.
    
            elif subchunk_name == b"DIFF":
                (surf.diff,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"LUMI":
                (surf.lumi,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"SPEC":
                (surf.spec,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"REFL":
                (surf.refl,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"RBLR":
                (surf.rblr,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"TRAN":
                (surf.tran,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"RIND":
                (surf.rind,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"TBLR":
                (surf.tblr,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"TRNL":
                (surf.trnl,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"GLOS":
                (surf.glos,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"SHRP":
                (surf.shrp,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"SMAN":
                (s_angle,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
                # print(s_angle)
                if s_angle > 0.0:
                    surf.smooth = True
            elif subchunk_name == b"BUMP":
                (surf.bump,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"BLOK":
                (block_type,) = struct.unpack("4s", surf_bytes[offset:offset + 4])
                texture = None
                debug = False
                #             if surf.name == "inc_hull_dark":
                #                 debug = True
                if block_type == b"IMAP" or block_type == b"PROC" or block_type == b"SHDR":
                    # print(surf.name, block_type)
                    texture = self.read_texture(surf_bytes, offset, subchunk_len, debug=debug)
                    #self.read_chunks(surf_bytes[offset:offset + subchunk_len])
                else:
                    print(f"Unimplemented texture type: {block_type}")
                
                if None is not texture:
                    texture.type = block_type.decode("ascii")
                    if texture.channel not in surf.textures.keys():
                        surf.textures[texture.channel] = []
                    surf.textures[texture.channel].append(texture)
            
            elif subchunk_name == b"RFOP":
                (surf.rfop, _) = struct.unpack(index, surf_bytes[offset:offset + 4])
            elif subchunk_name == b"TROP":
                (surf.trop, _) = struct.unpack(index, surf_bytes[offset:offset + 4])
            elif subchunk_name == b"SIDE":
                (surf.side, ) = struct.unpack(index, surf_bytes[offset:offset + 2])
            elif subchunk_name == b"VERS":
                #self.unimplemented(subchunk_name)
                # Not in Standard
                pass
            elif subchunk_name == b"NODS":
                #self.unimplemented(subchunk_name)
                (xx,) = struct.unpack(">H", surf_bytes[offset:offset + 2])
                #print(xx)
            elif subchunk_name == b"GVAL":
                self.unimplemented(subchunk_name)
            elif subchunk_name == b"NVSK":
                self.unimplemented(subchunk_name)
            elif subchunk_name == b"CLRF":
                self.unimplemented(subchunk_name)
            elif subchunk_name == b"CLRH":
                self.unimplemented(subchunk_name)
            elif subchunk_name == b"ADTR":
                self.unimplemented(subchunk_name)
            elif subchunk_name == b"RIMG":
                self.unimplemented(subchunk_name)
            elif subchunk_name == b"ALPH":
                self.unimplemented(subchunk_name)
            elif subchunk_name == b"BUF1":
                self.unimplemented(subchunk_name)
            elif subchunk_name == b"BUF2":
                self.unimplemented(subchunk_name)
            elif subchunk_name == b"BUF3":
                self.unimplemented(subchunk_name)
            elif subchunk_name == b"BUF4":
                self.unimplemented(subchunk_name)
            else:
                print(f"Unimplemented SubBlock: {subchunk_name}")
    
            offset += subchunk_len
    
        self.surfs[surf.name] = surf
    
    def read_chunks(self, lwo_bytes):
        """Read the object's tmap data."""
        self.offset = 0
        block_size = len(lwo_bytes)
        
        print(self.offset, block_size)
        y = OrderedDict()
        while self.offset < block_size:
            (subchunk_name,) = struct.unpack("4s", lwo_bytes[self.offset:self.offset + 4])
            self.offset += 4
            (subchunk_len,) = struct.unpack(">H", lwo_bytes[self.offset:self.offset + 2])
            self.offset += 2
          
            index = CMAP[subchunk_name]
            print("chunk", subchunk_name, subchunk_len)            
            if "string" == index:
                y[subchunk_name] = lwo_bytes[self.offset:self.offset+subchunk_len]

#             elif SurfT.BLOK == subchunk_name:
#                 pass
#                 #self.read_chunks(lwo_bytes[offset:offset+xoffset])
            else:
                y[subchunk_name] = struct.unpack(index, lwo_bytes[self.offset:self.offset+subchunk_len])
            self.offset += subchunk_len
           
        
        pprint(y)
        return(y)
        #exit()
    
    def read_texture(self, surf_bytes, offset, subchunk_len, debug=False):
        texture = _surf_texture()
        ordinal, ord_len = self.read_lwostring(surf_bytes[offset + 4:])
        suboffset = 6 + ord_len
        while suboffset < subchunk_len:
            (subsubchunk_name,) = struct.unpack(
                "4s", surf_bytes[offset + suboffset:offset + suboffset + 4]
            )
            suboffset += 4
            (subsubchunk_len,) = struct.unpack(
                ">H", surf_bytes[offset + suboffset:offset + suboffset + 2]
            )
            suboffset += 2
            print(subsubchunk_name, suboffset, subchunk_len)
            if subsubchunk_name == b"CHAN":
                (texture.channel,) = struct.unpack(
                    "4s", surf_bytes[offset + suboffset:offset + suboffset + 4],
                )
                texture.channel = texture.channel.decode("ascii")
            elif subsubchunk_name == b"OPAC":
                (texture.opactype,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset:offset + suboffset + 2],
                )
                (texture.opac,) = struct.unpack(
                    ">f", surf_bytes[offset + suboffset + 2: offset + suboffset + 6],
                )
                # print("opactype",opactype)
            elif subsubchunk_name == b"ENAB":
                (texture.enab,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset:offset + suboffset + 2],
                )
            elif subsubchunk_name == b"IMAG":
                (texture.clipid,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset:offset + suboffset + 2],
                )
            elif subsubchunk_name == b"PROJ":
                (texture.projection,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset:offset + suboffset + 2],
                )
            elif subsubchunk_name == b"VMAP":
                texture.uvname, name_len = self.read_lwostring(surf_bytes[offset + suboffset:])
                # print(f"VMAP {texture.uvname} {name_len}")
            elif subsubchunk_name == b"FUNC":  # This is the procedural
                texture.func, name_len = self.read_lwostring(surf_bytes[offset + suboffset:])
            elif subsubchunk_name == b"NEGA":
                (texture.nega,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset:offset + suboffset + 2],
                )
            elif subsubchunk_name == b"TMAP":
                self.read_chunks(surf_bytes[offset + suboffset:offset + suboffset + subsubchunk_len])
                #self.unimplemented(subsubchunk_name)
            elif subsubchunk_name == b"AXIS":
                #self.read_chunks(surf_bytes[offset + suboffset:offset + suboffset + subsubchunk_len])
                self.unimplemented(subsubchunk_name)
                xx,= struct.unpack(
                    ">H",
                    surf_bytes[offset + suboffset:offset + suboffset + 2],
                )
                print(xx)
            elif subsubchunk_name == b"WRAP":
                self.unimplemented(subsubchunk_name)
            elif subsubchunk_name == b"WRPW":
                self.unimplemented(subsubchunk_name)
            elif subsubchunk_name == b"WRPH":
                self.unimplemented(subsubchunk_name)
            elif subsubchunk_name == b"AAST":
                self.unimplemented(subsubchunk_name)
            elif subsubchunk_name == b"PIXB":
                self.unimplemented(subsubchunk_name)
            elif subsubchunk_name == b"VALU":
                self.unimplemented(subsubchunk_name)
            elif subsubchunk_name == b"TAMP":
                self.unimplemented(subsubchunk_name)
            elif subsubchunk_name == b"STCK":
                self.unimplemented(subsubchunk_name)
            else:
                print(f"Unimplemented SubSubBlock: {subsubchunk_name}")
            suboffset += subsubchunk_len
        return texture

    def read_lwo(self, f):
        """Read version 2 file, LW 6+."""
        self.last_pols_count = 0
        self.just_read_bones = False
        print(f"LWO v2 Format")

        while True:
            try:
                rootchunk = chunk.Chunk(f)
            except EOFError:
                break

            if rootchunk.chunkname == b"TAGS":
                self.read_tags(rootchunk.read())
            elif rootchunk.chunkname == b"LAYR":
                self.read_layr(rootchunk.read())
            elif rootchunk.chunkname == b"PNTS":
                self.read_pnts(rootchunk.read())
            elif rootchunk.chunkname == b"VMAP":
                vmap_type = rootchunk.read(4)

                if vmap_type == b"WGHT":
                    self.read_weightmap(rootchunk.read())
                elif vmap_type == b"MORF":
                    self.read_morph(rootchunk.read(), False)
                elif vmap_type == b"SPOT":
                    self.read_morph(rootchunk.read(), True)
                elif vmap_type == b"TXUV":
                    self.read_uvmap(rootchunk.read())
                elif vmap_type == b"RGB " or vmap_type == b"RGBA":
                    self.read_colmap(rootchunk.read())
                elif vmap_type == b"NORM":
                    self.read_normmap(rootchunk.read())
                elif vmap_type == b"PICK":
                    rootchunk.skip()  # SKIPPING
                else:
                    print(f"Skipping vmap_type: {vmap_type}")
                    rootchunk.skip()

            elif rootchunk.chunkname == b"VMAD":
                vmad_type = rootchunk.read(4)

                if vmad_type == b"TXUV":
                    self.read_uv_vmad(rootchunk.read(), self.last_pols_count)
                elif vmad_type == b"RGB " or vmad_type == b"RGBA":
                    self.read_color_vmad(rootchunk.read(), self.last_pols_count)
                elif vmad_type == b"WGHT":
                    # We only read the Edge Weight map if it's there.
                    self.read_weight_vmad(rootchunk.read())
                elif vmad_type == b"NORM":
                    self.read_normal_vmad(rootchunk.read())
                else:
                    print(f"Skipping vmad_type: {vmad_type}")
                    rootchunk.skip()

            elif rootchunk.chunkname == b"POLS":
                face_type = rootchunk.read(4)
                self.just_read_bones = False
                # PTCH is LW's Subpatches, SUBD is CatmullClark.
                if (face_type == b"FACE" or face_type == b"PTCH" or face_type == b"SUBD"):
                    self.last_pols_count = self.read_pols(rootchunk.read())
                    if face_type != b"FACE":
                        self.layers[-1].has_subds = True
                elif face_type == b"BONE" and self.handle_layer:
                    self.read_bones(rootchunk.read())
                    self.just_read_bones = True
                else:
                    print(f"Skipping face_type: {face_type}")
                    rootchunk.skip()

            elif rootchunk.chunkname == b"PTAG":
                (tag_type,) = struct.unpack("4s", rootchunk.read(4))
                if tag_type == b"SURF" and not self.just_read_bones:
                    # Ignore the surface data if we just read a bones chunk.
                    self.read_surf_tags(rootchunk.read(), self.last_pols_count)
                elif tag_type == b"BNUP":
                    self.read_bone_tags(rootchunk.read(), "BNUP")
                    raise
                elif tag_type == b"BONE":
                    self.read_bone_tags(rootchunk.read(), "BONE")
                    raise
                elif tag_type == b"PART":
                    rootchunk.skip()  # SKIPPING
                elif tag_type == b"COLR":
                    rootchunk.skip()  # SKIPPING
                else:
                    print(f"Skipping tag: {tag_type}")
                    rootchunk.skip()
            elif rootchunk.chunkname == b"SURF":
                self.read_surf(rootchunk.read())
            elif rootchunk.chunkname == b"CLIP":
                self.read_clip(rootchunk.read())
            elif rootchunk.chunkname == b"BBOX":
                rootchunk.skip()  # SKIPPING
            elif rootchunk.chunkname == b"VMPA":
                rootchunk.skip()  # SKIPPING
            elif rootchunk.chunkname == b"PNTS":
                rootchunk.skip()  # SKIPPING
            elif rootchunk.chunkname == b"POLS":
                rootchunk.skip()  # SKIPPING
            elif rootchunk.chunkname == b"PTAG":
                rootchunk.skip()  # SKIPPING
            else:
                print(f"Skipping Chunk: {rootchunk.chunkname}")
                rootchunk.skip()


class LWO(LWO2):

    def __init__(self):
        super().__init__()
        self.type = "LWO"

    def read_pols(self, pol_bytes):
        """
        Read the polygons, each one is just a list of point indexes.
        But it also includes the surface index.
        """
        print(f"\tReading Layer ({self.layers[-1].name}) Polygons")
        offset = 0
        chunk_len = len(pol_bytes)
        old_pols_count = len(self.layers[-1].pols)
        poly = 0
    
        while offset < chunk_len:
            (pnts_count,) = struct.unpack(">H", pol_bytes[offset:offset + 2])
            offset += 2
            all_face_pnts = []
            for j in range(pnts_count):
                (face_pnt,) = struct.unpack(">H", pol_bytes[offset:offset + 2])
                offset += 2
                all_face_pnts.append(face_pnt)
            all_face_pnts.reverse()
    
            self.layers[-1].pols.append(all_face_pnts)
            (sid,) = struct.unpack(">h", pol_bytes[offset:offset + 2])
            offset += 2
            sid = abs(sid) - 1
            if sid not in self.layers[-1].surf_tags:
                self.layers[-1].surf_tags[sid] = []
            self.layers[-1].surf_tags[sid].append(poly)
            poly += 1
    
        return len(self.layers[-1].pols) - old_pols_count


    def read_layr(self, layr_bytes):
        """Read the object's layer data."""
        # XXX: Need to check what these two exactly mean for a LWOB/LWLO file.
        new_layr = _obj_layer()
        new_layr.index, flags = struct.unpack(">HH", layr_bytes[0:4])

        print("Reading Object Layer")
        offset = 4
        layr_name, name_len = self.read_lwostring(layr_bytes[offset:])
        offset += name_len

        if name_len > 2 and layr_name != "noname":
            new_layr.name = layr_name
        else:
            # new_layr.name = f"Layer {new_layr.index}"
            new_layr.name = "Layer {}".format(new_layr.index)

        self.layers.append(new_layr)
    
    def read_surf(self, surf_bytes, dirpath=None):
        """Read the object's surface data."""
        if len(self.surfs) == 0:
            print("Reading Object Surfaces")
    
        surf = _obj_surf()
        name, name_len = self.read_lwostring(surf_bytes)
        if len(name) != 0:
            surf.name = name
    
        offset = name_len
        chunk_len = len(surf_bytes)
        while offset < chunk_len:
            (subchunk_name,) = struct.unpack("4s", surf_bytes[offset:offset + 4])
            offset += 4
            (subchunk_len,) = struct.unpack(">H", surf_bytes[offset:offset + 2])
            offset += 2
    
            # Now test which subchunk it is.
            if subchunk_name == b"COLR":
                color = struct.unpack(">BBBB", surf_bytes[offset:offset + 4])
                surf.colr = [color[0] / 255.0, color[1] / 255.0, color[2] / 255.0]
    
            elif subchunk_name == b"DIFF":
                (surf.diff,) = struct.unpack(">h", surf_bytes[offset:offset + 2])
                surf.diff /= 256.0  # Yes, 256 not 255.
    
            elif subchunk_name == b"LUMI":
                (surf.lumi,) = struct.unpack(">h", surf_bytes[offset:offset + 2])
                surf.lumi /= 256.0
    
            elif subchunk_name == b"SPEC":
                (surf.spec,) = struct.unpack(">h", surf_bytes[offset:offset + 2])
                surf.spec /= 256.0
    
            elif subchunk_name == b"REFL":
                (surf.refl,) = struct.unpack(">h", surf_bytes[offset:offset + 2])
                surf.refl /= 256.0
    
            elif subchunk_name == b"TRAN":
                (surf.tran,) = struct.unpack(">h", surf_bytes[offset:offset + 2])
                surf.tran /= 256.0
    
            elif subchunk_name == b"RIND":
                (surf.rind,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
    
            elif subchunk_name == b"GLOS":
                (surf.glos,) = struct.unpack(">h", surf_bytes[offset:offset + 2])
    
            elif subchunk_name == b"SMAN":
                (s_angle,) = struct.unpack(">f", surf_bytes[offset:offset + 4])
                if s_angle > 0.0:
                    surf.smooth = True
    
            elif subchunk_name in [b"CTEX", b"DTEX", b"STEX", b"RTEX", b"TTEX", b"BTEX"]:
                texture = None
    
            elif subchunk_name == b"TIMG":
                path, path_len = self.read_lwostring(surf_bytes[offset:])
                if path == "(none)":
                    continue
                texture = _surf_texture_5()
                path = dirpath + os.sep + path.replace("//", "")
                texture.path = path
                surf.textures_5.append(texture)
    
            elif subchunk_name == b"TFLG":
                if texture:
                    (mapping,) = struct.unpack(">h", surf_bytes[offset:offset + 2])
                    if mapping & 1:
                        texture.X = True
                    elif mapping & 2:
                        texture.Y = True
                    elif mapping & 4:
                        texture.Z = True
            elif subchunk_name == b"FLAG":
                pass  # SKIPPING
            elif subchunk_name == b"VLUM":
                pass  # SKIPPING
            elif subchunk_name == b"VDIF":
                pass  # SKIPPING
            elif subchunk_name == b"VSPC":
                pass  # SKIPPING
            elif subchunk_name == b"VRFL":
                pass  # SKIPPING
            elif subchunk_name == b"VTRN":
                pass  # SKIPPING
            elif subchunk_name == b"RFLT":
                pass  # SKIPPING
            elif subchunk_name == b"ALPH":
                pass  # SKIPPING
            else:
                print(f"Unimplemented SubBlock: {subchunk_name}")
    
            offset += subchunk_len
    
        self.surfs[surf.name] = surf

    def read_lwo(self, f):
        """Read version 1 file, LW < 6."""
        self.last_pols_count = 0
        #print(f"LWO v1 Format")

        while True:
            try:
                rootchunk = chunk.Chunk(f)
            except EOFError:
                break

            if rootchunk.chunkname == b"SRFS":
                self.read_tags(rootchunk.read())
            elif rootchunk.chunkname == b"LAYR":
                self.read_layr(rootchunk.read())
            elif rootchunk.chunkname == b"PNTS":
                if len(self.layers) == 0:
                    # LWOB files have no LAYR chunk to set this up.
                    nlayer = _obj_layer()
                    nlayer.name = "Layer 1"
                    self.layers.append(nlayer)
                self.read_pnts(rootchunk.read())
            elif rootchunk.chunkname == b"POLS":
                self.last_pols_count = self.read_pols(rootchunk.read())
            elif rootchunk.chunkname == b"PCHS":
                self.last_pols_count = self.read_pols(rootchunk.read())
                self.layers[-1].has_subds = True
            elif rootchunk.chunkname == b"PTAG":
                (tag_type,) = struct.unpack("4s", rootchunk.read(4))
                if tag_type == b"SURF":
                    raise Exception("Missing commented out function")
                #                     read_surf_tags_5(
                #                         rootchunk.read(), self.layers, self.last_pols_count
                #                     )
                else:
                    rootchunk.skip()
            elif rootchunk.chunkname == b"SURF":
                self.read_surf(rootchunk.read())
            else:
                # For Debugging \/.
                print(f"Skipping Chunk: {rootchunk.chunkname}")
                rootchunk.skip()

class LWOParser(object):
    
    def __init__(self, filename):
        self.filename = filename
        
        self.lwo = OrderedDict()
        
        self.f = open(self.filename, "rb")
        
        self.read_chunks()
        self.f.close()
        del self.f
        
        pprint(self.lwo)
 
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
        while self.f.tell() < self.endbyte:
            pnts.append(struct.unpack(">fff", self.f.read(12)))
        #return(pnts)

    def read_pols(self):
        pols = []
        (type, ) = struct.unpack(">4s", self.f.read(4))
        
        while self.f.tell() < self.endbyte:
           face_pnt = self.read_vx2()
           pols.append(face_pnt)

        #return pols
    
    def read_ptag(self):
        x = OrderedDict()
        (type, ) = struct.unpack(">4s", self.f.read(4))
        x[type] = {}
        while self.f.tell() < self.endbyte:
            part = self.read_vx2()
            (smgp, ) = struct.unpack(">H", self.f.read(2))
            x[type][part] = smgp
        return(x)
        pprint(x)

    def read_surf(self):
        x = {}
        name = self.read_lwostring()
        source = self.read_lwostring()
        print(name, source)
        
        while self.f.tell() < self.endbyte:
            (type, ) = struct.unpack(">4s", self.f.read(4))
            (subchunk_len, ) = struct.unpack(">H", self.f.read(2))
            print(type, subchunk_len)
            
            if b"NODS" == type:
                #x[type] = self.read_chunks()
                print(self.f.tell()+subchunk_len)
                self.f.seek(self.f.tell()+subchunk_len)
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
        else:
            self.f.seek(self.endbyte)

        
        #pprint(x) 
        if b'LAYR' == chunk_name or b'PTAG' == chunk_name:
            if not chunk_name in self.lwo.keys():
                self.lwo[chunk_name] = []
            self.lwo[chunk_name].append(x)
        else:
            self.lwo[chunk_name] = x
        
        if b'FORM' == chunk_name:
            #print(self.f.tell(), endbyte)
            while self.f.tell() < endbyte:
                self.read_chunks()
                print(self.f.tell(), endbyte)
        
        if not self.f.tell() == self.endbyte:
            raise Exception(f"{self.f.tell()} != {self.endbyte}")

        return chunk_name, x

class LWO3(object):

    def __init__(self):
        super().__init__()
        self.type = "LWO3"


class lwoObject(object):
    def __init__(self, filename):
        self.name, self.ext = os.path.splitext(os.path.basename(filename))
        self.filename = os.path.abspath(filename)
        
        self.lwo = None
        
        self.images = []
        self.search_paths = []
        self.allow_missing_images = False
        self.absfilepath = True
        
        self.load_hidden = False

    @property
    def layers(self):
        if None is self.lwo:
            return []
        else:
            layers = []
            for l in self.lwo.layers:
                if not l.hidden or self.load_hidden:
                    layers.append(l)
            return layers
        
    @property
    def surfs(self):
        if None is self.lwo:
            return {}
        else:
            return self.lwo.surfs
        
    @property
    def tags(self):
        if None is self.lwo:
            return []
        else:
            return self.lwo.tags
        
    @property
    def clips(self):
        if None is self.lwo:
            return {}
        else:
            return self.lwo.clips
        
    def __eq__(self, x):
        __slots__ = (
            "layers",
            "surfs",
            "tags",
            "clips",
            "images",
        )
        for k in __slots__:
            a = getattr(self, k)
            b = getattr(x, k)
            if not a == b:
#                 print(f"{k} mismatch:")
#                 print(f"\t{a} != {b}")
                return False
        return True
    

    def parse_lwo(self):
        
        p = LWOParser(self.filename)
        
        exit()


    def read(
        self, ADD_SUBD_MOD=True, LOAD_HIDDEN=False, SKEL_TO_ARM=True,
    ):
        self.add_subd_mod = ADD_SUBD_MOD
        self.load_hidden = LOAD_HIDDEN
        self.skel_to_arm = SKEL_TO_ARM

        
        #self.parse_lwo()
       
        self.f = open(self.filename, "rb")
        try:
            header, chunk_size, chunk_name = struct.unpack(">4s1L4s", self.f.read(12))
        except:
            print(f"Error parsing file header! Filename {self.filename}")
            self.f.close()
            return

        print(f"Importing LWO: {self.filename}")
        if chunk_name == b"LWO2":
            self.lwo = LWO2()
        elif chunk_name == b"LWOB" or chunk_name == b"LWLO":
            # LWOB and LWLO are the old format, LWLO is a layered object.
            self.lwo = LWO()
        else:
            print("Not a supported file type!")
            self.f.close()
            return
        print(f"{self.lwo.type}")
        
        self.lwo.read_lwo(self.f)
        
        self.f.close()
        del self.f
        
        print(f"Validating LWO: {self.filename}")
        self.validate_lwo()

    def pprint(self):

        layers = []
        for x in self.layers:
            layers.append(x.dict)
        surfs = {}
        for x in self.surfs:
            surfs[x] = self.surfs[x].dict
        d = OrderedDict()
        d["layers"] = (layers,)
        d["surfs"] = (surfs,)
        d["tags"] = (self.tags,)
        d["clips"] = (self.clips,)
        d["images"] = (self.images,)
        pprint(d)

    def resolve_clips(self):
        for c_id in self.clips:
            cwd = os.getcwd()

            orig_path = self.clips[c_id]["orig_path"]
            imagefile = os.path.basename(orig_path)
            dirpath = os.path.dirname(self.filename)
            os.chdir(dirpath)

            search_paths = []
            for spath in self.search_paths:
                spath = re.sub("dirpath", "", spath)
                spath = dirpath + spath
                search_paths.append(spath)

            files = [orig_path]
            for search_path in search_paths:
                files.extend(glob("{0}/{1}".format(search_path, imagefile)))

            ifile = None
            for f in files:
                if self.absfilepath:
                    y = os.path.abspath(f)
                else:
                    y = os.path.relpath(f)

                if os.path.isfile(y):
                    ifile = y
                    if ifile not in self.images:
                        self.images.append(ifile)
                    continue
            if None is ifile and not self.allow_missing_images:
                raise lwoNoImageFoundException(
                    "No valid image found for path: {} {}".format(
                        orig_path, search_paths
                    )
                )

            os.chdir(cwd)
            self.clips[c_id]["new_path"] = ifile

    def validate_lwo(self):
        self.resolve_clips()
        for surf_key in self.surfs:
            surf_data = self.surfs[surf_key]
            for textures_type in surf_data.textures.keys():
                for texture in surf_data.textures[textures_type]:
                    ci = texture.clipid
                    if ci not in self.clips.keys():
                        print(f"WARNING in material {surf_data.name}")
                        print(f"\tci={ci}, not present in self.clips.keys():")
                        # pprint(self.clips)
                        self.clips[ci] = {"new_path": None}
                    texture.clip = self.clips[ci]
