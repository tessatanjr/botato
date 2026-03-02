import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

const client = axios.create({ baseURL: BASE_URL })

export const ingestFile = async (fileOrUrl, embeddingProvider) => {
  const form = new FormData()
  form.append('embedding_provider', embeddingProvider)

  if (typeof fileOrUrl === 'string') {
    form.append('url', fileOrUrl)
  } else {
    form.append('file', fileOrUrl)
  }

  const res = await axios.post('/api/upload', form)

  return res.data
}

// returns sessionid
export const startChatSession = () => client.post('/chat/start')

export const sendChatMessage = (
  sessionId,
  question,
  llmModel,
  embeddingProvider,
  topK = 5
) =>
  client.post('/chat', {
    session_id: sessionId,
    question,
    llm_model: llmModel,
    embedding_provider: embeddingProvider,
    top_k: topK,
  })

// clear chat history
export const resetChat = () => client.post('/reset/chat')

// clears indexes + chat history
export const resetAll = async () => {
  await client.post('/reset', null, {
    params: { embedding_provider: 'openai' },
  })
  await client.post('/reset', null, {
    params: { embedding_provider: 'minilm' },
  })
  await client.post('/reset/chat')
}
