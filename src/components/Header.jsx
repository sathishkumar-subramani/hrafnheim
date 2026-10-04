import { useEffect, useRef, useState } from 'react'

export default function Header({ realms, active, onSelect }) {
  const [open, setOpen] = useState(false)
  const panelRef = useRef(null)
  const toggleRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const onKey = (e) => {
      if (e.key === 'Escape') {
        setOpen(false)
        toggleRef.current?.focus()
      }
    }
    window.addEventListener('keydown', onKey)
    panelRef.current?.querySelector('button')?.focus()
    return () => window.removeEventListener('keydown', onKey)
  }, [open])

  const travel = (i) => {
    onSelect(i)
    setOpen(false)
  }

  return (
    <header className="top">
      <a className="wordmark" href="#">Hrafnheim</a>

      <nav className="top__nav" aria-label="Main">
        <ul>
          <li><a href="#realms" aria-current="page">Realms</a></li>
          <li><a href="#saga">Saga</a></li>
          <li><a href="#gallery">Gallery</a></li>
        </ul>
      </nav>

      <a className="top__cta" href="#join">Join the saga</a>

      <button
        ref={toggleRef}
        type="button"
        className={`menu-btn${open ? ' is-open' : ''}`}
        aria-expanded={open}
        aria-controls="realm-menu"
        onClick={() => setOpen((o) => !o)}
      >
        <span className="sr-only">{open ? 'Close menu' : 'Open menu'}</span>
        <i aria-hidden="true" />
        <i aria-hidden="true" />
      </button>

      <div
        id="realm-menu"
        ref={panelRef}
        className={`menu${open ? ' is-open' : ''}`}
        inert={!open}
      >
        <p className="menu__heading">Travel to</p>
        <ol className="menu__realms">
          {realms.map((r, i) => (
            <li key={r.id}>
              <button
                type="button"
                aria-current={i === active ? 'step' : undefined}
                onClick={() => travel(i)}
              >
                <span className="numeral">{r.numeral}</span>
                {r.title}
              </button>
            </li>
          ))}
        </ol>
        <ul className="menu__links">
          <li><a href="#saga">Saga</a></li>
          <li><a href="#gallery">Gallery</a></li>
          <li><a href="#join">Join the saga</a></li>
        </ul>
      </div>
    </header>
  )
}
