
'use client'

import { useState, useCallback } from 'react'
import { Upload, File, CheckCircle, XCircle, Loader2 } from 'lucide-react'

interface FileUploadProps {
  onUploadSuccess: (filename: string) => void
}

interface UploadResult {
  filename: string
  status: 'success' | 'error' | 'uploading'
  message: string
  fileHash?: string
  chunksAdded?: number
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    handleFiles(files)
  }, [])

  const handleFiles = async (files: File[]) => {
    for (const file of files) {
      await uploadFile(file)
    }
  }

  const uploadFile = async (file: File) => {
    const filename = file.name

    // Add uploading status
    setUploadResults(prev => [...prev, {
      filename,
      status: 'uploading',
      message: 'Uploading...'
    }])

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (data.success) {
        setUploadResults(prev => prev.map(result => 
          result.filename === filename
            ? {
                filename,
                status: 'success' as const,
                message: data.message,
                fileHash: data.file_hash,
                chunksAdded: data.chunks_added
              }
            : result
        ))
        onUploadSuccess(filename)
      } else {
        throw new Error(data.error || 'Upload failed')
      }
    } catch (error) {
      setUploadResults(prev => prev.map(result => 
        result.filename === filename
          ? {
              filename,
              status: 'error' as const,
              message: error instanceof Error ? error.message : 'Upload failed'
            }
          : result
      ))
    }
  }

  const clearResults = () => {
    setUploadResults([])
  }

  return (
    <div className="p-6">
      {/* Upload Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragOver
            ? 'border-purple-400 bg-purple-400/10'
            : 'border-slate-600 hover:border-slate-500'
        }`}
      >
        <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-white mb-2">
          Upload Smart Contract Files
        </h3>
        <p className="text-slate-400 mb-4">
          Drag and drop your .sol files here, or click to browse
        </p>
        <input
          type="file"
          multiple
          accept=".sol,.txt"
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="inline-flex items-center px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg cursor-pointer transition-colors"
        >
          <Upload className="w-5 h-5 mr-2" />
          Choose Files
        </label>
        <p className="text-xs text-slate-500 mt-2">
          Supported formats: .sol, .txt (Max 10MB per file)
        </p>
      </div>

      {/* Upload Results */}
      {uploadResults.length > 0 && (
        <div className="mt-6">
          <div className="flex justify-between items-center mb-4">
            <h4 className="text-lg font-semibold text-white">Upload Results</h4>
            <button
              onClick={clearResults}
              className="text-sm text-slate-400 hover:text-white transition-colors"
            >
              Clear
            </button>
          </div>
          <div className="space-y-3">
            {uploadResults.map((result, index) => (
              <div
                key={index}
                className="bg-slate-700/50 rounded-lg p-4 border border-slate-600"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {result.status === 'uploading' && (
                        <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                      )}
                      {result.status === 'success' && (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      )}
                      {result.status === 'error' && (
                        <XCircle className="w-5 h-5 text-red-400" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <File className="w-4 h-4 text-slate-400" />
                        <span className="font-medium text-white">{result.filename}</span>
                      </div>
                      <p className={`text-sm mt-1 ${
                        result.status === 'success' ? 'text-green-400' :
                        result.status === 'error' ? 'text-red-400' :
                        'text-blue-400'
                      }`}>
                        {result.message}
                      </p>
                      {result.status === 'success' && result.chunksAdded && (
                        <div className="text-xs text-slate-400 mt-1">
                          {result.chunksAdded} chunks added to knowledge base
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Tips */}
      <div className="mt-6 bg-slate-800/50 rounded-lg p-4 border border-slate-700">
        <h4 className="text-sm font-semibold text-white mb-2">Upload Tips</h4>
        <ul className="text-sm text-slate-400 space-y-1">
          <li>• Upload Solidity (.sol) files for best analysis results</li>
          <li>• Files are processed and added to the AI knowledge base</li>
          <li>• Uploaded contracts can be referenced in chat conversations</li>
          <li>• Duplicate files are automatically detected and skipped</li>
          <li>• Maximum file size: 10MB per file</li>
        </ul>
      </div>
    </div>
  )
}
