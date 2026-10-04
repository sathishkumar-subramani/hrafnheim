// One entry per slide. Order = order of the journey.
// Images live in public/img/slides/slide-{n}-layer-{back|middle|front}.webp
export const realms = [
  {
    id: 'frost',
    numeral: 'I',
    title: 'Frost',
    accent: '#a9dce6',
    lore: 'The fjord froze in a single night, and the longships froze with it. Walk the ice where the old fleet still waits, and listen for what moves beneath.',
    cta: 'Cross the ice',
  },
  {
    id: 'ember',
    numeral: 'II',
    title: 'Ember',
    accent: '#f0913f',
    lore: 'Deep under the mountain the forge has never cooled. Its smiths are long gone, but the fire still remembers every blade they made.',
    cta: 'Enter the forge',
  },
  {
    id: 'roots',
    numeral: 'III',
    title: 'Roots',
    accent: '#cdc77e',
    lore: 'Every realm hangs from the same tree. Down among its roots the runes still glow for anyone patient enough to read them.',
    cta: 'Read the runes',
  },
  {
    id: 'storm',
    numeral: 'IV',
    title: 'Storm',
    accent: '#bcb3f7',
    lore: 'At the top of the world the stones stand in a ring, and the sky answers back. Only the wanderer has climbed this far.',
    cta: 'Climb the peak',
  },
]

// Same idea as the original Basic3D slider:
// a bigger swiper offset = the layer lags more = it feels further away.
// `drift` is the extra pointer-movement depth in px (front moves most).
export const layers = [
  { name: 'back', parallax: '35%', drift: 6 },
  { name: 'middle', parallax: '25%', drift: 16 },
  { name: 'front', parallax: '14%', drift: 30 },
]

export const layerSrc = (slideIndex, layerName) =>
  `${import.meta.env.BASE_URL}img/slides/slide-${slideIndex + 1}-layer-${layerName}.webp`
