# Hrafnheim — layered parallax slider (React)

A React rebuild of the Basic3D parallax slider: four realms (Frost, Ember, Roots, Storm),
each made of three depth layers that slide at different speeds, with the stacked
falling-letter titles from the original `letters.js`.

The images in `public/img/slides` are procedural placeholders so the site runs right away.
Swap them for your Nano Banana Pro images using the steps below.

## Run it

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # production build in dist/
```

Node 18, 20 or 22.

## Use your own images

1. Generate 4 images in Higgsfield with **Nano Banana Pro, 2K, 16:9**.
   The prompts are in `prompts/nano-banana-pro-prompts.md`.
2. Save them as `tools/raw/frost.png`, `ember.png`, `roots.png`, `storm.png`.
3. Install the splitter once (Python 3.10+):

   ```bash
   pip install -r tools/requirements.txt
   ```

4. Split each image into layers. This overwrites the placeholders:

   ```bash
   python tools/split_layers.py tools/raw/frost.png --slide 1 --preview
   python tools/split_layers.py tools/raw/ember.png --slide 2 --preview
   python tools/split_layers.py tools/raw/roots.png --slide 3 --preview
   python tools/split_layers.py tools/raw/storm.png --slide 4 --preview
   ```

   The first run downloads the Depth Anything V2 Small model (about 100 MB).
   `--preview` writes magenta-backed JPGs into `tools/raw/` so you can check each cutout.

5. Refresh the browser.

### Getting cleaner layers

| Problem | Fix |
|---|---|
| Middle layer takes too much of the image | raise `--mid` (e.g. `0.62`) |
| Front layer misses the main subject | lower `--front` (e.g. `0.75`) |
| Hard or jagged edges | raise `--feather` (e.g. `6`) |
| Thin halo around cutouts | raise `--grow` (e.g. `2`) |

For full control, do what you did in the original PSDs: run with `--save-depth`,
paint over `tools/raw/slide-N-depth.png` in Photoshop (white = near, black = far),
then feed it back:

```bash
python tools/split_layers.py tools/raw/storm.png --slide 4 --depth tools/raw/slide-4-depth.png
```

## How the parallax works

`src/data/realms.js` holds the layer settings:

```js
export const layers = [
  { name: 'back',   parallax: '35%', drift: 6  },
  { name: 'middle', parallax: '25%', drift: 16 },
  { name: 'front',  parallax: '14%', drift: 30 },
]
```

- `parallax` is Swiper's `data-swiper-parallax` offset, the same values as Basic3D.
  A bigger offset makes the layer lag more, so it feels further away.
- `drift` is the extra pointer movement in px. The front layer moves most.
  It is turned off on touch screens and for reduced motion.
- The active slide zooms to 1.15 (Basic3D used 1.25). Change it in
  `src/styles/global.css` under `.slider__item`.

## Change the content

Edit the `realms` array in `src/data/realms.js`. Each realm has a title, accent color,
lore text and button label. To add a fifth realm, add an entry and add
`slide-5-layer-back.webp`, `-middle.webp` and `-front.webp` to `public/img/slides`.

## Project structure

```
src/
  App.jsx                  Swiper, layers and overlay
  components/
    Header.jsx             wordmark, nav, slide-out realm menu
    RealmTitle.jsx         stacked letters and lore for one realm
    RealmNav.jsx           bottom journey bar
  hooks/
    usePointerDrift.js     eased mouse position as CSS variables
    useReducedMotion.js
  data/realms.js           content and layer settings
  styles/global.css
  assets/fonts/            Grenze Gotisch and Spectral (SIL OFL), self-hosted
public/img/slides/         slide-N-layer-{back,middle,front}.webp
tools/
  split_layers.py          one image to three depth layers
  make_placeholders.py     regenerates the placeholder art
prompts/                   Nano Banana Pro prompts
```

## Deploy to IIS

`vite.config.js` uses `base: './'`, so the build works from a sub-folder.

1. Run `npm run build`.
2. Copy the contents of `dist/` into the IIS site or application folder.
3. If `.webp` or `.woff2` files return 404, add their MIME types (`image/webp`,
   `font/woff2`) in IIS Manager under MIME Types.
