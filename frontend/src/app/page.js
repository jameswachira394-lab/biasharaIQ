'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import Link from 'next/link'

export default function Home() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && user) {
      router.replace('/dashboard')
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-[#0F6B4F] border-t-transparent animate-spin" />
          <span className="text-[#9CA3AF]">Loading BiasharaIQ...</span>
        </div>
      </div>
    )
  }

  // If user is not logged in, show the landing page
  return (
    <div className="landing-page">
      {/* SECTION 1: HERO */}
      <section style={{ paddingTop: '48px', paddingBottom: '48px' }}>
        <div className="container hero-flex">
          <div className="hero-content">
            <h1>Know Where Your Money Goes. Control Your Business.</h1>
            <p style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>
              BiasharaIQ helps small businesses track profit, manage cash flow, and avoid running out of money.
            </p>
            <div className="btn-group">
              <Link href="/login" className="btn btn-primary-landing">Get Started Free →</Link>
              <a href="#how-it-works" className="btn btn-secondary-landing">See How It Works</a>
            </div>
            <p style={{ marginTop: '1rem', fontSize: '0.8rem', color: '#9CA3AF' }}>No credit card required • Free plan available</p>
          </div>
          <div className="hero-visual">
            <div className="dashboard-mock">
              <div className="mock-metrics">
                <div className="metric-card"><div className="metric-label">Total Profit</div><div className="metric-value">KSh 48,250</div></div>
                <div className="metric-card"><div className="metric-label">Expenses</div><div className="metric-value">KSh 23,180</div></div>
                <div className="metric-card"><div className="metric-label"><span className="days-left">Days remaining</span></div><div className="metric-value">12 days</div></div>
              </div>
              <div className="mock-chart">
                <div style={{ flex: 1 }}><div className="bar bar-md" style={{ height: '58px' }}></div><div style={{ fontSize: '0.7rem' }}>Sales</div></div>
                <div style={{ flex: 1 }}><div className="bar bar-sm" style={{ height: '32px', background: '#F97316' }}></div><div style={{ fontSize: '0.7rem' }}>Marketing</div></div>
                <div style={{ flex: 1 }}><div className="bar bar-sm" style={{ height: '28px', background: '#10B981' }}></div><div style={{ fontSize: '0.7rem' }}>Stock</div></div>
                <div style={{ flex: 1 }}><div className="bar" style={{ height: '46px', background: '#3B82F6' }}></div><div style={{ fontSize: '0.7rem' }}>Profit</div></div>
              </div>
              <div style={{ marginTop: '24px', background: '#00000030', borderRadius: '24px', padding: '12px', fontSize: '0.75rem', color: '#aaa', textAlign: 'center' }}>
                📊 Real‑time dashboard • Track every shilling
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 2: PROBLEM */}
      <section style={{ backgroundColor: 'rgba(18, 24, 33, 0.4)' }}>
        <div className="container">
          <div style={{ maxWidth: '700px', margin: '0 auto', textAlign: 'center' }}>
            <span className="trust-badge" style={{ marginBottom: '16px' }}>⚠️ The struggle is real</span>
            <h2>Running a business shouldn&apos;t feel like guessing.</h2>
          </div>
          <div className="features-grid" style={{ marginTop: '48px', gridTemplateColumns: '1fr', gap: '20px' }}>
            <div className="landing-card" style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '2rem' }}>❓</span><span><strong>You don’t know your real profit</strong> — numbers just confuse you.</span>
            </div>
            <div className="landing-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <span style={{ fontSize: '2rem' }}>⏳</span><span><strong>Money runs out before the month ends</strong> — every single time.</span>
            </div>
            <div className="landing-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <span style={{ fontSize: '2rem' }}>📈</span><span><strong>Expenses keep increasing without control</strong> — hidden leaks everywhere.</span>
            </div>
            <div className="landing-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <span style={{ fontSize: '2rem' }}>💸</span><span><strong>You mix business and personal money</strong> — total confusion at tax time.</span>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 3: SOLUTION */}
      <section>
        <div className="container text-center">
          <h2>BiasharaIQ gives you clarity and control.</h2>
          <p style={{ maxWidth: '680px', margin: '0 auto 32px' }}>Stop drowning in receipts. Start making confident decisions.</p>
          <div className="features-grid">
            <div className="landing-card"><span style={{ fontSize: '2rem' }}>💰</span><h3>Track every shilling</h3><p>Money in & out — simple, fast, and accurate.</p></div>
            <div className="landing-card"><span style={{ fontSize: '2rem' }}>📈</span><h3>See your real profit instantly</h3><p>Real-time profit calculation, no waiting until end of month.</p></div>
            <div className="landing-card"><span style={{ fontSize: '2rem' }}>⏲️</span><h3>Know how long your money will last</h3><p>Cash runway + days remaining forecast.</p></div>
            <div className="landing-card"><span style={{ fontSize: '2rem' }}>🧠</span><h3>Get smart insights on your spending</h3><p>AI detects wasteful subscriptions and irregular expenses.</p></div>
          </div>
        </div>
      </section>

      {/* SECTION 4: CORE FEATURES */}
      <section style={{ backgroundColor: '#0a0e12' }}>
        <div className="container">
          <div className="text-center"><h2>Everything you need to thrive</h2><p>Powerful, yet simple tools.</p></div>
          <div className="features-grid">
            <div className="landing-card"><span style={{ fontSize: '2rem' }}>🎯</span><h3>Profit Tracking</h3><p>“See exactly how much your business makes.” Gross vs net profit updated live.</p></div>
            <div className="landing-card"><span style={{ fontSize: '2rem' }}>⚠️</span><h3>Cash Flow Alerts</h3><p>“Know when your money is running out before it’s too late.” Smart notifications on your phone.</p></div>
            <div className="landing-card"><span style={{ fontSize: '2rem' }}>🔍</span><h3>Expense Insights</h3><p>“Identify where your money is being wasted.” Categorize and spot spending spikes.</p></div>
            <div className="landing-card"><span style={{ fontSize: '2rem' }}>🤖</span><h3>AI Assistant</h3><p>“Ask questions and get smart answers about your business.” No more spreadsheets guesswork.</p></div>
          </div>
        </div>
      </section>

      {/* SECTION 5: AI FEATURE */}
      <section>
        <div className="container">
          <div className="ai-bubble">
            <div className="ask-badge">✨ AI-Powered Intelligence</div>
            <h2 style={{ marginTop: '8px' }}>Your Business, Explained by AI.</h2>
            <p style={{ fontSize: '1.1rem' }}>Just ask: <strong>“Why is my profit low?”</strong> or <strong>“Where am I losing money?”</strong> and get clear answers based on your data — in seconds.</p>
            <div style={{ background: '#00000030', borderRadius: '60px', padding: '12px 24px', marginTop: '24px', fontStyle: 'italic', borderLeft: '4px solid #10B981' }}>
              “M-Pesa & cash transactions analyzed. You lost KSh 8,200 on idle stock and unrecorded expenses last month.”
            </div>
            <p className="mt-4" style={{ marginBottom: 0 }}><strong>No guesswork. Just real insights.</strong></p>
          </div>
        </div>
      </section>

      {/* SECTION 6: HOW IT WORKS */}
      <section id="how-it-works">
        <div className="container text-center">
          <h2>From chaos to clarity in 3 steps</h2>
          <div className="steps">
            <div className="step-item"><div className="step-num">1</div><div><h3>Add your income & expenses</h3><p>Record sales, purchases, or connect via CSV — super fast.</p></div></div>
            <div className="step-item"><div className="step-num">2</div><div><h3>See your profit & cash flow</h3><p>Interactive dashboard shows your real-time financial health.</p></div></div>
            <div className="step-item"><div className="step-num">3</div><div><h3>Get insights and grow</h3><p>AI tips help you cut waste, increase profit, and plan ahead.</p></div></div>
          </div>
        </div>
      </section>

      {/* SECTION 7: TRUST / SOCIAL PROOF */}
      <section style={{ paddingTop: '32px' }}>
        <div className="container social-proof">
          <div className="trust-badge" style={{ marginBottom: '24px' }}>🇰🇪 Built for small businesses in Kenya</div>
          <div className="landing-card" style={{ maxWidth: '700px', margin: '0 auto' }}>
            <p style={{ fontWeight: 500, fontSize: '1rem' }}>“Designed for real-world biashara — from mama mboga to boutique owners. Already helping 500+ businesses track profit and sleep better.”</p>
            <p style={{ marginTop: '12px', color: '#10B981' }}>— BiasharaIQ early access community</p>
          </div>
        </div>
      </section>

      {/* SECTION 8: PRICING */}
      <section>
        <div className="container text-center">
          <h2>Simple, transparent pricing</h2>
          <p>Start free, upgrade when you need advanced insights.</p>
          <div className="pricing-row">
            <div className="pricing-card">
              <h3>Free Plan</h3>
              <div className="price">KSh 0</div>
              <p style={{ margin: '16px 0' }}>✔ Track up to 200 transactions/month<br/>✔ Basic dashboard & profit view<br/>✔ Expense categories<br/>✔ Email support</p>
              <Link href="/login" className="btn btn-primary-landing w-100" style={{ textAlign: 'center' }}>Start Free →</Link>
            </div>
            <div className="pricing-card" style={{ borderTop: '3px solid #10B981' }}>
              <h3>Pro Plan</h3>
              <div className="price">KSh 499<span style={{ fontSize: '1rem' }}>/month</span></div>
              <p style={{ margin: '16px 0' }}>✔ Unlimited transactions<br/>✔ AI Assistant & cash flow predictions<br/>✔ Smart insights & waste detection<br/>✔ Days remaining forecast + alerts<br/>✔ Priority support</p>
              <Link href="/login" className="btn btn-primary-landing w-100">Get Pro →</Link>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 9: FINAL CTA */}
      <section style={{ background: 'linear-gradient(135deg, #0e151d, #091017)' }}>
        <div className="container text-center">
          <h2>Stop guessing. Start understanding your business.</h2>
          <p style={{ marginBottom: '32px', maxWidth: '550px', marginLeft: 'auto', marginRight: 'auto' }}>Join hundreds of Kenyan entrepreneurs who finally know where their money goes.</p>
          <Link href="/login" className="btn btn-primary-landing btn-block-mobile" style={{ padding: '14px 40px', fontSize: '1.2rem' }}>Get Started Free →</Link>
          <p style={{ marginTop: '24px', fontSize: '0.85rem' }}>No setup fee. Cancel anytime.</p>
        </div>
      </section>

      {/* SECTION 10: FOOTER */}
      <footer>
        <div className="container">
          <div className="footer-links">
            <a href="#">About</a>
            <a href="#">Contact</a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
          </div>
          <div className="text-center" style={{ fontSize: '0.8rem' }}>
            © 2025 BiasharaIQ — clarity & control for your biashara. 
          </div>
        </div>
      </footer>
    </div>
  )
}
