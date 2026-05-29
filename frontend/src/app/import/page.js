'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, FileText, CheckCircle, Loader, ArrowLeft, X, Edit3, FileSpreadsheet, Image, File } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import AppLayout from '@/components/ui/AppLayout'
import Toast from '@/components/ui/Toast'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const CATEGORIES = [
    'Sales', 'Income', 'Bills', 'Transfer', 'Bank Transfer',
    'Airtime', 'Shopping', 'Charges', 'Cash Withdrawal', 'Cash Deposit',
    'Salary', 'Savings', 'Loans', 'Refund', 'Uncategorized',
]

export default function ImportPage() {
    const router = useRouter()
    const { user } = useAuth()
    const [step, setStep] = useState('upload') // upload, preview, success
    const [isDragging, setIsDragging] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [confirming, setConfirming] = useState(false)
    const [toast, setToast] = useState(null)

    // Preview data from backend
    const [batchId, setBatchId] = useState(null)
    const [docType, setDocType] = useState('')
    const [previewTransactions, setPreviewTransactions] = useState([])
    const [successCount, setSuccessCount] = useState(0)

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
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
        ]
        const validExtensions = ['.pdf', '.csv', '.jpg', '.jpeg', '.png', '.webp', '.xlsx', '.xls']
        const fileExt = '.' + file.name.split('.').pop().toLowerCase()
        if (!validTypes.includes(file.type) && !validExtensions.includes(fileExt)) {
            setToast({
                type: 'error',
                message: 'Invalid file type. Please upload PDF, CSV, Excel (.xlsx/.xls), JPG, or PNG.',
            })
            return
        }

        if (file.size > 50 * 1024 * 1024) {
            setToast({ type: 'error', message: 'File is too large. Maximum size is 50MB.' })
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
            setDocType(data.doc_type)
            setPreviewTransactions(data.transactions || [])
            setStep('preview')

            setToast({
                type: 'success',
                message: `Extracted ${data.transaction_count} transactions. Please review and confirm.`,
            })
        } catch (error) {
            const detail = error.response?.data?.detail
            setToast({ type: 'error', message: detail || error.message || 'Failed to upload file' })
        } finally {
            setUploading(false)
        }
    }

    const handleCategoryChange = (index, newCategory) => {
        setPreviewTransactions(prev => {
            const updated = [...prev]
            updated[index] = { ...updated[index], category: newCategory }
            return updated
        })
    }

    const handleConfirm = async () => {
        if (confirming) return
        setConfirming(true)
        try {
            const token = typeof window !== 'undefined' ? localStorage.getItem('biasharaiq_token') : null

            // Build updates map: { txId: { category } } for any edited categories
            const updates = {}
            previewTransactions.forEach(tx => {
                updates[tx.id] = { category: tx.category }
            })

            await axios.post(`${API_URL}/uploads/confirm/${batchId}`, { updates }, {
                headers: {
                    'Content-Type': 'application/json',
                    ...(token && { Authorization: `Bearer ${token}` }),
                },
            })

            setSuccessCount(previewTransactions.length)
            setStep('success')
            setToast({ type: 'success', message: `Successfully imported ${previewTransactions.length} transactions!` })

            setTimeout(() => {
                router.push('/transactions')
            }, 2500)
        } catch (error) {
            const detail = error.response?.data?.detail
            setToast({ type: 'error', message: detail || 'Failed to confirm transactions' })
        } finally {
            setConfirming(false)
        }
    }

    const handleCancel = async () => {
        try {
            const token = typeof window !== 'undefined' ? localStorage.getItem('biasharaiq_token') : null
            await axios.delete(`${API_URL}/uploads/cancel/${batchId}`, {
                headers: { ...(token && { Authorization: `Bearer ${token}` }) },
            })
            setToast({ type: 'info', message: 'Import cancelled.' })
        } catch (e) {
            // best effort
        }
        setStep('upload')
        setPreviewTransactions([])
        setBatchId(null)
    }

    // ─── SUCCESS SCREEN ───
    if (step === 'success') {
        return (
            <AppLayout>
                <div className="max-w-2xl mx-auto text-center py-16">
                    <div className="w-20 h-20 rounded-full bg-[#27AE60]/10 flex items-center justify-center mx-auto mb-6">
                        <CheckCircle size={48} className="text-[#27AE60]" />
                    </div>
                    <h1 className="text-3xl font-bold mb-2 text-[#3C2A1E]">Import Successful!</h1>
                    <p className="text-[#8B5E3C] mb-2 text-lg">
                        {successCount} transactions have been imported
                    </p>
                    <p className="text-[#A67B5B] text-sm">Redirecting to transactions...</p>
                </div>
            </AppLayout>
        )
    }

    // ─── PREVIEW SCREEN ───
    if (step === 'preview') {
        const totalIncome = previewTransactions
            .filter(tx => tx.type === 'income')
            .reduce((sum, tx) => sum + tx.amount, 0)
        const totalExpense = previewTransactions
            .filter(tx => tx.type === 'expense')
            .reduce((sum, tx) => sum + tx.amount, 0)

        return (
            <AppLayout>
                <div className="max-w-5xl mx-auto">
                    {/* Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                        <div>
                            <button
                                onClick={handleCancel}
                                className="flex items-center gap-1 text-sm text-[#8B5E3C] hover:text-[#3C2A1E] mb-2 transition-colors"
                            >
                                <ArrowLeft size={16} /> Back
                            </button>
                            <h1 className="text-2xl font-bold text-[#3C2A1E]">Review Imported Transactions</h1>
                            <p className="text-sm text-[#8B5E3C] mt-1">
                                Source: <span className="font-semibold capitalize">{docType}</span> • {previewTransactions.length} transactions found
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={handleCancel}
                                className="px-5 py-2.5 text-sm font-semibold rounded-lg border border-[#C4A484] text-[#8B5E3C] hover:bg-[#F5EFE6] transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleConfirm}
                                disabled={confirming}
                                className="px-5 py-2.5 text-sm font-semibold rounded-lg bg-[#27AE60] text-white hover:bg-[#219a52] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                            >
                                {confirming ? <><Loader size={16} className="animate-spin" /> Confirming...</> : <><CheckCircle size={16} /> Confirm Import</>}
                            </button>
                        </div>
                    </div>

                    {/* Summary Cards */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
                        <div className="p-4 rounded-lg bg-[#F5EFE6] border border-[#E8DDD0]">
                            <p className="text-xs text-[#A67B5B] uppercase font-semibold">Transactions</p>
                            <p className="text-2xl font-bold text-[#3C2A1E]">{previewTransactions.length}</p>
                        </div>
                        <div className="p-4 rounded-lg bg-[#E8F5E9] border border-[#C8E6C9]">
                            <p className="text-xs text-[#2E7D32] uppercase font-semibold">Total Income</p>
                            <p className="text-2xl font-bold text-[#2E7D32]">KES {totalIncome.toLocaleString()}</p>
                        </div>
                        <div className="p-4 rounded-lg bg-[#FBE9E7] border border-[#FFCCBC] col-span-2 sm:col-span-1">
                            <p className="text-xs text-[#C62828] uppercase font-semibold">Total Expenses</p>
                            <p className="text-2xl font-bold text-[#C62828]">KES {totalExpense.toLocaleString()}</p>
                        </div>
                    </div>

                    {/* Transactions Table */}
                    <div className="bg-white rounded-lg border border-[#E8DDD0] overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="bg-[#F5EFE6] text-left text-xs text-[#8B5E3C] uppercase tracking-wider">
                                        <th className="px-4 py-3 font-semibold">Date</th>
                                        <th className="px-4 py-3 font-semibold">Category</th>
                                        <th className="px-4 py-3 font-semibold">Description</th>
                                        <th className="px-4 py-3 font-semibold text-right">Amount (KES)</th>
                                        <th className="px-4 py-3 font-semibold">Type</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-[#F0E8DE]">
                                    {previewTransactions.map((tx, idx) => (
                                        <tr key={tx.id || idx} className="hover:bg-[#FDFAF6] transition-colors">
                                            <td className="px-4 py-3 text-[#3C2A1E] whitespace-nowrap">
                                                {new Date(tx.date).toLocaleDateString('en-KE', { day: '2-digit', month: 'short', year: 'numeric' })}
                                            </td>
                                            <td className="px-4 py-3">
                                                <select
                                                    value={tx.category}
                                                    onChange={(e) => handleCategoryChange(idx, e.target.value)}
                                                    className="w-full min-w-[130px] px-2 py-1 text-sm rounded border border-[#E8DDD0] bg-white text-[#3C2A1E] focus:border-[#8B5E3C] focus:outline-none focus:ring-1 focus:ring-[#8B5E3C]/30 cursor-pointer"
                                                >
                                                    {CATEGORIES.includes(tx.category) ? null : (
                                                        <option value={tx.category}>{tx.category}</option>
                                                    )}
                                                    {CATEGORIES.map(cat => (
                                                        <option key={cat} value={cat}>{cat}</option>
                                                    ))}
                                                </select>
                                            </td>
                                            <td className="px-4 py-3 text-[#5C4033] max-w-[280px] truncate" title={tx.description}>
                                                {tx.description}
                                            </td>
                                            <td className={`px-4 py-3 text-right font-semibold whitespace-nowrap ${tx.type === 'income' ? 'text-[#27AE60]' : 'text-[#C62828]'}`}>
                                                {tx.type === 'income' ? '+' : '-'}{Number(tx.amount).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold ${
                                                    tx.type === 'income'
                                                        ? 'bg-[#E8F5E9] text-[#2E7D32]'
                                                        : 'bg-[#FBE9E7] text-[#C62828]'
                                                }`}>
                                                    {tx.type === 'income' ? 'Income' : 'Expense'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Bottom Actions */}
                    <div className="flex justify-between items-center mt-6 pb-8">
                        <p className="text-xs text-[#A67B5B]">
                            <Edit3 size={12} className="inline mr-1" />
                            You can edit categories before confirming
                        </p>
                        <button
                            onClick={handleConfirm}
                            disabled={confirming}
                            className="px-6 py-3 text-sm font-bold rounded-lg bg-[#27AE60] text-white hover:bg-[#219a52] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                        >
                            {confirming ? <><Loader size={16} className="animate-spin" /> Confirming...</> : <><CheckCircle size={16} /> Confirm & Import All</>}
                        </button>
                    </div>
                </div>

                {toast && (
                    <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />
                )}
            </AppLayout>
        )
    }

    // ─── UPLOAD SCREEN ───
    return (
        <AppLayout>
            <div className="max-w-2xl mx-auto">
                <h1 className="text-3xl font-bold mb-2 text-[#3C2A1E]">Import Transactions</h1>
                <p className="text-[#8B5E3C] mb-8">
                    Upload M-Pesa statements, bank exports, Excel or CSV files to add transactions
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
                                Processing statement...
                            </h2>
                            <p className="text-[#8B5E3C]">
                                Extracting and categorizing transactions
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
                                    accept=".pdf,.csv,.xlsx,.xls,.jpg,.jpeg,.png,.webp"
                                    onChange={(e) => {
                                        if (e.target.files?.[0]) {
                                            uploadFile(e.target.files[0])
                                        }
                                    }}
                                    disabled={uploading}
                                    className="hidden"
                                />
                                <span className="inline-block px-6 py-2 bg-[#8B5E3C] text-white rounded-lg cursor-pointer hover:bg-[#6F4A2D] transition-colors">
                                    Choose File
                                </span>
                            </label>
                            <p className="text-sm text-[#A67B5B] mt-4">
                                Max 50MB • Supports PDF, CSV, Excel (.xlsx/.xls), JPG, PNG
                            </p>
                        </>
                    )}
                </div>

                {/* Supported formats */}
                <div className="mt-12 grid md:grid-cols-2 gap-6">
                    <div className="p-4 bg-[#F5EFE6] rounded-lg flex gap-3">
                        <FileText size={24} className="text-[#8B5E3C] shrink-0 mt-0.5" />
                        <div>
                            <h3 className="font-semibold mb-1 text-[#3C2A1E]">M-Pesa Statement</h3>
                            <p className="text-sm text-[#8B5E3C]">
                                Export your Safaricom M-Pesa statement PDF or Excel
                            </p>
                        </div>
                    </div>
                    <div className="p-4 bg-[#F5EFE6] rounded-lg flex gap-3">
                        <File size={24} className="text-[#8B5E3C] shrink-0 mt-0.5" />
                        <div>
                            <h3 className="font-semibold mb-1 text-[#3C2A1E]">Bank Statement</h3>
                            <p className="text-sm text-[#8B5E3C]">
                                KCB, Equity, Co-op, or generic bank PDFs
                            </p>
                        </div>
                    </div>
                    <div className="p-4 bg-[#F5EFE6] rounded-lg flex gap-3">
                        <FileSpreadsheet size={24} className="text-[#8B5E3C] shrink-0 mt-0.5" />
                        <div>
                            <h3 className="font-semibold mb-1 text-[#3C2A1E]">Excel / CSV</h3>
                            <p className="text-sm text-[#8B5E3C]">
                                Spreadsheet exports (.xlsx, .xls, .csv)
                            </p>
                        </div>
                    </div>
                    <div className="p-4 bg-[#F5EFE6] rounded-lg flex gap-3">
                        <Image size={24} className="text-[#8B5E3C] shrink-0 mt-0.5" />
                        <div>
                            <h3 className="font-semibold mb-1 text-[#3C2A1E]">Image / Scan</h3>
                            <p className="text-sm text-[#8B5E3C]">
                                Photos or screenshots of receipts and invoices
                            </p>
                        </div>
                    </div>
                </div>

                {/* How it works */}
                <div className="mt-10 p-6 bg-[#F5EFE6] rounded-lg border border-dashed border-[#C4A484]">
                    <h3 className="font-semibold text-[#3C2A1E] mb-3">How it works</h3>
                    <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 text-sm text-[#8B5E3C]">
                        <span className="flex items-center gap-2"><span className="w-6 h-6 rounded-full bg-[#8B5E3C] text-white text-xs flex items-center justify-center font-bold">1</span> Upload statement</span>
                        <span className="hidden sm:block text-[#C4A484]">→</span>
                        <span className="flex items-center gap-2"><span className="w-6 h-6 rounded-full bg-[#8B5E3C] text-white text-xs flex items-center justify-center font-bold">2</span> Review & edit categories</span>
                        <span className="hidden sm:block text-[#C4A484]">→</span>
                        <span className="flex items-center gap-2"><span className="w-6 h-6 rounded-full bg-[#8B5E3C] text-white text-xs flex items-center justify-center font-bold">3</span> Confirm import</span>
                    </div>
                </div>
            </div>

            {toast && (
                <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />
            )}
        </AppLayout>
    )
}
