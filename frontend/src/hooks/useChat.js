import { useState } from 'react'
import { useAppContext, INDEXER_OPTIONS } from '../context/AppContext'
import { startChatSession, sendChatMessage, resetChat } from '../services/api'

export function useChat() {
  const { indexer, messages, setMessages, sessionId, setSessionId} = useAppContext()
  const [isLoading, setIsLoading] = useState(false)

  const addMessage = (role, text, sources = []) => {
    const msg = { id: crypto.randomUUID(), role, text, sources }
    setMessages((prev) => [...prev, msg])
    return msg
  }

  const getOrCreateSession = async () => {
    if (sessionId) return sessionId
    const { data } = await startChatSession()
    setSessionId(data.session_id)
    return data.session_id
  }

  const sendMessage = async (question) => {
    if (!question.trim() || isLoading) return
    addMessage('user', question)
    setIsLoading(true)

    try {
      const sid = await getOrCreateSession()
      const activeIndexer = INDEXER_OPTIONS.find((o) => o.value === indexer)
      const { data } = await sendChatMessage(
        sid,
        question,
        activeIndexer.llm_model,
        activeIndexer.embedding_provider
      )
      console.log('API response:', data)
      const sources = data.retrieved_chunks ?? []
      addMessage('bot', data.answer, sources)
    } catch {
      addMessage('bot', 'Something went wrong. Is the backend running?')
    } finally {
      setIsLoading(false)
    }
  }

  const resetChatHistory = async () => {
    await resetChat()
    setMessages([])
    setSessionId(null)
  }

  return { messages, isLoading, sendMessage, resetChatHistory }
}
