# Create your own pet

Turn a favorite character into a desktop companion, drawn by hand or with an image generation tool. A pet needs sprite sheets and registration data. Helico provides walking, jumping, blinking, and mouse interaction.

Settings discovers and installs community pets from Helico's public catalog. A development build can preview packs from a local directory. Copy this guide to give an agent the requirements for preparing the artwork and configuration. [Public catalog](https://github.com/run-bigpig/helico/blob/main/catalog-v2.json)

## 1. Design the character and artwork

Start with a complete character reference, then create each pose from it. Keep the same identity, proportions, colors, and material across frames, facing right by default; the app mirrors the character when it turns. A distinct head and body, clear eyes, and recognizable limbs make registration and animation easier.

Use static WebP images with transparent backgrounds, not animated images. Keep the entire character, antennae, and limbs within each cell with some room at the edges. Include no text, grid lines, or background. Keep a consistent foot baseline in standing and walking frames, with a continuous sequence of contact, support, lift, and swing.

| File | Pixel dimensions | Content |
|---|---|---|
| `poses.webp` | 1024 × 1024 | 4 columns × 4 rows, 256 × 256 per cell; layout below |
| `walk.webp` | 1024 × 768 | 4 columns × 3 rows, 12 continuous walking frames in row order, 256 × 256 per cell |
| `face.webp` | 288 × 80 | 3 columns × 1 row, 96 × 80 per column; facial material to fill behind animated eyes |

Arrange `poses.webp` from left to right, top to bottom:

| Row | Column 1 | Column 2 | Column 3 | Column 4 |
|---|---|---|---|---|
| 1 | Idle | Waiting | Working (running) | Review |
| 2 | Sad (failed) | Waving | Jumping | Sitting (sit) |
| 3 | Napping (nap) | Hanging (hang) | Reserved | Sprinting (sprint) |
| 4 | Legacy walk 1 | Legacy walk 2 | Legacy walk 3 | Legacy walk 4 |

Walking currently uses the separate `walk.webp`; peeking reuses the idle head. Follow the reference resource layout for the reserved and legacy cells.

The optional typing pose requires both `typing.webp` and `typing-base.webp` (512 × 512 each), together with `rig.typing`. The first shows the complete character at a computer with both hands on the keys; the second removes both arms and fills in the body and keyboard. Incomplete sets fail validation. Start with the three base images for a first pet.

## 2. Register the head, eyes, and walk

Extract the Helico Jade pack and use the `rig` in its `manifest.json` as a starting point. Measure and register the new artwork after replacing the sprites. [Helico Jade pack](https://github.com/run-bigpig/helico/releases/tag/helico-jade-v1.0.0)

Registration uses **256 × 256 cell coordinates**, with the origin at the top left, x increasing rightward, and y downward. The 512px typing images use the same coordinate basis.

| Configuration | What to provide |
|---|---|
| `layout.head` | Idle head rectangle including antennae: left, top, right, bottom |
| `layout.idleNeck` / `idleFloor` | Idle neck connection point and foot baseline |
| `layout.walkNecks` / `walkFloor` | One neck connection point for each of the 12 walking frames and a shared walking foot baseline |
| `faces` | At least the idle neck position; eye centers, radii, angles, and local material tone adjustments for each pose as needed; closed-eye poses may omit eyes |
| `eyes` | Style: textured (original iris), stitched, or ink; colors, facial material column, and sampling offsets |
| `armEdge` | Arm clipping boundary as a percentage from 0 to 100 |
| Optional `typing` | Vertical offsetY, overall scale (optional, defaults to 1, anchored at the bottom center of the canvas), typing cycleMs, and each arm's clipping path (clip), shoulder pivot, and lift angle |

Coordinates range from 0 to 256. Necks must be above the foot baseline, head rectangles must have positive width and height, and `walkNecks` must contain exactly 12 entries. See the Format 1 definition in `packages/protocol/src/pet.ts` for all fields and ranges.

## 3. Build the resource pack

Put the atlases and `manifest.json` in the same directory. Update the manifest with a new `id`, `version`, localized names and descriptions, and the `rig` for your artwork. Run Helico's packager with Python 3 and Pillow. [Packaging script](https://github.com/run-bigpig/helico/blob/main/build/pet-art/package_pet.py)

```sh
python3 -m pip install Pillow
python3 build/pet-art/package_pet.py ./my-pet ./pet-release
```

The script recalculates sizes and SHA-256 digests in the manifest, creates a preview from the idle sprite, and writes the ZIP, preview, and a single-entry `catalog-v2.json` to `pet-release/`. Append `--repository <owner>/<repo>` if you publish from your own GitHub repository.

Resource packs must meet these requirements:

- Use `format: 1`. The id is at most 64 characters, starts with a lowercase letter, and contains only lowercase letters, digits, and hyphens. Choose a new id. The built-in Helico mascot uses the reserved helico-butterfly id. Use three numeric version components, such as `1.0.0`.
- Supply zh and en names and descriptions, each 1–160 characters. The manifest id and version must match the catalog entry.
- The ZIP root contains `manifest.json`, the three base WebP images, and any fully declared optional typing images. The manifest contains the `rig`, and the catalog entry contains the preview.
- Both the ZIP and the total extracted contents must be at most 4 MiB. Each WebP is at most 2 MiB and the manifest at most 64 KiB. Image dimensions, byte counts, and SHA-256 digests must match.
- Catalog previews may be PNG or WebP, at most 512px on each side, with an encoded data URL no longer than 48,000 characters.

## 4. Preview in a development build

Copy `catalog-v2.json` to `catalog.json` in the same directory. In your Helico development environment, replace the example path with the absolute path to `pet-release/`. In Windows PowerShell, set `$env:HELICO_HOME` and `$env:HELICO_PET_DIRECTORY` before running the task.

```sh
HELICO_HOME=~/.helico-demo HELICO_PET_DIRECTORY=/path/to/pet-release task run TAGS=purego
```

Open **Settings → Pet** and select **Download & use**. The development build reads and validates the pack from the local directory and stores test data in `~/.helico-demo`.

Check idle, working, waiting, and failed states, then blinking, gaze, turning, walking, dragging, and peeking for smooth connections. Check transparent edges and static frames at the smallest and largest sizes, on light and dark backgrounds, and with reduced motion. After changes, increase the version, rebuild, then select **Update & use** in Settings.

## 5. Publish the pack

Upload the ZIP to a release tagged `<id>-v<version>` in the same GitHub repository as the catalog. Verify the download digest, then merge the new entry into `catalog-v2.json` on `main`. To submit a pack for Helico's public catalog, include the preview and release URL. [Helico repository](https://github.com/run-bigpig/helico) · [Submit a pack](https://github.com/run-bigpig/helico/issues/new)
