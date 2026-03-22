import { useEffect, useMemo, useRef, useState } from 'react'

function countMatches(value, search) {
  if (!search) return 0

  if (value === null || typeof value !== 'object') {
    return String(value).toLowerCase().includes(search) ? 1 : 0
  }

  if (Array.isArray(value)) {
    return value.reduce((sum, item) => sum + countMatches(item, search), 0)
  }

  return Object.entries(value).reduce((sum, [key, val]) => {
    const keyMatches = key.toLowerCase().includes(search) ? 1 : 0
    return sum + keyMatches + countMatches(val, search)
  }, 0)
}

function renderMatch(text, matches, matchState) {
  if (!matches) {
    return <span>{text}</span>
  }

  const matchIndex = matchState.current
  matchState.current += 1
  const className = matchIndex === matchState.activeIndex ? 'hit active' : 'hit'

  return (
    <span className={className} data-match-index={matchIndex}>
      {text}
    </span>
  )
}

function shouldNodeBeOpen(expansionMode, depth) {
  if (expansionMode === 'all') return true
  if (expansionMode === 'none') return false
  return depth < 1
}

function renderTree(value, search, matchState, depth = 0, expansionMode = 'default') {
  if (value === null || typeof value !== 'object') {
    const text = String(value)
    const matches = search ? text.toLowerCase().includes(search) : false
    return renderMatch(text, matches, matchState)
  }

  if (Array.isArray(value)) {
    return (
      <div className="tree-array">
        {value.map((item, idx) => (
          <details key={`${depth}-${idx}`} open={shouldNodeBeOpen(expansionMode, depth)}>
            <summary>[{idx}]</summary>
            <div className="tree-node">{renderTree(item, search, matchState, depth + 1, expansionMode)}</div>
          </details>
        ))}
      </div>
    )
  }

  return (
    <div className="tree-object">
      {Object.entries(value).map(([key, val]) => {
        const keyHit = search ? key.toLowerCase().includes(search) : false
        const isExpandable = val !== null && typeof val === 'object'

        if (!isExpandable) {
          return (
            <div key={`${depth}-${key}`} className="tree-leaf">
              <span className="key">
                {renderMatch(key, keyHit, matchState)}:
              </span>{' '}
              {renderTree(val, search, matchState, depth + 1, expansionMode)}
            </div>
          )
        }

        return (
          <details key={`${depth}-${key}`} open={shouldNodeBeOpen(expansionMode, depth)}>
            <summary>
              <span className="key">{renderMatch(key, keyHit, matchState)}</span>
            </summary>
            <div className="tree-node">{renderTree(val, search, matchState, depth + 1, expansionMode)}</div>
          </details>
        )
      })}
    </div>
  )
}

export default function JsonViewer({ value }) {
  const [mode, setMode] = useState('tree')
  const [search, setSearch] = useState('')
  const [expansionMode, setExpansionMode] = useState('default')
  const [activeMatchIndex, setActiveMatchIndex] = useState(0)
  const [treeVersion, setTreeVersion] = useState(0)
  const treeRef = useRef(null)

  const pretty = useMemo(() => JSON.stringify(value ?? {}, null, 2), [value])
  const normalizedSearch = search.trim().toLowerCase()
  const totalMatches = useMemo(() => countMatches(value, normalizedSearch), [value, normalizedSearch])

  useEffect(() => {
    setActiveMatchIndex(0)
  }, [normalizedSearch])

  useEffect(() => {
    if (!normalizedSearch || !totalMatches) return
    if (activeMatchIndex < totalMatches) return
    setActiveMatchIndex(totalMatches - 1)
  }, [activeMatchIndex, normalizedSearch, totalMatches])

  useEffect(() => {
    if (!normalizedSearch || mode !== 'tree') return
    const activeMatch = treeRef.current?.querySelector(`[data-match-index="${activeMatchIndex}"]`)
    let currentNode = activeMatch?.parentElement
    while (currentNode) {
      if (currentNode.tagName === 'DETAILS') {
        currentNode.open = true
      }
      currentNode = currentNode.parentElement
    }
    activeMatch?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, [activeMatchIndex, mode, normalizedSearch, totalMatches])

  async function copyJson() {
    await navigator.clipboard.writeText(pretty)
  }

  function moveMatch(step) {
    if (!totalMatches) return
    setActiveMatchIndex((current) => (current + step + totalMatches) % totalMatches)
  }

  function handleExpandAll() {
    setExpansionMode('all')
    setTreeVersion((current) => current + 1)
  }

  function handleCollapse() {
    setExpansionMode('none')
    setTreeVersion((current) => current + 1)
  }

  const matchState = { current: 0, activeIndex: activeMatchIndex }

  return (
    <section className="json-viewer">
      <div className="toolbar">
        <button onClick={() => setMode('tree')} className={mode === 'tree' ? 'active' : ''}>Tree</button>
        <button onClick={() => setMode('raw')} className={mode === 'raw' ? 'active' : ''}>Raw</button>
        <button onClick={copyJson}>Copy JSON</button>
        <button onClick={handleExpandAll}>Expand all</button>
        <button onClick={handleCollapse}>Collapse</button>
        {mode === 'tree' && (
          <>
            <input
              placeholder="Search key/value"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {normalizedSearch && (
              <>
                <span className="match-counter">
                  {totalMatches ? `${activeMatchIndex + 1}/${totalMatches}` : '0/0'}
                </span>
                <button onClick={() => moveMatch(-1)} disabled={!totalMatches}>↑</button>
                <button onClick={() => moveMatch(1)} disabled={!totalMatches}>↓</button>
              </>
            )}
          </>
        )}
      </div>

      {mode === 'raw' ? (
        <pre className="json-raw">{pretty}</pre>
      ) : (
        <div key={`tree-${treeVersion}-${expansionMode}`} ref={treeRef} className="json-tree">
          {renderTree(value, normalizedSearch, matchState, 0, expansionMode)}
        </div>
      )}
    </section>
  )
}
