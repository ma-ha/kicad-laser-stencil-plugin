from __future__ import absolute_import

import io
import json
import logging
import os
import re
import sys
import math
from datetime import datetime

import wx

from . import units
from .config import Config
from ..dialog import SettingsDialog
from ..ecad.common import EcadParser, Component
from ..errors import ParsingException


class Logger(object):

    def __init__(self, cli=False):
        self.cli = cli
        self.logger = logging.getLogger('LaserStencil')
        self.logger.setLevel(logging.INFO)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
                "%(asctime)-15s %(levelname)s %(message)s")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def info(self, *args):
        if self.cli:
            self.logger.info(*args)

    def error(self, msg):
        if self.cli:
            self.logger.error(msg)
        else:
            wx.MessageBox(msg)

    def warn(self, msg):
        if self.cli:
            self.logger.warn(msg)
        else:
            wx.LogWarning(msg)


log = None  # type: Logger or None

# -----------------------------------------------------------------------------

def skip_component(m, config):
    # type: (Component, Config) -> bool
    # skip blacklisted components
    ref_prefix = re.findall('^[A-Z]*', m.ref)[0]
    if m.ref in config.component_blacklist:
        return True
    if ref_prefix + '*' in config.component_blacklist:
        return True

    if config.blacklist_empty_val and m.val in ['', '~']:
        return True

    # skip virtual components if needed
    if config.blacklist_virtual and m.attr == 'Virtual':
        return True

    # skip components with dnp field not empty
    # if config.dnp_field \
    #         and config.dnp_field in m.extra_fields \
    #         and m.extra_fields[config.dnp_field]:
    #     return True

    # skip components with wrong variant field
    # if config.board_variant_field and config.board_variant_whitelist:
    #     ref_variant = m.extra_fields.get(config.board_variant_field, '')
    #     if ref_variant not in config.board_variant_whitelist:
    #         return True

    # if config.board_variant_field and config.board_variant_blacklist:
    #     ref_variant = m.extra_fields.get(config.board_variant_field, '')
    #     if ref_variant and ref_variant in config.board_variant_blacklist:
    #         return True

    return False

# -----------------------------------------------------------------------------

def generate_stencil(pcb_footprints, config):
    # type: (list, Config) -> dict
    """
    Generate BOM from pcb layout.
    :param pcb_footprints: list of footprints on the pcb
    :param config: Config object
    :param extra_data: Extra fields data
    :return: dict of BOM tables (qty, value, footprint, refs) and dnp components
    """

    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c)
                for c in re.split('([0-9]+)', key)]

    def natural_sort(l):
        """
        Natural sort for strings containing numbers
        """

        return sorted(l, key=lambda r: (alphanum_key(r[0]), r[1]))

    # build grouped part list
    skipped_components = []
    part_groups = {}
    for i, f in enumerate(pcb_footprints):
        if skip_component(f, config):
            skipped_components.append(i)
            continue

        # group part refs by value and footprint
        norm_value, unit = units.componentValue(f.val)

        extras = []
        # if config.extra_fields:
        #     extras = [f.extra_fields.get(ef, '')
        #               for ef in config.extra_fields]

        group_key = (norm_value, unit, tuple(extras), f.footprint, f.attr)
        valrefs = part_groups.setdefault(group_key, [f.val, []])
        valrefs[1].append((f.ref, i))

    # build bom table, sort refs
    bom_table = []
    for (_, _, extras, footprint, _), valrefs in part_groups.items():
        bom_row = (
            len(valrefs[1]), valrefs[0], footprint,
            natural_sort(valrefs[1]), extras)
        bom_table.append(bom_row)

    # sort table by reference prefix, footprint and quantity
    def sort_func(row):
        qty, _, fp, rf, e = row
        prefix = re.findall('^[A-Z]*', rf[0][0])[0]
        if prefix in config.component_sort_order:
            ref_ord = config.component_sort_order.index(prefix)
        else:
            ref_ord = config.component_sort_order.index('~')
        return ref_ord, e, fp, -qty, alphanum_key(rf[0][0])

    # if '~' not in config.component_sort_order:
    #     config.component_sort_order.append('~')
    # bom_table = sorted(bom_table, key=sort_func)

    result = {
        'both': bom_table,
        'skipped': skipped_components
    }

    for layer in ['F', 'B']:
        filtered_table = []
        for row in bom_table:
            filtered_refs = [ref for ref in row[3]
                             if pcb_footprints[ref[1]].layer == layer]
            if filtered_refs:
                filtered_table.append((len(filtered_refs), row[1],
                                       row[2], filtered_refs, row[4]))

        # result[layer] = sorted(filtered_table, key=sort_func)
        result[layer] = filtered_table

    return result

