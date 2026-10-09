import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 1. Bootstrap CSS first
import 'bootstrap/dist/css/bootstrap.min.css'
// 2. Our design system overrides Bootstrap — must come AFTER
import './assets/main.css'
// 3. Bootstrap JS
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

createApp(App).use(router).mount('#app')
