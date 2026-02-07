# Krita to OpenToonz Exporter

Export animated paint layers as image sequences with timing data transfered over to OpenToonz/Tahoma2D scene files (.tnz), retaining layer stacking order.

## Overview
Key Features:
- Export Krita animation layers as numbered image sequences
- Generate a OpenToonz/Tahoma2D scene file, keeping layer stacking order and frame times
- Support for grouped layers, static layers, reference layers
- Compatible with OpenToonz and Tahoma2D

## Use Cases
- **Traditional animation workflow**: Export rough animation from Krita for celpaint or compositing in OpenToonz/Tahoma2D

## Installation
1. Download the plugin by clicking the green `Code` button at the top and save as `.ZIP`
2. In Krita, navigate to the menu: `Tools/Scripts/Install Python Plugin from File...`
3. Select the downloaded `.ZIP` file
4. Restart Krita

## Usage
1. Go to `Tools > Scripts > Export Animation Layers (XDTS)...`
2. Select an export directory and configure options
3. Click export

## Export Options

### Flatten animated groups
> Group layers containing animated children are exported as single flattened images. This is useful when you have separate layers for lines and paint, or multiple layers for different colored lines, inside a group that should be combined in the final export. When disabled, only individual paint layers are exported.

### Include invisible layers
> Export layers that are currently hidden in the layer panel.

### Include reference layers (grey-labeled)
> Export layers marked with a grey color label. By default, grey-labeled layers are treated as animation reference guides and excluded from export.

### Include non-animated layers
> Export static layers (without animation keyframes) as single images. Useful for backgrounds, layouts, peg bars, or safety margin frames. Static layers are exported directly into the export folder without subfolders and not included in the .XDTS exposure sheet file.

## Features
- Export animated layers as separate PNG sequences
- Preserve keyframe timing and hold frames
- Exports only one copy of a "Cloned" keyframe (clones are converted to exposures in OpenToonz)
- Support for flattening groups into animation layers
- Toggle invisible layers
- And reference layers

## Output Structure
```
chosen_directory/
└── DocumentName/              # Export folder (named after your document)
    ├── DocumentName.tnz       # OpenToonz/Tahoma2D scene file
    ├── BG1.png                # Static layers (single images, no folder)
    ├── Layout.png             # Another static layer
    ├── A/                     # Folder for each animated layer/group
    │   ├── A_0001.png
    │   ├── A_0002.png
    │   └── ...
    ├── B/
    │   ├── B_0001.png
    │   └── ...
    └── ...
```

## How to Open in OpenToonz/Tahoma2D

### Option 1:
Head to the Browser room (or open a File Browser panel) and find the exported `.tnz` file on your system

### Option 2:
Go to the menu: `File > Load Scene` and find the exported `.tnz` file.

## Troubleshooting

### "No animated layers found" error
This error appears when no exportable animation layers are detected. Check that:

- Your document has paint layers (or groups with paint layers inside)
- The layers have animation keyframes on the timeline
- The layers are visible, or enable "Include invisible layers"
- The layers don't have a grey color label, or enable "Include reference layers"

## Requirements
- Krita 5.0 or later
- OpenToonz or Tahoma2D (⚠️ required for generating the `.tnz` scene file)

## Contributing

Contributions, bug reports, and feature requests are welcome! Please open an issue or submit a pull request.

# License
This plugin is released under the GPL-3.0 license. See LICENSE file for details.

## Related Projects

- [Krita](https://krita.org/) - Free and open-source painting program
- [Krita to XDTS Exporter](https://github.com/konero/KritaToXDTS/) - Krita plugin
- [OpenToonz](https://opentoonz.github.io/e/) - Open-source animation production software
- [Tahoma2D](https://tahoma2d.org/) - Community fork of OpenToonz
