// Example of what useAuth might look like
import { ref } from 'vue'

const currentUser = ref<string | null>(null)

export function useAuth() {
  
  const login = async (u: string, p: string) => {
    // Simulate API call
    if (u && p) {
      currentUser.value = u
    } else {
      throw new Error("Invalid credentials")
    }
  }

  const signup = async (u: string, p: string) => {
    // Simulate API call
    if (u && p) {
      currentUser.value = u
    } else {
      throw new Error("Cannot create account")
    }
  }

  const logout = () => {
    currentUser.value = null
  }

  return {
    currentUser,
    login,
    signup,
    logout
  }
}