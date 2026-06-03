# Krita to OpenToonz / Tahoma2D Exporter

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

A **Toonz Raster Level** is an advanced raster format that supports features such as **color indexing**. Instead of storing colors directly, each pixel references a **style** in the Palette window. This means that changing a style's color automatically updates every area painted with that style throughout the level.

Toonz Raster Levels can also be easily **masked** in the compositor. For example, if you want to isolate an eye highlight and apply a glow or bloom effect, you can reference the highlight by its style ID number.

Select your raster levels (blue) in the Xsheet/Timeline, then choose **Level > Convert > Convert to Toonz Raster...** from the top menu.

If your artwork is aliased (pixel art or artwork without anti-aliasing), the conversion process is generally straightforward:

1. Set the file format to **TLV**.
2. Set the mode to:

   * **Unpainted TLV from non-AA source** for line-only artwork.
   * **Painted TLV from non-AA source** for artwork that is already painted.

For anti-aliased artwork, results can vary and the process is generally not recommended. You will need two versions of your image sequence:

* A **lines-only** sequence, including any color separation lines that define boundaries between colors such as base colors and shadows.
* A **painted** sequence containing the final line art and fills.

OpenToonz uses the lines-only sequence to detect linework and color boundaries within the painted sequence. Once both sequences are prepared, follow the same conversion steps as above, but use:

* **Unpainted TLV** for the lines-only sequence.
* **Painted TLV from two images** for the painted sequence.

If you are converting line art only and do not need paint information, use **Unpainted TLV**.

**TODO**: I'll see if we can export a *_np lines-only reference during the export process, and how that'll work in practice...

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
