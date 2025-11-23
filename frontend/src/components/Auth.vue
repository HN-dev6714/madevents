<template>
  <div class="auth-container">
    <!-- NEW: Close Button -->
    <button class="close-btn" @click="$emit('close')">×</button>

    <h2>{{ isRegister ? 'Create Account' : 'Welcome Back' }}</h2>

    <!-- Existing Form -->
    <form @submit.prevent="handleSubmit">
      <!-- ... keep your existing inputs ... -->
      <div class="form-group">
        <label for="username">Username</label>
        <input id="username" v-model="username" type="text" required placeholder="Enter username" />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input id="password" v-model="password" type="password" required placeholder="Enter password" />
      </div>

      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

      <button type="submit" class="submit-btn">
        {{ isRegister ? 'Sign Up' : 'Log In' }}
      </button>
    </form>

    <!-- Existing Toggle -->
    <div class="toggle-mode">
      <p v-if="!isRegister">
        Don't have an account? <a href="#" @click.prevent="toggleMode">Sign Up</a>
      </p>
      <p v-else>
        Already have an account? <a href="#" @click.prevent="toggleMode">Log In</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

// NEW: Define the events this component emits
defineEmits(['close'])

const { login, signup } = useAuth()
const isRegister = ref(false)
const username = ref('')
const password = ref('')
const errorMessage = ref('')

function toggleMode() {
  isRegister.value = !isRegister.value
  errorMessage.value = ''
}

async function handleSubmit() {
  errorMessage.value = ''
  try {
    if (isRegister.value) {
      await signup(username.value, password.value)
    } else {
      await login(username.value, password.value)
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Authentication failed.'
  }
}
</script>

<style scoped>
/* NEW: Ensure container allows absolute positioning of the X button */
.auth-container {
  position: relative; 
  text-align: left;
  color: #333;
  width: 100%;
}

/* NEW: Styles for the X button */
.close-btn {
  position: absolute;
  top: -10px;   /* Adjusts position relative to the container */
  right: -10px; 
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  line-height: 1;
  padding: 5px;
}

.close-btn:hover {
  color: #c42116; /* Red on hover */
}

.auth-container {
  text-align: left;
  color: #333;
  width: 100%;
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
  text-align: center;
  color: #c42116; /* Matches your Nav theme */
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box; /* Keeps padding inside width */
  transition: border-color 0.2s;
}

input:focus {
  outline: none;
  border-color: #c42116;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #c42116;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  margin-top: 10px;
  transition: background-color 0.2s;
}

.submit-btn:hover {
  background-color: #a11b12;
}

.error-message {
  color: #d9534f;
  background-color: #f2dede;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 0.9rem;
  text-align: center;
}

.toggle-mode {
  margin-top: 20px;
  text-align: center;
  font-size: 0.9rem;
}

.toggle-mode a {
  color: #c42116;
  font-weight: bold;
  text-decoration: none;
}

.toggle-mode a:hover {
  text-decoration: underline;
}
</style>