import struct
import chunk

from .lwoBase import LWOBase, _obj_layer, _obj_surf, _surf_texture, _surf_position


class LWO2(LWOBase):
    """Read version 2 file, LW 6+."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_types = [b"LWO2"]
        self.last_pols_count = 0
        self.just_read_bones = False

    def read_vx(self):
        """Read a variable-length index."""
        pointdata = self.sbytes[self.offset : self.offset + 4]
        if 0 == len(pointdata):
            self.error("Incomplete lwo file, no more valid points: {self.filename}")
        if pointdata[0] != 255:
            index = pointdata[0] * 256 + pointdata[1]
            size = 2
        else:
            index = pointdata[1] * 65536 + pointdata[2] * 256 + pointdata[3]
            size = 4
        self.offset += size
        return index

    def read_clip(self):
        """Read texture clip path"""
        self.sbytes = self.bytes2()
        (c_id, ) = self.unpack(">L")
        
        self.offset += 6
        orig_path = self.read_lwostring()
        self.clips[c_id] = orig_path

    def read_layr(self):
        """Read the object's layer data."""
        self.sbytes = self.bytes2()
        new_layr = _obj_layer()
        new_layr.index, flags = self.unpack(">HH")

        if flags > 0 and not self.ch.load_hidden:
            return False

        self.info("Reading Object Layer")
        pivot = self.unpack(">fff")
        # Swap Y and Z to match Blender's pitch.
        new_layr.pivot = [pivot[0], pivot[2], pivot[1]]
        layr_name = self.read_lwostring()

        if layr_name:
            new_layr.name = layr_name
        else:
            new_layr.name = f"Layer {new_layr.index + 1}"

        if len(self.sbytes) == self.offset + 2:
            (new_layr.parent_index, ) = self.unpack(">h")

        self.layers.append(new_layr)

    def read_weightmap(self):
        """Read a weight map's values."""
        self.sbytes = self.bytes2()
        self.offset += 2
        name = self.read_lwostring()
        weights = []

        while self.offset < len(self.sbytes):
            pnt_id = self.read_vx()
            (value,) = self.unpack(">f")
            weights.append([pnt_id, value])

        self.layers[-1].wmaps[name] = weights

    def read_morph(self, is_abs):
        """Read an endomorph's relative or absolute displacement values."""
        self.sbytes = self.bytes2()
        self.offset += 2
        name = self.read_lwostring()
        deltas = []

        while self.offset < len(self.sbytes):
            pnt_id = self.read_vx()
            pos = self.unpack(">fff")
            pnt = self.layers[-1].pnts[pnt_id]

            if is_abs:
                deltas.append([pnt_id, pos[0], pos[2], pos[1]])
            else:
                # Swap the Y and Z to match Blender's pitch.
                deltas.append(
                    [pnt_id, pnt[0] + pos[0], pnt[1] + pos[2], pnt[2] + pos[1]]
                )

            self.layers[-1].morphs[name] = deltas

    def read_colmap(self):
        """Read the RGB or RGBA color map."""
        self.sbytes = self.bytes2()
        (dia,) = self.unpack(">H")
        name = self.read_lwostring()
        colors = {}

        if dia == 3:
            while self.offset < len(self.sbytes):
                pnt_id = self.read_vx()
                col = self.unpack(">fff")
                colors[pnt_id] = (col[0], col[1], col[2])
        elif dia == 4:
            while self.offset < len(self.sbytes):
                pnt_id = self.read_vx()
                col = self.unpack(">ffff")
                colors[pnt_id] = (col[0], col[1], col[2])

        if name in self.layers[-1].colmaps:
            if "PointMap" in self.layers[-1].colmaps[name]:
                self.layers[-1].colmaps[name]["PointMap"].update(colors)
            else:
                self.layers[-1].colmaps[name]["PointMap"] = colors
        else:
            self.layers[-1].colmaps[name] = dict(PointMap=colors)

    def read_normmap(self):
        """Read vertex normal maps."""
        self.sbytes = self.bytes2()
        self.offset += 2
        name = self.read_lwostring()
        vnorms = {}

        while self.offset < len(self.sbytes):
            pnt_id = self.read_vx()
            norm = self.unpack(">fff")
            vnorms[pnt_id] = [norm[0], norm[2], norm[1]]

        self.layers[-1].vnorms = vnorms

    def read_color_vmad(self):
        """Read the Discontinuous (per-polygon) RGB values."""
        self.sbytes = self.bytes2()
        (dia,) = self.unpack(">H")
        name = self.read_lwostring()
        colors = {}
        abs_pid = len(self.layers[-1].pols) - self.last_pols_count

        if dia == 3:
            while self.offset < len(self.sbytes):
                pnt_id = self.read_vx()
                pol_id = self.read_vx()

                # The PolyID in a VMAD can be relative, this offsets it.
                pol_id += abs_pid
                col = self.unpack(">fff")
                if pol_id in colors:
                    colors[pol_id][pnt_id] = (col[0], col[1], col[2])
                else:
                    colors[pol_id] = dict({pnt_id: (col[0], col[1], col[2])})
        elif dia == 4:
            while self.offset < len(self.sbytes):
                pnt_id = self.read_vx()
                pol_id = self.read_vx()

                pol_id += abs_pid
                col = self.unpack(">ffff")
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

    def read_uvmap(self):
        """Read the simple UV coord values."""
        self.sbytes = self.bytes2()
        self.offset += 2
        name = self.read_lwostring()
        uv_coords = {}

        while self.offset < len(self.sbytes):
            pnt_id = self.read_vx()
            pos = self.unpack(">ff")
            uv_coords[pnt_id] = (pos[0], pos[1])

        if name in self.layers[-1].uvmaps_vmap:
            if "PointMap" in self.layers[-1].uvmaps_vmap[name]:
                self.layers[-1].uvmaps_vmap[name]["PointMap"].update(uv_coords)
            else:
                self.layers[-1].uvmaps_vmap[name]["PointMap"] = uv_coords
        else:
            self.layers[-1].uvmaps_vmap[name] = dict(PointMap=uv_coords)

    def read_uv_vmad(self):
        """Read the Discontinuous (per-polygon) uv values."""
        self.sbytes = self.bytes2()
        self.offset += 2
        name = self.read_lwostring()
        uv_coords = {}
        abs_pid = len(self.layers[-1].pols) - self.last_pols_count

        while self.offset < len(self.sbytes):
            pnt_id = self.read_vx()
            pol_id = self.read_vx()

            pol_id += abs_pid
            pos = self.unpack(">ff")
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

    def read_weight_vmad(self):
        """Read the VMAD Weight values."""
        self.sbytes = self.bytes2()
        self.offset += 2
        name = self.read_lwostring()
        if name != "Edge Weight":
            return  # We just want the Catmull-Clark edge weights

        # Some info: LW stores a face's points in a clock-wize order (with the
        # normal pointing at you). This gives edges a 'direction' which is used
        # when it comes to storing CC edge weight values. The weight is given
        # to the point preceding the edge that the weight belongs to.
        while self.offset < len(self.sbytes):
            pnt_id = self.read_vx()
            pol_id = self.read_vx()
            (weight,) = struct.unpack(">f")

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

            self.layers[-1].edge_weights[f"{second_pnt} {pnt_id}"] = weight

    def read_normal_vmad(self):
        """Read the VMAD Split Vertex Normals"""
        self.sbytes = self.bytes2()
        self.offset += 2
        name = self.read_lwostring()
        lnorms = {}

        while self.offset < len(self.sbytes):
            pnt_id = self.read_vx()
            pol_id = self.read_vx()
            norm = self.unpack(">fff")
            if not (pol_id in lnorms.keys()):
                lnorms[pol_id] = []
            lnorms[pol_id].append([pnt_id, norm[0], norm[2], norm[1]])

        self.info(f"LENGTH {len(lnorms.keys())}")
        self.layers[-1].lnorms = lnorms

    def read_pols(self):
        """Read the layer's polygons, each one is just a list of point indexes."""
        self.info(f"    Reading Layer ({self.layers[-1].name}) Polygons")
        self.sbytes = self.bytes2()
        pols_count = len(self.sbytes)
        old_pols_count = len(self.layers[-1].pols)

        while self.offset < pols_count:
            (pnts_count,) = self.unpack(">H")
            all_face_pnts = []
            for j in range(pnts_count):
                face_pnt = self.read_vx()
                all_face_pnts.append(face_pnt)
            all_face_pnts.reverse()  # correct normals

            self.layers[-1].pols.append(all_face_pnts)

        self.last_pols_count = len(self.layers[-1].pols) - old_pols_count

    def read_bones(self):
        """Read the layer's skelegons."""
        self.info(f"    Reading Layer ({self.layers[-1].name}) Bones")
        self.sbytes = self.bytes2()

        while self.offset < len(self.sbytes):
            (pnts_count,) = self.unpack(">H")
            all_bone_pnts = []
            for j in range(pnts_count):
                bone_pnt = self.read_vx()
                all_bone_pnts.append(bone_pnt)

            self.layers[-1].bones.append(all_bone_pnts)

    def read_bone_tags(self, type):
        """Read the bone name or roll tags."""
        self.sbytes = self.bytes2()

        if "BONE" == type:
            bone_dict = self.layers[-1].bone_names
        elif "BNUP" == type:
            bone_dict = self.layers[-1].bone_rolls
        else:
            return

        while self.offset < len(self.sbytes):
            pid = self.read_vx()
            (tid,) = self.unpack(">H")
            bone_dict[pid] = self.tags[tid]

    def read_position(self, length):
        p = _surf_position()

        slength = self.offset + length
        while self.offset < slength:
            b = self.read_lwohead()

            if b"CNTR" == b.name:
                p.cntr = self.unpack(">fffh")
            elif b"SIZE" == b.name:
                p.size = self.unpack(">fffh")
            elif b"ROTA" == b.name:
                p.rota = self.unpack(">fffh" )
            elif b"FALL" == b.name:
                p.fall = self.unpack(">hfffh")
            elif b"OREF" == b.name:
                p.oref = self.read_lwostring()
            elif b"CSYS" == b.name:
                (p.csys,) = self.unpack(">h")
            self.offset = b.skip
        return p

    def read_texture(self, length):
        texture = _surf_texture()
        
        slength = self.offset + length
        while self.offset < slength:
            b = self.read_lwohead()
            
            if b"TMAP" == b.name:
                texture.position = self.read_position(b.length)
            elif b"CHAN" == b.name:
                (texture.channel,) = self.unpack("4s")
                texture.channel = texture.channel.decode("ascii")
            elif b"OPAC" == b.name:
                (texture.opactype,) = self.unpack(">H")
                (texture.opac,) = self.unpack(">f")
            elif b"ENAB" == b.name:
                (texture.enab,) = self.unpack(">H")
            elif b"IMAG" == b.name:
                (texture.clipid,) = self.unpack(">H")
            elif b"PROJ" == b.name:
                (texture.projection,) = self.unpack(">H")
            elif b"VMAP" == b.name:
                texture.uvname = self.read_lwostring()
            elif b"FUNC" == b.name:  # This is the procedural
                texture.func = self.read_lwostring()
            elif b"NEGA" == b.name:
                (texture.nega,) = self.unpack(">H")
            elif b"AXIS" == b.name:
                (texture.axis,) = self.unpack(">H")
            elif b"WRAP" == b.name: # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")
            elif b"WRPW" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"WRPH" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"AAST" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"PIXB" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"VALU" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"TAMP" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"STCK" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"PNAM" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"INAM" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"GRST" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"GREN" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"GRPT" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"IKEY" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"FKEY" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            elif b"GVER" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubSubBlock: {b.name}")          
            else: # pragma: no cover
                print(self.offset, slength)
                print(self.sbytes[self.offset:], slength)
                self.error(f"Unsupported SubSubBlock: {b.name}")
            
            if not self.offset == b.skip:
                self.debug(f"Skip issue: {b.name} {self.offset} {b.skip}")                                
            self.offset = b.skip

        return texture

    def read_surf_tags(self):
        """Read the list of PolyIDs and tag indexes."""
        self.info(f"    Reading Layer ({self.layers[-1].name}) Surface Assignments")
        self.sbytes = self.bytes2()

        # Read in the PolyID/Surface Index pairs.
        abs_pid = len(self.layers[-1].pols) - self.last_pols_count
        if 0 == len(self.layers[-1].pols):
            return
        if abs_pid < 0:
            raise Exception(
                len(self.layers[-1].pols), self.last_pols_count, self.layers[-1].pols
            )
        while self.offset < len(self.sbytes):
            pid = self.read_vx()
            (sid,) = self.unpack(">H")
            if sid not in self.layers[-1].surf_tags:
                self.layers[-1].surf_tags[sid] = []
            self.layers[-1].surf_tags[sid].append(pid + abs_pid)

    def read_surf(self):
        """Read the object's surface data."""
        self.sbytes = self.bytes2()
        if len(self.surfs) == 0:
            self.info("Reading Object Surfaces")

        surf = _obj_surf()
        name = self.read_lwostring()
        if len(name) != 0:
            surf.name = name

        s_name = self.read_lwostring()
        
        while self.offset < len(self.sbytes) :
            b = self.read_lwohead()
            
            # Now test which subchunk it is.
            if b"COLR" == b.name:
                surf.colr = self.unpack(">fff")
                # Don't bother with any envelopes for now.

            elif b"DIFF" == b.name:
                (surf.diff,) = self.unpack(">f")

            elif b"LUMI" == b.name:
                (surf.lumi,) = self.unpack(">f")

            elif b"SPEC" == b.name:
                (surf.spec,) = self.unpack(">f")

            elif b"REFL" == b.name:
                (surf.refl,) = self.unpack(">f")

            elif b"RBLR" == b.name:
                (surf.rblr,) = self.unpack(">f")

            elif b"TRAN" == b.name:
                (surf.tran,) = self.unpack(">f")

            elif b"RIND" == b.name:
                (surf.rind,) = self.unpack(">f")

            elif b"TBLR" == b.name:
                (surf.tblr,) = self.unpack(">f")

            elif b"TRNL" == b.name:
                (surf.trnl,) = self.unpack(">f")

            elif b"GLOS" == b.name:
                (surf.glos,) = self.unpack(">f")

            elif b"SHRP" == b.name:
                (surf.shrp,) = self.unpack(">f")

            elif b"SMAN" == b.name:
                (s_angle,)   = self.unpack(">f")
                if s_angle > 0.0:
                    surf.smooth = True
            elif b"BUMP" == b.name:
                (surf.bump,) = self.unpack(">f")

            elif b"BLOK" == b.name:
                length = b.length
                (block_type,) = self.unpack("4s")
                (num,) = self.unpack(">H")
                length -= 6
                texture = None
                if (
                       b"IMAP" == block_type
                    or b"PROC" == block_type
                    or b"SHDR" == block_type
                    or b"GRAD" == block_type
                ):
                    self.offset += 2
                    length -= 2
                   
                    # uss-defiant.lwo
                    #xxyy b'PROC\x00*\xff\x00CHAN\x00\x04DI'
                    #xxyy b'PROC\x00,\xff\x80\x00\x00CHAN\x00\x04'
                    if 44 == num:
                        self.offset += 2
                        length -= 2
                        
                    texture = self.read_texture(length)
                else:
                    self.error(f"Unimplemented texture type: {block_type}")
                
                if not texture is None:
                    texture.type = block_type.decode("ascii")
                    if texture.channel not in surf.textures:
                        surf.textures[texture.channel] = []
                    surf.textures[texture.channel].append(texture)
            elif b"VERS" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"NODS" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"GVAL" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"NVSK" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"CLRF" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"CLRH" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"ADTR" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"SIDE" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"RFOP" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"RIMG" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"TIMG" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"TROP" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"ALPH" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"BUF1" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"BUF2" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"BUF3" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"BUF4" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"LINE" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"NORM" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"RFRS" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"VCOL" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"RFLS" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"CMNT" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"FLAG" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"RSAN" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"LCOL" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"LSIZ" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            elif b"TSAN" == b.name:  # pragma: no cover
                self.debug(f"Unimplemented SubChunk: {b.name}")
            else: # pragma: no cover
                self.error(f"Unsupported SubBlock: {b.name}")

            self.offset = b.skip

        self.surfs[surf.name] = surf

    def parse_tags(self):
        chunkname = self.rootchunk.chunkname
        if b"TAGS" == chunkname:
            self.read_tags()
        elif b"LAYR" == chunkname:
            self.read_layr()
        elif b"PNTS" == chunkname:
            self.read_pnts()
        elif b"VMAP" == chunkname:
            vmap_type = self.rootchunk.read(4)

            if vmap_type == b"WGHT":
                self.read_weightmap()
            elif vmap_type == b"MORF":
                self.read_morph(False)
            elif vmap_type == b"SPOT":
                self.read_morph(True)
            elif vmap_type == b"TXUV":
                self.read_uvmap()
            elif vmap_type == b"RGB " or vmap_type == b"RGBA":
                self.read_colmap()
            elif vmap_type == b"NORM":
                self.read_normmap()
            elif vmap_type == b"PICK": # pragma: no cover
                self.debug(f"Unimplemented vmap_type: {vmap_type}")
                self.rootchunk.skip()
            elif vmap_type == b"MBAL": # pragma: no cover
                self.debug(f"Unimplemented vmap_type: {vmap_type}")
                self.rootchunk.skip()
            elif vmap_type == b"MNVW": # pragma: no cover
                self.debug(f"Unimplemented vmap_type: {vmap_type}")
                self.rootchunk.skip()
            else: # pragma: no cover
                self.error(f"Skipping vmap_type: {vmap_type}")
                self.rootchunk.skip()

        elif b"VMAD" == chunkname:
            vmad_type = self.rootchunk.read(4)

            if vmad_type == b"TXUV":
                self.read_uv_vmad()
            elif vmad_type == b"RGB " or vmad_type == b"RGBA":
                self.read_color_vmad()
            elif vmad_type == b"WGHT":
                # We only read the Edge Weight map if it's there.
                self.read_weight_vmad()
            elif vmad_type == b"NORM":
                self.read_normal_vmad()
            elif vmad_type == b"MORF": # pragma: no cover
                self.debug(f"Unimplemented vmad_type: {vmad_type}")
                self.rootchunk.skip()
            elif vmad_type == b"MNVW": # pragma: no cover
                self.debug(f"Unimplemented vmad_type: {vmad_type}")
                self.rootchunk.skip()
            elif vmad_type == b"APSL": # pragma: no cover
                self.debug(f"Unimplemented vmad_type: {vmad_type}")
                self.rootchunk.skip()
            else: # pragma: no cover
                self.error(f"Unsupported vmad_type: {vmad_type}")
                self.rootchunk.skip()

        elif b"POLS" == chunkname:
            face_type = self.rootchunk.read(4)
            self.just_read_bones = False
            # PTCH is LW's Subpatches, SUBD is CatmullClark.
            if (
                face_type == b"FACE" or face_type == b"PTCH" or face_type == b"SUBD"
            ):
                self.read_pols()
                if face_type != b"FACE":
                    self.layers[-1].has_subds = True
            elif face_type == b"BONE":
                self.read_bones()
                self.just_read_bones = True
            elif face_type == b"CURV": # pragma: no cover
                self.debug(f"Unimplemented face_type: {face_type}")
                self.rootchunk.skip()
            elif face_type == b"PTCL": # pragma: no cover
                self.debug(f"Unimplemented face_type: {face_type}")
                self.rootchunk.skip()
            else: # pragma: no cover
                self.error(f"Unsupported face_type: {face_type}")
                self.rootchunk.skip()

        elif b"PTAG" == chunkname:
            (tag_type,) = struct.unpack("4s", self.rootchunk.read(4))
