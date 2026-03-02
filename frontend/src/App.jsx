import { AppProvider } from './context/AppContext'
import Header from './components/layout/Header'
import UploadZone from './components/ingestion/UploadZone'
import ChatPanel from './components/chat/ChatPanel'

export default function App() {
  return (
    <AppProvider>
      <div className="flex flex-col h-screen bg-zinc-950 text-zinc-200 overflow-hidden">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <aside className="w-80 flex-shrink-0 border-r border-zinc-800 bg-zinc-900 flex flex-col overflow-hidden">
            <div className="p-4 border-b border-zinc-800">
              <h2 className="font-semibold text-zinc-200 text-sm">
                Document Ingestion
              </h2>
              <p className="text-xs text-zinc-500 mt-1">
                Upload docs to build your knowledge base
              </p>
            </div>
            <UploadZone />
          </aside>
          <ChatPanel />
        </div>
      </div>
    </AppProvider>
  )
}
