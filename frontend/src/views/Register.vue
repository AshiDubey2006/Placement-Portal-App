<template>
  <div class="register-page">
    <div class="register-left">
      <div class="brand-block">
        <div class="brand-icon">🎓</div>
        <h1>Placement Portal</h1>
        <p>Join your campus recruitment ecosystem. Students find their first role. Companies find the best talent.</p>
      </div>
    </div>

    <div class="register-right">
      <div class="register-card">
        <h2>Create account</h2>
        <p class="subtitle">Choose your role to get started</p>

        <!-- Role toggle -->
        <div class="role-toggle">
          <button :class="['role-btn', { active: role === 'student' }]" @click="role = 'student'" type="button">
            🎓 Student
          </button>
          <button :class="['role-btn', { active: role === 'company' }]" @click="role = 'company'" type="button">
            🏢 Company
          </button>
        </div>

        <form @submit.prevent="register" novalidate>
          <!-- Common -->
          <div class="row-2">
            <div class="field-group" :class="{ error: submitted && !form.email }">
              <label>Email <span class="req">*</span></label>
              <input type="email" v-model="form.email" placeholder="you@example.com" />
              <span class="field-error">Required.</span>
            </div>
            <div class="field-group" :class="{ error: submitted && form.password.length < 6 }">
              <label>Password <span class="req">*</span></label>
              <input type="password" v-model="form.password" placeholder="Min 6 chars" />
              <span class="field-error">Min 6 characters.</span>
            </div>
          </div>

          <!-- STUDENT fields -->
          <template v-if="role === 'student'">
            <div class="row-2">
              <div class="field-group" :class="{ error: submitted && !form.first_name }">
                <label>First Name <span class="req">*</span></label>
                <input type="text" v-model="form.first_name" placeholder="Riya" />
                <span class="field-error">Required.</span>
              </div>
              <div class="field-group" :class="{ error: submitted && !form.last_name }">
                <label>Last Name <span class="req">*</span></label>
                <input type="text" v-model="form.last_name" placeholder="Sharma" />
                <span class="field-error">Required.</span>
              </div>
            </div>
            <div class="row-2">
              <div class="field-group" :class="{ error: submitted && !form.roll_number }">
                <label>Roll Number <span class="req">*</span></label>
                <input type="text" v-model="form.roll_number" placeholder="21CSE001" />
                <span class="field-error">Required.</span>
              </div>
              <div class="field-group">
                <label>Phone</label>
                <input type="tel" v-model="form.phone" placeholder="+91 98765 43210" />
              </div>
            </div>
            <div class="row-3">
              <div class="field-group" :class="{ error: submitted && !form.branch }">
                <label>Branch <span class="req">*</span></label>
                <select v-model="form.branch">
                  <option value="">Select</option>
                  <option value="CSE">CSE</option>
                  <option value="IT">IT</option>
                  <option value="ECE">ECE</option>
                  <option value="EEE">EEE</option>
                  <option value="MECH">MECH</option>
                  <option value="CIVIL">CIVIL</option>
                  <option value="AIDS">AIDS</option>
                  <option value="OTHER">Other</option>
                </select>
                <span class="field-error">Required.</span>
              </div>
              <div class="field-group" :class="{ error: submitted && !form.year }">
                <label>Year <span class="req">*</span></label>
                <select v-model="form.year">
                  <option value="">Select</option>
                  <option :value="1">1st Year</option>
                  <option :value="2">2nd Year</option>
                  <option :value="3">3rd Year</option>
                  <option :value="4">4th Year</option>
                </select>
                <span class="field-error">Required.</span>
              </div>
              <div class="field-group" :class="{ error: submitted && (form.cgpa === '' || Number(form.cgpa) < 0 || Number(form.cgpa) > 10) }">
                <label>CGPA <span class="req">*</span></label>
                <input type="number" step="0.01" min="0" max="10" v-model="form.cgpa" placeholder="8.50" />
                <span class="field-error">0 – 10.</span>
              </div>
            </div>
          </template>

          <!-- COMPANY fields -->
          <template v-if="role === 'company'">
            <div class="field-group" :class="{ error: submitted && !form.company_name }">
              <label>Company Name <span class="req">*</span></label>
              <input type="text" v-model="form.company_name" placeholder="Acme Corp" />
              <span class="field-error">Required.</span>
            </div>
            <div class="row-2">
              <div class="field-group">
                <label>HR Contact Name</label>
                <input type="text" v-model="form.hr_contact" placeholder="Priya Mehta" />
              </div>
              <div class="field-group">
                <label>HR Email</label>
                <input type="email" v-model="form.hr_email" placeholder="hr@company.com" />
              </div>
            </div>
            <div class="row-2">
              <div class="field-group">
                <label>Industry</label>
                <input type="text" v-model="form.industry" placeholder="Software / Finance…" />
              </div>
              <div class="field-group">
                <label>Location</label>
                <input type="text" v-model="form.location" placeholder="Bangalore, India" />
              </div>
            </div>
            <div class="field-group">
              <label>Website</label>
              <input type="url" v-model="form.website" placeholder="https://company.com" />
            </div>
            <div class="info-note">
              ℹ️ Company accounts require admin approval before you can post drives.
            </div>
          </template>

          <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>
          <div v-if="successMsg" class="success-banner">{{ successMsg }}</div>

          <button type="submit" class="btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Registering…' : `Register as ${role === 'student' ? 'Student' : 'Company'}` }}
          </button>
        </form>

        <div class="divider"></div>
        <p class="alt-link">Already have an account? <router-link to="/login">Sign in</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const blank = () => ({
  email: '', password: '',
  first_name: '', last_name: '', roll_number: '', phone: '', branch: '', year: '', cgpa: '',
  company_name: '', hr_contact: '', hr_email: '', website: '', industry: '', location: '', description: ''
})

