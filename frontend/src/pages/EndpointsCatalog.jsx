export default function EndpointsCatalog({ endpoints, selectedId, onSelect }) {
  return (
    <section className="surface-card catalog-panel">
      <div className="section-head">
        <div>
          <p className="eyebrow">Catalog</p>
          <h2>Список ручек</h2>
        </div>
        <span className="counter-badge">{endpoints.length}</span>
      </div>

      <div className="catalog">
        {endpoints.map((endpoint) => (
          <button
            key={endpoint.id}
            className={`endpoint-card ${selectedId === endpoint.id ? 'selected' : ''}`}
            onClick={() => onSelect(endpoint.id)}
          >
            <span className="endpoint-method">{endpoint.method}</span>
            <strong>{endpoint.title}</strong>
            <span className="endpoint-path">{endpoint.path}</span>
          </button>
        ))}
      </div>
    </section>
  )
}
