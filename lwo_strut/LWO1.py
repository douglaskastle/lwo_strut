import struct
import chunk

from .lwoBase import LWOBase, _lwo_base, _obj_layer, _obj_surf

#, _obj_surf, _surf_texture, _surf_position
class _surf_texture_5(_lwo_base):
    __slots__ = ("id", "image", "X", "Y", "Z")

    def __init__(self):
        self.id = id(self)
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

    def read_layr(self, layr_bytes):
        """Read the object's layer data."""
        # XXX: Need to check what these two exactly mean for a LWOB/LWLO file.
        new_layr = _obj_layer()
        new_layr.index, flags = struct.unpack(">HH", layr_bytes[0:4])

        self.info("Reading Object Layer")
        offset = 4
        layr_name, name_len = self.read_lwostring(layr_bytes[offset:])
        offset += name_len

        if name_len > 2 and layr_name != "noname":
            new_layr.name = layr_name
        else:
            new_layr.name = f"Layer {new_layr.index}"

        self.layers.append(new_layr)

    def read_pols(self, pol_bytes):
        """
        Read the polygons, each one is just a list of point indexes.
        But it also includes the surface index.
        """
        self.info(f"    Reading Layer ({self.layers[-1].name}) Polygons")
        offset = 0
        chunk_len = len(pol_bytes)
        old_pols_count = len(self.layers[-1].pols)
        poly = 0

        while offset < chunk_len:
            (pnts_count,) = struct.unpack(">H", pol_bytes[offset : offset + 2])
            offset += 2
            all_face_pnts = []
            for j in range(pnts_count):
                (face_pnt,) = struct.unpack(">H", pol_bytes[offset : offset + 2])
                offset += 2
                all_face_pnts.append(face_pnt)
            all_face_pnts.reverse()

            self.layers[-1].pols.append(all_face_pnts)
            (sid,) = struct.unpack(">h", pol_bytes[offset : offset + 2])
            offset += 2
            sid = abs(sid) - 1
            if sid not in self.layers[-1].surf_tags:
                self.layers[-1].surf_tags[sid] = []
            self.layers[-1].surf_tags[sid].append(poly)
            poly += 1

        return len(self.layers[-1].pols) - old_pols_count

    def read_surf(self, surf_bytes, dirpath=None):
        """Read the object's surface data."""
        if len(self.surfs) == 0:
            self.info("Reading Object Surfaces 5")

        surf = _obj_surf()
        name, name_len = self.read_lwostring(surf_bytes)
        if len(name) != 0:
            surf.name = name

        offset = name_len
        chunk_len = len(surf_bytes)
        while offset < chunk_len:
            (subchunk_name,) = struct.unpack("4s", surf_bytes[offset : offset + 4])
            offset += 4
            (subchunk_len,) = struct.unpack(">H", surf_bytes[offset : offset + 2])
            offset += 2

            # Now test which subchunk it is.
            if subchunk_name == b"COLR":
                color = struct.unpack(">BBBB", surf_bytes[offset : offset + 4])
                surf.colr = [color[0] / 255.0, color[1] / 255.0, color[2] / 255.0]

            elif subchunk_name == b"DIFF":
                (surf.diff,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
                surf.diff /= 256.0  # Yes, 256 not 255.

            elif subchunk_name == b"LUMI":
                (surf.lumi,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
                surf.lumi /= 256.0

            elif subchunk_name == b"SPEC":
                (surf.spec,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
                surf.spec /= 256.0

            elif subchunk_name == b"REFL":
                (surf.refl,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
                surf.refl /= 256.0

            elif subchunk_name == b"TRAN":
                (surf.tran,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
                surf.tran /= 256.0

            elif subchunk_name == b"RIND":
                (surf.rind,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

            elif subchunk_name == b"GLOS":
                (surf.glos,) = struct.unpack(">h", surf_bytes[offset : offset + 2])

            elif subchunk_name == b"SMAN":
                (s_angle,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
                if s_angle > 0.0:
                    surf.smooth = True

            elif subchunk_name in [b"CTEX", b"DTEX", b"STEX", b"RTEX", b"TTEX", b"BTEX", b"LTEX"]:
                texture = None

            elif subchunk_name == b"TIMG":
                path, path_len = self.read_lwostring(surf_bytes[offset:])
                if path == "(none)":
                    continue

                texture = _surf_texture_5()
                self.clips[texture.id] = path
                surf.textures_5.append(texture)
                surf.textures[texture.id] = texture

            elif subchunk_name == b"TFLG":
                if texture:
                    (mapping,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
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
                self.l.debug(f"Unimplemented SubBlock: {subchunk_name}")

            offset += subchunk_len

        self.surfs[surf.name] = surf
    
    def read_lwo(self):
        """Read version 1 file, LW < 6."""
        self.f = open(self.filename, "rb")
        try:
            header, chunk_size, chunk_name = struct.unpack(">4s1L4s", self.f.read(12))
        except:
            self.error(f"Error parsing file header! Filename {self.filename}")
            self.f.close()
            return
        
        if not chunk_name in self.file_types:
            raise Exception(f"Incorrect file type: {chunk_name} not in {self.file_types}")
        self.file_type = chunk_name

        self.last_pols_count = 0
        self.info(f"Importing LWO: {self.filename}\nLWO v1 Format")

        while True:
            try:
                rootchunk = chunk.Chunk(self.f)
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
                # if handle_layer:
                self.error(f"Skipping Chunk: {rootchunk.chunkname}")
                rootchunk.skip()
        del self.f
