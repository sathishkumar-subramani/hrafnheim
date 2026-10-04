// Bottom journey bar: one stop per realm, the line fills as you travel.
export default function RealmNav({ realms, active, onSelect }) {
  return (
    <nav className="realms" aria-label="Realms">
      <ol className="realms__list">
        {realms.map((r, i) => (
          <li key={r.id}>
            <button
              type="button"
              className={`realms__item${i === active ? ' is-active' : ''}${i < active ? ' is-past' : ''}`}
              aria-current={i === active ? 'step' : undefined}
              onClick={() => onSelect(i)}
            >
              <span className="numeral">{r.numeral}</span>
              <span className="realms__name">{r.title}</span>
            </button>
          </li>
        ))}
      </ol>
      <p className="realms__hint">Scroll, swipe or use the arrow keys to travel</p>
    </nav>
  )
}
