
import { ref } from 'vue'

const raw = localStorage.getItem('currentUser')
const parsed = raw === null ? null : raw
const currentUser = ref<string | number | null>(parsed)

function setUser(id: string | number | null) {
  currentUser.value = id
  if (id === null) {
    localStorage.removeItem('currentUser')
  }
  else{
    localStorage.setItem('currentUser', String(id))
  }
}

async function logout(apiBase = 'http://localhost:8000') {
  try {
    await fetch(`${apiBase}/logout`, { method: 'POST', credentials: 'include' })
  } catch (e) {
    // ignore network errors; still clear local state
  }
  setUser(null)
}

export function useAuth() {
  return {
    currentUser,
    setUser,
    logout,
  }
}
