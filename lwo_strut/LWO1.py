import struct
import chunk

from .lwoBase import LWOBase, _lwo_base, _obj_layer, _obj_surf

class _surf_texture_5(_lwo_base):
    __slots__ = ("id", "image", "X", "Y", "Z")

    def __init__(self):
        self.clipid = id(self)
        self.rev = 5
        self.image = None
        self.X = False
        self.Y = False
        self.Z = False


class LWO1(LWOBase):
    """Read version 1 file, LW < 6."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_types = [b"LWOB", b"LWLO"]

    def read_layr(self):
        """Read the object's layer data."""
        self.sbytes = self.bytes2()
        # XXX: Need to check what these two exactly mean for a LWOB/LWLO file.
        new_layr = _obj_layer()
        new_layr.index, flags = self.unpack(">HH")

        self.info("Reading Object Layer")
        layr_name = self.read_lwostring3()
        
        #offset += name_len

        if name_len > 2 and layr_name != "noname":
            new_layr.name = layr_name
        else:
            new_layr.name = f"Layer {new_layr.index}"

        self.layers.append(new_layr)

    def read_pols(self):
        """
        Read the polygons, each one is just a list of point indexes.
        But it also includes the surface index.
        """
        self.sbytes = self.bytes2()
        self.info(f"    Reading Layer ({self.layers[-1].name}) Polygons")
        old_pols_count = len(self.layers[-1].pols)
        poly = 0

        while self.offset < len(self.sbytes):
            (pnts_count,) = self.unpack(">H")
            all_face_pnts = []
            for j in range(pnts_count):
                (face_pnt,) = self.unpack(">H")
                all_face_pnts.append(face_pnt)
            all_face_pnts.reverse()

            self.layers[-1].pols.append(all_face_pnts)
            (sid,) = self.unpack(">h")
            sid = abs(sid) - 1
            if sid not in self.layers[-1].surf_tags:
                self.layers[-1].surf_tags[sid] = []
            self.layers[-1].surf_tags[sid].append(poly)
            poly += 1

        return len(self.layers[-1].pols) - old_pols_count

    def read_surf(self):
        """Read the object's surface data."""
        self.sbytes = self.bytes2()
        if len(self.surfs) == 0:
            self.info("Reading Object Surfaces 5")

        surf = _obj_surf()
        name = self.read_lwostring3()
        if len(name) != 0:
            surf.name = name

        while self.offset < len(self.sbytes):
            (subchunk_name,) = self.unpack("4s")
            (subchunk_len,) = self.unpack(">H")

            # Now test which subchunk it is.
            if b"COLR" == subchunk_name:
                color = self.unpack(">BBBB")
                surf.colr = [color[0] / 255.0, color[1] / 255.0, color[2] / 255.0]

            elif b"DIFF" == subchunk_name:
                (surf.diff,) = self.unpack(">h")
                surf.diff /= 256.0  # Yes, 256 not 255.

            elif b"LUMI" == subchunk_name:
                (surf.lumi,) = self.unpack(">h")
                surf.lumi /= 256.0

            elif b"SPEC" == subchunk_name:
                (surf.spec,) = self.unpack(">h")
                surf.spec /= 256.0

            elif b"REFL" == subchunk_name:
                (surf.refl,) = self.unpack(">h")
                surf.refl /= 256.0

            elif b"TRAN" == subchunk_name:
                (surf.tran,) = self.unpack(">h")
                surf.tran /= 256.0

            elif b"RIND" == subchunk_name:
                (surf.rind,) = self.unpack(">f")

            elif b"GLOS" == subchunk_name:
                (surf.glos,) = self.unpack(">h")

            elif b"SMAN" == subchunk_name:
                (s_angle,) = self.unpack(">f")
                if s_angle > 0.0:
                    surf.smooth = True

            elif subchunk_name in [b"CTEX", b"DTEX", b"STEX", b"RTEX", b"TTEX", b"BTEX", b"LTEX"]:
                texture = None

            elif b"TIMG" == subchunk_name:
                path = self.read_lwostring3()
                if path == "(none)":
                    continue

                texture = _surf_texture_5()
                self.clips[texture.clipid] = path
               
                if texture.clipid not in surf.textures:
                    surf.textures[texture.clipid] = []
                surf.textures[texture.clipid].append(texture)

            elif b"TFLG" == subchunk_name:
                if texture:
                    (mapping,) = self.unpack(">h")
                    if mapping & 1:
                        texture.X = True
                    elif mapping & 2:
                        texture.Y = True
                    elif mapping & 4:
                        texture.Z = True
            elif b"FLAG" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"VLUM" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"VDIF" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"VSPC" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"VRFL" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"VTRN" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"RFLT" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"ALPH" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TOPC" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TWRP" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TSIZ" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TCTR" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TAAS" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TVAL" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TFP0" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TAMP" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"RIMG" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TCLR" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TFAL" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TVEL" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TREF" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TALP" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"EDGE" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"GLOW" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TIP0" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TFP1" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TFP2" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TFP3" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"SPBF" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"SHDR" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"SDAT" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"IMSQ" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            else:
                self.error(f"Unsupported SubBlock: {subchunk_name}")

            self.offset += subchunk_len

        self.surfs[surf.name] = surf
    
    def parse_tags(self):
        chunkname = self.rootchunk.chunkname
        if b"SRFS" == chunkname:
            self.read_tags()
        elif b"LAYR" == chunkname:
            self.read_layr()
        elif b"PNTS" == chunkname:
            if len(self.layers) == 0:
                # LWOB files have no LAYR chunk to set this up.
                nlayer = _obj_layer()
                nlayer.name = "Layer 1"
                self.layers.append(nlayer)
            self.read_pnts()
        elif b"POLS" == chunkname:
            self.last_pols_count = self.read_pols()
        elif b"PCHS" == chunkname:
            self.last_pols_count = self.read_pols()
            self.layers[-1].has_subds = True
        elif b"PTAG" == chunkname:
            (tag_type,) = struct.unpack("4s", self.rootchunk.read(4))
            self.rootchunk.skip()
        elif b"SURF" == chunkname:
            self.read_surf()
        else:
            # For Debugging \/.
            # if handle_layer:
            self.error(f"Skipping Chunk: {chunkname}")
            self.rootchunk.skip()
