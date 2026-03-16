const STATUS = {
  queued: { label: 'ready', className: 'bg-zinc-800 text-zinc-400' },
  indexing: {
    label: 'indexing…',
    className: 'bg-yellow-950 text-yellow-400 animate-pulse',
  },
  done: { label: 'indexed', className: 'bg-emerald-950 text-emerald-400' },
  error: { label: 'error', className: 'bg-red-950 text-red-400' },
}

const INDEXER_LABELS = {
  openai_gpt4: { label: 'OpenAI', className: 'bg-blue-950 text-blue-400' },
  openai_gpt5: { label: 'OpenAI', className: 'bg-blue-950 text-blue-400' },
  openai_llama: { label: 'OpenAI', className: 'bg-blue-950 text-blue-400' },
  minilm_gpt4: { label: 'MiniLM', className: 'bg-purple-950 text-purple-400' },
  minilm_gpt5: { label: 'MiniLM', className: 'bg-purple-950 text-purple-400' },
  minilm_llama: { label: 'MiniLM', className: 'bg-purple-950 text-purple-400' },
}

export default function FileItem({ name, status, indexer, isUrl }) {
  const s = STATUS[status] || STATUS.queued
  const i = INDEXER_LABELS[indexer] || {
    label: indexer,
    className: 'bg-zinc-800 text-zinc-400',
  }

  const ext = isUrl ? 'URL' : name.split('.').pop().toUpperCase()

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-900 border border-zinc-800">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-zinc-200 truncate">{name}</p>
        <p className="text-xs text-zinc-500 font-mono">{ext}</p>
      </div>
      <span
        className={`text-xs font-mono px-2 py-1 rounded-full ${i.className}`}
      >
        {i.label}
      </span>
      <span
        className={`text-xs font-mono px-2 py-1 rounded-full ${s.className}`}
      >
        {s.label}
      </span>
    </div>
  )
}