#             if tag_type == b"SURF" and not self.just_read_bones:
#                 # Ignore the surface data if we just read a bones chunk.
#                 self.read_surf_tags()
            if tag_type == b"SURF":
                # Ignore the surface data if we just read a bones chunk.
                self.read_surf_tags()

            elif tag_type == b"BNUP":
                self.read_bone_tags("BNUP")
            elif tag_type == b"BONE":
                self.read_bone_tags("BONE")
            elif tag_type == b"COLR":  # pragma: no cover
                self.debug(f"Unimplemented tag_type: {tag_type}") 
                self.rootchunk.skip()
            elif tag_type == b"PART":   # pragma: no cover
                self.debug(f"Unimplemented tag_type: {tag_type}")
                self.rootchunk.skip()
            
#             elif self.ch.skel_to_arm:
#                 if tag_type == b"BNUP":
#                     self.read_bone_tags("BNUP")
#                 elif tag_type == b"BONE":
#                     self.read_bone_tags("BONE")
#                 else:
#                     self.error(f"Skipping tag: {tag_type}")
#                     self.rootchunk.skip()
#            
#             elif tag_type == b"BNUP":
#                 self.rootchunk.skip()
#             elif tag_type == b"BONE":
#                 self.rootchunk.skip()
            
            elif tag_type == b"BNWT":  # pragma: no cover
                self.debug(f"Unimplemented tag_type: {tag_type}")  
                self.rootchunk.skip()
            elif tag_type == b"SKCL":  # pragma: no cover
                self.debug(f"Unimplemented tag_type: {tag_type}")  
                self.rootchunk.skip()
            elif tag_type == b"SKID":  # pragma: no cover
                self.debug(f"Unimplemented tag_type: {tag_type}")  
                self.rootchunk.skip()
            elif tag_type == b"TXUV":  # pragma: no cover
                self.debug(f"Unimplemented tag_type: {tag_type}")  
                self.rootchunk.skip()
            else:  # pragma: no cover
                self.error(f"Unsupported tag_type: {tag_type}")
                self.rootchunk.skip()
        elif b"FORM" == chunkname:
            #self.read_form()
            (tag_type,) = struct.unpack("4s", self.rootchunk.read(4))
            if tag_type == b"SURF":
                self.read_surf()
            else:
                self.error(f"Unsupported tag_type: {tag_type}")
                self.rootchunk.skip()
        elif b"SURF" == chunkname:
            self.read_surf()
        elif b"CLIP" == chunkname:
            self.read_clip()
        elif b"BBOX" == chunkname:  # pragma: no cover
            self.debug(f"Unimplemented Chunk: {chunkname}")  
            self.rootchunk.skip()
        elif b"VMPA" == chunkname:  # pragma: no cover
            self.debug(f"Unimplemented Chunk: {chunkname}")  
            self.rootchunk.skip()
        elif b"PNTS" == chunkname:  # pragma: no cover
            self.debug(f"Unimplemented Chunk: {chunkname}")  
            self.rootchunk.skip()
        elif b"POLS" == chunkname:  # pragma: no cover
            self.debug(f"Unimplemented Chunk: {chunkname}")  
            self.rootchunk.skip()
        elif b"PTAG" == chunkname:  # pragma: no cover
            self.debug(f"Unimplemented Chunk: {chunkname}")  
            self.rootchunk.skip()
        elif b"ENVL" == chunkname:  # pragma: no cover
            self.debug(f"Unimplemented Chunk: {chunkname}")  
            self.rootchunk.skip()
        else:  # pragma: no cover
            self.error(f"Skipping Chunk: {chunkname}")       
            self.rootchunk.skip()
 
