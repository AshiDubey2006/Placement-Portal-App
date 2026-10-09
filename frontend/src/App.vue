<template>
  <div id="app">
    <nav class="topnav" v-if="isAuthenticated">
      <div class="nav-inner">
        <a class="nav-brand" href="#" @click.prevent="navigateToDashboard">
          🎓 <span>Placement Portal</span>
        </a>
        <div class="nav-links">
          <router-link v-if="userRole === 'admin'"   to="/admin/dashboard"   class="nav-link">Dashboard</router-link>
          <router-link v-if="userRole === 'company'" to="/company/dashboard" class="nav-link">Dashboard</router-link>
          <router-link v-if="userRole === 'student'" to="/student/dashboard" class="nav-link">Dashboard</router-link>
        </div>
        <div class="nav-right">
          <span class="role-chip" :class="`chip-${userRole}`">{{ userRole }}</span>
          <span class="nav-username">{{ userName }}</span>
          <button class="logout-btn" @click="logout">Logout</button>
        </div>
      </div>
    </nav>

    <div class="toast-stack">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="`toast-${t.type}`">
        {{ t.message }}
        <button class="toast-close" @click="removeToast(t.id)">×</button>
      </div>
    </div>

    <router-view @auth-changed="refreshAuth" @show-toast="addToast" />

    <footer class="site-footer" v-if="isAuthenticated">
      © 2026 Placement Portal — Campus Recruitment System
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const isAuthenticated = ref(false)
    const userRole = ref('')
    const userName = ref('')
    const toasts = ref([])
    let tc = 0

    const refreshAuth = () => {
      isAuthenticated.value = !!localStorage.getItem('token')
      userRole.value = localStorage.getItem('userRole') || ''
      userName.value = localStorage.getItem('userName') || ''
    }
    onMounted(() => { refreshAuth(); window.addEventListener('storage', refreshAuth) })

    const logout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('userRole')
      localStorage.removeItem('userName')
      refreshAuth()
      router.push('/login')
    }
    const navigateToDashboard = () => {
      const map = { admin: '/admin/dashboard', company: '/company/dashboard', student: '/student/dashboard' }
      if (map[userRole.value]) router.push(map[userRole.value])
    }
    const addToast = ({ message, type = 'success' }) => {
      const id = ++tc
      toasts.value.push({ id, message, type })
      setTimeout(() => removeToast(id), 4000)
    }
    const removeToast = (id) => { toasts.value = toasts.value.filter(t => t.id !== id) }

    return { isAuthenticated, userRole, userName, toasts, refreshAuth, logout, navigateToDashboard, addToast, removeToast }
  }
}
</script>
