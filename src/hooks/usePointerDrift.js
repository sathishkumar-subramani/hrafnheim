import { useEffect } from 'react'

// Writes --px / --py (-1 … 1) on the element, eased every frame.
// CSS turns those into a small per-layer offset, so the layers keep
// drifting at different depths even between slide changes.
export function usePointerDrift(ref, enabled) {
  useEffect(() => {
    const el = ref.current
    if (!el || !enabled) return
    if (window.matchMedia('(pointer: coarse)').matches) return

    let tx = 0, ty = 0, x = 0, y = 0, frame = 0

    const onMove = (e) => {
      tx = (e.clientX / window.innerWidth) * 2 - 1
      ty = (e.clientY / window.innerHeight) * 2 - 1
    }
    const onLeave = () => { tx = 0; ty = 0 }

    const tick = () => {
      x += (tx - x) * 0.06
      y += (ty - y) * 0.06
      el.style.setProperty('--px', x.toFixed(4))
      el.style.setProperty('--py', y.toFixed(4))
      frame = requestAnimationFrame(tick)
    }

    window.addEventListener('pointermove', onMove, { passive: true })
    document.addEventListener('pointerleave', onLeave)
    frame = requestAnimationFrame(tick)

    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('pointermove', onMove)
      document.removeEventListener('pointerleave', onLeave)
      el.style.setProperty('--px', '0')
      el.style.setProperty('--py', '0')
    }
  }, [ref, enabled])
}