# -----------------------------------------------------------------------------

def open_file(filename):
    import subprocess
    try:
        if sys.platform.startswith('win'):
            os.startfile(filename)
        elif sys.platform.startswith('darwin'):
            subprocess.call(('open', filename))
        elif sys.platform.startswith('linux'):
            subprocess.call(('xdg-open', filename))
    except OSError as oe:
        log.warn('Failed to open browser: {}'.format(oe.message))


def process_substitutions( gcode_name_format, pcb_file_name, metadata, pcb_side ):
    # type: (str, str, dict)->str
    name = gcode_name_format.replace('%f', os.path.splitext(pcb_file_name)[0])
    name = name.replace('%p', metadata['title'])
    name = name.replace('%c', metadata['company'])
    name = name.replace('%r', metadata['revision'])
    name = name.replace('%d', metadata['date'].replace(':', '-'))
    now = datetime.now()
    name = name.replace('%D', now.strftime('%Y-%m-%d'))
    name = name.replace('%T', now.strftime('%H-%M-%S'))
    # sanitize the name to avoid characters illegal in file systems
    name = name.replace('\\', '/')
    name = re.sub(r'[?%*:|"<>]', '_', name)
    return name + '_' + pcb_side + '.gcode'

# -----------------------------------------------------------------------------

