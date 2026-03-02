import MessageList from './MessageList'
import ChatInput from './ChatInput'
import { useChat } from '../../hooks/useChat'

export default function ChatPanel() {
  const { messages, isLoading, sendMessage } = useChat()

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <div className="px-6 py-3 border-b border-zinc-800 flex-shrink-0">
        <h2 className="text-sm font-medium text-zinc-400">Chat Interface</h2>
      </div>
      <MessageList messages={messages} isLoading={isLoading} />
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  )
}
