import { createContext, useContext, useState } from 'react'

const AppContext = createContext(null)

export const INDEXER_OPTIONS = [
  {
    value: 'openai_gpt4',
    label: 'GPT-4 · OpenAI Embeddings',
    llm_model: 'gpt-4',
    embedding_provider: 'openai',
  },
  {
    value: 'openai_gpt5',
    label: 'GPT-5 · OpenAI Embeddings',
    llm_model: 'gpt-5',
    embedding_provider: 'openai',
  },
  {
    value: 'openai_llama',
    label: 'Llama 3 · OpenAI Embeddings',
    llm_model: 'llama3:latest',
    embedding_provider: 'openai',
  },
  {
    value: 'minilm_gpt4',
    label: 'GPT-4 · MiniLM',
    llm_model: 'gpt-4',
    embedding_provider: 'minilm',
  },
  {
    value: 'minilm_gpt5',
    label: 'GPT-5 · MiniLM',
    llm_model: 'gpt-5',
    embedding_provider: 'minilm',
  },
  {
    value: 'minilm_llama',
    label: 'Llama 3 · MiniLM',
    llm_model: 'llama3:latest',
    embedding_provider: 'minilm',
  },
]

// global wrapper for the app in /src/App.jsx
export function AppProvider({ children }) {
  const [indexer, setIndexer] = useState('openai')
  const [files, setFiles] = useState([])
  const [messages, setMessages] = useState([])
  const [sessionId, setSessionId] = useState(null)

  return (
    <AppContext.Provider value={{ indexer, setIndexer, files, setFiles, messages, setMessages, sessionId, setSessionId }}>
      {children}
    </AppContext.Provider>
  )
}

// hook for components to access the context
export const useAppContext = () => useContext(AppContext)