def round_floats(o, precision):
    if isinstance(o, float):
        return round(o, precision)
    if isinstance(o, dict):
        return {k: round_floats(v, precision) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [round_floats(x, precision) for x in o]
    return o

# -----------------------------------------------------------------------------

def searchNearestNextEdge( sortEdges, px, py ):
  nextEdge = 0
  reverse = False
  if len( sortEdges ) > 0:
    dist = abs( px - sortEdges[0]["startx"] ) + abs( py - sortEdges[0]["starty"] )
    i = 0
    for someEdge in sortEdges:
      dist2 = abs( px - someEdge["startx"] ) + abs( py - someEdge["startx"] )
      if dist2 < dist:
        nextEdge = i
        dist = dist2
        reverse = False
      dist3 = abs( px - someEdge["endx"] ) + abs( py - someEdge["endy"] )
      if dist3 < dist:
        nextEdge = i
        dist = dist3
        reverse = True
      i += 1
  return nextEdge, reverse, dist


def gcode_border( pcbdata, config, pcb_side ):
  gcode = ''
  intensity = str( config.laser_border_intensity )
  speed     = " F" + str( config.laser_border_speed )

  minx = pcbdata["edges_bbox"]["minx"] 
  miny = pcbdata["edges_bbox"]["miny"]
  maxx = pcbdata["edges_bbox"]["maxx"] 
  maxy = pcbdata["edges_bbox"]["maxy"]
  def cX( x ):
    if pcb_side is "F":
      return str( round_floats( x - minx, 3 ) )
    else:
      return str( round_floats( maxx - x, 3 ) )
    
  def cY( y ):
    if pcb_side is "F":
      return str( round_floats( y - miny, 3 ) )
    else: 
      return str( round_floats( maxy - y, 3 ) )

  # prepare optimization of laser path
  sortEdges = []
  for edge in pcbdata["edges"]:
    newEdge = { "startx": edge["start"][0], "starty": edge["start"][1], "endx": edge["end"][0], "endy": edge["end"][1] }
    sortEdges.append( newEdge )

  nextEdge = 0
  reverse = False
  px = 0
  py = 0
  while len( sortEdges ) > 0:
    nextEdge, reverse, d = searchNearestNextEdge( sortEdges, px, py )
    edge = sortEdges.pop( nextEdge )
    gcode += '( n='+str(nextEdge)+ ' d='+str(d)+' )\n'
    if reverse :
      gcode += 'G00 X'+cX(edge["endx"])   + ' Y'+cY(edge["endy"])   + '\n'
      gcode += 'M03 S'+intensity +'\n'
      gcode += 'G01 X'+cX(edge["startx"]) + ' Y'+cY(edge["starty"]) + speed +'\n'
      gcode += 'M05 S0\n\n'
      px = edge["startx"]
      py = edge["starty"]
    else:
      gcode += 'G00 X'+cX(edge["startx"]) + ' Y'+cY(edge["starty"]) + '\n'
      gcode += 'M03 S'+intensity +'\n'
      gcode += 'G01 X'+cX(edge["endx"])   + ' Y'+cY(edge["endy"])   + speed +'\n'
      gcode += 'M05 S0\n\n'
      px = edge["endx"]
      py = edge["endy"]
      
  # for edge in pcbdata["edges"]:
  #   eStart = edge["start"]
  #   gcode += 'G00 X'+cX(eStart[0])+ ' Y'+cY(eStart[1]) +'\n'
  #   eEnd = edge["end"]
  #   gcode += 'M03 S'+laser_intensity +'\n'
  #   gcode += 'G01 X'+cX(eEnd[0])+ ' Y'+cY(eEnd[1]) +' F100\n'
  #   gcode += 'M05 S0\n\n'
  return gcode


def gcode_border_sim( pcbdata, pcb_side ):
  gcode = ''
  minx = pcbdata["edges_bbox"]["minx"] 
  miny = pcbdata["edges_bbox"]["miny"]
  maxx = pcbdata["edges_bbox"]["maxx"] 
  maxy = pcbdata["edges_bbox"]["maxy"]
  def cX( x ):
    return str( round_floats( maxx - x, 3 ) )
    
  def cY( y ):
    if pcb_side is "F":
      return str( round_floats( y - miny, 3 ) )
    else: 
      return str( round_floats( maxy - y, 3 ) )

  # prepare optimization of laser path
  sortEdges = []
  for edge in pcbdata["edges"]:
    newEdge = { "startx": edge["start"][0], "starty": edge["start"][1], "endx": edge["end"][0], "endy": edge["end"][1] }
    sortEdges.append( newEdge )

  nextEdge = 0
  reverse = False
  px = 0
  py = 0
  while len( sortEdges ) > 0:
    nextEdge, reverse, d = searchNearestNextEdge( sortEdges, px, py )
    edge = sortEdges.pop( nextEdge )
    
    if reverse :
      gcode += 'G00 X'+cX(edge["endx"])   + ' Y'+cY(edge["endy"])   +'\n'
      gcode += 'G00 X'+cX(edge["startx"]) + ' Y'+cY(edge["starty"]) +'\n'
      px = edge["startx"]
      py = edge["starty"]
    else:
      gcode += 'G00 X'+cX(edge["startx"]) + ' Y'+cY(edge["starty"]) +'\n'
      gcode += 'G00 X'+cX(edge["endx"])   + ' Y'+cY(edge["endy"])   +'\n'
      px = edge["endx"]
      py = edge["endy"]

   
  # for edge in pcbdata["edges"]:
  #   eStart = edge["start"]
  #   gcode += 'G00 X'+cX(eStart[0])+ ' Y'+cY(eStart[1]) +'\n'
  #   eEnd = edge["end"]
  #   gcode += 'G00 X'+cX(eEnd[0])+ ' Y'+cY(eEnd[1]) +'\n'
  return gcode

# -----------------------------------------------------------------------------

def gcode_pads( pcbdata, config, pcb_side ):
  gcode = ''
  passes    = config.laser_pad_passes
  intensity = str( config.laser_pad_intensity )
  x_w =  float( config.laser_x_width ) / 2
  y_w =  float( config.laser_y_width ) / 2
  speed = " F" + str( config.laser_speed )
  minx = pcbdata["edges_bbox"]["minx"] 
  miny = pcbdata["edges_bbox"]["miny"]
  maxx = pcbdata["edges_bbox"]["maxx"]  
  maxy = pcbdata["edges_bbox"]["maxy"]

  def cX( x0, dx, dy, a ):
    x = math.cos( a ) * dx - math.sin( a ) * dy 
    # gcode += '('+str(x)
    if x < 0:
      x += x_w 
    else:
      x -= x_w 
    x += x0 
    # gcode += ' '+str(x)+')'
    if pcb_side is "F":
      return str( round_floats( x - minx, 3 ) )
    else:
      return str( round_floats( maxx - x, 3 ) )
    
  def cY( y0, dx, dy, a ):
    y = math.sin( a ) * dx + math.cos( a ) * dy 
    if y < 0:
      y += y_w 
    else:
      y -= y_w 
    y += y0
    if pcb_side is "F":
      return str( round_floats( y - miny, 3 ) )
    else: 
      return str( round_floats( maxy - y, 3 ) )
  
  def gCd( pad ):
    px = pad["px"]
    py = pad["py"]
    sx = pad["sx"]
    sy = pad["sy"]
    a  = pad["angle"]
    gcode = 'G00 X'+cX( px, -sx,  sy, a )+ ' Y'+cY( py, -sx,  sy, a ) +'\n'
    gcode += 'M03 S'+intensity +'\n'
    for passCnt in range(passes):
      gcode += 'G01 X'+cX( px, -sx,  sy, a )+ ' Y'+cY( py, -sx,  sy, a ) + speed+'\n'
      gcode += 'G01 X'+cX( px,  sx,  sy, a )+ ' Y'+cY( py,  sx,  sy, a ) +'\n'
      gcode += 'G01 X'+cX( px,  sx, -sy, a )+ ' Y'+cY( py,  sx, -sy, a ) +'\n'
      gcode += 'G01 X'+cX( px, -sx, -sy, a )+ ' Y'+cY( py, -sx, -sy, a ) +'\n'
    gcode += 'M05 S0\n'
    return gcode

  sortFps = []
  for footprint in pcbdata["footprints"]:
    if footprint["layer"] is pcb_side:
      if footprint["ref"] in config.component_blacklist:
        gcode += "( BLACKLIST FOOTPRINT: "+ footprint["ref"] + " skipped )\n"         
      else:
        fpPads = []
        x = 0
        y = 0
        for pad in footprint["pads"]:
          if pad["type"] is "smd":
            if pad["shape"] is "roundrect" or pad["shape"] is "rect" :
              # gcode += "(" + repr (pad ) + ")\n"
              newPad = { 'ref': footprint["ref"], 
                'px': pad["pos"][0], 'py': pad["pos"][1], 
                'sx': pad["size"][0] / 2, 'sy': pad["size"][1] / 2, 
                'angle': math.radians( pad["angle"] ) }
              x =  pad["pos"][0]
              y =  pad["pos"][1]
              fpPads.append( newPad )
            else:
              gcode += "  ( "+footprint["ref"] +" / ignored shape: " + pad["shape"] + ")\n"
          else:
            gcode += "  ( "+footprint["ref"] +" / ignored type: " + pad["type"] + ")\n"
       
        if len( fpPads ) > 0:
          newFP = { 'ref': footprint["ref"], 'px': x, 'py': y, 'pads': fpPads }
          sortFps.append( newFP )

  nextFP = 0
  while len( sortFps ) > 0:
    fp = sortFps.pop( nextFP )
    px = fp["px"]
    py = fp["py"]
    gcode += "\n( "+fp["ref"] +"  " + str(px) +" / "+ str(py) + ")\n"

    for padNo in range(0, len(fp["pads"]) ):
      if padNo % 2 == 0: # even 
        gcode += "( "+fp["ref"] +" pad #" + str(padNo) + ")\n"
        gcode += gCd( fp["pads"][padNo] )
    for padNo in range(0, len(fp["pads"]) ):
      if padNo % 2 != 0: # odd
        gcode += "( "+fp["ref"] +" pad #" + str(padNo) + ")\n"
        gcode += gCd( fp["pads"][padNo] )

    if len( sortFps ) > 0:
      # find next nearest footprint
      nextFP = 0
      minD = abs( px - sortFps[0]["px"] ) + abs( py - sortFps[0]["py"] )
      i = 0
      for aFP in sortFps:
        dist2 = abs( px - aFP["px"] ) + abs( py - aFP["py"] )
        if dist2 < minD:
          nextFP = i
          minD = dist2
        i += 1
      #   gcode += "( "+str(i) +"  d "+str(dist2)+ " "+ aFP["ref"] +" )\n"
      # gcode += "(==> d "+str(minD)+ " "+str(nextFP)+" )\n"

  return gcode

# -----------------------------------------------------------------------------

def generate_file(pcb_file_dir, pcb_file_name, pcbdata, config, pcb_side):
    def get_file_content(file_name):
        path = os.path.join(os.path.dirname(__file__), "..", "gcode", file_name)
        if not os.path.exists(path):
            return ""
        with io.open(path, 'r', encoding='utf-8') as f:
            return f.read()

    if os.path.isabs(config.gcode_dest_dir):
        gcode_file_dir = config.gcode_dest_dir
    else:
        gcode_file_dir = os.path.join(pcb_file_dir, config.gcode_dest_dir)
    gcode_file_name = process_substitutions( config.gcode_name_format, pcb_file_name, pcbdata['metadata'], pcb_side)
    gcode_file_name = os.path.join(gcode_file_dir, gcode_file_name)
    gcode_file_dir = os.path.dirname(gcode_file_name)
    if not os.path.isdir(gcode_file_dir):
        os.makedirs(gcode_file_dir)

    log.info("Wrting GCode")
    # config_js = "var config = " + config.get_html_config()

    gcode = get_file_content("stencil.gcode")
    gcode = gcode.replace('(**BORDER**)', gcode_border( pcbdata, config, pcb_side ) )
    gcode = gcode.replace('(**PADS**)',   gcode_pads( pcbdata, config, pcb_side ) )

    # gcode = gcode.replace('(**BORDER**)', repr( pcbdata ) )
    
    with io.open(gcode_file_name, 'wt', encoding='utf-8') as gcode_file:
        gcode_file.write(gcode)

    log.info("Created file %s", gcode_file_name)
    return gcode_file_name

# -----------------------------------------------------------------------------

def generate_edge_file(pcb_file_dir, pcb_file_name, pcbdata, config, pcb_side):
    def get_file_content(file_name):
        path = os.path.join(os.path.dirname(__file__), "..", "gcode", file_name)
        if not os.path.exists(path):
            return ""
        with io.open(path, 'r', encoding='utf-8') as f:
            return f.read()

    if os.path.isabs(config.gcode_dest_dir):
        gcode_file_dir = config.gcode_dest_dir
    else:
        gcode_file_dir = os.path.join(pcb_file_dir, config.gcode_dest_dir)
    gcode_file_name = process_substitutions( config.gcode_name_format, pcb_file_name, pcbdata['metadata'], pcb_side+'_Edge' )
    gcode_file_name = os.path.join(gcode_file_dir, gcode_file_name)
    gcode_file_dir = os.path.dirname(gcode_file_name)
    if not os.path.isdir(gcode_file_dir):
        os.makedirs(gcode_file_dir)

    log.info("Wrting GCode")
    # config_js = "var config = " + config.get_gcode_config()

    gcode = get_file_content("stencil.gcode")
    gcode = gcode.replace('(**PADS**)', '' )
    gcode = gcode.replace('(**BORDER**)', gcode_border_sim( pcbdata, pcb_side ) )
    
    with io.open(gcode_file_name, 'wt', encoding='utf-8') as gcode_file:
        gcode_file.write(gcode)

    log.info("Created file %s", gcode_file_name)
    return gcode_file_name

# -----------------------------------------------------------------------------

def main(parser, config, logger):
    # type: (EcadParser, Config, Logger) -> None
    global log
    log = logger
    pcb_file_name = os.path.basename(parser.file_name)
    pcb_file_dir = os.path.dirname(parser.file_name)

    pcbdata, components = parser.parse()
    if not pcbdata and not components:
        raise ParsingException('Parsing failed.')

    pcbdata["bom"] = generate_stencil(components, config)
    pcbdata["laser_stencil_version"] = config.version

    # build BOM
    gcode_file = generate_file(pcb_file_dir, pcb_file_name, pcbdata, config, "F")

    # if config.open_browser:
    #     logger.info("Opening file in browser")
    #     open_file(gcode_file)

    # build BOM
    gcode_file = generate_file(pcb_file_dir, pcb_file_name, pcbdata, config, "B")

    # if config.open_browser:
    #     logger.info("Opening file in browser")
    #     open_file(gcode_file)

    gcode_file = generate_edge_file(pcb_file_dir, pcb_file_name, pcbdata, config, "F")
    gcode_file = generate_edge_file(pcb_file_dir, pcb_file_name, pcbdata, config, "B")


# -----------------------------------------------------------------------------

def run_with_dialog(parser, config, logger):
    # type: (EcadParser, Config, Logger) -> None
    def save_config(dialog_panel):
        config.set_from_dialog(dialog_panel)
        config.save()

    config.load_from_ini()
    dlg = SettingsDialog(
            extra_data_func=parser.extra_data_func,
            config_save_func=save_config,
            file_name_format_hint=config.FILE_NAME_FORMAT_HINT,
            version=config.version
    )
    try:
        config.netlist_initial_directory = os.path.dirname(parser.file_name)
        # extra_data_file = parser.latest_extra_data(
        #         extra_dirs=[config.gcode_dest_dir])
        # if extra_data_file is not None:
        #     dlg.set_extra_data_path(extra_data_file)
        config.transfer_to_dialog(dlg.panel)
        if dlg.ShowModal() == wx.ID_OK:
            config.set_from_dialog(dlg.panel)
            main(parser, config, logger)
    finally:
        dlg.Destroy()
