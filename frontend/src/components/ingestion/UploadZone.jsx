import { useRef, useState } from 'react'
import FileList from './FileList'
import { useFileUpload } from '../../hooks/useFileUpload'
import { useChat } from '../../hooks/useChat'

export default function UploadZone() {
  const { files, addFiles, addUrl, runIndexing, resetDocuments } =
    useFileUpload()
  const [urlInput, setUrlInput] = useState('')

  const { resetChatHistory } = useChat()
  const [dragging, setDragging] = useState(false)
  const [indexing, setIndexing] = useState(false)
  const [resetting, setResetting] = useState(false)
  const inputRef = useRef()

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    addFiles([...e.dataTransfer.files])
  }

  const handleAddUrl = () => {
    const trimmed = urlInput.trim()
    if (!trimmed) return
    addUrl(trimmed)
    setUrlInput('')
  }

  const handleIndex = async () => {
    setIndexing(true)
    await runIndexing()
    setIndexing(false)
  }

  // only clears chat — documents stay
  const handleResetChat = async () => {
    setResetting(true)
    await resetChatHistory()
    setResetting(false)
  }

  // clears everything — documents + index + chat
  const handleResetAll = async () => {
    setResetting(true)
    await resetDocuments()
    await resetChatHistory()
    setResetting(false)
  }

  const busy = indexing || resetting

  return (
    <div className="flex flex-col gap-4 p-4 flex-1 overflow-hidden">
      <div
        onClick={() => inputRef.current.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
                ${dragging ? 'border-emerald-400 bg-emerald-950/30' : 'border-zinc-700 hover:border-zinc-500'}`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf, .docx"
          className="hidden"
          onChange={(e) => {
            addFiles([...e.target.files])
            e.target.value = ''
          }}
        />
        <p className="text-3xl mb-2">📄</p>
        <p className="text-sm font-semibold text-zinc-300">Drop files here</p>
        <p className="text-xs text-zinc-500 mt-1">PDF or Word documents</p>
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Or paste a URL..."
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAddUrl()}
          className="flex-1 px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-700 
      text-sm text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-zinc-500"
        />
        <button
          onClick={handleAddUrl}
          disabled={!urlInput.trim()}
          className="px-3 py-2 rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-300 
      text-sm hover:bg-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Add
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        <FileList files={files} />
      </div>

      <div className="flex flex-col gap-2">
        <button
          onClick={handleIndex}
          disabled={files.length === 0 || busy}
          className="w-full py-3 rounded-lg bg-emerald-500 text-zinc-950 font-semibold text-sm
            hover:bg-emerald-400 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {indexing ? '⏳ Indexing…' : '⚡ Index Documents'}
        </button>

        {/* Divider */}
        <div className="flex items-center gap-2 py-1">
          <div className="flex-1 h-px bg-zinc-800" />
          <span className="text-xs text-zinc-600 font-mono">reset</span>
          <div className="flex-1 h-px bg-zinc-800" />
        </div>

        {/* Reset chat only */}
        <button
          onClick={handleResetChat}
          disabled={busy}
          className="w-full py-2.5 rounded-lg bg-zinc-800 text-zinc-300 font-medium text-sm border border-zinc-700
            hover:bg-zinc-700 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {resetting ? '⏳ Resetting…' : '💬 Clear Chat History'}
        </button>

        {/* Reset everything */}
        <button
          onClick={handleResetAll}
          disabled={busy}
          className="w-full py-2.5 rounded-lg bg-zinc-800 text-red-400 font-medium text-sm border border-zinc-700
            hover:bg-red-950 hover:border-red-800 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {resetting ? '⏳ Resetting…' : '🗑 Clear Everything'}
        </button>
      </div>
    </div>
  )
}
