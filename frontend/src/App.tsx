import { useState, useRef, useEffect } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  citations?: string[]
}

// API URL: from config.json (deployed) or env (local)
function useApiUrl() {
  const [apiUrl, setApiUrl] = useState<string>(
    (import.meta.env.VITE_API_URL as string) || '/api'
  )
  const [configLoaded, setConfigLoaded] = useState(!import.meta.env.PROD || !!import.meta.env.VITE_API_URL)

  useEffect(() => {
    // In production, load from config.json (set at deploy time)
    if (import.meta.env.PROD && !import.meta.env.VITE_API_URL) {
      fetch('/config.json?t=' + Date.now())
        .then((r) => r.json())
        .then((c) => {
          if (c.apiUrl) setApiUrl(c.apiUrl)
          setConfigLoaded(true)
        })
        .catch(() => setConfigLoaded(true))
    }
  }, [])

  return { apiUrl, configLoaded }
}

function App() {
  const { apiUrl, configLoaded } = useApiUrl()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => crypto.randomUUID())
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  useEffect(scrollToBottom, [messages])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setMessages((prev: Message[]) => [...prev, { role: 'user', content: text }])
    setLoading(true)

    try {
      const chatMessages = [...messages, { role: 'user', content: text }].map((m) => ({
        role: m.role,
        content: m.content,
      }))

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 90000) // 90s (Lambda timeout is 60s)
      const res = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: chatMessages, session_id: sessionId }),
        signal: controller.signal,
      })
      clearTimeout(timeoutId)

      const responseText = await res.text()
      if (!res.ok) {
        const err = (() => {
          try {
            return JSON.parse(responseText)
          } catch {
            return {}
          }
        })()
        throw new Error(err.detail || err.error || `HTTP ${res.status}`)
      }

      const data = (() => {
        try {
          return JSON.parse(responseText)
        } catch {
          throw new Error('Invalid response from server. Try refreshing the page.')
        }
      })()
      setMessages((prev: Message[]) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          citations: data.citations,
        },
      ])
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to get response'
      const hint = msg.includes('403')
        ? ' The API may be restricted or the config is outdated. Try refreshing the page.'
        : msg.includes('Invalid response') || msg.includes('<!DOCTYPE')
        ? ' The server returned an error page. Try refreshing or wait a few minutes for deployment.'
        : msg.includes('abort') || msg.includes('AbortError')
        ? ' Request timed out. The API may be slow — try again.'
        : msg.includes('fetch') || msg.includes('Failed')
        ? ' Make sure the backend is running (uvicorn app:app --reload) and AWS credentials are configured.'
        : ''
      setMessages((prev: Message[]) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${msg}.${hint}`,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const suggestedQuestions: { name: string; question: string }[] = [
    { name: 'Buying SaaS ($18k)', question: 'I need to buy a SaaS tool for my team — $18k/year. What do I do?' },
    { name: 'New vendor paperwork', question: 'We want to use a new vendor. What paperwork is required?' },
    { name: 'SOW template & email', question: 'Give me the SOW template and draft an email to procurement with the required intake details.' },
    { name: "Today's date", question: "What is the date today?" },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-ink-700/60 px-6 py-5 backdrop-blur-sm bg-ink-950/80">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-amber to-amber-600 flex items-center justify-center text-ink-950 font-bold text-lg shadow-lg shadow-amber-500/20">
            P
          </div>
          <div>
            <h1 className="text-xl font-semibold text-ink-300 tracking-tight">
              Policy Knowledge Agent
            </h1>
            <p className="text-sm text-ink-400 mt-0.5 flex items-center gap-2 flex-wrap">
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-ink-800 border border-ink-600/50 text-ink-300 text-xs font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-accent-amber animate-pulse" />
                Policy knowledge base
              </span>
              <span className="text-ink-500">•</span>
              <span className="text-ink-400">Answers with citations</span>
              <span className="text-ink-500">•</span>
              <span className="text-accent-cyan">Web search when needed</span>
            </p>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-6 py-8 max-w-3xl mx-auto w-full">
        {messages.length === 0 ? (
          <div className="space-y-8">
            <div className="text-center space-y-3">
              <p className="text-ink-400 text-lg">
                Ask <span className="text-accent-amber font-medium">anything</span> — policy, process, or general questions.
              </p>
              <p className="text-ink-500 text-sm max-w-md mx-auto">
                Grounded in your procurement policies. Searches the web when the knowledge base doesn&apos;t have the answer.
              </p>
            </div>
            <div className="space-y-3">
              <p className="text-xs font-medium text-ink-500 uppercase tracking-wider">Try these</p>
              <div className="grid gap-2">
                {suggestedQuestions.map((item) => (
                  <button
                    key={item.question}
                    onClick={() => setInput(item.question)}
                    className="group block w-full text-left px-4 py-3.5 rounded-xl bg-ink-800/60 border border-ink-600/40 hover:border-accent-amber/40 hover:bg-ink-800 transition-all duration-200 text-sm text-ink-300 hover:text-ink-100"
                  >
                    <span className="font-medium text-ink-400 group-hover:text-accent-amber transition-colors">{item.name}</span>
                    <span className="block mt-1 text-ink-200 group-hover:text-ink-100 transition-colors">{item.question}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((m: Message, i: number) => (
              <div
                key={i}
                className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3.5 ${
                    m.role === 'user'
                      ? 'bg-gradient-to-br from-accent-amber to-amber-600 text-ink-950 font-medium shadow-lg shadow-amber-500/20'
                      : 'bg-ink-700/90 border border-ink-600/50 text-white backdrop-blur-sm'
                  }`}
                >
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</div>
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-ink-500/50 text-xs text-ink-300">
                      Sources: {m.citations.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-ink-700/90 border border-ink-600/50 rounded-2xl px-4 py-3.5 backdrop-blur-sm">
                  <div className="flex gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-accent-amber animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 rounded-full bg-accent-amber animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 rounded-full bg-accent-amber animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      <footer className="border-t border-ink-700/60 px-6 py-4 backdrop-blur-sm bg-ink-950/60">
        <form
          onSubmit={(e: React.FormEvent) => {
            e.preventDefault()
            sendMessage()
          }}
          className="flex gap-3 max-w-3xl mx-auto"
        >
          <input
            type="text"
            value={input}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
            placeholder="Ask anything — policy, process, or general..."
            className="flex-1 rounded-xl bg-ink-800/80 border border-ink-600/40 px-4 py-3 text-ink-100 placeholder-ink-500 focus:outline-none focus:ring-2 focus:ring-accent-amber/40 focus:border-accent-amber/60 transition-all"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim() || !configLoaded}
            title={!configLoaded ? 'Loading...' : undefined}
            className="px-6 py-3 rounded-xl bg-gradient-to-br from-accent-amber to-amber-600 text-ink-950 font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-amber-500/20 transition-all"
          >
            Send
          </button>
        </form>
      </footer>
    </div>
  )
}

export default App
