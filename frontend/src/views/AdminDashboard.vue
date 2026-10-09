<template>
  <div class="page">
    <!-- Header -->
    <div class="page-header">
      <h1>Admin Dashboard</h1>
      <span class="badge badge-purple">Institute Placement Cell</span>
    </div>

    <!-- Alert -->
    <div v-if="alert.msg" class="alert" :class="`alert-${alert.type}`">
      <span>{{ alert.msg }}</span>
      <button class="alert-close" @click="alert.msg = ''">×</button>
    </div>

    <!-- KPI -->
    <div class="kpi-grid">
      <div class="kpi-card" style="--accent:#2563eb">
        <div class="kpi-label">Students</div>
        <div class="kpi-value">{{ stats.total_students ?? '—' }}</div>
      </div>
      <div class="kpi-card" style="--accent:#16a34a">
        <div class="kpi-label">Companies</div>
        <div class="kpi-value">{{ stats.total_companies ?? '—' }}</div>
      </div>
      <div class="kpi-card" style="--accent:#0891b2">
        <div class="kpi-label">Drives</div>
        <div class="kpi-value">{{ stats.total_drives ?? '—' }}</div>
      </div>
      <div class="kpi-card" style="--accent:#d97706">
        <div class="kpi-label">Applications</div>
        <div class="kpi-value">{{ stats.total_applications ?? '—' }}</div>
      </div>
      <div class="kpi-card" style="--accent:#dc2626">
        <div class="kpi-label">Pending Companies</div>
        <div class="kpi-value">{{ stats.pending_companies ?? '—' }}</div>
      </div>
      <div class="kpi-card" style="--accent:#7c3aed">
        <div class="kpi-label">Pending Drives</div>
        <div class="kpi-value">{{ stats.pending_drives ?? '—' }}</div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tab-bar">
      <button v-for="t in tabs" :key="t.id" class="tab-btn" :class="{ active: activeTab === t.id }" @click="switchTab(t.id)">
        {{ t.label }}
      </button>
    </div>

    <!-- ====== COMPANIES ====== -->
    <div v-show="activeTab === 'companies'">
      <div class="toolbar">
        <input class="search-input" type="text" placeholder="Search companies…" v-model="coSearch" @input="searchCompanies" />
        <select class="filter-select" v-model="coStatus" @change="searchCompanies">
          <option value="">All statuses</option>
          <option value="Pending">Pending</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>
      <div class="card">
        <div class="table-wrap">
          <table>
            <thead><tr><th>#</th><th>Company</th><th>Industry</th><th>Location</th><th>Status</th><th>Blacklisted</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-if="companies.length === 0"><td colspan="7"><div class="empty-state"><div class="empty-icon">🏢</div><p>No companies found.</p></div></td></tr>
              <tr v-for="(c,i) in companies" :key="c.id">
                <td class="muted">{{ i+1 }}</td>
                <td><strong>{{ c.company_name }}</strong><br><small class="muted">{{ c.hr_email }}</small></td>
                <td>{{ c.industry || '—' }}</td>
                <td>{{ c.location || '—' }}</td>
                <td><span class="badge" :class="statusBadge(c.approval_status)">{{ c.approval_status }}</span></td>
                <td><span class="badge" :class="c.is_blacklisted ? 'badge-red' : 'badge-gray'">{{ c.is_blacklisted ? 'Yes' : 'No' }}</span></td>
                <td>
                  <div class="btn-row">
                    <button v-if="c.approval_status==='Pending'" class="btn btn-sm btn-green" @click="approveCompany(c.id)">Approve</button>
                    <button v-if="c.approval_status==='Pending'" class="btn btn-sm btn-red" @click="rejectCompany(c.id)">Reject</button>
                    <button v-if="!c.is_blacklisted" class="btn btn-sm btn-yellow" @click="blacklistCompany(c.id)">Blacklist</button>
                    <button v-else class="btn btn-sm btn-ghost" @click="activateCompany(c.id)">Unblock</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ====== DRIVES ====== -->
    <div v-show="activeTab === 'drives'">
      <div class="toolbar">
        <input class="search-input" type="text" placeholder="Search drives…" v-model="drSearch" @input="searchDrives" />
        <select class="filter-select" v-model="drStatus" @change="searchDrives">
          <option value="">All statuses</option>
          <option value="Pending">Pending</option>
          <option value="Approved">Approved</option>
          <option value="Closed">Closed</option>
        </select>
      </div>
      <div class="card">
        <div class="table-wrap">
          <table>
            <thead><tr><th>#</th><th>Company</th><th>Job Title</th><th>Deadline</th><th>Applicants</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-if="drives.length === 0"><td colspan="7"><div class="empty-state"><div class="empty-icon">📋</div><p>No drives found.</p></div></td></tr>
              <tr v-for="(d,i) in drives" :key="d.id">
                <td class="muted">{{ i+1 }}</td>
                <td>{{ d.company_name }}</td>
                <td><strong>{{ d.job_title }}</strong></td>
                <td>{{ fmt(d.application_deadline) }}</td>
                <td><span class="badge badge-blue">{{ d.applicant_count }}</span></td>
                <td><span class="badge" :class="statusBadge(d.status)">{{ d.status }}</span></td>
                <td>
                  <div class="btn-row" v-if="d.status==='Pending'">
                    <button class="btn btn-sm btn-green" @click="approveDrive(d.id)">Approve</button>
                    <button class="btn btn-sm btn-red" @click="rejectDrive(d.id)">Reject</button>
                  </div>
                  <span v-else class="muted">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ====== STUDENTS ====== -->
    <div v-show="activeTab === 'students'">
      <div class="toolbar">
        <input class="search-input" type="text" placeholder="Search by name or roll number…" v-model="stSearch" @input="searchStudents" />
      </div>
      <div class="card">
        <div class="table-wrap">
          <table>
            <thead><tr><th>#</th><th>Name</th><th>Roll No.</th><th>Branch</th><th>Year</th><th>CGPA</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-if="students.length === 0"><td colspan="8"><div class="empty-state"><div class="empty-icon">🎓</div><p>No students found.</p></div></td></tr>
              <tr v-for="(s,i) in students" :key="s.id">
                <td class="muted">{{ i+1 }}</td>
                <td><strong>{{ s.full_name }}</strong></td>
                <td>{{ s.roll_number }}</td>
                <td>{{ s.branch }}</td>
                <td>{{ s.year }}</td>
                <td>{{ s.cgpa }}</td>
                <td><span class="badge" :class="s.is_blacklisted ? 'badge-red' : 'badge-green'">{{ s.is_blacklisted ? 'Blacklisted' : 'Active' }}</span></td>
                <td>
                  <button v-if="!s.is_blacklisted" class="btn btn-sm btn-yellow" @click="blacklistStudent(s.id)">Blacklist</button>
                  <button v-else class="btn btn-sm btn-ghost" @click="activateStudent(s.id)">Unblock</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ====== APPLICATIONS ====== -->
    <div v-show="activeTab === 'applications'">
      <div class="card">
        <div class="table-wrap">
          <table>
            <thead><tr><th>#</th><th>Student</th><th>Company</th><th>Drive</th><th>Applied On</th><th>Status</th></tr></thead>
            <tbody>
              <tr v-if="applications.length === 0"><td colspan="6"><div class="empty-state"><div class="empty-icon">📄</div><p>No applications yet.</p></div></td></tr>
              <tr v-for="(a,i) in applications" :key="a.id">
                <td class="muted">{{ i+1 }}</td>
                <td><strong>{{ a.student_name }}</strong><br><small class="muted">{{ a.student_roll_number }}</small></td>
                <td>{{ a.company_name }}</td>
                <td>{{ a.drive_title }}</td>
                <td>{{ fmt(a.application_date) }}</td>
                <td><span class="badge" :class="appBadge(a.status)">{{ a.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ====== STATISTICS ====== -->
    <div v-show="activeTab === 'statistics'">
      <div class="charts-grid">
        <div class="card">
          <div class="card-header">Application Status Breakdown</div>
          <div class="chart-body"><canvas id="appChart"></canvas></div>
        </div>
        <div class="card">
          <div class="card-header">Students by Branch</div>
          <div class="chart-body"><canvas id="branchChart"></canvas></div>
        </div>
        <div class="card chart-wide">
          <div class="card-header">Applications per Company</div>
          <div class="chart-body"><canvas id="companyChart"></canvas></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '../api'
Chart.register(...registerables)

export default {
  name: 'AdminDashboard',
  setup() {
    const tabs = [
      { id: 'companies', label: 'Companies' },
      { id: 'drives', label: 'Drives' },
      { id: 'students', label: 'Students' },
      { id: 'applications', label: 'Applications' },
      { id: 'statistics', label: '📊 Statistics' }
    ]
    const activeTab = ref('companies')
    const stats = ref({})
    const companies = ref([])
    const drives = ref([])
    const students = ref([])
    const applications = ref([])
    const statistics = ref({})
    const alert = ref({ msg: '', type: 'success' })
    const coSearch = ref(''); const coStatus = ref('')
    const drSearch = ref(''); const drStatus = ref('')
    const stSearch = ref('')
    let charts = {}

    const showAlert = (msg, type = 'success') => { alert.value = { msg, type }; setTimeout(() => alert.value.msg = '', 4000) }

    const loadDashboard = async () => {
      try {
        // Load each independently so one failure doesn't block others
        const [sRes, coRes, drRes, stRes, apRes] = await Promise.all([
          api.admin.getDashboard(),
          api.admin.getCompanies(),
          api.admin.getDrives(),
          api.admin.getStudents(),
          api.admin.getApplications()
        ])
        stats.value = sRes.data
        companies.value = coRes.data.companies
        drives.value = drRes.data.drives
        students.value = stRes.data.students
        applications.value = apRes.data.applications
      } catch (e) {
        showAlert('Some data failed to load: ' + (e.response?.data?.error || e.message), 'danger')
      }
    }

    const loadStatistics = async () => {
      try {
        const res = await api.admin.getStatistics()
        statistics.value = res.data
      } catch (e) { showAlert('Statistics load failed.', 'danger') }
    }

    const switchTab = async (id) => {
      activeTab.value = id
      if (id === 'statistics') { await loadStatistics(); await nextTick(); renderCharts() }
    }

    const renderCharts = () => {
      Object.values(charts).forEach(c => c.destroy()); charts = {}
      const s = statistics.value

      const appEl = document.getElementById('appChart')
      if (appEl) charts.app = new Chart(appEl, { type: 'doughnut', data: {
        labels: ['Applied', 'Shortlisted', 'Selected'],
        datasets: [{ data: [s.total_applications - (s.shortlisted_students||0) - (s.selected_students||0), s.shortlisted_students||0, s.selected_students||0],
          backgroundColor: ['#60a5fa', '#fbbf24', '#34d399'], borderWidth: 0 }]
      }, options: { plugins: { legend: { position: 'bottom' } }, cutout: '60%' } })

      const brEl = document.getElementById('branchChart')
      if (brEl && s.branch_stats?.length) charts.branch = new Chart(brEl, { type: 'bar', data: {
        labels: s.branch_stats.map(b => b.branch),
        datasets: [{ label: 'Students', data: s.branch_stats.map(b => b.count),
          backgroundColor: '#818cf8', borderRadius: 6 }]
      }, options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: '#f1f5f9' } }, x: { grid: { display: false } } } } })

      const coEl = document.getElementById('companyChart')
      if (coEl && s.company_stats?.length) charts.company = new Chart(coEl, { type: 'bar', data: {
        labels: s.company_stats.map(c => c.company),
        datasets: [
          { label: 'Drives', data: s.company_stats.map(c => c.drives), backgroundColor: '#60a5fa', borderRadius: 4 },
          { label: 'Applications', data: s.company_stats.map(c => c.applications), backgroundColor: '#34d399', borderRadius: 4 }
        ]
      }, options: { indexAxis: 'y', plugins: { legend: { position: 'top' } }, scales: { x: { beginAtZero: true, grid: { color: '#f1f5f9' } }, y: { grid: { display: false } } } } })
    }

    const searchCompanies = async () => { const r = await api.admin.getCompanies({ search: coSearch.value, status: coStatus.value }); companies.value = r.data.companies }
    const searchDrives    = async () => { const r = await api.admin.getDrives({ search: drSearch.value, status: drStatus.value }); drives.value = r.data.drives }
    const searchStudents  = async () => { const r = await api.admin.getStudents({ search: stSearch.value }); students.value = r.data.students }

    const approveCompany  = async id => { await api.admin.approveCompany(id);  showAlert('Company approved.');         await loadDashboard() }
    const rejectCompany   = async id => { await api.admin.rejectCompany(id);   showAlert('Company rejected.','warning'); await loadDashboard() }
    const blacklistCompany= async id => { if (!confirm('Blacklist this company?')) return; await api.admin.blacklistCompany(id); showAlert('Blacklisted.','warning'); await loadDashboard() }
    const activateCompany = async id => { await api.admin.activateCompany(id); showAlert('Company unblocked.');        await loadDashboard() }
    const approveDrive    = async id => { await api.admin.approveDrive(id);    showAlert('Drive approved.');           await loadDashboard() }
    const rejectDrive     = async id => { await api.admin.rejectDrive(id);     showAlert('Drive rejected.','warning'); await loadDashboard() }
    const blacklistStudent= async id => { if (!confirm('Blacklist this student?')) return; await api.admin.blacklistStudent(id); showAlert('Blacklisted.','warning'); await loadDashboard() }
    const activateStudent = async id => { await api.admin.activateStudent(id); showAlert('Student unblocked.');        await loadDashboard() }

    const statusBadge = s => ({ 'badge-green': s==='Approved', 'badge-red': s==='Rejected'||s==='Closed', 'badge-yellow': s==='Pending' })
    const appBadge    = s => ({ 'badge-blue': s==='Applied', 'badge-yellow': s==='Shortlisted', 'badge-green': s==='Selected', 'badge-red': s==='Rejected' })
    const fmt = d => d ? new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' }) : '—'

    onMounted(loadDashboard)
    return { tabs, activeTab, stats, companies, drives, students, applications, alert,
             coSearch, coStatus, drSearch, drStatus, stSearch,
             switchTab, searchCompanies, searchDrives, searchStudents,
             approveCompany, rejectCompany, blacklistCompany, activateCompany,
             approveDrive, rejectDrive, blacklistStudent, activateStudent,
             statusBadge, appBadge, fmt }
  }
}
</script>

<style scoped>
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.search-input { flex: 1; min-width: 200px; border: 1.5px solid #e2e8f0; border-radius: 8px; padding: 9px 14px; font-size: 0.88rem; outline: none; background: #fff; }
.search-input:focus { border-color: #3b82f6; }
.filter-select { border: 1.5px solid #e2e8f0; border-radius: 8px; padding: 9px 14px; font-size: 0.88rem; outline: none; background: #fff; }
.btn-row { display: flex; gap: 6px; flex-wrap: wrap; }
.muted { color: #94a3b8; font-size: 0.82rem; }
.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.chart-wide { grid-column: 1 / -1; }
.chart-body { padding: 20px; }
@media (max-width: 768px) { .charts-grid { grid-template-columns: 1fr; } }
</style>