export default {
  name: 'RegisterPage',
  setup() {
    const router = useRouter()
    const role = ref('student')
    const form = reactive(blank())
    const errorMsg = ref('')
    const successMsg = ref('')
    const loading = ref(false)
    const submitted = ref(false)

    watch(role, () => { Object.assign(form, blank()); submitted.value = false; errorMsg.value = '' })

    const valid = () => {
      if (!form.email || form.password.length < 6) return false
      if (role.value === 'student')
        return !!(form.first_name && form.last_name && form.roll_number && form.branch && form.year &&
                  form.cgpa !== '' && Number(form.cgpa) >= 0 && Number(form.cgpa) <= 10)
      return !!form.company_name
    }

    const register = async () => {
      submitted.value = true
      if (!valid()) return
      loading.value = true; errorMsg.value = ''; successMsg.value = ''
      const payload = { email: form.email, password: form.password, role: role.value }
      if (role.value === 'student') Object.assign(payload, { first_name: form.first_name, last_name: form.last_name, roll_number: form.roll_number, branch: form.branch, year: Number(form.year), cgpa: Number(form.cgpa), phone: form.phone })
      else Object.assign(payload, { company_name: form.company_name, hr_contact: form.hr_contact, hr_email: form.hr_email || form.email, website: form.website, industry: form.industry, location: form.location })
      try {
        await api.auth.register(payload)
        successMsg.value = role.value === 'company' ? 'Registered! Await admin approval.' : 'Registered! Redirecting to login…'
        setTimeout(() => router.push('/login'), 1800)
      } catch (e) {
        errorMsg.value = e.response?.data?.error || 'Registration failed.'
      } finally { loading.value = false }
    }

    return { role, form, errorMsg, successMsg, loading, submitted, register }
  }
}
</script>

<style scoped>
* { box-sizing: border-box; }
.register-page { display: flex; min-height: 100vh; font-family: 'Segoe UI', system-ui, sans-serif; }

.register-left {
  width: 360px; flex-shrink: 0;
  background: linear-gradient(145deg, #0f172a 0%, #1e3a5f 50%, #0e4d92 100%);
  display: flex; align-items: center; justify-content: center; padding: 48px 36px;
}
.brand-block { color: #fff; }
.brand-icon { font-size: 48px; margin-bottom: 14px; }
.brand-block h1 { font-size: 1.9rem; font-weight: 700; margin: 0 0 12px; }
.brand-block p { color: #94a3b8; line-height: 1.6; font-size: 0.95rem; }

.register-right { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px 32px; background: #f8fafc; overflow-y: auto; }
.register-card { width: 100%; max-width: 560px; }
.register-card h2 { font-size: 1.7rem; font-weight: 700; color: #0f172a; margin: 0 0 4px; }
.subtitle { color: #64748b; margin: 0 0 24px; font-size: 0.92rem; }

.role-toggle { display: flex; gap: 8px; margin-bottom: 28px; background: #e2e8f0; border-radius: 10px; padding: 4px; }
.role-btn { flex: 1; padding: 9px; border: none; border-radius: 8px; font-size: 0.95rem; font-weight: 600; cursor: pointer; background: transparent; color: #64748b; transition: all 0.2s; }
.role-btn.active { background: #fff; color: #1d4ed8; box-shadow: 0 1px 4px rgba(0,0,0,0.12); }

.row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }

.field-group { display: flex; flex-direction: column; gap: 5px; margin-bottom: 14px; }
.field-group label { font-size: 0.82rem; font-weight: 600; color: #374151; }
.req { color: #ef4444; }
.field-group input, .field-group select {
  border: 1.5px solid #e2e8f0; border-radius: 8px; padding: 10px 12px;
  font-size: 0.92rem; outline: none; transition: border-color 0.2s; background: #fff; color: #0f172a;
}
.field-group input:focus, .field-group select:focus { border-color: #3b82f6; }
.field-group.error input, .field-group.error select { border-color: #ef4444; }
.field-error { display: none; font-size: 0.76rem; color: #ef4444; }
.field-group.error .field-error { display: block; }

.info-note { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 10px 14px; font-size: 0.85rem; color: #1d4ed8; margin-bottom: 14px; }

.btn-primary {
  width: 100%; padding: 13px; background: #2563eb; color: #fff;
  border: none; border-radius: 8px; font-size: 1rem; font-weight: 600;
  cursor: pointer; transition: background 0.2s; display: flex;
  align-items: center; justify-content: center; gap: 8px; margin-top: 8px;
}
.btn-primary:hover:not(:disabled) { background: #1d4ed8; }
.btn-primary:disabled { background: #93c5fd; cursor: not-allowed; }

.error-banner { background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; border-radius: 8px; padding: 10px 14px; font-size: 0.87rem; margin-bottom: 14px; }
.success-banner { background: #f0fdf4; border: 1px solid #bbf7d0; color: #16a34a; border-radius: 8px; padding: 10px 14px; font-size: 0.87rem; margin-bottom: 14px; }
.spinner { width: 15px; height: 15px; border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.divider { border: none; border-top: 1px solid #e2e8f0; margin: 22px 0; }
.alt-link { text-align: center; font-size: 0.9rem; color: #64748b; margin: 0; }
.alt-link a { color: #2563eb; font-weight: 600; text-decoration: none; }
.alt-link a:hover { text-decoration: underline; }

@media (max-width: 768px) {
  .register-left { display: none; }
  .register-right { padding: 24px 20px; }
  .row-2 { grid-template-columns: 1fr; }
  .row-3 { grid-template-columns: 1fr 1fr; }
}
</style>
