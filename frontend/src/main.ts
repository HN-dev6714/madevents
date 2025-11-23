import './assets/main.css';
import { createApp } from 'vue'
//import { setupCalendar } from 'v-calendar'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)
//app.use(setupCalendar, {})

app.mount('#app')
