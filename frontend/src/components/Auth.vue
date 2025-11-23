<template>
  <div class="auth">
    <div class="tabs">
      <button :class="{active: mode === 'login'}" @click="mode = 'login'">Login</button>
      <button :class="{active: mode === 'signup'}" @click="mode = 'signup'">Sign Up</button>
    </div>

    <div v-if="mode === 'login'" class="panel">
      <form @submit.prevent="handleLogin">
        <label>Username
          <input v-model="state.loginUsername" type="text" required />
        </label>
        <label>Password
          <input v-model="state.loginPassword" type="password" required />
        </label>
        <button type="submit">Log in</button>
      </form>
    </div>

    <div v-else class="panel">
      <form @submit.prevent="handleSignup">
        <label>Username
          <input v-model="state.signupUsername" type="text" required />
        </label>
        <label>Password
          <input v-model="state.signupPassword" type="password" required />
        </label>
        <button type="submit">Create account & sign in</button>
      </form>
    </div>

    <div class="status">
      <div v-if="currentUser">
        <strong>Logged in as:</strong> {{ currentUser }}
        <button @click="handleLogout">Logout</button>
      </div>
      <div v-else>
        <small>Not logged in</small>
      </div>
      <div v-if="message" class="message">{{ message }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive } from 'vue'

  interface IAuth {
    loginUsername: string | null,
    loginPassword: string | null,
    signupUsername: string | null,
    signupPassword: string | null
  }

  const state = reactive<IAuth>({
    loginUsername: null,
    loginPassword: null,
    signupUsername: null,
    signupPassword: null
  })

  const API_BASE = 'http://localhost:8000'

  const mode = ref<'login'|'signup'>('login')

  import { useAuth } from '@/composables/useAuth'
  const { currentUser, setUser } = useAuth()
  const message = ref<string | null>(null)

  async function handleLogin() {
    message.value = null
    if (!state.loginUsername || state.loginUsername.trim() === '') {
      message.value = 'Provide a username to log in.'
      return
    }
    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ Username: state.loginUsername, Password: state.loginPassword })
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || res.statusText)
      }
      setUser(state.loginUsername)
      message.value = 'Logged in successfully.'
    } catch (err: any) {
      message.value = `Login failed: ${err.message}`
    }
  }

  async function handleSignup() {
    message.value = null
    if (!state.signupPassword) {
      message.value = 'Password required for signup.'
      return
    }
    if (!state.signupUsername || state.signupUsername.trim() === '') {
      message.value = 'Username required for signup.'
      return
    }
    try {
      const body: any = { Password: state.signupPassword, Username: state.signupUsername }

      const res = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      if (!res.ok) {
        const txt = await res.text()
        throw new Error(txt || res.statusText) // TODO: Add toast message
      }
      const data = await res.json()
      // auto-login after signup
      const loginRes = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ IDu: data.IDu, Password: state.signupPassword })
      })
      if (!loginRes.ok) {
        const txt = await loginRes.text()
        throw new Error(txt || loginRes.statusText)
      }
      setUser(data.IDu)
      message.value = 'Account created and logged in.'
      // clear signup form
      state.signupPassword = null
      state.signupUsername = null
      mode.value = 'login'
    } catch (err: any) {
      message.value = `Signup failed: ${err.message}`
    }
  }

  async function handleLogout() {
    message.value = null
    try {
      await fetch(`${API_BASE}/logout`, { method: 'POST', credentials: 'include' })
    } catch (err: any) {
      // ignore network errors for logout, still clear UI
    }
    setUser(null)
    message.value = 'Logged out.'
  }
</script>

<style scoped>
  .auth {
    border: 2px solid #ddd;
    padding: 12px;
    border-radius: 6px;
    max-width: 420px;
  }
  .tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
  }
  .tabs button {
    padding: 6px 10px;
    border: 2px solid #ccc;
    background: #f7f7f7;
  }
  .tabs button.active {
    padding: 6px 10px;
    border: 2px solid #ccc;
    background: lightblue;
  }
  .panel label {
    display: block;
    margin-bottom: 8px;
  }
  .panel input {
    width: 100;
    padding: 6px;
    margin-top: 4px;
  }
  .status {
    margin-top: 12px;
  }
  .message {
    margin-top: 8px;
    color: rgb(242, 3, 3)
  }
</style>
