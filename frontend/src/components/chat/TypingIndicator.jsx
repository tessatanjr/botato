export default function TypingIndicator() {
  return (
    <div className="flex gap-3 max-w-2xl">
      <div className="w-8 h-8 rounded-lg bg-emerald-950 border border-emerald-800 flex items-center justify-center text-xs font-mono text-emerald-400 flex-shrink-0">
        AI
      </div>
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl rounded-tl-sm px-4 py-3 flex gap-1.5 items-center">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-zinc-500 animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  )
}
