import { useState } from 'react'
import { ChevronDown, ChevronUp, FileText } from 'lucide-react'

function ChunkItem({ chunk, index }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="border border-zinc-700 rounded-lg overflow-hidden">
      {/* Header — always visible */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-full flex items-center justify-between px-3 py-2 bg-zinc-800 hover:bg-zinc-700 transition-colors text-left"
      >
        <div className="flex items-center gap-2 min-w-0">
          <FileText size={12} className="text-emerald-400 flex-shrink-0" />
          <span className="text-xs font-mono text-zinc-300 truncate">
            {chunk.source}
          </span>
          <span className="text-xs font-mono text-zinc-600 flex-shrink-0">
            · {chunk.index}
          </span>
        </div>
        {isOpen ? (
          <ChevronUp size={12} className="text-zinc-500 flex-shrink-0 ml-2" />
        ) : (
          <ChevronDown size={12} className="text-zinc-500 flex-shrink-0 ml-2" />
        )}
      </button>

      {/* Chunk text — shown when open */}
      {isOpen && (
        <div className="px-3 py-2.5 bg-zinc-900 border-t border-zinc-700">
          <p className="text-xs text-zinc-400 leading-relaxed whitespace-pre-wrap font-mono">
            {chunk.text}
          </p>
        </div>
      )}
    </div>
  )
}

export default function SourceChunks({ chunks }) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!chunks || chunks.length === 0) return null

  // deduplicate by index + source combination
  const unique = chunks.filter(
    (chunk, i, self) =>
      i ===
      self.findIndex(
        (c) => c.index === chunk.index && c.source === chunk.source
      )
  )

  return (
    <div className="mt-3 pt-3 border-t border-zinc-700">
      {/* Toggle to show/hide all chunks */}
      <button
        onClick={() => setIsExpanded((prev) => !prev)}
        className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors mb-2"
      >
        {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        <span className="font-mono">
          {unique.length} source chunk{unique.length !== 1 ? 's' : ''} retrieved
        </span>
      </button>

      {/* Chunk list */}
      {isExpanded && (
        <div className="flex flex-col gap-1.5">
          {unique.map((chunk, i) => (
            <ChunkItem key={i} chunk={chunk} index={i + 1} />
          ))}
        </div>
      )}
    </div>
  )
}
