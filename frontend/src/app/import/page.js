'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react'
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
    const [batchId, setBatchId] = useState(null)
    const [uploadData, setUploadData] = useState(null)
    const [transactions, setTransactions] = useState([])
    const [editingTx, setEditingTx] = useState(null)
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
            setBatchId(data.batch_id)
            setUploadData(data)

            // Fetch preview
            const previewResponse = await axios.get(
                `${API_URL}/uploads/preview/${data.batch_id}`,
                {
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                }
            )
            const previewData = previewResponse.data
            setTransactions(previewData.transactions || [])

            setToast({
                type: 'success',
                message: `Successfully parsed ${data.transaction_count} transactions!`,
            })
        } catch (error) {
            const detail = error.response?.data?.detail
            const msg = detail || error.message || 'Failed to upload file'
            setToast({
                type: 'error',
                message: msg,
            })
            console.error('Upload error:', error)
            // Reset so the upload form is shown again
            setUploadData(null)
            setBatchId(null)
            setTransactions([])
        } finally {
            setUploading(false)
        }
    }

    const handleCategoryChange = (txId, newCategory) => {
        setTransactions(
            transactions.map((tx) =>
                tx.id === txId ? { ...tx, category: newCategory } : tx
            )
        )
        setEditingTx(null)
    }

    const handleDescriptionChange = (txId, newDescription) => {
        setTransactions(
            transactions.map((tx) =>
                tx.id === txId ? { ...tx, description: newDescription } : tx
            )
        )
    }

    const handleConfirm = async () => {
        if (!batchId) return

        try {
            setUploading(true)
            const updates = {}
            transactions.forEach((tx) => {
                updates[tx.id] = {
                    category: tx.category,
                    description: tx.description,
                }
            })

            const token = typeof window !== 'undefined' ? localStorage.getItem('biasharaiq_token') : null

            const response = await axios.post(
                `${API_URL}/uploads/confirm/${batchId}`,
                { updates },
                {
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                }
            )

            setToast({
                type: 'success',
                message: 'Transactions imported successfully!',
            })

            setTimeout(() => {
                router.push('/transactions')
            }, 1500)
        } catch (error) {
            setToast({
                type: 'error',
                message: error.response?.data?.detail || error.message || 'Failed to confirm',
            })
        } finally {
            setUploading(false)
        }
    }

    const handleCancel = async () => {
        if (!batchId) {
            setBatchId(null)
            setUploadData(null)
            setTransactions([])
            return
        }

        try {
            const token = typeof window !== 'undefined' ? localStorage.getItem('biasharaiq_token') : null
            await axios.delete(`${API_URL}/uploads/cancel/${batchId}`, {
                headers: token ? { Authorization: `Bearer ${token}` } : {},
            })
            setBatchId(null)
            setUploadData(null)
            setTransactions([])
            setToast({
                type: 'info',
                message: 'Import cancelled',
            })
        } catch (error) {
            setToast({
                type: 'error',
                message: 'Failed to cancel',
            })
        }
    }

    if (!uploadData) {
        return (
            <AppLayout>
                <div className="max-w-2xl mx-auto">
                    <h1 className="text-3xl font-bold mb-2 text-[#3C2A1E]">Import Transactions</h1>
                    <p className="text-[#8B5E3C] mb-8">
                        Upload M-Pesa statements, bank exports, invoices, or CSV files
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
                            <h3 className="font-semibold mb-2 text-[#3C2A1E]">Invoice Image</h3>
                            <p className="text-sm text-[#8B5E3C]">
                                Upload invoice photos for AI extraction
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

    // Preview + review
    return (
        <AppLayout>
            <div className="max-w-5xl mx-auto">
                <h1 className="text-3xl font-bold mb-2 text-[#3C2A1E]">Review & Confirm</h1>
                <p className="text-[#8B5E3C] mb-8">
                    {uploadData.filename} • {uploadData.doc_type.toUpperCase()} • {uploadData.transaction_count} transactions
                </p>

                {/* Summary */}
                <div className="bg-[#F5EFE6] rounded-lg p-6 mb-8">
                    <h2 className="font-semibold mb-4 text-[#3C2A1E]">Summary</h2>
                    <div className="grid md:grid-cols-3 gap-4">
                        <div>
                            <p className="text-sm text-[#8B5E3C]">Total Income</p>
                            <p className="text-2xl font-bold text-[#27AE60]">
                                KES {(uploadData.summary?.total_income ?? 0).toLocaleString()}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-[#8B5E3C]">Total Expenses</p>
                            <p className="text-2xl font-bold text-[#E57373]">
                                KES {(uploadData.summary?.total_expenses ?? 0).toLocaleString()}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-[#8B5E3C]">Net</p>
                            <p className={`text-2xl font-bold ${(uploadData.summary?.net ?? 0) >= 0 ? 'text-[#27AE60]' : 'text-[#E57373]'}`}>
                                KES {(uploadData.summary?.net ?? 0).toLocaleString()}
                            </p>
                        </div>
                    </div>
                    {uploadData.summary?.narrative && (
                        <p className="mt-4 text-sm text-[#8B5E3C] italic">
                            {uploadData.summary.narrative}
                        </p>
                    )}
                </div>

                {/* Transactions table */}
                <div className="bg-white rounded-lg border border-[#C4A484]/20 overflow-hidden mb-8">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-[#F5EFE6] border-b border-[#C4A484]/20">
                                <tr>
                                    <th className="px-4 py-3 text-left font-semibold text-[#3C2A1E]">Date</th>
                                    <th className="px-4 py-3 text-left font-semibold text-[#3C2A1E]">Description</th>
                                    <th className="px-4 py-3 text-left font-semibold text-[#3C2A1E]">Amount</th>
                                    <th className="px-4 py-3 text-left font-semibold text-[#3C2A1E]">Type</th>
                                    <th className="px-4 py-3 text-left font-semibold text-[#3C2A1E]">Category</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transactions.map((tx, idx) => (
                                    <tr
                                        key={tx.id}
                                        className={`border-b border-[#C4A484]/10 ${idx % 2 === 0 ? 'bg-white' : 'bg-[#F5EFE6]/30'}`}
                                    >
                                        <td className="px-4 py-3 text-[#8B5E3C]">
                                            {tx.date ? new Date(tx.date).toLocaleDateString() : 'N/A'}
                                        </td>
                                        <td className="px-4 py-3">
                                            <input
                                                type="text"
                                                value={tx.description}
                                                onChange={(e) =>
                                                    handleDescriptionChange(tx.id, e.target.value)
                                                }
                                                className="w-full bg-transparent text-[#3C2A1E] hover:bg-white/50 px-2 py-1 rounded border border-transparent hover:border-[#C4A484]/30 focus:border-[#8B5E3C] focus:outline-none"
                                            />
                                        </td>
                                        <td className="px-4 py-3 font-semibold text-[#3C2A1E]">
                                            {tx.type === 'income' ? '+' : '-'}
                                            KES {(tx.amount ?? 0).toLocaleString()}
                                        </td>
                                        <td className="px-4 py-3">
                                            <span
                                                className={`px-2 py-1 rounded text-xs font-semibold ${tx.type === 'income'
                                                    ? 'bg-[#27AE60]/10 text-[#27AE60]'
                                                    : 'bg-[#E57373]/10 text-[#E57373]'
                                                    }`}
                                            >
                                                {tx.type}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            {editingTx === tx.id ? (
                                                <input
                                                    type="text"
                                                    value={tx.category}
                                                    onChange={(e) =>
                                                        handleCategoryChange(tx.id, e.target.value)
                                                    }
                                                    onBlur={() => setEditingTx(null)}
                                                    onKeyDown={(e) => {
                                                        if (e.key === 'Enter') setEditingTx(null)
                                                    }}
                                                    autoFocus
                                                    className="w-full px-2 py-1 border border-[#8B5E3C] rounded text-[#3C2A1E] focus:outline-none"
                                                />
                                            ) : (
                                                <div
                                                    onClick={() => setEditingTx(tx.id)}
                                                    className="px-2 py-1 bg-[#C4A484]/10 text-[#8B5E3C] rounded cursor-pointer hover:bg-[#C4A484]/20"
                                                >
                                                    {tx.category || 'Uncategorized'}
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Action buttons */}
                <div className="flex gap-4">
                    <button
                        onClick={handleCancel}
                        disabled={uploading}
                        className="flex-1 px-6 py-3 border border-[#C4A484] text-[#8B5E3C] rounded-lg hover:bg-[#F5EFE6] disabled:opacity-50 transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleConfirm}
                        disabled={uploading || transactions.length === 0}
                        className="flex-1 px-6 py-3 bg-[#8B5E3C] text-white rounded-lg hover:bg-[#6F4A2D] disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
                    >
                        {uploading ? (
                            <>
                                <Loader size={18} className="animate-spin" />
                                Importing...
                            </>
                        ) : (
                            <>
                                <CheckCircle size={18} />
                                Confirm & Import
                            </>
                        )}
                    </button>
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
