import { useAppContext, INDEXER_OPTIONS } from '../../context/AppContext'

export default function Header() {
  const { indexer, setIndexer } = useAppContext()

  return (
    <header className="flex items-center justify-between px-6 h-14 border-b border-zinc-800 bg-zinc-950 flex-shrink-0">
      <span className="font-serif text-xl text-emerald-400 tracking-tight">
        botato <span className="text-zinc-500 italic">studio</span>
      </span>

      <div className="flex items-center gap-3">
        <span className="text-xs text-zinc-500 font-mono">model</span>
        <select
          value={indexer}
          onChange={(e) => setIndexer(e.target.value)}
          className="bg-zinc-900 border border-zinc-700 text-zinc-300 text-xs font-mono px-3 py-1.5 rounded-full outline-none cursor-pointer hover:border-zinc-500 transition-colors"
        >
          {INDEXER_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
      </div>
    </header>
  )
}
