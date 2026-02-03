# Krita to OpenToonz Exporter

A Krita plugin that exports animations from Krita to OpenToonz scene files (.tnz), including PNG level sequences with preserved timing.

## Features
- Export animated layers as PNG sequences
- Preserve keyframe timing and hold frames
- Support for groups, invisible layers, and reference layers
- Cross-platform (Windows, macOS, Linux)

## Requirements
- Krita 5.0 or later
- OpenToonz installed

## Download
1. Go to the GitHub repository page.
2. Click the green **Code** button at the top right.
3. Select **Download ZIP** to download the repository as a ZIP file.

## Install (Windows)
1. Extract the downloaded ZIP file.
2. Copy the `opentoonz_exporter` folder into your Krita plugins directory:  
   `%APPDATA%\krita\pykrita\`
3. Restart Krita.
4. Access the plugin via **Tools → Scripts → Export Animation to OpenToonz Scene...**

## Usage
1. Open your animation project in Krita.
2. Run the plugin from the menu.
3. Set the path to your OpenToonz installation.
4. Choose export location and options.
5. Click **Export** to generate the .tnz scene.

> **Note:** By default, the plugin skips reference layers (layers marked with a **grey color label** in Krita). These are typically used for rough animation, sketches, or timing guides. Enable "Include Reference Layers" in the export options if you need them in OpenToonz.

## Manual
For detailed instructions, see the [Manual](opentoonz_exporter/Manual.html).

## License
GPL-3.0
