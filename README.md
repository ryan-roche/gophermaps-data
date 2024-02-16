This repository is for the map data and walking instructions for the gophermaps project.

# Mapping
A critical part of our backend is a neo4j graph database representing the layout of the buildings and the tunnels & skyways connecting them.
In order to generate this database, we first have to map out these tunnels and skyways. We'll be using [JOSM](https://josm.openstreetmap.de) to do this.

## Getting Started
1. Clone the repository. It contains the data we'll be editing and a reference image for the gopher way from PTS

2. Install JOSM

3. Launch JOSM. You'll see this screen:
<img width="1624" alt="image" src="https://github.com/ryan-roche/gophermaps-data/assets/48164514/3a6c3b0c-e90b-4bdb-93a0-bca7e803a876">

4. Click the blue folder icon and open the `map.osm` file from the repository
<img width="205" alt="image" src="https://github.com/ryan-roche/gophermaps-data/assets/48164514/ae262652-62d5-4657-8e7c-ee977450e123">

5. When the data loads, you'll see something like this- some nodes and lines on a black background:
<img width="1624" alt="image" src="https://github.com/ryan-roche/gophermaps-data/assets/48164514/24c1a9a2-c1d7-4a79-8fec-3c9a1770cf74">
Needless to say, there isn't much to go off of right now for mapping out the Gopher Way. We'll be adding an Image Layer to use as a reference.
In order to do that, though, we'll need to install the PicLayer Extension.

6. Open the JOSM Settings panel. On macOS, you open it like you do for any other app-
<img width="300" alt="image" src="https://github.com/ryan-roche/gophermaps-data/assets/48164514/f978307c-30b9-4828-a6ac-685f05324c78">

7. Click the blue puzzle-piece icon to view the plugin settings
<img width="912" alt="image" src="https://github.com/ryan-roche/gophermaps-data/assets/48164514/aee51950-c9fa-4850-b985-de32de68aa70">

8. Search for the PicLayer extension and check the box to download it
<img width="912" alt="image" src="https://github.com/ryan-roche/gophermaps-data/assets/48164514/819113f7-770b-404f-8960-c19c23378424">

9. Click "OK" to close the preferences panel

10. Now that we have PicLayer installed, you'll see the "New picture layer from file..." option in the Imagery menu
<img width="420" alt="image" src="https://github.com/ryan-roche/gophermaps-data/assets/48164514/f62fc56e-40dc-465e-a522-9464371f7055">

11. Select the `pts-gw-map.png` image file. It should automatically load the corresponding calibration file to align the image layer with the map data.

You're now ready to begin mapping. The plugin woill remain installed, but you may need to reload the image layer from the Imagery menu the next time you run JOSM

## Editing the Map data

> [!TIP]
> If you're finding it difficult to see the map data with the image layer behind it,
> you can adjust its opacity by clicking button with the icon of an eye with a gradient underneath it in the layers panel on the top-right of the screen.
> <img width="350" alt="image" src="https://github.com/ryan-roche/gophermaps-data/assets/48164514/b5b2cb74-3e49-4f5f-a47b-93b2fedb0538">

The core components of the OSM data is nodes and "ways". Nodes are the little squares you see on the map, and ways are the lines connecting.
Both nodes and ways can be given tags, as shown by the contents of the "tags/memberships" panel when they're selected.

These tags play a vital role in making this project "work", so it is crucial that we all follow the same standards for tagging.
Before I go over the style guide, however, I'll show you how to create nodes and ways.

### Creating Nodes and Ways
> [!NOTE]
> For this section, I'll have the opacity of the image layer reduced so that the map data can be more easily discerned

First, make sure that the map data layer is selected. You'll know it's selected if there's a green check mark next to the `map.osm` layer in the Layers panel.

![ezgif-4-d667257780](https://github.com/ryan-roche/gophermaps-data/assets/48164514/ef22971c-13a1-419b-9ac7-b8b878c41fe0)

Your mode/tool selection can be found on the left edge of the window. Tooltips are available if you hover your mouse, and the functionality is rather self-explanatory

<img width="350" alt="image" src="https://github.com/ryan-roche/gophermaps-data/assets/48164514/03bdea47-e07d-4b27-a4d1-806db1cc32d9">

For now, select the "Draw Nodes" tool.

![ezgif-6-323dafa56b](https://github.com/ryan-roche/gophermaps-data/assets/48164514/11b334ab-8092-4a85-9abb-f013d10d4f44)

- Clicking on the map when in this mode will create a node, and clicking again will create another node and automatically connect them with a way
- If you just want to create a single node, hitting the Escape key will finish the operation

We want a node on each of the "dots" on the reference image, and for the ways to match the lines on the image. For the tunnels that aren't straight lines, simply use multiple nodes.
Alternatively, you can draw a straight line from the start to the end, switch to the move/select mode, and click the + in the middle of the line to bisect it with a new node, and move it into place.

When you're done working, save the map.osm file and commit your changes to the git repository. JOSM will ask you if you want to upload the changes. DO NOT DO SO.

![ezgif-6-e78f4d904e](https://github.com/ryan-roche/gophermaps-data/assets/48164514/9db73d4c-58b7-4390-ad31-2ea6696b6df8)

### Mapping Standards
- Every Gopher Way entrance in each building (the white circles on the PTS map) should have a node
- Each entrance node should be connected to each entrance node in the same building. This is how we will index and provide instructions on moving within buildings to the different tunnels
The following image shows what a mapped building should look like:
<img width="345" alt="image" src="https://github.com/ryan-roche/gophermaps-data/assets/48164514/14c87505-b1b8-49d1-adf9-5587b29023f9">

### Tagging Standards
OSM tags are stored as key:value pairs. *They are case-sensitive*.

Building Entrance Nodes should have the following tags:
- **"building"** with the name of the building as the value
- **"floor"** with the floor number the tunnel entrance is on. Alphabetic floors "e.g. G, B, SB" should be capitalized

Ways connecting Building Entrance Nodes *in the same building* should have the following tags:
- **"type"** with the value "inter-building"

Ways connecting *different buildings* should have the following tags:
- **"type"** with the value "tunnel" or "skyway" depending on the type of the connection

---

# Instruction-writing
TBD.
