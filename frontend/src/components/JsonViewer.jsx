import { useMemo, useState } from 'react'

function renderTree(value, search, depth = 0, expandAll = false) {
  if (value === null || typeof value !== 'object') {
    const text = String(value)
    const matches = search ? text.toLowerCase().includes(search.toLowerCase()) : true
    return <span className={matches ? 'hit' : ''}>{text}</span>
  }

  if (Array.isArray(value)) {
    return (
      <div className="tree-array">
        {value.map((item, idx) => (
          <details key={`${depth}-${idx}`} open={expandAll || depth < 1}>
            <summary>[{idx}]</summary>
            <div className="tree-node">{renderTree(item, search, depth + 1, expandAll)}</div>
          </details>
        ))}
      </div>
    )
  }

  return (
    <div className="tree-object">
      {Object.entries(value).map(([key, val]) => {
        const keyHit = search ? key.toLowerCase().includes(search.toLowerCase()) : false
        const isExpandable = val !== null && typeof val === 'object'

        if (!isExpandable) {
          return (
            <div key={`${depth}-${key}`} className="tree-leaf">
              <span className={keyHit ? 'key hit' : 'key'}>{key}:</span> {renderTree(val, search, depth + 1, expandAll)}
            </div>
          )
        }

        return (
          <details key={`${depth}-${key}`} open={expandAll || depth < 1}>
            <summary>
              <span className={keyHit ? 'key hit' : 'key'}>{key}</span>
            </summary>
            <div className="tree-node">{renderTree(val, search, depth + 1, expandAll)}</div>
          </details>
        )
      })}
    </div>
  )
}

export default function JsonViewer({ value }) {
  const [mode, setMode] = useState('tree')
  const [search, setSearch] = useState('')
  const [expandAll, setExpandAll] = useState(false)

  const pretty = useMemo(() => JSON.stringify(value ?? {}, null, 2), [value])

  async function copyJson() {
    await navigator.clipboard.writeText(pretty)
  }

  return (
    <section className="json-viewer">
      <div className="toolbar">
        <button onClick={() => setMode('tree')} className={mode === 'tree' ? 'active' : ''}>Tree</button>
        <button onClick={() => setMode('raw')} className={mode === 'raw' ? 'active' : ''}>Raw</button>
        <button onClick={copyJson}>Copy JSON</button>
        <button onClick={() => setExpandAll(true)}>Expand all</button>
        <button onClick={() => setExpandAll(false)}>Collapse</button>
        <input
          placeholder="Search key/value"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {mode === 'raw' ? (
        <pre className="json-raw">{pretty}</pre>
      ) : (
        <div className="json-tree">{renderTree(value, search, 0, expandAll)}</div>
      )}
    </section>
  )
}
