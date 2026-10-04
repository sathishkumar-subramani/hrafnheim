// Big stacked title + lore for one realm.
// Each letter gets its own z-index and transition time, exactly like the
// letters.js trick in the original Basic3D site, so they land one after another.
export default function RealmTitle({ realm, state }) {
  const isActive = state === 'active'

  return (
    <section
      className={`realm realm--${state}`}
      aria-hidden={!isActive}
      inert={!isActive}
    >
      <h2 className="realm__title" aria-label={realm.title}>
        {Array.from(realm.title).map((ch, i) => (
          <span
            key={i}
            className="letter"
            aria-hidden="true"
            style={{ zIndex: -i, '--d': `${i / 5 + 1}s` }}
          >
            {ch}
          </span>
        ))}
      </h2>

      <div className="realm__info">
        <p>{realm.lore}</p>
        <a className="button" href={`#${realm.id}`}>
          {realm.cta}
        </a>
      </div>
    </section>
  )
}
