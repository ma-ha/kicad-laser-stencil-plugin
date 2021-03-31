"""Config object"""

import argparse
import os
import re

from wx import FileConfig

from .. import dialog


class Config:
    FILE_NAME_FORMAT_HINT = (
        'Output file name format supports substitutions:\n'
        '\n'
        '    %f : original pcb file name without extension.\n'
        '    %p : pcb/project title from pcb metadata.\n'
        '    %c : company from pcb metadata.\n'
        '    %r : revision from pcb metadata.\n'
        '    %d : pcb date from metadata if available, '
        'file modification date otherwise.\n'
        '    %D : generation date.\n'
        '    %T : generation time.\n'
        '\n'
        'Extension .gcode will be added automatically.'
    )  # type: str

    # Helper constants
    config_file = os.path.join(os.path.dirname(__file__), '..', 'stencil-config.ini')

    # Defaults
    gcode_dest_dir = 'stencil/'  # This is relative to pcb file directory
    gcode_name_format = 'Stencil'
    component_blacklist = []
    blacklist_virtual = True
    blacklist_empty_val = False
    laser_x_width = 0.08
    laser_y_width = 0.08
    laser_pad_passes = 6
    laser_pad_intensity = 255
    laser_speed = 100
    laser_border_intensity = 20
    laser_border_speed = 200
    
    @staticmethod
    def _split(s):
        """Splits string by ',' and drops empty strings from resulting array."""
        return [a.replace('\\,', ',') for a in re.split(r'(?<!\\),', s) if a]

    @staticmethod
    def _join(lst):
        return ','.join([s.replace(',', '\\,') for s in lst])

    def __init__(self, version):
        self.version = version

    def load_from_ini(self):
        """Init from config file if it exists."""
        if not os.path.isfile(self.config_file):
            return
        f = FileConfig(localFilename=self.config_file)

        f.SetPath('/general')
        self.gcode_dest_dir = f.Read('gcode_dest_dir', self.gcode_dest_dir)
        self.gcode_name_format = f.Read('gcode_name_format', self.gcode_name_format)

        self.laser_x_width          = f.Read('laser_x_width', str( self.laser_x_width) )
        self.laser_y_width          = f.Read('laser_x_width', str( self.laser_y_width) )
        self.laser_pad_passes       = f.Read('laser_pad_passes', str( self.laser_pad_passes) )
        self.laser_pad_intensity    = f.Read('laser_pad_intensity', str( self.laser_pad_intensity) )
        self.laser_border_intensity = f.Read('laser_border_intensity', str( self.laser_border_intensity) )
        self.laser_speed            = f.Read('laser_speed', str( self.laser_speed) )
        self.laser_border_speed     = f.Read('laser_border_speed', str( self.laser_border_speed) )
        self.component_blacklist    = self._split(f.Read( 'component_blacklist',','.join(self.component_blacklist)))
        self.blacklist_virtual      = f.ReadBool('blacklist_virtual', self.blacklist_virtual)
        self.blacklist_empty_val    = f.ReadBool( 'blacklist_empty_val', self.blacklist_empty_val)


    def save(self):
        f = FileConfig(localFilename=self.config_file)
        f.SetPath('/general')
        gcode_dest_dir = self.gcode_dest_dir
        if gcode_dest_dir.startswith(self.netlist_initial_directory):
            gcode_dest_dir = os.path.relpath(gcode_dest_dir, self.netlist_initial_directory)
        f.Write('gcode_dest_dir', gcode_dest_dir)
        f.Write('gcode_name_format', self.gcode_name_format)
        f.Write('laser_x_width',          str( self.laser_x_width) )
        f.Write('laser_y_width',          str( self.laser_y_width) )
        f.Write('laser_pad_passes',       str( self.laser_pad_passes) )
        f.Write('laser_pad_intensity',    str( self.laser_pad_intensity) )
        f.Write('laser_border_intensity', str( self.laser_border_intensity) )
        f.Write('laser_speed',            str( self.laser_speed) )
        f.Write('laser_border_speed',     str( self.laser_border_speed) )
        f.Write('component_blacklist',    ','.join(self.component_blacklist))
        f.WriteBool('blacklist_virtual',  self.blacklist_virtual)
        f.WriteBool('blacklist_empty_val',self.blacklist_empty_val)
        f.Flush()

    def set_from_dialog(self, dlg):
        self.gcode_dest_dir = dlg.general.bomDirPicker.Path
        self.gcode_name_format = dlg.general.fileNameFormatTextControl.Value
        self.component_blacklist = dlg.general.blacklistBox.GetItems()
        self.blacklist_virtual   = dlg.general.blacklistVirtualCheckbox.IsChecked()
        self.blacklist_empty_val = dlg.general.blacklistEmptyValCheckbox.IsChecked()
        # self.laser_x_width       = int( dlg.general.laserXWidthTextControl.Value )
        # self.laser_y_width       = int( dlg.general.laserYWidthTextControl.Value )
        self.laser_pad_intensity = int( dlg.general.laserPowerTextControl.Value )
        self.laser_pad_passes    = int( dlg.general.laserPassesTextControl.Value )
        self.laser_speed         = int( dlg.general.laserSpeedTextControl.Value )
        # self.laser_border_speed  = int( dlg.general.laserBorderSpeedTextControl.Value )
        self.laser_border_intensity = int( dlg.general.borderPowerTextControl.Value )

    def transfer_to_dialog(self, dlg):
        import os.path
        if os.path.isabs(self.gcode_dest_dir):
            dlg.general.bomDirPicker.Path = self.gcode_dest_dir
        else:
            dlg.general.bomDirPicker.Path = os.path.join(self.netlist_initial_directory, self.gcode_dest_dir)
        dlg.general.fileNameFormatTextControl.Value = self.gcode_name_format
        dlg.general.blacklistBox.SetItems(self.component_blacklist)
        dlg.general.blacklistVirtualCheckbox.Value = self.blacklist_virtual
        # dlg.general.laserXWidthTextControl.Value  = str( self.laser_x_width )
        # dlg.general.laserXYidthTextControl.Value  = str( self.laser_y_width )
        dlg.general.laserPowerTextControl.Value  = str( self.laser_pad_intensity )
        dlg.general.laserPassesTextControl.Value = str( self.laser_pad_passes )
        dlg.general.laserSpeedTextControl.Value  = str( self.laser_speed )
        # dlg.general.laserBorderSpeedTextControl.Value  = str( self.laser_border_speed )
        dlg.general.borderPowerTextControl.Value = str( self.laser_border_intensity )
