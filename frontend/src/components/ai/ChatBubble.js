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
          ? 'bg-emerald-500/15 border border-emerald-500/25'
          : 'bg-blue-500/15 border border-blue-500/25'
      )}>
        {isUser
          ? <User size={14} className="text-emerald-400" />
          : <Bot size={14} className="text-blue-400" />
        }
      </div>

      {/* Bubble */}
      <div className={clsx(
        'max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed',
        isUser
          ? 'bg-emerald-500/10 border border-emerald-500/15 text-emerald-50 rounded-tr-sm'
          : 'bg-[#111827] border border-[#1e2d3d] text-slate-200 rounded-tl-sm'
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
