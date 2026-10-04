# Image prompts — Higgsfield, Nano Banana Pro

Settings for every image:

- Model: **Nano Banana Pro**
- Resolution: **2K**
- Aspect ratio: **16:9**
- One image per realm, 4 in total

Save the downloads as `tools/raw/frost.png`, `ember.png`, `roots.png`, `storm.png`,
then split each one into parallax layers (see README → "Use your own images").

Every prompt asks for a dark foreground, a clear midground and a hazy background,
because `split_layers.py` cuts the layers by depth. Strong separation = clean layers.
The upper-middle is kept calm because the big realm title sits there.

---

## 1. Frost

```
Cinematic dark Norse-myth fantasy matte painting, photoreal detail. A frozen fjord at blue hour. In the midground, the wreck of an ancient wooden longship is locked at an angle in cracked sea ice, its torn sail frozen stiff. Far behind, black cliffs draped in glaciers rise into a deep teal night sky with a faint green aurora. The foreground along the bottom edge is a wall of jagged translucent blue ice shards and snow-covered boulders, sharp and very close to the camera. Light snow drifting, cold mist between foreground, midground and background, strong atmospheric perspective. Calm open sky in the upper middle of the frame. No people, no text, no logos, no watermark.
```

## 2. Ember

```
Cinematic dark Norse-myth fantasy matte painting, photoreal detail. The inside of a vast volcanic caldera. Rivers of molten lava wind across black basalt plains toward a smoking volcano in the far distance, under ash clouds lit orange from below. In the midground stand the ruins of an ancient mountain forge: a colossal stone anvil, broken pillars carved with knotwork, heavy iron chains hanging from them. The foreground along the bottom edge is cracked obsidian boulders glowing orange at the seams, very close to the camera. Floating embers, heat haze, deep smoke between the layers, strong atmospheric perspective. Calm dark sky in the upper middle of the frame. No people, no text, no logos, no watermark.
```

## 3. Roots

```
Cinematic dark Norse-myth fantasy matte painting, photoreal detail. Deep beneath a colossal world tree. Giant moss-covered roots arch through an ancient misty forest, shafts of pale gold light falling through the fog. In the midground, a weathered standing runestone carved with faintly glowing golden runes stands between two roots. Far behind, the trunks of enormous trees fade into green mist. The foreground along the bottom corners is dark ferns and gnarled roots, very close to the camera and slightly out of focus. Floating spores catching the light, layered fog, strong atmospheric perspective. Calm misty space in the upper middle of the frame. No people, no text, no logos, no watermark.
```

## 4. Storm

```
Cinematic dark Norse-myth fantasy matte painting, photoreal detail. A mountain summit at the top of the world during a violent thunderstorm. In the midground, a ring of tall weathered standing stones with one stone lintel crowns the peak. Far behind, a jagged mountain range fades under violet storm clouds split by a branching lightning bolt. In the foreground, on a dark rock ledge in the lower right third, a lone hooded wanderer in a heavy fur cloak holding a long spear, seen from behind, small in the frame. Slanting rain, wind-blown mist between the layers, strong atmospheric perspective. Calm stormy sky in the upper middle of the frame. No text, no logos, no watermark.
```

---

### If a result is close but not right

- Title area too busy → add: `keep the upper middle third of the frame empty and softly lit`
- Layers blend together → add: `foreground in deep silhouette, midground in half-light, background pale with haze`
- Too bright for white text → add: `low-key exposure, deep shadows`
