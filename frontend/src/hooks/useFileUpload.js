import { useAppContext, INDEXER_OPTIONS } from '../context/AppContext'
import { ingestFile, resetAll } from '../services/api'

export function useFileUpload() {
  const { files, setFiles, indexer } = useAppContext()
  const activeIndexer = INDEXER_OPTIONS.find((o) => o.value === indexer)

  const addFiles = (newFiles) => {
    const entries = newFiles
      .filter(
        (f) =>
          !files.find((x) => x.file.name === f.name && x.indexer === indexer)
      )
      .map((f) => ({
        id: crypto.randomUUID(),
        file: f,
        status: 'queued',
        indexer,
      }))
    setFiles((prev) => [...prev, ...entries])
  }

  const updateStatus = (id, status) =>
    setFiles((prev) => prev.map((f) => (f.id === id ? { ...f, status } : f)))

  const runIndexing = async () => {
    const queued = files.filter((f) => f.status === 'queued')
    for (const f of queued) {
      updateStatus(f.id, 'indexing')
      try {
        await ingestFile(f.file, activeIndexer.embedding_provider)
        updateStatus(f.id, 'done')
      } catch {
        updateStatus(f.id, 'error')
      }
    }
  }

  const resetDocuments = async () => {
    await resetAll()
    setFiles([])
  }

  return { files, addFiles, runIndexing, resetDocuments }
}
