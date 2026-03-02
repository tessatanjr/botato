import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

export default function MessageList({ messages, isLoading }) {
  const bottomRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-center text-zinc-600 gap-3">
        <span className="text-4xl opacity-40">🥔</span>
        <p className="text-zinc-500 font-medium">Botato is ready to chat</p>
        <p className="text-xs max-w-xs">
          Upload and index your documents, then ask anything.
        </p>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
      {messages.map((m) => (
        <MessageBubble
          key={m.id}
          role={m.role}
          text={m.text}
          sources={m.sources}
        />
      ))}
      {isLoading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}
