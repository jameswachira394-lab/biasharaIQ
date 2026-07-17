import { Bot, User } from 'lucide-react'
import clsx from 'clsx'

export default function ChatBubble({ role, content, loading = false }) {
  const isUser = role === 'user'

  return (
    <div className={clsx('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
      {/* Avatar */}
      <div className={clsx(
        'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5',
        isUser
          ? 'bg-[#2E7D32]/15 border border-[#2E7D32]/25'
          : 'bg-[#1A1F71]/15 border border-[#1A1F71]/25'
      )}>
        {isUser
          ? <User size={14} className="text-[#2E7D32]" />
          : <Bot size={14} className="text-[#1A1F71]" />
        }
      </div>

      {/* Bubble */}
      <div className={clsx(
        'max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed',
        isUser
          ? 'bg-[#2E7D32]/10 border border-[#2E7D32]/15 text-[#1E1E1E] rounded-tr-sm'
          : 'bg-[#0A2540] border border-[#F5F5F5] text-[#FFFFFF] rounded-tl-sm'
      )}>
        {loading ? (
          <div className="flex items-center gap-1.5 py-0.5">
            {[0, 150, 300].map(delay => (
              <div
                key={delay}
                className="w-1.5 h-1.5 rounded-full bg-[#2E7D32] animate-pulse-soft"
                style={{ animationDelay: `${delay}ms` }}
              />
            ))}
          </div>
        ) : (
          <p className="whitespace-pre-wrap">{content}</p>
        )}
      </div>
    </div>
  )
}
