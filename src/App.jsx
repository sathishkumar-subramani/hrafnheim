import { useEffect, useRef, useState } from 'react'
import { Swiper, SwiperSlide } from 'swiper/react'
import { Parallax, Mousewheel, Keyboard, A11y } from 'swiper/modules'

import Header from './components/Header.jsx'
import RealmTitle from './components/RealmTitle.jsx'
import RealmNav from './components/RealmNav.jsx'
import { realms, layers, layerSrc } from './data/realms.js'
import { usePointerDrift } from './hooks/usePointerDrift.js'
import { useReducedMotion } from './hooks/useReducedMotion.js'

export default function App() {
  const [active, setActive] = useState(0)
  const swiperRef = useRef(null)
  const stageRef = useRef(null)
  const reduced = useReducedMotion()

  usePointerDrift(stageRef, !reduced)

  // Warm the cache so the next realm never pops in half-loaded.
  useEffect(() => {
    realms.forEach((_, i) =>
      layers.forEach((l) => {
        const img = new Image()
        img.src = layerSrc(i, l.name)
      }),
    )
  }, [])

  const travel = (i) => swiperRef.current?.slideTo(i)

  const stateOf = (i) => (i === active ? 'active' : i < active ? 'before' : 'after')

  return (
    <div
      ref={stageRef}
      className="stage"
      style={{ '--accent': realms[active].accent }}
    >
      <h1 className="sr-only">Hrafnheim, a journey through four realms</h1>

      <Swiper
        className="slider"
        modules={[Parallax, Mousewheel, Keyboard, A11y]}
        speed={reduced ? 500 : 1700}
        parallax
        mousewheel={{ thresholdDelta: 30 }}
        keyboard={{ enabled: true }}
        a11y={{
          prevSlideMessage: 'Previous realm',
          nextSlideMessage: 'Next realm',
        }}
        onSwiper={(s) => (swiperRef.current = s)}
        onSlideChange={(s) => setActive(s.activeIndex)}
      >
        {realms.map((realm, i) => (
          <SwiperSlide key={realm.id} className="slider__item" aria-label={realm.title}>
            {layers.map((layer) => (
              <div
                key={layer.name}
                className={`slider__layer slider__layer--${layer.name}`}
                data-swiper-parallax={layer.parallax}
              >
                <div
                  className="slider__img"
                  style={{
                    backgroundImage: `url(${layerSrc(i, layer.name)})`,
                    '--drift': layer.drift,
                  }}
                />
              </div>
            ))}
          </SwiperSlide>
        ))}
      </Swiper>

      <div className="ui">
        <Header realms={realms} active={active} onSelect={travel} />

        <main className="hero">
          {realms.map((realm, i) => (
            <RealmTitle key={realm.id} realm={realm} state={stateOf(i)} />
          ))}
        </main>

        <RealmNav realms={realms} active={active} onSelect={travel} />
      </div>
    </div>
  )
}
