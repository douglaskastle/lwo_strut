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

    CMAP = {
        b'COLR' : ">BBBB",
        b'DIFF' : ">h",
        b'LUMI' : ">h",
        b'SPEC' : ">h",
        b'REFL' : ">h",
        b'TRAN' : ">h",
        b'RIND' : ">f",
        b'GLOS' : ">h",
        b'SMAN' : ">f",
        b'CTEX' : None,
        b'DTEX' : None,
        b'STEX' : None,
        b'RTEX' : None,
        b'TTEX' : None,
        b'BTEX' : None,
        b'LTEX' : None,
        b'TIMG' : None,
        b'TFLG' : ">h",
        b'FLAG' : None,
        b'VLUM' : None,
        b'VDIF' : None,
        b'VSPC' : None,
        b'VRFL' : None,
        b'VTRN' : None,
        b'RFLT' : None,
        b'ALPH' : None,
        b'TOPC' : None,
        b'TWRP' : None,
        b'TSIZ' : None,
        b'TCTR' : None,
        b'TAAS' : None,
        b'TVAL' : None,
        b'TFP0' : None,
        b'TAMP' : None,
        b'RIMG' : None,
        b'TCLR' : None,
        b'TFAL' : None,
        b'TVEL' : None,
        b'TREF' : None,
        b'TALP' : None,
        b'EDGE' : None,
        b'GLOW' : None,
        b'TIP0' : None,
        b'TFP1' : None,
        b'TFP2' : None,
        b'TFP3' : None,
        b'SPBF' : None,
        b'SHDR' : None,
        b'SDAT' : None,
        b'IMSQ' : None,
    }


    """Read version 1 file, LW < 6."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_types = [b"LWOB", b"LWLO"]

    def read_layr(self):
        """Read the object's layer data."""
        # XXX: Need to check what these two exactly mean for a LWOB/LWLO file.
        new_layr = _obj_layer()
        new_layr.index, flags = self.unpack(">HH")

        self.info("Reading Object Layer")
        layr_name = self.read_lwostring()
        
        if self.chunklength > 2 and layr_name != "noname":
            new_layr.name = layr_name
        else:
            new_layr.name = f"Layer {new_layr.index}"

        self.layers.append(new_layr)

    def read_pols(self):
        """
        Read the polygons, each one is just a list of point indexes.
        But it also includes the surface index.
        """
        self.info(f"    Reading Layer ({self.layers[-1].name}) Polygons")
        old_pols_count = len(self.layers[-1].pols)
        poly = 0

        while self.offset < len(self.bytes):
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
        if len(self.surfs) == 0:
            self.info("Reading Object Surfaces 5")

        surf = _obj_surf()
        name = self.read_lwostring()
        if len(name) != 0:
            surf.name = name

        while self.offset < len(self.bytes):
            b = self.read_block()

            # Now test which subchunk it is.
            if b"COLR" == b.name:
                color = b.values
                surf.colr = [color[0] / 255.0, color[1] / 255.0, color[2] / 255.0]

            elif b"DIFF" == b.name:
                surf.diff = b.values[0]
                surf.diff /= 256.0  # Yes, 256 not 255.

            elif b"LUMI" == b.name:
                surf.lumi = b.values[0]
                surf.lumi /= 256.0

            elif b"SPEC" == b.name:
                surf.spec = b.values[0]
                surf.spec /= 256.0

            elif b"REFL" == b.name:
                surf.refl = b.values[0]
                surf.refl /= 256.0

            elif b"TRAN" == b.name:
                surf.tran = b.values[0]
                surf.tran /= 256.0

            elif b"RIND" == b.name:
                surf.rind = b.values[0]

            elif b"GLOS" == b.name:
                surf.glos = b.values[0]
                surf.glos /= 256.0

            elif b"SMAN" == b.name:
                s_angle = b.values[0]
                if s_angle > 0.0:
                    surf.smooth = True

            elif b.name in [b"CTEX", b"DTEX", b"STEX", b"RTEX", b"TTEX", b"BTEX", b"LTEX"]:
                texture = None

            elif b"TIMG" == b.name:
                path = self.read_lwostring()
                if path == "(none)":
                    continue

                texture = _surf_texture_5()
                self.clips[texture.clipid] = path
               
                if texture.clipid not in surf.textures:
                    surf.textures[texture.clipid] = []
                surf.textures[texture.clipid].append(texture)

            elif b"TFLG" == b.name:
                if texture:
                    mapping = b.values[0]
                    if mapping & 1:
                        texture.X = True
                    elif mapping & 2:
                        texture.Y = True
                    elif mapping & 4:
                        texture.Z = True
            elif b"FLAG" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"VLUM" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"VDIF" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"VSPC" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"VRFL" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"VTRN" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"RFLT" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"ALPH" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TOPC" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TWRP" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TSIZ" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TCTR" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TAAS" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TVAL" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TFP0" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TAMP" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"RIMG" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TCLR" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TFAL" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TVEL" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TREF" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TALP" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"EDGE" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"GLOW" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TIP0" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TFP1" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TFP2" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"TFP3" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"SPBF" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"SHDR" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"SDAT" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            elif b"IMSQ" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubBlock: {b.name}")  
            else: # pragma: no cover
                self.error(f"Unsupported SubBlock: {b.name}")

            self.offset = b.skip

        self.surfs[surf.name] = surf
    
    def mapping_tags(self):
        if b"SRFS" == self.chunkname:
            self.read_tags()
        elif b"LAYR" == self.chunkname:
            self.read_layr()
        elif b"PNTS" == self.chunkname:
            if len(self.layers) == 0:
                # LWOB files have no LAYR chunk to set this up.
                nlayer = _obj_layer()
                nlayer.name = "Layer 1"
                self.layers.append(nlayer)
            self.read_pnts()
        elif b"POLS" == self.chunkname:
            self.last_pols_count = self.read_pols()
        elif b"PCHS" == self.chunkname:
            self.last_pols_count = self.read_pols()
            self.layers[-1].has_subds = True
        elif b"PTAG" == self.chunkname:
            #(tag_type = ("4s")
            self.rootchunk.skip()
        elif b"SURF" == self.chunkname:
            self.read_surf()
        else:
            # For Debugging \/.
            # if handle_layer:
            self.error(f"Skipping Chunk: {self.chunkname}")
            self.rootchunk.skip()
