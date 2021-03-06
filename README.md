# G-Code Laser Stencil Generator for KiCAD PCBs
 
KiCAD Pcbnew plugin to generat laser cutter G-Code files for solder paste stencils

![Screenshot](screen.png)

Generated G-Code files:

* `<NAME>_F_Edge.gcode`: Front side stencil border (laser off): for adjusting the position of the stencil
* `<NAME>_F.gcode`: Front side stencil containing border markings and footprint cuttings
* `<NAME>_B_Edge.gcode`: Back side stencil border
* `<NAME>_B.gcode`: Back side stencil cutting

The plugin is based on the awesome [iBom plugin](https://github.com/openscopeproject/InteractiveHtmlBom) code.

# Installation

Copy the whole `laser-stencil` folder (including all files and sub-folders) into your KiCAD plugin directory.

* Windows
  * `%APPDATA%\kicad\scripting\plugins`
  * (e.g. `C:\Users\[USERNAME]\AppData\Roaming\kicad\scripting\plugins`)

* Linux
  * `~/.kicad/scripting/plugins` or
  * `~/.kicad_plugins`

* MacOS
  * `~/Library/Application Support/kicad/scripting/plugins`
  * or on newer versions: `~/Library/Preferences/kicad/scripting/plugins`

Restart of Pcbnew.

The plugin icon should appear in the tool bar.

# Config

Not all configuration parameters are in the dialog. 
To change these defaults, open the dialog, click "Save current settings" and
edit the "stencil-config.ini" text file in the plugin folder.

These settings are available only via config file:
* laser_x_width (defauly=0.08)
* laser_y_width (default=0.08)
* laser_border_speed (default=200)

To reset settings, just delete the respective config lines or the whole file.

# TODO

* support other than "rect" and "roundrect" pads 
* make "roundrect" with rounded corners, not simply rectangular
* clean up non used code
* test on other than Ubuntu (sorry, no Win or Mac here)

# Feedback welcome

Please feel free to create a GitHub "issue" for feature requests, issues or questions.

# License

MIT License, Copyright (c) 2021 ma-ha