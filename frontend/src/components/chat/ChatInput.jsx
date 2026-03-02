import { useState, useRef } from 'react'
import { Send } from 'lucide-react'

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState('')
  const ref = useRef()

  const handleSend = () => {
    if (!value.trim() || disabled) return
    onSend(value.trim())
    setValue('')
    ref.current.style.height = 'auto'
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = (e) => {
    setValue(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 140) + 'px'
  }

  return (
    <div className="flex gap-3 items-end p-4 border-t border-zinc-800">
      <textarea
        ref={ref}
        rows={1}
        value={value}
        onChange={handleInput}
        onKeyDown={handleKey}
        placeholder="Ask something about your documents…"
        className="flex-1 bg-zinc-900 border border-zinc-700 focus:border-emerald-500 rounded-xl px-4 py-3 text-sm text-zinc-200 placeholder-zinc-600 resize-none outline-none transition-colors max-h-36"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        className="w-11 h-11 rounded-xl bg-emerald-500 text-zinc-950 flex items-center justify-center hover:bg-emerald-400 transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex-shrink-0"
      >
        <Send size={16} />
      </button>
    </div>
  )
}
