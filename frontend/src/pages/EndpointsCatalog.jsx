export default function EndpointsCatalog({ endpoints, selectedId, onSelect }) {
  return (
    <section className="card">
      <h2>Endpoints Catalog</h2>
      <div className="catalog">
        {endpoints.map((endpoint) => (
          <button
            key={endpoint.id}
            className={`endpoint-card ${selectedId === endpoint.id ? 'selected' : ''}`}
            onClick={() => onSelect(endpoint.id)}
          >
            <strong>{endpoint.method}</strong> {endpoint.path}
            <span>{endpoint.title}</span>
          </button>
        ))}
      </div>
    </section>
  )
}
