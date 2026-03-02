import FileItem from './FileItem'

export default function FileList({ files }) {
  if (files.length === 0) {
    return (
      <p className="text-xs text-zinc-600 text-center py-6">
        No files added yet
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs font-mono text-zinc-600 uppercase tracking-widest mb-1">
        Queued Documents
      </p>
      {files.map((f) => (
        <FileItem
          key={f.id}
          name={f.isUrl ? f.url : f.file.name}
          status={f.status}
          indexer={f.indexer}
          isUrl={f.isUrl}
        />
      ))}
    </div>
  )
}
