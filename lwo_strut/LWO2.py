import struct
import chunk

from .lwoBase import LWOBase, _obj_layer, _obj_surf, _surf_texture, _surf_position


class LWO2(LWOBase):
    """Read version 2 file, LW 6+."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_types = [b"LWO2"]

    def read_clip(self, clip_bytes):
        """Read texture clip path"""
        c_id = struct.unpack(">L", clip_bytes[0:4])[0]
        orig_path, path_len = self.read_lwostring(clip_bytes[10:])
        self.clips[c_id] = orig_path

    def read_vx(self, pointdata):
        """Read a variable-length index."""
        if pointdata[0] != 255:
            index = pointdata[0] * 256 + pointdata[1]
            size = 2
        else:
            index = pointdata[1] * 65536 + pointdata[2] * 256 + pointdata[3]
            size = 4

        return index, size

    def read_layr(self, layr_bytes):
        """Read the object's layer data."""
        new_layr = _obj_layer()
        new_layr.index, flags = struct.unpack(">HH", layr_bytes[0:4])

        if flags > 0 and not self.ch.load_hidden:
            return False

        self.info("Reading Object Layer")
        offset = 4
        pivot = struct.unpack(">fff", layr_bytes[offset : offset + 12])
        # Swap Y and Z to match Blender's pitch.
        new_layr.pivot = [pivot[0], pivot[2], pivot[1]]
        offset += 12
        layr_name, name_len = self.read_lwostring(layr_bytes[offset:])
        offset += name_len

        if layr_name:
            new_layr.name = layr_name
        else:
            new_layr.name = f"Layer {new_layr.index + 1}"

        if len(layr_bytes) == offset + 2:
            (new_layr.parent_index,) = struct.unpack(">h", layr_bytes[offset : offset + 2])

        self.layers.append(new_layr)
        return True

    def read_weightmap(self, weight_bytes):
        """Read a weight map's values."""
        chunk_len = len(weight_bytes)
        offset = 2
        name, name_len = self.read_lwostring(weight_bytes[offset:])
        offset += name_len
        weights = []

        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(weight_bytes[offset : offset + 4])
            offset += pnt_id_len
            (value,) = struct.unpack(">f", weight_bytes[offset : offset + 4])
            offset += 4
            weights.append([pnt_id, value])

        self.layers[-1].wmaps[name] = weights

    def read_morph(self, morph_bytes, is_abs):
        """Read an endomorph's relative or absolute displacement values."""
        chunk_len = len(morph_bytes)
        offset = 2
        name, name_len = self.read_lwostring(morph_bytes[offset:])
        offset += name_len
        deltas = []

        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(morph_bytes[offset : offset + 4])
            offset += pnt_id_len
            pos = struct.unpack(">fff", morph_bytes[offset : offset + 12])
            offset += 12
            pnt = self.layers[-1].pnts[pnt_id]

            if is_abs:
                deltas.append([pnt_id, pos[0], pos[2], pos[1]])
            else:
                # Swap the Y and Z to match Blender's pitch.
                deltas.append([pnt_id, pnt[0] + pos[0], pnt[1] + pos[2], pnt[2] + pos[1]])

            self.layers[-1].morphs[name] = deltas
    
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
                pnt_id, pnt_id_len = self.read_vx(col_bytes[offset : offset + 4])
                offset += pnt_id_len
                col = struct.unpack(">fff", col_bytes[offset : offset + 12])
                offset += 12
                colors[pnt_id] = (col[0], col[1], col[2])
        elif dia == 4:
            while offset < chunk_len:
                pnt_id, pnt_id_len = self.read_vx(col_bytes[offset : offset + 4])
                offset += pnt_id_len
                col = struct.unpack(">ffff", col_bytes[offset : offset + 16])
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
        name, name_len = self.self.read_lwostring(norm_bytes[offset:])
        offset += name_len
        vnorms = {}

        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(norm_bytes[offset : offset + 4])
            offset += pnt_id_len
            norm = struct.unpack(">fff", norm_bytes[offset : offset + 12])
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
                pnt_id, pnt_id_len = self.read_vx(col_bytes[offset : offset + 4])
                offset += pnt_id_len
                pol_id, pol_id_len = self.read_vx(col_bytes[offset : offset + 4])
                offset += pol_id_len
    
                # The PolyID in a VMAD can be relative, this offsets it.
                pol_id += abs_pid
                col = struct.unpack(">fff", col_bytes[offset : offset + 12])
                offset += 12
                if pol_id in colors:
                    colors[pol_id][pnt_id] = (col[0], col[1], col[2])
                else:
                    colors[pol_id] = dict({pnt_id: (col[0], col[1], col[2])})
        elif dia == 4:
            while offset < chunk_len:
                pnt_id, pnt_id_len = self.read_vx(col_bytes[offset : offset + 4])
                offset += pnt_id_len
                pol_id, pol_id_len = self.read_vx(col_bytes[offset : offset + 4])
                offset += pol_id_len
    
                pol_id += abs_pid
                col = struct.unpack(">ffff", col_bytes[offset : offset + 16])
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
            pnt_id, pnt_id_len = self.read_vx(uv_bytes[offset : offset + 4])
            offset += pnt_id_len
            pos = struct.unpack(">ff", uv_bytes[offset : offset + 8])
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
            pnt_id, pnt_id_len = self.read_vx(uv_bytes[offset : offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = self.read_vx(uv_bytes[offset : offset + 4])
            offset += pol_id_len
    
            pol_id += abs_pid
            pos = struct.unpack(">ff", uv_bytes[offset : offset + 8])
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
            pnt_id, pnt_id_len = self.read_vx(ew_bytes[offset : offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = self.read_vx(ew_bytes[offset : offset + 4])
            offset += pol_id_len
            (weight,) = struct.unpack(">f", ew_bytes[offset : offset + 4])
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
    
            self.layers[-1].edge_weights[f"{second_pnt} {pnt_id}"] = weight
    
    
    def read_normal_vmad(self, norm_bytes):
        """Read the VMAD Split Vertex Normals"""
        chunk_len = len(norm_bytes)
        offset = 2
        name, name_len = self.read_lwostring(norm_bytes[offset:])
        lnorms = {}
        offset += name_len
    
        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(norm_bytes[offset : offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = self.read_vx(norm_bytes[offset : offset + 4])
            offset += pol_id_len
            norm = struct.unpack(">fff", norm_bytes[offset : offset + 12])
            offset += 12
            if not (pol_id in lnorms.keys()):
                lnorms[pol_id] = []
            lnorms[pol_id].append([pnt_id, norm[0], norm[2], norm[1]])
    
        self.info(f"LENGTH {len(lnorms.keys())}")
        self.layers[-1].lnorms = lnorms
    
    
    def read_pols(self, pol_bytes):
        """Read the layer's polygons, each one is just a list of point indexes."""
        self.info(f"    Reading Layer ({self.layers[-1].name}) Polygons")
        offset = 0
        pols_count = len(pol_bytes)
        old_pols_count = len(self.layers[-1].pols)
    
        while offset < pols_count:
            (pnts_count,) = struct.unpack(">H", pol_bytes[offset : offset + 2])
            offset += 2
            all_face_pnts = []
            for j in range(pnts_count):
                face_pnt, data_size = self.read_vx(pol_bytes[offset : offset + 4])
                offset += data_size
                all_face_pnts.append(face_pnt)
            all_face_pnts.reverse()  # correct normals
    
            self.layers[-1].pols.append(all_face_pnts)
    
        return len(self.layers[-1].pols) - old_pols_count
    
    
    def read_bones(self, bone_bytes):
        """Read the layer's skelegons."""
        self.info(f"    Reading Layer ({self.layers[-1].name}) Bones")
        offset = 0
        bones_count = len(bone_bytes)
    
        while offset < bones_count:
            (pnts_count,) = struct.unpack(">H", bone_bytes[offset : offset + 2])
            offset += 2
            all_bone_pnts = []
            for j in range(pnts_count):
                bone_pnt, data_size = self.read_vx(bone_bytes[offset : offset + 4])
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
            pid, pid_len = self.read_vx(tag_bytes[offset : offset + 4])
            offset += pid_len
            (tid,) = struct.unpack(">H", tag_bytes[offset : offset + 2])
            offset += 2
            bone_dict[pid] = self.tags[tid]
    
    
    def read_surf_tags(self, tag_bytes, last_pols_count):
        """Read the list of PolyIDs and tag indexes."""
        self.info(f"    Reading Layer ({self.layers[-1].name}) Surface Assignments")
        offset = 0
        chunk_len = len(tag_bytes)
    
        # Read in the PolyID/Surface Index pairs.
        abs_pid = len(self.layers[-1].pols) - last_pols_count
        if 0 == len(self.layers[-1].pols):
            return
        if abs_pid < 0:
            raise Exception(len(self.layers[-1].pols), last_pols_count, self.layers[-1].pols)
        while offset < chunk_len:
            pid, pid_len = self.read_vx(tag_bytes[offset : offset + 4])
            offset += pid_len
            (sid,) = struct.unpack(">H", tag_bytes[offset : offset + 2])
            offset += 2
            if sid not in self.layers[-1].surf_tags:
                self.layers[-1].surf_tags[sid] = []
            self.layers[-1].surf_tags[sid].append(pid + abs_pid)
    
    def read_position(self, surf_bytes, offset, subchunk_len):
        p = _surf_position()
        suboffset = 0
        
        while suboffset < subchunk_len:
            (subsubchunk_name,) = struct.unpack(
                "4s", surf_bytes[offset + suboffset: offset + suboffset + 4]
            )
            suboffset += 4        
            (slen,) = struct.unpack(
                ">H", surf_bytes[offset + suboffset : offset + suboffset + 2]
            )
            suboffset += 2
        
            if b"CNTR" == subsubchunk_name:
                p.cntr = struct.unpack(
                    ">fffh", surf_bytes[offset + suboffset : offset + suboffset + slen]
                )
            elif b"SIZE" == subsubchunk_name:
                p.size = struct.unpack(
                    ">fffh", surf_bytes[offset + suboffset : offset + suboffset + slen]
                )
            elif b"ROTA" == subsubchunk_name:
                p.rota = struct.unpack(
                    ">fffh", surf_bytes[offset + suboffset : offset + suboffset + slen]
                )
            elif b"FALL" == subsubchunk_name:
                p.fall = struct.unpack(
                    ">hfffh", surf_bytes[offset + suboffset : offset + suboffset + slen]
                )
            elif b"OREF" == subsubchunk_name:
                p.oref, name_len = self.read_lwostring(surf_bytes[offset + suboffset :])
            elif b"CSYS" == subsubchunk_name:
                (p.csys,) = struct.unpack(
                    ">h", surf_bytes[offset + suboffset : offset + suboffset + slen]
                )
            suboffset += slen
        return p
    
    def read_texture(self, surf_bytes, offset, subchunk_len, debug=False):
        texture = _surf_texture()
        ordinal, ord_len = self.read_lwostring(surf_bytes[offset + 4 :])
        suboffset = 6 + ord_len
        while suboffset < subchunk_len:
            (subsubchunk_name,) = struct.unpack(
                "4s", surf_bytes[offset + suboffset : offset + suboffset + 4]
            )
            suboffset += 4
            (subsubchunk_len,) = struct.unpack(
                ">H", surf_bytes[offset + suboffset : offset + suboffset + 2]
            )
            suboffset += 2
            if subsubchunk_name == b"TMAP":
                texture.position = self.read_position(surf_bytes, (offset + suboffset), subsubchunk_len)
            elif subsubchunk_name == b"CHAN":
                (texture.channel,) = struct.unpack(
                    "4s", surf_bytes[offset + suboffset : offset + suboffset + 4],
                )
                texture.channel = texture.channel.decode("ascii")
            elif subsubchunk_name == b"OPAC":
                (texture.opactype,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
                )
                (texture.opac,) = struct.unpack(
                    ">f", surf_bytes[offset + suboffset + 2 : offset + suboffset + 6],
                )
            elif subsubchunk_name == b"ENAB":
                (texture.enab,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
                )
            elif subsubchunk_name == b"IMAG":
                (texture.clipid,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
                )
            elif subsubchunk_name == b"PROJ":
                (texture.projection,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
                )
            elif subsubchunk_name == b"VMAP":
                texture.uvname, name_len = self.read_lwostring(surf_bytes[offset + suboffset :])
            elif subsubchunk_name == b"FUNC":  # This is the procedural
                texture.func, name_len = self.read_lwostring(surf_bytes[offset + suboffset :])
            elif subsubchunk_name == b"NEGA":
                (texture.nega,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
                )
            elif subsubchunk_name == b"AXIS":
                (texture.axis,) = struct.unpack(
                    ">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
                )
            elif subsubchunk_name == b"WRAP":
                self.l.debug(f"SubSubBlock: {subsubchunk_name} {subchunk_len}")
            elif subsubchunk_name == b"WRPW":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"WRPH":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"AAST":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"PIXB":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"VALU":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"TAMP":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"STCK":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"PNAM":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"INAM":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"GRST":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"GREN":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"GRPT":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"IKEY":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            elif subsubchunk_name == b"FKEY":
                self.l.debug(f"SubSubBlock: {subsubchunk_name}")
            else:
                self.error(f"Unimplemented SubSubBlock: {subsubchunk_name}")
                raise
            suboffset += subsubchunk_len
        
        return texture
    
    
    def read_surf(self, surf_bytes):
        """Read the object's surface data."""
        if len(self.surfs) == 0:
            self.info("Reading Object Surfaces")
    
        surf = _obj_surf()
        name, name_len = self.read_lwostring(surf_bytes)
        if len(name) != 0:
            surf.name = name
    
        # We have to read this, but we won't use it...yet.
        s_name, s_name_len = self.read_lwostring(surf_bytes[name_len:])
        offset = name_len + s_name_len
        block_size = len(surf_bytes)
        while offset < block_size:
            (subchunk_name,) = struct.unpack("4s", surf_bytes[offset : offset + 4])
            offset += 4
            (subchunk_len,) = struct.unpack(">H", surf_bytes[offset : offset + 2])
            offset += 2
    
            # Now test which subchunk it is.
            if subchunk_name == b"COLR":
                surf.colr = struct.unpack(">fff", surf_bytes[offset : offset + 12])
                # Don't bother with any envelopes for now.
    
            elif subchunk_name == b"DIFF":
                (surf.diff,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"LUMI":
                (surf.lumi,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"SPEC":
                (surf.spec,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"REFL":
                (surf.refl,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"RBLR":
                (surf.rblr,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"TRAN":
                (surf.tran,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"RIND":
                (surf.rind,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"TBLR":
                (surf.tblr,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"TRNL":
                (surf.trnl,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"GLOS":
                (surf.glos,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"SHRP":
                (surf.shrp,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"SMAN":
                (s_angle,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
                # self.l.debug(s_angle)
                if s_angle > 0.0:
                    surf.smooth = True
            elif subchunk_name == b"BUMP":
                (surf.bump,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
    
            elif subchunk_name == b"BLOK":
                (block_type,) = struct.unpack("4s", surf_bytes[offset : offset + 4])
                texture = None
                if block_type == b"IMAP" or block_type == b"PROC" \
                or block_type == b"SHDR" or block_type == b"GRAD":
                    # self.l.debug(surf.name, block_type)
                    texture = self.read_texture(surf_bytes, offset, subchunk_len)
                else:
                    self.error(f"Unimplemented texture type: {block_type}")
                if None is not texture:
                    texture.type = block_type.decode("ascii")
                    if texture.channel not in surf.textures.keys():
                        surf.textures[texture.channel] = []
                    surf.textures[texture.channel].append(texture)
            elif subchunk_name == b"VERS":
                pass
            elif subchunk_name == b"NODS":
                pass
            elif subchunk_name == b"GVAL":
                pass
            elif subchunk_name == b"NVSK":
                pass
            elif subchunk_name == b"CLRF":
                pass
            elif subchunk_name == b"CLRH":
                pass
            elif subchunk_name == b"ADTR":
                pass
            elif subchunk_name == b"SIDE":
                pass
            elif subchunk_name == b"RFOP":
                pass
            elif subchunk_name == b"RIMG":
                pass
            elif subchunk_name == b"TIMG":
                pass
            elif subchunk_name == b"TROP":
                pass
            elif subchunk_name == b"ALPH":
                pass
            elif subchunk_name == b"BUF1":
                pass
            elif subchunk_name == b"BUF2":
                pass
            elif subchunk_name == b"BUF3":
                pass
            elif subchunk_name == b"BUF4":
                pass
            elif subchunk_name == b"LINE":
                pass
            elif subchunk_name == b"NORM":
                pass
            else:
                self.error(f"Unimplemented SubBlock: {subchunk_name}")
    
            offset += subchunk_len
    
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
            raise Exception(f"Incorrect file type: {chunk_name} not in {self.file_types}")
        self.file_type = chunk_name
            
        self.info(f"Importing LWO: {self.filename}")
        self.info(f"{self.file_type.decode('ascii')} Format")

        self.handle_layer = True
        self.last_pols_count = 0
        self.just_read_bones = False
        while True:
            try:
                rootchunk = chunk.Chunk(self.f)
            except EOFError:
                break

            if rootchunk.chunkname == b"TAGS":
                self.read_tags(rootchunk.read())
            elif rootchunk.chunkname == b"LAYR":
                self.handle_layer = self.read_layr(rootchunk.read())
            elif rootchunk.chunkname == b"PNTS" and self.handle_layer:
                self.read_pnts(rootchunk.read())
            elif rootchunk.chunkname == b"VMAP" and self.handle_layer:
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
                    self.l.debug(f"Skipping vmap_type: {vmap_type}")
                    rootchunk.skip()

            elif rootchunk.chunkname == b"VMAD" and self.handle_layer:
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
                    self.l.debug(f"Skipping vmad_type: {vmad_type}")
                    rootchunk.skip()

            elif rootchunk.chunkname == b"POLS" and self.handle_layer:
                face_type = rootchunk.read(4)
                self.just_read_bones = False
                # PTCH is LW's Subpatches, SUBD is CatmullClark.
                if (
                    face_type == b"FACE" or face_type == b"PTCH" or face_type == b"SUBD"
                ) and self.handle_layer:
                    self.last_pols_count = self.read_pols(rootchunk.read())
                    if face_type != b"FACE":
                        self.layers[-1].has_subds = True
                elif face_type == b"BONE" and self.handle_layer:
                    self.read_bones(rootchunk.read())
                    self.just_read_bones = True
                else:
                    self.l.debug(f"Skipping face_type: {face_type}")
                    rootchunk.skip()

            elif rootchunk.chunkname == b"PTAG" and self.handle_layer:
                (tag_type,) = struct.unpack("4s", rootchunk.read(4))
                if tag_type == b"SURF" and not self.just_read_bones:
                    # Ignore the surface data if we just read a bones chunk.
                    self.read_surf_tags(rootchunk.read(), self.last_pols_count)

                elif self.ch.skel_to_arm:
                    if tag_type == b"BNUP":
                        self.read_bone_tags(rootchunk.read(), "BNUP")
                    elif tag_type == b"BONE":
                        self.read_bone_tags(rootchunk.read(), "BONE")
                    elif tag_type == b"PART":
                        rootchunk.skip()  # SKIPPING
                    elif tag_type == b"COLR":
                        rootchunk.skip()  # SKIPPING
                    else:
                        self.l.debug(f"Skipping tag: {tag_type}")
                        rootchunk.skip()
                else:
                    self.l.debug(f"Skipping tag_type: {tag_type}")
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
                # if self.handle_layer:
                self.l.debug(f"Skipping Chunk: {rootchunk.chunkname}")
                rootchunk.skip()
        del self.f
