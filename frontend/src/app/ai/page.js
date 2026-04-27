'use client'
import { useState, useRef, useEffect } from 'react'
import { aiApi } from '@/utils/api'
import AppLayout from '@/components/ui/AppLayout'
import { Bot, Send, User, Sparkles, RotateCcw } from 'lucide-react'
import clsx from 'clsx'

const STARTER_QUESTIONS = [
  "Why am I losing money?",
  "What should I fix in my spending?",
  "How many days can my business survive?",
  "Which expense category should I cut?",
  "Am I making a good profit this month?",
  "What is my biggest financial risk?",
]

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={clsx('flex gap-3 animate-fade-in', isUser ? 'flex-row-reverse' : 'flex-row')}>
      <div className={clsx('w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5',
        isUser ? 'bg-[#0F6B4F]/15 border border-[#0F6B4F]/25' : 'bg-blue-500/15 border border-blue-500/25')}>
        {isUser ? <User size={14} className="text-[#10B981]" /> : <Bot size={14} className="text-blue-400" />}
      </div>
      <div className={clsx('max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed',
        isUser
          ? 'bg-[#0F6B4F]/10 border border-[#0F6B4F]/15 text-emerald-50 rounded-tr-sm'
          : 'bg-[#121821] border border-[#1A2535] text-[#E5E7EB] rounded-tl-sm')}>
        {msg.content}
      </div>
    </div>
  )
}

export default function AIPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const msg = text || input.trim()
    if (!msg || loading) return
    setInput('')
    setError('')

    const userMsg = { role: 'user', content: msg }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }))
      const res = await aiApi.chat(msg, history)
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }])
    } catch (err) {
      setError('Failed to get AI response. Check your API key configuration.')
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const reset = () => { setMessages([]); setError('') }

  return (
    <AppLayout>
      <div className="flex flex-col h-[calc(100vh-8rem)] md:h-[calc(100vh-4rem)] stagger-children">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-blue-500/15 border border-blue-500/25 flex items-center justify-center">
                <Bot size={14} className="text-blue-400" />
              </div>
              <h1 className="font-display font-bold text-2xl text-[#E5E7EB]">AI Advisor</h1>
              <span className="text-xs bg-[#0F6B4F]/15 text-[#10B981] px-2 py-0.5 rounded-full border border-[#0F6B4F]/25 font-semibold">LIVE DATA</span>
            </div>
            <p className="text-[#9CA3AF] text-sm mt-0.5 ml-9">Ask anything about your finances. Answers are based on your real data.</p>
          </div>
          {messages.length > 0 && (
            <button onClick={reset} className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5">
              <RotateCcw size={12} /> New Chat
            </button>
          )}
        </div>

        {/* Chat area */}
        <div className="flex-1 overflow-y-auto card p-4 space-y-4 min-h-0">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center py-8">
              <div className="w-14 h-14 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-4">
                <Sparkles size={24} className="text-blue-400" />
              </div>
              <h3 className="font-display font-semibold text-[#E5E7EB] mb-1">BiasharaIQ AI Advisor</h3>
              <p className="text-[#9CA3AF] text-sm mb-6 max-w-sm">
                I analyze your actual business data to give you specific, actionable financial advice — not generic tips.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
                {STARTER_QUESTIONS.map((q) => (
                  <button key={q} onClick={() => send(q)}
                    className="text-left text-xs p-3 rounded-lg bg-[#121821] border border-[#1A2535] hover:border-[#0F6B4F] text-[#9CA3AF] hover:text-[#E5E7EB] transition-all">
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => <Message key={i} msg={msg} />)}
              {loading && (
                <div className="flex gap-3 animate-fade-in">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/15 border border-blue-500/25 flex items-center justify-center flex-shrink-0">
                    <Bot size={14} className="text-blue-400" />
                  </div>
                  <div className="bg-[#121821] border border-[#1A2535] px-4 py-3 rounded-2xl rounded-tl-sm">
                    <div className="flex items-center gap-1.5">
                      {[0, 150, 300].map(d => (
                        <div key={d} className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse-soft" style={{ animationDelay: `${d}ms` }} />
                      ))}
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </>
          )}
        </div>

        {error && (
          <div className="mt-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">{error}</div>
        )}

        {/* Input */}
        <div className="mt-3 flex gap-3">
          <input
            ref={inputRef}
            className="input-dark flex-1"
            placeholder="Ask about your finances..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
            disabled={loading}
          />
          <button
            onClick={() => send()}
            disabled={!input.trim() || loading}
            className="btn-primary px-4 disabled:opacity-40"
          >
            <Send size={16} />
          </button>
        </div>
        <p className="text-xs text-[#4B5563] text-center mt-2">
          Responses are grounded in your actual transaction data. No hallucinations.
        </p>
      </div>
    </AppLayout>
  )
}
