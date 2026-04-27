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
          ? 'bg-[#0F6B4F]/15 border border-[#0F6B4F]/25'
          : 'bg-blue-500/15 border border-blue-500/25'
      )}>
        {isUser
          ? <User size={14} className="text-[#10B981]" />
          : <Bot size={14} className="text-blue-400" />
        }
      </div>

      {/* Bubble */}
      <div className={clsx(
        'max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed',
        isUser
          ? 'bg-[#0F6B4F]/10 border border-[#0F6B4F]/15 text-emerald-50 rounded-tr-sm'
          : 'bg-[#121821] border border-[#1A2535] text-[#E5E7EB] rounded-tl-sm'
      )}>
        {loading ? (
          <div className="flex items-center gap-1.5 py-0.5">
            {[0, 150, 300].map(delay => (
              <div
                key={delay}
                className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse-soft"
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
