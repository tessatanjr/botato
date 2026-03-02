import SourceChunks from './SourceChunks'

export default function MessageBubble({ role, text, sources = [] }) {
  const isUser = role === 'user'

  return (
    <div
      className={`flex gap-3 max-w-2xl ${isUser ? 'self-end flex-row-reverse' : ''}`}
    >
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-mono flex-shrink-0
        ${
          isUser
            ? 'bg-zinc-800 border border-zinc-700 text-zinc-400'
            : 'bg-emerald-950 border border-emerald-800 text-emerald-400'
        }`}
      >
        {isUser ? 'U' : 'AI'}
      </div>

      <div
        className={`rounded-xl px-4 py-3 text-sm leading-relaxed
        ${
          isUser
            ? 'bg-emerald-950 border border-emerald-900 text-emerald-100 rounded-tr-sm'
            : 'bg-zinc-900 border border-zinc-800 text-zinc-200 rounded-tl-sm'
        }`}
      >
        <p className="whitespace-pre-wrap">{text}</p>
        {!isUser && <SourceChunks chunks={sources} />}
      </div>
    </div>
  )
}
