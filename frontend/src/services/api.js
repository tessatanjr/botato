import axios from 'axios'

const client = axios.create({ baseURL: '/api' })

// Upload & index a file
export const ingestFile = (file, embeddingProvider) => {
  const form = new FormData()
  form.append('file', file)
  form.append('embedding_provider', embeddingProvider)
  return client.post('/upload', form)
}

// Start a new chat session — returns { session_id }
export const startChatSession = () => client.post('/chat/start')

// Send a message in an existing session
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

// clears chat history only — documents stay indexed
export const resetChat = () => client.post('/reset/chat')

// clears documents + index + chat history
export const resetAll = async () => {
  await client.post('/reset', null, {
    params: { embedding_provider: 'openai' },
  })
  await client.post('/reset', null, {
    params: { embedding_provider: 'minilm' },
  })
  await client.post('/reset/chat')
}
