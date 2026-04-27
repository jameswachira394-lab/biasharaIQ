import clsx from 'clsx'

export default function Spinner({ size = 'md', className = '' }) {
  const sizes = { sm: 'w-4 h-4 border', md: 'w-6 h-6 border-2', lg: 'w-10 h-10 border-2' }
  return (
    <div className={clsx(
      'rounded-full border-[#10B981] border-t-transparent animate-spin',
      sizes[size] || sizes.md,
      className
    )} />
  )
}

export function PageLoader({ message = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="flex flex-col items-center gap-3">
        <Spinner size="lg" />
        <p className="text-[#9CA3AF] text-sm">{message}</p>
      </div>
    </div>
  )
}

export function InlineLoader() {
  return (
    <div className="flex items-center gap-2 text-[#9CA3AF] text-sm">
      <Spinner size="sm" />
      <span>Loading...</span>
    </div>
  )
}
