<template>
  <div class="login-page">
    <!-- Left panel -->
    <div class="login-left">
      <div class="left-content">
        <div class="logo-wrap">
          <span class="logo-icon">🎓</span>
          <span class="logo-text">Placement Portal</span>
        </div>

        <div class="hero-text">
          <h1>Your campus<br><span class="accent">recruitment hub.</span></h1>
          <p>Connecting students, companies, and institutes — all in one place.</p>
        </div>

        <div class="stat-cards">
          <div class="stat-card">
            <div class="stat-num">3</div>
            <div class="stat-label">Roles</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">∞</div>
            <div class="stat-label">Opportunities</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">1</div>
            <div class="stat-label">Platform</div>
          </div>
        </div>

        <div class="feature-pills">
          <span class="pill">✦ Smart eligibility matching</span>
          <span class="pill">✦ Real-time tracking</span>
          <span class="pill">✦ Auto reminders</span>
        </div>
      </div>
    </div>

    <!-- Right panel -->
    <div class="login-right">
      <div class="login-form-wrap">
        <div class="form-header">
          <h2>Welcome back</h2>
          <p>Sign in to your account</p>
        </div>

        <form @submit.prevent="login" novalidate>
          <div class="field" :class="{ invalid: submitted && !email }">
            <label>Email address</label>
            <div class="input-wrap">
              <svg class="input-icon" viewBox="0 0 20 20" fill="none"><path d="M2.5 5.5A1.5 1.5 0 014 4h12a1.5 1.5 0 011.5 1.5v9A1.5 1.5 0 0116 16H4a1.5 1.5 0 01-1.5-1.5v-9z" stroke="currentColor" stroke-width="1.5"/><path d="M2.5 6l7.5 5 7.5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
              <input type="email" v-model="email" placeholder="you@example.com" autocomplete="email" />
            </div>
            <span class="err-msg">Please enter your email.</span>
          </div>

          <div class="field" :class="{ invalid: submitted && !password }">
            <label>Password</label>
            <div class="input-wrap">
              <svg class="input-icon" viewBox="0 0 20 20" fill="none"><rect x="4" y="9" width="12" height="9" rx="1.5" stroke="currentColor" stroke-width="1.5"/><path d="M7 9V6a3 3 0 016 0v3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
              <input :type="showPwd ? 'text' : 'password'" v-model="password"
                     placeholder="••••••••" autocomplete="current-password" />
              <button type="button" class="eye-btn" @click="showPwd = !showPwd" tabindex="-1">
                <svg v-if="!showPwd" viewBox="0 0 20 20" fill="none"><path d="M2 10s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6z" stroke="currentColor" stroke-width="1.5"/><circle cx="10" cy="10" r="2.5" stroke="currentColor" stroke-width="1.5"/></svg>
                <svg v-else viewBox="0 0 20 20" fill="none"><path d="M3 3l14 14M8.46 8.52A2.5 2.5 0 0012.5 12.5M6.1 6.16C4.37 7.23 2.9 8.9 2 10c1.63 2.4 4.5 6 8 6a8.4 8.4 0 004-1.05M9 4.1A8.1 8.1 0 0110 4c3.5 0 6.37 3.6 8 6a13 13 0 01-1.93 2.58" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
              </button>
            </div>
            <span class="err-msg">Please enter your password.</span>
          </div>

          <div v-if="errorMsg" class="error-banner">
            <svg viewBox="0 0 20 20" fill="none" style="width:16px;height:16px;flex-shrink:0"><circle cx="10" cy="10" r="8" stroke="#dc2626" stroke-width="1.5"/><path d="M10 6v4M10 13h.01" stroke="#dc2626" stroke-width="1.5" stroke-linecap="round"/></svg>
            {{ errorMsg }}
          </div>

          <button type="submit" class="sign-in-btn" :disabled="loading">
            <span v-if="loading" class="btn-spinner"></span>
            <span>{{ loading ? 'Signing in…' : 'Sign In' }}</span>
          </button>
        </form>

        <div class="form-footer">
          <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

export default {
  name: 'LoginPage',
  emits: ['auth-changed'],
  setup(_, { emit }) {
    const router = useRouter()
    const email = ref('')
    const password = ref('')
    const errorMsg = ref('')
    const loading = ref(false)
    const submitted = ref(false)
    const showPwd = ref(false)

    const login = async () => {
      submitted.value = true
      if (!email.value || !password.value) return
      loading.value = true
      errorMsg.value = ''
      try {
        const res = await api.auth.login({ email: email.value, password: password.value })
        const { access_token, user } = res.data
        localStorage.setItem('token', access_token)
        localStorage.setItem('userRole', user.role)
        let name = user.email
        if (user.role === 'student' && user.student) name = user.student.full_name
        else if (user.role === 'company' && user.company) name = user.company.company_name
        localStorage.setItem('userName', name)
        emit('auth-changed')
        const routes = { admin: '/admin/dashboard', company: '/company/dashboard', student: '/student/dashboard' }
        router.push(routes[user.role] || '/login')
      } catch (e) {
        errorMsg.value = e.response?.data?.error || 'Invalid credentials. Please try again.'
      } finally {
        loading.value = false
      }
    }

    return { email, password, errorMsg, loading, submitted, showPwd, login }
  }
}
</script>

