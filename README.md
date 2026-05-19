# Krita to OpenToonz Exporter

Export animated paint layers as image sequences with timing data transfered over to OpenToonz/Tahoma2D scene files (.tnz) automatically and retaining layer stacking order.

Features:
- Support for grouped layers, static layers, reference layers (marked with a grey color label)
- Has native deduplication, this means **clone** frames are only exported once and instanced in OpenToonz's X-Sheet (1--2--1)

## Installation
1. Download the plugin by clicking the green Code button at the top and save as .ZIP
2. Inside Krita, goto **Tools/Scripts/Install Python Plugin from File...** and select the .ZIP file and restart Krita

## Usage
1. Go to **Tools > Scripts > Export Animation to OpenToonz Scene...**
2. Select an export directory and configure options and click the Export button

## Export Options
### Flatten animated groups
> Group layers containing animated layers are exported as baked single flattened images. This is due to common convention, useful when you have separate layers for lines and paint (or multiple layers for different color separation lines) inside a group that should be combined in the final export. When disabled, only individual paint layers are exported.

### Include invisible layers
> Export layers that are currently hidden in the layer panel.

### Include reference layers (grey-labeled)
> Export layers marked with a grey color label. By default, grey-labeled layers are treated as animation reference guides and excluded from export.

### Include non-animated layers
> Export static layers (without animation keyframes) as single images. Useful for backgrounds, layouts, peg bars, or safety margin frames. Static layers are exported directly into the export folder without subfolders.

## Output Structure
```
> DocumentName/              # Export folder (named after your document)
--> DocumentName.tnz         # OpenToonz (or Tahoma2D) project scene file
----> BG1.png                # Static layers (single images, no folder)
----> Layout.png             # Another static layer
----> A/                     # Folder for each animated layer/group
------> A_0001.png
------> A_0002.png
----> B/
------> B_0001.png
etc...
```

## How to Open in OpenToonz/Tahoma2D
### Option 1:
Head to the Browser room (or open a File Browser panel) and find the exported **.tnz** scene file on your system.

### Option 2:
Go to the menu: **File > Load Scene** and find the exported **.tnz** scene file.

## Tips
### Convert Animation to Toonz Raster Levels
A **Toonz Raster Level** is a more advanced raster layer that supports features like **color indexing**, where each pixel references a **style** (in the Palette window) so when you change the color of the style it's automatically updated instantly anywhere that style was drawn or painted. These can also be quickly **masked** in the compositor, for example if you want to grab the color of the eye highlight to apply a glow or bloom effect to it, you can reference it by the style's ID number.

Select your raster layers (blue) on the X-Sheet/Timeline and go to the top menu **Level > Convert > Convert to Toonz Raster...**. Note that if your work is aliased (meaning there is no anti-aliasing or smoothness/blur in the artwork) the conversion is straightforward.

1. For the file format, select **tlv**
2. Mode should be set to **Unpainted TLV from non-AA source** for lines only artwork or **Painted TLV from non-AA source** if the artwork is already painted

For artwork that is anti-aliased your miliage may vary and it's not recommended. You will need two copies of your image sequences, one that is lines only (including color separation lines that define the borders between two colors like base colors and shadows), and one that contains the main lineart and paint. OpenToonz will use the lines only sequence to try and detect where **lines** are in the fully painted sequence and the boundaries between two colors. Then, follow the above steps but use **Unpainted TLV** and **Painted TLV from two images**. If you're only converting lines (no paint) use the first option.

## Troubleshooting

### "No animated layers found"
This error appears when no exportable animation layers are detected. Check that:

- The layers have animation keyframes on the timeline
- The layers are visible (or enable **Include invisible layers**)
- The layers don't have a grey color label (or enable **Include reference layers**)

## Requirements
- OpenToonz or Tahoma2D (⚠️ required for generating the **.tnz** scene file via CLI automatically)

## Contributing
Contributions, bug reports, and feature requests are welcome! Please open an issue or submit a pull request.

## License
This plugin is released under the GPL-3.0 license. See LICENSE file for details.

## Related Projects
- [Krita](https://krita.org/)
- [Krita to XDTS Exporter](https://github.com/konero/KritaToXDTS/)
- [OpenToonz](https://opentoonz.github.io/e/)
- [Tahoma2D](https://tahoma2d.org/)
