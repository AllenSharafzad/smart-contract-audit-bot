
'use client'

import { useState } from 'react'
import { Shield, Zap, AlertTriangle, FileText, Loader2, Copy, Check } from 'lucide-react'

interface AnalysisResult {
  success: boolean
  analysis?: string
  improvements?: string
  timestamp?: string
  error?: string
}

export default function ContractAnalysis() {
  const [contractCode, setContractCode] = useState('')
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [improvementsResult, setImprovementsResult] = useState<AnalysisResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isGettingImprovements, setIsGettingImprovements] = useState(false)
  const [activeTab, setActiveTab] = useState<'analysis' | 'improvements'>('analysis')
  const [copied, setCopied] = useState(false)

  const analyzeContract = async () => {
    if (!contractCode.trim()) return

    setIsAnalyzing(true)
    setAnalysisResult(null)

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contract_content: contractCode,
        }),
      })

      const data = await response.json()
      setAnalysisResult(data)
    } catch (error) {
      setAnalysisResult({
        success: false,
        error: error instanceof Error ? error.message : 'Analysis failed'
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getImprovements = async () => {
    if (!contractCode.trim()) return

    setIsGettingImprovements(true)
    setImprovementsResult(null)

    try {
      const response = await fetch('http://localhost:8000/improvements', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contract_content: contractCode,
        }),
      })

      const data = await response.json()
      setImprovementsResult(data)
    } catch (error) {
      setImprovementsResult({
        success: false,
        error: error instanceof Error ? error.message : 'Improvements analysis failed'
      })
    } finally {
      setIsGettingImprovements(false)
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    }
  }

  const formatAnalysisText = (text: string) => {
    return text.split('\n').map((line, index) => {
      if (line.startsWith('##')) {
        return (
          <h3 key={index} className="text-lg font-semibold mt-6 mb-3 text-purple-300">
            {line.substring(2).trim()}
          </h3>
        )
      }
      if (line.startsWith('###')) {
        return (
          <h4 key={index} className="text-md font-semibold mt-4 mb-2 text-blue-300">
            {line.substring(3).trim()}
          </h4>
        )
      }
      if (line.startsWith('- ') || line.startsWith('* ')) {
        return (
          <li key={index} className="ml-4 list-disc mb-1 text-slate-300">
            {line.substring(2)}
          </li>
        )
      }
      if (line.includes('CRITICAL') || line.includes('HIGH')) {
        return (
          <p key={index} className="mb-2 text-red-400 font-medium">
            {line}
          </p>
        )
      }
      if (line.includes('MEDIUM')) {
        return (
          <p key={index} className="mb-2 text-yellow-400 font-medium">
            {line}
          </p>
        )
      }
      if (line.includes('LOW') || line.includes('INFORMATIONAL')) {
        return (
          <p key={index} className="mb-2 text-blue-400 font-medium">
            {line}
          </p>
        )
      }
      if (line.trim() === '') {
        return <br key={index} />
      }
      return (
        <p key={index} className="mb-2 text-slate-300">
          {line}
        </p>
      )
    })
  }

  const sampleContract = `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleToken {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    
    function transfer(address to, uint256 amount) public {
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
    
    function mint(uint256 amount) public {
        totalSupply += amount;
        balances[msg.sender] += amount;
    }
}`

  return (
    <div className="p-6">
      {/* Contract Input */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-3">
          <label className="block text-sm font-medium text-white">
            Smart Contract Code
          </label>
          <button
            onClick={() => setContractCode(sampleContract)}
            className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
          >
            Load Sample Contract
          </button>
        </div>
        <textarea
          value={contractCode}
          onChange={(e) => setContractCode(e.target.value)}
          placeholder="Paste your Solidity contract code here..."
          className="w-full h-64 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm"
        />
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4 mb-6">
        <button
          onClick={analyzeContract}
          disabled={!contractCode.trim() || isAnalyzing}
          className="flex items-center space-x-2 px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
        >
          {isAnalyzing ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Shield className="w-5 h-5" />
          )}
          <span>Security Analysis</span>
        </button>

        <button
          onClick={getImprovements}
          disabled={!contractCode.trim() || isGettingImprovements}
          className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
        >
          {isGettingImprovements ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Zap className="w-5 h-5" />
          )}
          <span>Get Improvements</span>
        </button>
      </div>

      {/* Results */}
      {(analysisResult || improvementsResult) && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
          {/* Tab Navigation */}
          <div className="flex border-b border-slate-700">
            <button
              onClick={() => setActiveTab('analysis')}
              className={`flex items-center space-x-2 px-6 py-4 transition-colors ${
                activeTab === 'analysis'
                  ? 'bg-slate-700 text-white border-b-2 border-purple-500'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <Shield className="w-5 h-5" />
              <span>Security Analysis</span>
              {analysisResult && (
                <span className={`w-2 h-2 rounded-full ${
                  analysisResult.success ? 'bg-green-400' : 'bg-red-400'
                }`} />
              )}
            </button>
            <button
              onClick={() => setActiveTab('improvements')}
              className={`flex items-center space-x-2 px-6 py-4 transition-colors ${
                activeTab === 'improvements'
                  ? 'bg-slate-700 text-white border-b-2 border-purple-500'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <Zap className="w-5 h-5" />
              <span>Improvements</span>
              {improvementsResult && (
                <span className={`w-2 h-2 rounded-full ${
                  improvementsResult.success ? 'bg-green-400' : 'bg-red-400'
                }`} />
              )}
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'analysis' && analysisResult && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-white">Security Analysis Results</h3>
                  {analysisResult.success && (
                    <button
                      onClick={() => copyToClipboard(analysisResult.analysis || '')}
                      className="flex items-center space-x-2 px-3 py-1 text-sm bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-md transition-colors"
                    >
                      {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      <span>{copied ? 'Copied!' : 'Copy'}</span>
                    </button>
                  )}
                </div>
                {analysisResult.success ? (
                  <div className="prose prose-invert max-w-none">
                    {formatAnalysisText(analysisResult.analysis || '')}
                  </div>
                ) : (
                  <div className="flex items-center space-x-2 text-red-400">
                    <AlertTriangle className="w-5 h-5" />
                    <span>{analysisResult.error}</span>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'improvements' && improvementsResult && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-white">Improvement Suggestions</h3>
                  {improvementsResult.success && (
                    <button
                      onClick={() => copyToClipboard(improvementsResult.improvements || '')}
                      className="flex items-center space-x-2 px-3 py-1 text-sm bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-md transition-colors"
                    >
                      {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      <span>{copied ? 'Copied!' : 'Copy'}</span>
                    </button>
                  )}
                </div>
                {improvementsResult.success ? (
                  <div className="prose prose-invert max-w-none">
                    {formatAnalysisText(improvementsResult.improvements || '')}
                  </div>
                ) : (
                  <div className="flex items-center space-x-2 text-red-400">
                    <AlertTriangle className="w-5 h-5" />
                    <span>{improvementsResult.error}</span>
                  </div>
                )}
              </div>
            )}

            {/* Show placeholder if no results for active tab */}
            {activeTab === 'analysis' && !analysisResult && (
              <div className="text-center text-slate-400 py-8">
                <Shield className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Run security analysis to see results here</p>
              </div>
            )}

            {activeTab === 'improvements' && !improvementsResult && (
              <div className="text-center text-slate-400 py-8">
                <Zap className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Get improvement suggestions to see results here</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Analysis Tips */}
      <div className="mt-6 bg-slate-800/50 rounded-lg p-4 border border-slate-700">
        <h4 className="text-sm font-semibold text-white mb-2">Analysis Features</h4>
        <ul className="text-sm text-slate-400 space-y-1">
          <li>• <strong>Security Analysis:</strong> Comprehensive vulnerability detection and risk assessment</li>
          <li>• <strong>Improvements:</strong> Code optimization and best practice recommendations</li>
          <li>• <strong>Severity Levels:</strong> CRITICAL, HIGH, MEDIUM, LOW, and INFORMATIONAL findings</li>
          <li>• <strong>Context-Aware:</strong> Analysis considers uploaded contracts for better insights</li>
        </ul>
      </div>
    </div>
  )
}
