import { createContext, useContext, useState } from 'react'

const AppContext = createContext(null)

export const INDEXER_OPTIONS = [
  {
    value: 'openai_gpt4',
    label: 'GPT-4 · OpenAI Embeddings',
    llm_model: 'gpt-4',
    embedding_provider: 'openai',
    localOnly: false,
  },
  {
    value: 'openai_gpt5',
    label: 'GPT-5 · OpenAI Embeddings',
    llm_model: 'gpt-5',
    embedding_provider: 'openai',
    localOnly: false,
  },
  {
    value: 'openai_llama',
    label: 'Llama 3 · OpenAI Embeddings',
    llm_model: 'llama3:latest',
    embedding_provider: 'openai',
    localOnly: true,
  },
  {
    value: 'minilm_gpt4',
    label: 'GPT-4 · MiniLM',
    llm_model: 'gpt-4',
    embedding_provider: 'minilm',
    localOnly: false,
  },
  {
    value: 'minilm_gpt5',
    label: 'GPT-5 · MiniLM',
    llm_model: 'gpt-5',
    embedding_provider: 'minilm',
    localOnly: false,
  },
  {
    value: 'minilm_llama',
    label: 'Llama 3 · MiniLM',
    llm_model: 'llama3:latest',
    embedding_provider: 'minilm',
    localOnly: true,
  },
]

export function AppProvider({ children }) {
  const [indexer, setIndexer] = useState('openai_gpt4')
  const [files, setFiles] = useState([])
  const [messages, setMessages] = useState([])
  const [sessionId, setSessionId] = useState(null)

  return (
    <AppContext.Provider
      value={{
        indexer,
        setIndexer,
        files,
        setFiles,
        messages,
        setMessages,
        sessionId,
        setSessionId,
      }}
    >
      {children}
    </AppContext.Provider>
  )
}

// hook for components to access the context
export const useAppContext = () => useContext(AppContext)
