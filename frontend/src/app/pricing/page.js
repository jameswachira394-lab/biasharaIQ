'use client'
import { useState } from 'react'
import AppLayout from '@/components/ui/AppLayout'
import { useAuth } from '@/context/AuthContext'
import { Check, X, Zap, Crown } from 'lucide-react'
import UpgradeModal from '@/components/subscription/UpgradeModal'

const PLANS = [
  {
    id: 'free',
    name: 'Free Plan',
    price: '0',
    description: 'Perfect for small side hustles',
    icon: <Zap className="text-semantic-textSecondary" size={24} />,
    features: [
      { text: 'Up to 200 txns / month', included: true },
      { text: 'Basic dashboard', included: true },
      { text: 'Expense categories', included: true },
      { text: 'AI Financial Advisor', included: false },
      { text: 'Smart waste detection', included: false },
      { text: 'Cash flow predictions', included: false },
    ],
    buttonText: 'Current Plan',
    buttonClass: 'btn-secondary w-full',
    isCurrent: true
  },
  {
    id: 'pro',
    name: 'Pro Plan',
    price: '499',
    description: 'Advanced insights for growing SMEs',
    icon: <Crown className="text-semantic-accentGold" size={24} />,
    popular: true,
    features: [
      { text: 'Unlimited transactions', included: true },
      { text: 'AI Financial Advisor', included: true },
      { text: 'Smart waste detection', included: true },
      { text: 'Cash flow predictions', included: true },
      { text: 'Runway forecasting', included: true },
      { text: 'Priority support', included: true },
    ],
    buttonText: 'Upgrade to Pro',
    buttonClass: 'btn-primary w-full',
    isCurrent: false
  }
]

export default function PricingPage() {
  const { user } = useAuth()
  const [showUpgrade, setShowUpgrade] = useState(false)

  const isPro = user?.plan === 'PRO'

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto py-10 px-4">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-display font-bold text-semantic-white mb-3">
            Choose Your <span className="gradient-text">Growth Tier</span>
          </h1>
          <p className="text-semantic-textSecondary max-w-lg mx-auto">
            Scale your financial intelligence as your business grows. 
            Upgrade to Pro for full AI capabilities.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {PLANS.map((plan) => {
            const current = (plan.id === 'pro' && isPro) || (plan.id === 'free' && !isPro)
            
            return (
              <div key={plan.id} className={`card p-8 flex flex-col relative ${plan.popular ? 'border-semantic-accentBlue/40 glow-blue' : ''}`}>
                {plan.popular && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-semantic-accentBlue text-white text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest">
                    Recommended
                  </span>
                )}
                
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      {plan.icon}
                      <h3 className="font-display font-bold text-xl text-semantic-white">{plan.name}</h3>
                    </div>
                    <p className="text-sm text-semantic-textSecondary">{plan.description}</p>
                  </div>
                </div>

                <div className="mb-8">
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-bold text-semantic-white">KES {plan.price}</span>
                    <span className="text-semantic-textSecondary text-sm">/month</span>
                  </div>
                </div>

                <div className="space-y-4 mb-10 flex-1">
                  {plan.features.map((feature, idx) => (
                    <div key={idx} className="flex items-center gap-3">
                      {feature.included ? (
                        <div className="w-5 h-5 rounded-full bg-semantic-success/10 flex items-center justify-center">
                          <Check size={12} className="text-semantic-success" />
                        </div>
                      ) : (
                        <div className="w-5 h-5 rounded-full bg-white/5 flex items-center justify-center">
                          <X size={12} className="text-semantic-textMuted" />
                        </div>
                      )}
                      <span className={`text-sm ${feature.included ? 'text-semantic-textLight' : 'text-semantic-textMuted'}`}>
                        {feature.text}
                      </span>
                    </div>
                  ))}
                </div>

                <button 
                  disabled={current || (plan.id === 'free' && isPro)}
                  onClick={() => plan.id === 'pro' && setShowUpgrade(true)}
                  className={current ? 'btn-secondary w-full opacity-50 cursor-default' : plan.buttonClass}
                >
                  {current ? 'Your Current Plan' : plan.buttonText}
                </button>
              </div>
            )
          })}
        </div>

        <div className="mt-16 card p-6 bg-semantic-accentBlue/5 border-dashed border-semantic-accentBlue/20 text-center">
          <p className="text-sm text-semantic-textSecondary">
            All payments are processed securely via <strong>M-Pesa</strong>. 
            Subscriptions are valid for 30 days and will auto-downgrade unless renewed.
          </p>
        </div>
      </div>

      <UpgradeModal isOpen={showUpgrade} onClose={() => setShowUpgrade(false)} />
    </AppLayout>
  )
}
