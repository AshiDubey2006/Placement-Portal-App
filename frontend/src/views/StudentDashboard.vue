<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>Student Dashboard</h1>
        <p v-if="student" style="color:#64748b;font-size:0.9rem;margin-top:4px">
          {{ student.roll_number }} · {{ student.branch }} · Year {{ student.year }} · CGPA {{ student.cgpa }}
        </p>
      </div>
    </div>

    <div v-if="alert.msg" class="alert" :class="`alert-${alert.type}`">
      <span>{{ alert.msg }}</span><button class="alert-close" @click="alert.msg=''">×</button>
    </div>

    <!-- Resume warning -->
    <div v-if="student && !student.resume_path" class="alert alert-warning">
      ⚠️ Upload your resume before applying to drives.
      <button class="btn btn-sm btn-yellow" style="margin-left:12px" @click="activeTab='profile'">Upload Now</button>
    </div>

    <!-- KPI -->
    <div class="kpi-grid">
      <div class="kpi-card" style="--accent:#2563eb"><div class="kpi-label">Eligible Drives</div><div class="kpi-value">{{ allDrives.length }}</div></div>
      <div class="kpi-card" style="--accent:#64748b"><div class="kpi-label">Applied</div><div class="kpi-value">{{ myApps.length }}</div></div>
      <div class="kpi-card" style="--accent:#d97706"><div class="kpi-label">Shortlisted</div><div class="kpi-value">{{ myApps.filter(a=>a.status==='Shortlisted').length }}</div></div>
      <div class="kpi-card" style="--accent:#16a34a"><div class="kpi-label">Selected</div><div class="kpi-value">{{ myApps.filter(a=>a.status==='Selected').length }}</div></div>
    </div>

    <!-- Tabs -->
    <div class="tab-bar">
      <button v-for="t in tabs" :key="t.id" class="tab-btn" :class="{active:activeTab===t.id}" @click="activeTab=t.id">{{ t.label }}</button>
    </div>

    <!-- ===== DRIVES ===== -->
    <div v-show="activeTab==='drives'">
      <div class="toolbar">
        <input class="search-input" type="text" v-model="q" @input="filterDrives" placeholder="Search by company or role…" />
        <select class="filter-select" v-model="filterMode" @change="filterDrives">
          <option value="all">All eligible</option>
          <option value="pending">Not applied yet</option>
          <option value="applied">Already applied</option>
        </select>
      </div>

      <div v-if="filtered.length===0" class="empty-state">
        <div class="empty-icon">🔍</div><p>No drives match your search.</p>
      </div>

      <div class="drives-grid">
        <div v-for="d in filtered" :key="d.id" class="drive-card" :class="{applied: d.already_applied}">
          <div class="drive-top">
            <div>
              <div class="drive-title">{{ d.job_title }}</div>
              <div class="drive-company">🏢 {{ d.company_name }}</div>
            </div>
            <span v-if="d.already_applied" class="badge badge-green">Applied</span>
          </div>
          <p class="drive-desc">{{ truncate(d.job_description, 120) }}</p>
          <div class="drive-meta">
            <span>📅 {{ fmt(d.application_deadline) }}</span>
            <span>💰 {{ d.salary_package || 'N/A' }}</span>
            <span>📍 {{ d.location || 'N/A' }}</span>
            <span>🎓 Min CGPA {{ d.min_cgpa }}</span>
            <span>🌿 {{ d.eligibility_branch || 'All branches' }}</span>
            <span>📆 Year {{ d.eligibility_year || 'All' }}</span>
          </div>
          <div class="drive-footer">
            <button v-if="!d.already_applied" class="btn btn-blue" style="width:100%"
                    @click="applyDrive(d.id)" :disabled="applyingId===d.id">
              <span v-if="applyingId===d.id" class="spin"></span>
              {{ applyingId===d.id ? 'Applying…' : 'Apply Now' }}
            </button>
            <button v-else class="btn btn-ghost" style="width:100%" disabled>✅ Applied</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== APPLICATIONS ===== -->
    <div v-show="activeTab==='applications'">
      <div class="card">
        <div class="card-header">
          My Application History
          <button class="btn btn-sm btn-ghost" @click="exportCSV" :disabled="exporting">
            <span v-if="exporting" class="spin"></span>
            {{ exporting ? 'Exporting…' : '⬇ Export CSV' }}
          </button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>#</th><th>Company</th><th>Role</th><th>Applied</th><th>Status</th><th>Interview</th><th>Remarks</th></tr></thead>
            <tbody>
              <tr v-if="myApps.length===0"><td colspan="7"><div class="empty-state"><div class="empty-icon">📄</div><p>No applications yet.</p></div></td></tr>
              <tr v-for="(a,i) in myApps" :key="a.id">
                <td class="muted">{{ i+1 }}</td>
                <td>{{ a.company_name }}</td>
                <td><strong>{{ a.drive_title }}</strong></td>
                <td>{{ fmt(a.application_date) }}</td>
                <td><span class="badge" :class="appBadge(a.status)">{{ a.status }}</span></td>
                <td>
                  <small v-if="a.interview_date">{{ fmtDT(a.interview_date) }}<br><span class="muted">{{ a.interview_location }}</span></small>
                  <span v-else class="muted">—</span>
                </td>
                <td><small class="muted">{{ a.remarks || '—' }}</small></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===== PROFILE ===== -->
    <div v-show="activeTab==='profile'">
      <div class="card">
        <div class="card-header">Edit Profile</div>
        <div style="padding:24px">
          <form @submit.prevent="saveProfile">
            <div class="form-row-2">
              <div class="form-field"><label>First Name *</label><input type="text" v-model="prof.first_name" required /></div>
              <div class="form-field"><label>Last Name *</label><input type="text" v-model="prof.last_name" required /></div>
            </div>
            <div class="form-row-2">
              <div class="form-field"><label>Phone</label><input type="tel" v-model="prof.phone" placeholder="+91 98765 43210" /></div>
              <div class="form-field"><label>Skills</label><input type="text" v-model="prof.skills" placeholder="Python, Java, React…" /></div>
            </div>
            <div class="form-field">
              <label>Resume (PDF / DOC / DOCX)</label>
              <input type="file" @change="onFile" accept=".pdf,.doc,.docx" style="border:none;padding:0" />
              <small v-if="student?.resume_path" class="badge badge-green" style="width:fit-content;margin-top:4px">
                ✅ Resume uploaded
              </small>
            </div>
            <button type="submit" class="btn btn-blue" :disabled="profLoading">
              <span v-if="profLoading" class="spin"></span>
              {{ profLoading ? 'Saving…' : 'Save Changes' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'

export default {
  name: 'StudentDashboard',
  setup() {
    const tabs = [{ id:'drives',label:'🎯 Drives' },{ id:'applications',label:'📋 Applications' },{ id:'profile',label:'👤 Profile' }]
    const activeTab = ref('drives')
    const student = ref(null)
    const allDrives = ref([])
    const filtered = ref([])
    const myApps = ref([])
    const applyingId = ref(null)
    const profLoading = ref(false)
    const exporting = ref(false)
    const q = ref('')
    const filterMode = ref('all')
    const alert = ref({ msg:'', type:'success' })
    const selFile = ref(null)
    const prof = reactive({ first_name:'', last_name:'', phone:'', skills:'' })

    const showAlert = (msg, type='success') => { alert.value={msg,type}; setTimeout(()=>alert.value.msg='',5000) }

    const load = async () => {
      try {
        const r = await api.student.getDashboard()
        student.value = r.data.student
        allDrives.value = r.data.eligible_drives
        myApps.value = r.data.my_applications
        Object.assign(prof, { first_name:student.value.first_name, last_name:student.value.last_name, phone:student.value.phone||'', skills:student.value.skills||'' })
        filterDrives()
      } catch(e){ showAlert('Failed to load.','danger') }
    }

    const filterDrives = () => {
      const sq = q.value.toLowerCase().trim()
      filtered.value = allDrives.value.filter(d => {
        const m = !sq || d.job_title.toLowerCase().includes(sq) || d.company_name.toLowerCase().includes(sq)
        const f = filterMode.value==='all' || (filterMode.value==='pending'&&!d.already_applied) || (filterMode.value==='applied'&&d.already_applied)
        return m && f
      })
    }

    const applyDrive = async id => {
      if (!student.value?.resume_path) { showAlert('Upload your resume first.','warning'); activeTab.value='profile'; return }
      if (!confirm('Apply for this drive?')) return
      applyingId.value = id
      try { await api.drive.apply(id); showAlert('Application submitted! 🎉'); await load() }
      catch(e){ showAlert(e.response?.data?.error||'Failed.','danger') }
      finally { applyingId.value=null }
    }

    const saveProfile = async () => {
      profLoading.value=true
      try {
        await api.student.updateProfile({...prof})
        if (selFile.value) { const fd=new FormData(); fd.append('resume',selFile.value); await api.student.uploadResume(fd); selFile.value=null }
        showAlert('Profile saved!'); await load()
      } catch(e){ showAlert('Failed.','danger') }
      finally { profLoading.value=false }
    }

    const onFile = e => { selFile.value = e.target.files[0] }

    const exportCSV = async () => {
      exporting.value=true
      try {
        const r = await api.student.exportApplications()
        const tid = r.data.task_id
        const poll = setInterval(async () => {
          try {
            const s = await api.student.getExportStatus(tid)
            if (s.data.status==='completed') {
              clearInterval(poll)
              const dl = await api.student.downloadExport(s.data.file_path)
              const url = URL.createObjectURL(new Blob([dl.data]))
              const a = document.createElement('a'); a.href=url; a.download=s.data.file_path||'applications.csv'
              document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url)
              showAlert('CSV downloaded!')
              exporting.value=false
            } else if (s.data.status==='failed') { clearInterval(poll); showAlert('Export failed.','danger'); exporting.value=false }
          } catch(e){ clearInterval(poll); exporting.value=false }
        }, 2000)
      } catch(e){ showAlert('Export failed.','danger'); exporting.value=false }
    }

    const appBadge = s => ({ 'badge-blue':s==='Applied','badge-yellow':s==='Shortlisted','badge-green':s==='Selected','badge-red':s==='Rejected' })
    const fmt   = d => d ? new Date(d).toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'}) : '—'
    const fmtDT = d => d ? new Date(d).toLocaleString() : '—'
    const truncate = (s,n) => s&&s.length>n ? s.substring(0,n)+'…' : (s||'')

    onMounted(load)
    return { tabs, activeTab, student, allDrives, filtered, myApps, applyingId, profLoading, exporting, q, filterMode, alert, prof,
             filterDrives, applyDrive, saveProfile, onFile, exportCSV, appBadge, fmt, fmtDT, truncate }
  }
}
</script>

<style scoped>
.toolbar { display:flex; gap:12px; margin-bottom:16px; flex-wrap:wrap; }
.search-input { flex:1; min-width:200px; border:1.5px solid #e2e8f0; border-radius:8px; padding:9px 14px; font-size:.88rem; outline:none; background:#fff; }
.search-input:focus { border-color:#3b82f6; }
.filter-select { border:1.5px solid #e2e8f0; border-radius:8px; padding:9px 14px; font-size:.88rem; outline:none; background:#fff; }

.drives-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:18px; }
.drive-card { background:#fff; border-radius:12px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,.06); border:1.5px solid #f1f5f9; transition:box-shadow .2s,border-color .2s; display:flex; flex-direction:column; gap:12px; }
.drive-card:hover { box-shadow:0 4px 16px rgba(0,0,0,.08); border-color:#e2e8f0; }
.drive-card.applied { border-color:#86efac; background:#f0fdf4; }
.drive-top { display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }
.drive-title { font-size:1rem; font-weight:700; color:#0f172a; }
.drive-company { font-size:0.82rem; color:#64748b; margin-top:3px; }
.drive-desc { font-size:0.83rem; color:#64748b; line-height:1.5; }
.drive-meta { display:flex; flex-wrap:wrap; gap:6px; }
.drive-meta span { font-size:0.76rem; color:#64748b; background:#f8fafc; padding:3px 8px; border-radius:20px; white-space:nowrap; }
.drive-footer { margin-top:auto; }

.form-row-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.form-field { display:flex; flex-direction:column; gap:5px; margin-bottom:14px; }
.form-field label { font-size:.82rem; font-weight:600; color:#374151; }
.form-field input,.form-field select,.form-field textarea { border:1.5px solid #e2e8f0; border-radius:8px; padding:9px 12px; font-size:.9rem; outline:none; transition:border-color .2s; }
.form-field input:focus { border-color:#3b82f6; }
.muted { color:#94a3b8; font-size:.82rem; }
@media(max-width:640px) { .form-row-2 { grid-template-columns:1fr; } }
</style>
