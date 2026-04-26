import Link from 'next/link'
import clsx from 'clsx'

export default function EmptyState({
  icon,
  title,
  description,
  action,
  actionHref,
  actionLabel,
  className = ''
}) {
  return (
    <div className={clsx('flex flex-col items-center justify-center py-16 text-center px-4', className)}>
      {icon && (
        <div className="w-14 h-14 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center mb-4 text-2xl">
          {icon}
        </div>
      )}
      <h3 className="font-display font-semibold text-slate-300 mb-1">{title}</h3>
      {description && <p className="text-slate-500 text-sm max-w-sm">{description}</p>}
      {actionHref && actionLabel && (
        <Link href={actionHref} className="btn-primary mt-5 text-sm">
          {actionLabel}
        </Link>
      )}
      {action && !actionHref && (
        <button onClick={action.onClick} className="btn-primary mt-5 text-sm">
          {actionLabel}
        </button>
      )}
    </div>
  )
}
