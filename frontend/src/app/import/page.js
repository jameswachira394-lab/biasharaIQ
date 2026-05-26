'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, FileText, CheckCircle, Loader } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import AppLayout from '@/components/ui/AppLayout'
import Toast from '@/components/ui/Toast'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ImportPage() {
    const router = useRouter()
    const { user } = useAuth()
    const [isDragging, setIsDragging] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [importSuccess, setImportSuccess] = useState(false)
    const [successData, setSuccessData] = useState(null)
    const [toast, setToast] = useState(null)

    const handleDragOver = (e) => {
        e.preventDefault()
        setIsDragging(true)
    }

    const handleDragLeave = () => {
        setIsDragging(false)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setIsDragging(false)
        const files = e.dataTransfer.files
        if (files.length > 0) {
            uploadFile(files[0])
        }
    }

    const uploadFile = async (file) => {
        if (!file) return

        // Validate file type
        const validTypes = [
            'application/pdf',
            'text/csv',
            'image/jpeg',
            'image/png',
            'image/webp',
        ]
        if (!validTypes.includes(file.type)) {
            setToast({
                type: 'error',
                message: 'Invalid file type. Please upload PDF, CSV, JPG, PNG, or WebP.',
            })
            return
        }

        // Validate file size (50MB max)
        if (file.size > 50 * 1024 * 1024) {
            setToast({
                type: 'error',
                message: 'File is too large. Maximum size is 50MB.',
            })
            return
        }

        setUploading(true)
        try {
            const formData = new FormData()
            formData.append('file', file)

            const token = typeof window !== 'undefined' ? localStorage.getItem('biasharaiq_token') : null

            const response = await axios.post(`${API_URL}/uploads/document`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    ...(token && { Authorization: `Bearer ${token}` }),
                },
            })

            const data = response.data
            setSuccessData(data)
            setImportSuccess(true)

            setToast({
                type: 'success',
                message: `Successfully imported ${data.transaction_count} transactions!`,
            })

            // Auto-redirect after 2 seconds
            setTimeout(() => {
                router.push('/transactions')
            }, 2000)
        } catch (error) {
            const detail = error.response?.data?.detail
            const msg = detail || error.message || 'Failed to upload file'
            setToast({
                type: 'error',
                message: msg,
            })
            console.error('Upload error:', error)
        } finally {
            setUploading(false)
        }
    }

    if (importSuccess) {
        return (
            <AppLayout>
                <div className="max-w-2xl mx-auto text-center">
                    <CheckCircle size={64} className="mx-auto mb-4 text-[#27AE60]" />
                    <h1 className="text-3xl font-bold mb-2 text-[#3C2A1E]">Import Successful!</h1>
                    <p className="text-[#8B5E3C] mb-4 text-lg">
                        {successData?.transaction_count} transactions have been imported
                    </p>
                    <p className="text-[#A67B5B]">
                        Redirecting to transactions...
                    </p>
                </div>
            </AppLayout>
        )
    }

    return (
        <AppLayout>
            <div className="max-w-2xl mx-auto">
                <h1 className="text-3xl font-bold mb-2 text-[#3C2A1E]">Import Transactions</h1>
                <p className="text-[#8B5E3C] mb-8">
                    Upload M-Pesa statements, bank exports, or CSV files to add transactions
                </p>

                {/* Upload zone */}
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${isDragging
                        ? 'border-[#8B5E3C] bg-[#F5EFE6]'
                        : 'border-[#C4A484] bg-white'
                        }`}
                >
                    {uploading ? (
                        <>
                            <Loader size={48} className="mx-auto mb-4 text-[#C4A484] animate-spin" />
                            <h2 className="text-xl font-semibold mb-2 text-[#3C2A1E]">
                                Importing file...
                            </h2>
                            <p className="text-[#8B5E3C]">
                                This may take a moment
                            </p>
                        </>
                    ) : (
                        <>
                            <Upload size={48} className="mx-auto mb-4 text-[#C4A484]" />
                            <h2 className="text-xl font-semibold mb-2 text-[#3C2A1E]">
                                Drag & drop your file
                            </h2>
                            <p className="text-[#8B5E3C] mb-4">
                                or click below to select
                            </p>
                            <label className="inline-block">
                                <input
                                    type="file"
                                    accept=".pdf,.csv,.jpg,.jpeg,.png,.webp"
                                    onChange={(e) => {
                                        if (e.target.files?.[0]) {
                                            uploadFile(e.target.files[0])
                                        }
                                    }}
                                    disabled={uploading}
                                    className="hidden"
                                />
                                <span className="inline-block px-6 py-2 bg-[#8B5E3C] text-white rounded-lg cursor-pointer hover:bg-[#6F4A2D] transition-colors disabled:opacity-50">
                                    {uploading ? 'Uploading...' : 'Choose File'}
                                </span>
                            </label>
                            <p className="text-sm text-[#A67B5B] mt-4">
                                Max 50MB • Supports PDF, CSV, JPG, PNG, WebP
                            </p>
                        </>
                    )}
                </div>

                {/* Supported formats */}
                <div className="mt-12 grid md:grid-cols-2 gap-6">
                    <div className="p-4 bg-[#F5EFE6] rounded-lg">
                        <FileText size={24} className="text-[#8B5E3C] mb-2" />
                        <h3 className="font-semibold mb-2 text-[#3C2A1E]">M-Pesa Statement</h3>
                        <p className="text-sm text-[#8B5E3C]">
                            Export your Safaricom M-Pesa statement PDF
                        </p>
                    </div>
                    <div className="p-4 bg-[#F5EFE6] rounded-lg">
                        <FileText size={24} className="text-[#8B5E3C] mb-2" />
                        <h3 className="font-semibold mb-2 text-[#3C2A1E]">Bank Statement</h3>
                        <p className="text-sm text-[#8B5E3C]">
                            KCB, Equity, Co-op, or generic bank PDFs
                        </p>
                    </div>
                    <div className="p-4 bg-[#F5EFE6] rounded-lg">
                        <FileText size={24} className="text-[#8B5E3C] mb-2" />
                        <h3 className="font-semibold mb-2 text-[#3C2A1E]">CSV Export</h3>
                        <p className="text-sm text-[#8B5E3C]">
                            Spreadsheet exports with transaction data
                        </p>
                    </div>
                    <div className="p-4 bg-[#F5EFE6] rounded-lg">
                        <FileText size={24} className="text-[#8B5E3C] mb-2" />
                        <h3 className="font-semibold mb-2 text-[#3C2A1E]">Notes</h3>
                        <p className="text-sm text-[#8B5E3C]">
                            Transactions are imported with "Uncategorized" - edit categories later
                        </p>
                    </div>
                </div>
            </div>

            {toast && (
                <Toast
                    type={toast.type}
                    message={toast.message}
                    onClose={() => setToast(null)}
                />
            )}
        </AppLayout>
    )
}
