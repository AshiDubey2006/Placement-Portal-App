<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1>{{ company?.company_name || 'Company Dashboard' }}</h1>
        <p v-if="company" style="color:#64748b;font-size:0.9rem;margin-top:4px">{{ company.industry }} · {{ company.location }}</p>
      </div>
      <span class="badge" :class="company?.approval_status === 'Approved' ? 'badge-green' : 'badge-yellow'">
        {{ company?.approval_status || '—' }}
      </span>
    </div>

    <div v-if="alert.msg" class="alert" :class="`alert-${alert.type}`">
      <span>{{ alert.msg }}</span>
      <button class="alert-close" @click="alert.msg=''">×</button>
    </div>

    <div v-if="company && company.approval_status !== 'Approved'" class="alert alert-warning">
      ⏳ Your company is awaiting admin approval. You can create drives once approved.
    </div>

    <!-- KPI -->
    <div class="kpi-grid">
      <div class="kpi-card" style="--accent:#2563eb"><div class="kpi-label">Total Drives</div><div class="kpi-value">{{ dashStats.total_drives ?? '—' }}</div></div>
      <div class="kpi-card" style="--accent:#16a34a"><div class="kpi-label">Total Applicants</div><div class="kpi-value">{{ dashStats.total_applicants ?? '—' }}</div></div>
      <div class="kpi-card" style="--accent:#0891b2"><div class="kpi-label">Approved Drives</div><div class="kpi-value">{{ activeDrives }}</div></div>
    </div>

    <!-- Tabs -->
    <div class="tab-bar">
      <button v-for="t in tabs" :key="t.id" class="tab-btn" :class="{active:activeTab===t.id}" @click="activeTab=t.id">{{ t.label }}</button>
    </div>

    <!-- ===== DRIVES ===== -->
    <div v-show="activeTab==='drives'">
      <div class="card">
        <div class="card-header">My Placement Drives</div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>#</th><th>Job Title</th><th>Package</th><th>Deadline</th><th>Applicants</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              <tr v-if="drives.length===0"><td colspan="7"><div class="empty-state"><div class="empty-icon">📋</div><p>No drives yet. Create your first one!</p></div></td></tr>
              <tr v-for="(d,i) in drives" :key="d.id">
                <td class="muted">{{ i+1 }}</td>
                <td><strong>{{ d.job_title }}</strong><br><small class="muted">{{ d.location }}</small></td>
                <td>{{ d.salary_package || '—' }}</td>
                <td>{{ fmt(d.application_deadline) }}</td>
                <td><span class="badge badge-blue">{{ d.applicant_count }}</span></td>
                <td><span class="badge" :class="driveBadge(d.status)">{{ d.status }}</span></td>
                <td>
                  <div class="btn-row">
                    <button class="btn btn-sm btn-blue" @click="viewApps(d)">Applications</button>
                    <button v-if="d.status!=='Approved'" class="btn btn-sm btn-ghost" @click="openEdit(d)">Edit</button>
                    <button v-if="d.status==='Approved'" class="btn btn-sm btn-warning" @click="closeDrive(d.id)">Close</button>
                    <button v-if="d.status!=='Approved'" class="btn btn-sm btn-danger" @click="deleteDrive(d.id)">Delete</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===== CREATE DRIVE ===== -->
    <div v-show="activeTab==='create'">
      <div class="card">
        <div class="card-header">Create New Placement Drive</div>
        <div style="padding:24px">
          <form @submit.prevent="createDrive" novalidate>
            <div class="form-row-2">
              <div class="form-field" :class="{err: ds && !nd.job_title}">
                <label>Job Title *</label>
                <input type="text" v-model="nd.job_title" placeholder="Software Engineer" />
                <span class="ferr">Required.</span>
              </div>
              <div class="form-field">
                <label>Salary Package</label>
                <input type="text" v-model="nd.salary_package" placeholder="₹8 LPA" />
              </div>
            </div>
            <div class="form-field" :class="{err: ds && !nd.job_description}">
              <label>Job Description *</label>
              <textarea v-model="nd.job_description" rows="4" placeholder="Describe the role…"></textarea>
              <span class="ferr">Required.</span>
            </div>
            <div class="form-row-3">
              <div class="form-field">
                <label>Eligible Branches</label>
                <input type="text" v-model="nd.eligibility_branch" placeholder="CSE, ECE, IT" />
                <small class="muted">Comma-separated. Blank = all.</small>
              </div>
              <div class="form-field">
                <label>Eligible Years</label>
                <input type="text" v-model="nd.eligibility_year" placeholder="3, 4" />
                <small class="muted">Comma-separated. Blank = all.</small>
              </div>
              <div class="form-field">
                <label>Min CGPA</label>
                <input type="number" step="0.01" min="0" max="10" v-model="nd.min_cgpa" placeholder="6.00" />
              </div>
            </div>
            <div class="form-row-3">
              <div class="form-field" :class="{err: ds && !nd.application_deadline}">
                <label>Application Deadline *</label>
                <input type="datetime-local" v-model="nd.application_deadline" />
                <span class="ferr">Required.</span>
              </div>
              <div class="form-field">
                <label>Drive Date</label>
                <input type="datetime-local" v-model="nd.drive_date" />
              </div>
              <div class="form-field">
                <label>Location</label>
                <input type="text" v-model="nd.location" placeholder="Bangalore / Online" />
              </div>
            </div>
            <button type="submit" class="btn btn-blue" :disabled="loading">
              <span v-if="loading" class="spin"></span>
              {{ loading ? 'Creating…' : 'Create Drive' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- ===== PROFILE ===== -->
    <div v-show="activeTab==='profile'">
      <div class="card">
        <div class="card-header">Edit Company Profile</div>
        <div style="padding:24px">
          <form @submit.prevent="updateProfile">
            <div class="form-row-2">
              <div class="form-field"><label>Company Name *</label><input type="text" v-model="prof.company_name" required /></div>
              <div class="form-field"><label>Industry</label><input type="text" v-model="prof.industry" /></div>
            </div>
            <div class="form-row-2">
              <div class="form-field"><label>HR Contact Name</label><input type="text" v-model="prof.hr_contact" /></div>
              <div class="form-field"><label>HR Email</label><input type="email" v-model="prof.hr_email" /></div>
            </div>
            <div class="form-row-2">
              <div class="form-field"><label>Website</label><input type="url" v-model="prof.website" /></div>
              <div class="form-field"><label>Location</label><input type="text" v-model="prof.location" /></div>
            </div>
            <div class="form-field"><label>Description</label><textarea v-model="prof.description" rows="3"></textarea></div>
            <button type="submit" class="btn btn-blue" :disabled="loading">
              <span v-if="loading" class="spin"></span>{{ loading ? 'Saving…' : 'Save Changes' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- ===== EDIT DRIVE MODAL ===== -->
    <div v-if="editModal" class="modal-overlay" @click.self="editModal=false">
      <div class="modal-box">
        <div class="modal-header"><h3>Edit Drive</h3><button class="modal-close" @click="editModal=false">×</button></div>
        <div class="modal-body">
          <form @submit.prevent="submitEdit">
            <div class="form-row-2">
              <div class="form-field"><label>Job Title</label><input type="text" v-model="ed.job_title" required /></div>
              <div class="form-field"><label>Package</label><input type="text" v-model="ed.salary_package" /></div>
            </div>
            <div class="form-field"><label>Description</label><textarea v-model="ed.job_description" rows="3" required></textarea></div>
            <div class="form-row-3">
              <div class="form-field"><label>Branches</label><input type="text" v-model="ed.eligibility_branch" /></div>
              <div class="form-field"><label>Years</label><input type="text" v-model="ed.eligibility_year" /></div>
              <div class="form-field"><label>Min CGPA</label><input type="number" step="0.01" min="0" max="10" v-model="ed.min_cgpa" /></div>
            </div>
            <div class="form-row-2">
              <div class="form-field"><label>Deadline</label><input type="datetime-local" v-model="ed.application_deadline" /></div>
              <div class="form-field"><label>Drive Date</label><input type="datetime-local" v-model="ed.drive_date" /></div>
            </div>
            <div class="form-field"><label>Location</label><input type="text" v-model="ed.location" /></div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="editModal=false">Cancel</button>
          <button class="btn btn-blue" @click="submitEdit" :disabled="loading">{{ loading ? 'Saving…' : 'Save Changes' }}</button>
        </div>
      </div>
    </div>

    <!-- ===== APPLICATIONS MODAL ===== -->
    <div v-if="appsModal" class="modal-overlay" @click.self="appsModal=false">
      <div class="modal-box" style="max-width:900px">
        <div class="modal-header"><h3>{{ curDrive?.job_title }} — Applications</h3><button class="modal-close" @click="appsModal=false">×</button></div>
        <div class="modal-body" style="padding:0">
          <div class="table-wrap">
            <table>
              <thead><tr><th>Student</th><th>Branch</th><th>CGPA</th><th>Status</th><th>Interview</th><th>Actions</th></tr></thead>
              <tbody>
                <tr v-if="applications.length===0"><td colspan="6"><div class="empty-state"><p>No applications yet.</p></div></td></tr>
                <tr v-for="a in applications" :key="a.id">
                  <td><strong>{{ a.student_name }}</strong><br><small class="muted">{{ a.student_roll_number }}</small></td>
                  <td>{{ a.student_branch }}</td>
                  <td>{{ a.student_cgpa }}</td>
                  <td><span class="badge" :class="appBadge(a.status)">{{ a.status }}</span></td>
                  <td>
                    <small v-if="a.interview_date">{{ fmtDT(a.interview_date) }}<br><span class="muted">{{ a.interview_location }}</span></small>
                    <span v-else class="muted">—</span>
                  </td>
                  <td>
                    <div class="btn-row">
                      <button v-if="a.status==='Applied'" class="btn btn-sm btn-yellow" @click="openShortlist(a)">Shortlist</button>
                      <button v-if="a.status==='Shortlisted'" class="btn btn-sm btn-green" @click="selectApp(a.id)">Select</button>
                      <button v-if="a.status==='Selected'" class="btn btn-sm btn-ghost" @click="offerLetter(a.id, a.student_name)">Offer Letter</button>
                      <button v-if="a.status!=='Rejected'&&a.status!=='Selected'" class="btn btn-sm btn-red" @click="rejectApp(a.id)">Reject</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== SHORTLIST MODAL ===== -->
    <div v-if="slModal" class="modal-overlay" @click.self="slModal=false">
      <div class="modal-box" style="max-width:440px">
        <div class="modal-header"><h3>Shortlist — {{ slTarget?.student_name }}</h3><button class="modal-close" @click="slModal=false">×</button></div>
        <div class="modal-body">
          <div class="form-field"><label>Interview Date & Time (optional)</label><input type="datetime-local" v-model="sl.interview_date" /></div>
          <div class="form-field"><label>Interview Location (optional)</label><input type="text" v-model="sl.interview_location" placeholder="Room 201 / Zoom link" /></div>
          <div class="form-field"><label>Remarks (optional)</label><textarea v-model="sl.remarks" rows="2"></textarea></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="slModal=false">Cancel</button>
          <button class="btn btn-yellow" @click="confirmShortlist">Confirm Shortlist</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, reactive, onMounted } from 'vue'
import api from '../api'

const blankDrive = () => ({ job_title:'', job_description:'', salary_package:'', eligibility_branch:'', eligibility_year:'', min_cgpa:0, application_deadline:'', drive_date:'', location:'' })

export default {
  name: 'CompanyDashboard',
  setup() {
    const tabs = [{ id:'drives',label:'My Drives' },{ id:'create',label:'+ New Drive' },{ id:'profile',label:'Profile' }]
    const activeTab = ref('drives')
    const company = ref(null)
    const drives = ref([])
    const dashStats = ref({})
    const applications = ref([])
    const loading = ref(false)
    const alert = ref({ msg:'', type:'success' })
    const ds = ref(false) // drive submitted

    const nd = reactive(blankDrive())
    const prof = reactive({ company_name:'', hr_contact:'', hr_email:'', website:'', industry:'', location:'', description:'' })

    const editModal = ref(false); const ed = reactive({}); const editId = ref(null)
    const appsModal = ref(false); const curDrive = ref(null)
    const slModal = ref(false); const slTarget = ref(null); const sl = reactive({ interview_date:'', interview_location:'', remarks:'' })

    const activeDrives = computed(() => drives.value.filter(d => d.status==='Approved').length)
    const showAlert = (msg, type='success') => { alert.value={msg,type}; setTimeout(() => alert.value.msg='', 4000) }

    const load = async () => {
      try {
        const [pR, dR, drR] = await Promise.all([api.company.getProfile(), api.company.getDashboard(), api.company.getDrives()])
        company.value = pR.data; dashStats.value = dR.data; drives.value = drR.data.drives
        Object.assign(prof, company.value)
      } catch (e) { showAlert('Failed to load dashboard.','danger') }
    }

    const createDrive = async () => {
      ds.value = true
      if (!nd.job_title || !nd.job_description || !nd.application_deadline) return
      loading.value = true
      try { await api.company.createDrive({...nd}); showAlert('Drive submitted for approval!'); Object.assign(nd, blankDrive()); ds.value=false; activeTab.value='drives'; await load() }
      catch (e) { showAlert(e.response?.data?.error || 'Failed.','danger') }
      finally { loading.value=false }
    }

    const updateProfile = async () => {
      loading.value=true
      try { await api.company.updateProfile({...prof}); showAlert('Profile updated.'); await load() }
      catch (e) { showAlert('Failed.','danger') }
      finally { loading.value=false }
    }

    const viewApps = async (drive) => {
      curDrive.value = drive
      const r = await api.company.getDriveApplications(drive.id)
      applications.value = r.data.applications
      appsModal.value = true
    }

    const toLocal = iso => iso ? iso.substring(0,16) : ''
    const openEdit = d => { editId.value=d.id; Object.assign(ed,{...d, application_deadline:toLocal(d.application_deadline), drive_date:toLocal(d.drive_date)}); editModal.value=true }
    const submitEdit = async () => { loading.value=true; try { await api.company.updateDrive(editId.value,{...ed}); showAlert('Drive updated.'); editModal.value=false; await load() } catch(e){showAlert('Failed.','danger')} finally{loading.value=false} }

    const openShortlist = a => { slTarget.value=a; Object.assign(sl,{interview_date:'',interview_location:'',remarks:''}); slModal.value=true }
    const confirmShortlist = async () => { try { await api.company.shortlistStudent(slTarget.value.id,{...sl}); showAlert('Shortlisted!'); slModal.value=false; await viewApps(curDrive.value) } catch(e){showAlert('Failed.','danger')} }
    const selectApp = async id => { if(!confirm('Mark as Selected?')) return; await api.company.selectStudent(id); showAlert('Selected! 🎉'); await viewApps(curDrive.value) }
    const rejectApp = async id => { if(!confirm('Reject this application?')) return; await api.company.rejectStudent(id,{}); showAlert('Rejected.','warning'); await viewApps(curDrive.value) }
    const offerLetter = async (id, name) => {
      try {
        const r = await api.company.generateOfferLetter(id)
        const url = URL.createObjectURL(new Blob([r.data],{type:'text/html'}))
        const a = document.createElement('a'); a.href=url; a.download=`Offer_${name.replace(/ /g,'_')}.html`
        document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url)
      } catch(e){showAlert('Failed.','danger')}
    }
    const closeDrive = async id => { if(!confirm('Close this drive? No new applications will be accepted.')) return; try { await api.company.closeDrive(id); showAlert('Drive closed.'); await load() } catch(e){showAlert('Failed.','danger')} }
    const deleteDrive = async id => { if(!confirm('Delete this drive? This cannot be undone.')) return; try { await api.company.deleteDrive(id); showAlert('Drive deleted.'); await load() } catch(e){showAlert('Failed.','danger')} }

    const driveBadge = s => ({ 'badge-green':s==='Approved','badge-red':s==='Closed','badge-yellow':s==='Pending' })
    const appBadge   = s => ({ 'badge-blue':s==='Applied','badge-yellow':s==='Shortlisted','badge-green':s==='Selected','badge-red':s==='Rejected' })
    const fmt   = d => d ? new Date(d).toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'}) : '—'
    const fmtDT = d => d ? new Date(d).toLocaleString() : '—'

    onMounted(load)
    return { tabs, activeTab, company, drives, dashStats, applications, loading, alert, ds, nd, prof, activeDrives,
             editModal, ed, appsModal, curDrive, slModal, slTarget, sl,
             createDrive, updateProfile, viewApps, openEdit, submitEdit,
             openShortlist, confirmShortlist, selectApp, rejectApp, offerLetter,
             closeDrive, deleteDrive,
             driveBadge, appBadge, fmt, fmtDT }
  }
}
</script>

<style scoped>
.form-row-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.form-row-3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; }
.form-field { display:flex; flex-direction:column; gap:5px; margin-bottom:14px; }
.form-field label { font-size:0.82rem; font-weight:600; color:#374151; }
.form-field input,.form-field select,.form-field textarea { border:1.5px solid #e2e8f0; border-radius:8px; padding:9px 12px; font-size:0.9rem; outline:none; transition:border-color .2s; }
.form-field input:focus,.form-field select:focus,.form-field textarea:focus { border-color:#3b82f6; }
.form-field.err input,.form-field.err textarea { border-color:#ef4444; }
.ferr { display:none; font-size:.76rem; color:#ef4444; }
.form-field.err .ferr { display:block; }
.btn-row { display:flex; gap:6px; flex-wrap:wrap; }
.muted { color:#94a3b8; font-size:0.82rem; }
@media(max-width:640px) { .form-row-2,.form-row-3 { grid-template-columns:1fr; } }
</style>