<style scoped>
/* ── LAYOUT ── */
.login-page {
  display: flex;
  min-height: 100vh;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ── LEFT PANEL ── */
.login-left {
  flex: 1;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  /* Rich multi-stop gradient — indigo → violet → deep blue */
  background:
    radial-gradient(ellipse at 20% 50%, #4f46e520 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, #7c3aed18 0%, transparent 50%),
    linear-gradient(145deg, #0d1117 0%, #0f172a 40%, #1a1040 70%, #0d1b35 100%);
}

/* Subtle animated orbs */
.login-left::before,
.login-left::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}
.login-left::before {
  width: 400px; height: 400px;
  background: radial-gradient(circle, #4f46e540, transparent 70%);
  top: -80px; left: -80px;
  animation: drift1 12s ease-in-out infinite alternate;
}
.login-left::after {
  width: 300px; height: 300px;
  background: radial-gradient(circle, #0ea5e930, transparent 70%);
  bottom: -60px; right: -60px;
  animation: drift2 15s ease-in-out infinite alternate;
}
@keyframes drift1 { to { transform: translate(60px, 40px); } }
@keyframes drift2 { to { transform: translate(-40px, -60px); } }

.left-content {
  position: relative;
  z-index: 1;
  max-width: 440px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 36px;
}

/* Logo */
.logo-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo-icon { font-size: 2rem; }
.logo-text {
  font-size: 1.15rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.01em;
}

/* Hero heading */
.hero-text h1 {
  font-size: 2.6rem;
  font-weight: 800;
  color: #f8fafc;
  line-height: 1.15;
  letter-spacing: -0.03em;
  margin-bottom: 14px;
}
.accent {
  background: linear-gradient(90deg, #818cf8, #38bdf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-text p {
  color: #94a3b8;
  font-size: 1rem;
  line-height: 1.65;
}

/* Stat cards row */
.stat-cards {
  display: flex;
  gap: 12px;
}
.stat-card {
  flex: 1;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 16px 12px;
  text-align: center;
  backdrop-filter: blur(8px);
}
.stat-num {
  font-size: 1.6rem;
  font-weight: 800;
  color: #e2e8f0;
  line-height: 1;
  margin-bottom: 4px;
}
.stat-label {
  font-size: 0.72rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* Feature pills */
.feature-pills {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pill {
  font-size: 0.85rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── RIGHT PANEL ── */
.login-right {
  width: 480px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 40px;
  background: #ffffff;
}

.login-form-wrap {
  width: 100%;
  max-width: 360px;
}

.form-header {
  margin-bottom: 32px;
}
.form-header h2 {
  font-size: 1.85rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
  margin-bottom: 4px;
}
.form-header p {
  color: #64748b;
  font-size: 0.92rem;
}

/* ── FIELDS ── */
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 18px;
}
.field label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #374151;
}
.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 12px;
  width: 17px;
  height: 17px;
  color: #94a3b8;
  pointer-events: none;
}
.input-wrap input {
  width: 100%;
  padding: 11px 40px 11px 38px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.93rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #f8fafc;
  color: #0f172a;
  font-family: inherit;
}
.input-wrap input:focus {
  border-color: #6366f1;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
}
.field.invalid .input-wrap input {
  border-color: #ef4444;
  background: #fff;
}
.eye-btn {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #94a3b8;
  display: flex;
  align-items: center;
}
.eye-btn svg { width: 18px; height: 18px; }
.eye-btn:hover { color: #475569; }
.err-msg {
  display: none;
  font-size: 0.76rem;
  color: #ef4444;
}
.field.invalid .err-msg { display: block; }

/* Error banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.86rem;
  margin-bottom: 16px;
}

/* Sign in button */
.sign-in-btn {
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 0.01em;
  box-shadow: 0 4px 14px rgba(99,102,241,0.35);
  margin-top: 4px;
}
.sign-in-btn:hover:not(:disabled) {
  opacity: 0.93;
  box-shadow: 0 6px 20px rgba(99,102,241,0.45);
  transform: translateY(-1px);
}
.sign-in-btn:active:not(:disabled) { transform: translateY(0); }
.sign-in-btn:disabled { opacity: 0.55; cursor: not-allowed; box-shadow: none; }

/* Spinner inside button */
.btn-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: btnSpin 0.65s linear infinite;
}
@keyframes btnSpin { to { transform: rotate(360deg); } }

/* Footer */
.form-footer {
  margin-top: 24px;
  text-align: center;
}
.form-footer p {
  font-size: 0.88rem;
  color: #64748b;
}
.form-footer a {
  color: #6366f1;
  font-weight: 600;
  text-decoration: none;
}
.form-footer a:hover { text-decoration: underline; }

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .login-left { display: none; }
  .login-right { width: 100%; padding: 32px 24px; }
}
</style>
