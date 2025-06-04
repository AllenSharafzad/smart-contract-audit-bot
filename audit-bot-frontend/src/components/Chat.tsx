
'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, AlertCircle } from 'lucide-react'

interface Message {
  id: string
  content: string
  sender: 'user' | 'bot'
  timestamp: Date
  contextUsed?: boolean
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your Smart Contract Audit Bot. I can help you with security analysis, vulnerability explanations, and best practices. What would you like to know?',
      sender: 'bot',
      timestamp: new Date(),
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [includeContext, setIncludeContext] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          include_context: includeContext,
        }),
      })

      const data = await response.json()

      if (data.success) {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response,
          sender: 'bot',
          timestamp: new Date(),
          contextUsed: data.context_used,
        }
        setMessages(prev => [...prev, botMessage])
      } else {
        throw new Error(data.error || 'Failed to get response')
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        sender: 'bot',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearConversation = async () => {
    try {
      await fetch('http://localhost:8000/clear-conversation', {
        method: 'POST',
      })
      setMessages([
        {
          id: '1',
          content: 'Conversation cleared! How can I help you with smart contract security?',
          sender: 'bot',
          timestamp: new Date(),
        }
      ])
    } catch (error) {
      console.error('Failed to clear conversation:', error)
    }
  }

  const formatMessage = (content: string) => {
    // Simple formatting for code blocks and lists
    return content.split('\n').map((line, index) => {
      if (line.startsWith('```')) {
        return null // Handle code blocks separately if needed
      }
      if (line.startsWith('- ') || line.startsWith('* ')) {
        return (
          <li key={index} className="ml-4 list-disc">
            {line.substring(2)}
          </li>
        )
      }
      if (line.startsWith('## ')) {
        return (
          <h3 key={index} className="text-lg font-semibold mt-4 mb-2 text-purple-300">
            {line.substring(3)}
          </h3>
        )
      }
      if (line.trim() === '') {
        return <br key={index} />
      }
      return (
        <p key={index} className="mb-2">
          {line}
        </p>
      )
    })
  }

  return (
    <div className="flex flex-col h-[600px]">
      {/* Chat Header */}
      <div className="p-4 border-b border-slate-700 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="includeContext"
              checked={includeContext}
              onChange={(e) => setIncludeContext(e.target.checked)}
              className="rounded border-slate-600 bg-slate-700 text-purple-600 focus:ring-purple-500"
            />
            <label htmlFor="includeContext" className="text-sm text-slate-300">
              Use uploaded contracts as context
            </label>
          </div>
        </div>
        <button
          onClick={clearConversation}
          className="px-3 py-1 text-sm bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-md transition-colors"
        >
          Clear Chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.sender === 'user'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-100'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  {message.sender === 'user' ? (
                    <User className="w-5 h-5 mt-1" />
                  ) : (
                    <Bot className="w-5 h-5 mt-1 text-purple-400" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="prose prose-invert max-w-none">
                    {formatMessage(message.content)}
                  </div>
                  <div className="flex items-center justify-between mt-2 text-xs opacity-70">
                    <span>{message.timestamp.toLocaleTimeString()}</span>
                    {message.contextUsed && (
                      <span className="flex items-center space-x-1 text-green-400">
                        <AlertCircle className="w-3 h-3" />
                        <span>Context used</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 text-slate-100 rounded-lg p-4 max-w-[80%]">
              <div className="flex items-center space-x-3">
                <Bot className="w-5 h-5 text-purple-400" />
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-700">
        <div className="flex space-x-3">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about smart contract security, vulnerabilities, or best practices..."
            className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
