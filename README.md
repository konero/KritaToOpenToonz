# Krita to OpenToonz Exporter

A Krita plugin that exports animations from Krita to OpenToonz native scene files (.tnz). Each animated layer (including non-animated as an option) is exported as a separate PNG image sequence. All timing is properly transferred over.

## Features
- Export animated layers as separate PNG sequences
- Preserve keyframe timing and hold frames
- Exports only one copy of a "Cloned" keyframe (clones are converted to exposures in OpenToonz)
- Support for flattening groups into animation layers
- Toggle invisible layers
- And reference layers

## Requirements
- Krita 5.0 or later
- OpenToonz or Tahoma2D installed (these create the actual scene file)

## Download
1. Click the green **Code** button at the top right.
2. Select **Download ZIP** to download the plugin as a ZIP file.

## Install

### Option 1: Using Krita's Plugin Importer (simplest)
1. In Krita, go to `Tools > Scripts > Import Python Plugin from File...`
2. Select the downloaded ZIP file.
3. Restart Krita.

### Option 2: Manual Installation (Windows)
1. Extract the downloaded ZIP file.
2. Copy all contents of the folder into your Krita plugins directory:  
   `%APPDATA%\krita\pykrita\`
3. Restart Krita.
4. You may need to enable the plugin, go to `Settings > Configure Krita > Scroll down to Python Plugins > Find Export Animation to OpenToonz`, check it to enable it and restart Krita again.

After installation, access the plugin via `Tools > Scripts > Export Animation to OpenToonz Scene...` (or set a shortcut key to call it or add to your toolbar).

## Usage
1. Run the plugin from: `Tools/Scripts/`.
2. Set the path to your OpenToonz (or Tahoma2D) installation from the `Settings` tab.
4. Choose export location and options.
5. Click **Export** to generate the .tnz scene.

> **Note:** By default, the plugin skips reference layers (layers marked with a `grey color label` in Krita). These are typically used for rough animation, sketches, or layouts. Enable `Include Reference Layers` in the export options if you need them in OpenToonz.

## Manual
For detailed instructions, see the [Manual](Manual.html).

## License
GPL-3.0
