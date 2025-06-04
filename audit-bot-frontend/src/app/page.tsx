
'use client'

import { useState, useRef } from 'react'
import { Upload, MessageCircle, FileText, Shield, Zap, AlertTriangle } from 'lucide-react'
import Chat from '@/components/Chat'
import FileUpload from '@/components/FileUpload'
import ContractAnalysis from '@/components/ContractAnalysis'

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat')
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])

  const tabs = [
    { id: 'chat', label: 'Chat', icon: MessageCircle },
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'analyze', label: 'Analyze', icon: Shield },
  ]

  const features = [
    {
      icon: Shield,
      title: 'Security Analysis',
      description: 'Comprehensive vulnerability detection and security assessment'
    },
    {
      icon: Zap,
      title: 'Gas Optimization',
      description: 'Identify opportunities to reduce gas costs and improve efficiency'
    },
    {
      icon: AlertTriangle,
      title: 'Best Practices',
      description: 'Ensure compliance with Solidity coding standards and patterns'
    },
    {
      icon: FileText,
      title: 'Detailed Reports',
      description: 'Get comprehensive audit reports with actionable recommendations'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Smart Contract Audit Bot</h1>
                <p className="text-slate-400 text-sm">AI-Powered Security Analysis</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm text-slate-400">Files Uploaded</div>
                <div className="text-lg font-semibold text-white">{uploadedFiles.length}</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">
            Secure Your Smart Contracts with AI
          </h2>
          <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto">
            Upload your Solidity contracts and get comprehensive security analysis, 
            vulnerability detection, and optimization recommendations powered by advanced AI.
          </p>
          
          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {features.map((feature, index) => (
              <div key={index} className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                <feature.icon className="w-8 h-8 text-purple-400 mb-4 mx-auto" />
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-slate-400 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-1 border border-slate-700">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-md transition-all ${
                  activeTab === tab.id
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="max-w-6xl mx-auto">
          {activeTab === 'chat' && (
            <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700 overflow-hidden">
              <div className="p-6 border-b border-slate-700">
                <h3 className="text-xl font-semibold text-white mb-2">Chat with Audit Bot</h3>
                <p className="text-slate-400">
                  Ask questions about smart contract security, get explanations of vulnerabilities, 
                  or discuss best practices with our AI audit expert.
                </p>
              </div>
              <Chat />
            </div>
          )}

          {activeTab === 'upload' && (
            <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700 overflow-hidden">
              <div className="p-6 border-b border-slate-700">
                <h3 className="text-xl font-semibold text-white mb-2">Upload Smart Contracts</h3>
                <p className="text-slate-400">
                  Upload your Solidity (.sol) files to add them to the knowledge base for analysis and chat context.
                </p>
              </div>
              <FileUpload onUploadSuccess={(filename) => setUploadedFiles(prev => [...prev, filename])} />
            </div>
          )}

          {activeTab === 'analyze' && (
            <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700 overflow-hidden">
              <div className="p-6 border-b border-slate-700">
                <h3 className="text-xl font-semibold text-white mb-2">Contract Analysis</h3>
                <p className="text-slate-400">
                  Paste your contract code for comprehensive security analysis and improvement suggestions.
                </p>
              </div>
              <ContractAnalysis />
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center text-slate-400">
          <div className="border-t border-slate-700 pt-8">
            <p className="mb-4">
              Built with FastAPI, LangChain, Pinecone, and Next.js
            </p>
            <div className="flex justify-center space-x-6 text-sm">
              <a href="/docs" className="hover:text-white transition-colors">API Docs</a>
              <a href="/health" className="hover:text-white transition-colors">Health Check</a>
              <a href="https://github.com" className="hover:text-white transition-colors">GitHub</a>
            </div>
          </div>
        </footer>
      </main>
    </div>
  )
}
