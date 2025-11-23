<template>
  <nav class="nav">
    <div class="left">
      <h1>MadEvents</h1>
    </div>
    <div class="right">
      <span v-if="currentUser">Signed in: {{ currentUser }}</span>
      <button v-if="!currentUser" @click="showAuth = !showAuth">
        {{ showAuth ? 'Close' : 'Sign In' }}
      </button>
      <button v-if="currentUser" @click="executeLogout">Logout</button>
    </div>
  </nav>
  <div v-if="showAuth && !currentUser" class="auth-panel">
    <Auth />
  </div>
</template>

<script setup lang="ts">
      import { ref } from 'vue'
      import { useAuth } from '@/composables/useAuth'
      import Auth from './Auth.vue'

      const { currentUser, logout } = useAuth()
      const showAuth = ref(false)

      function executeLogout() {
          logout()
          showAuth.value = false
      }
</script>

<style scoped>
    .nav { 
      display: flex; 
      justify-content: space-between; 
      align-items: center;
      padding: 8px 12px; 
      border-bottom:1px solid #eee;
      background-color: #c42116;
      position: sticky;
      top: 0; /* This is the key property that tells it to stick to the top of the viewport */
      z-index: 1000;
    }

    h1 {
      margin: 4px;
      color: white;
    }

    .nav .right a { 
      margin-right: 24px; 
      text-decoration: none; 
    }

    .nav button { 
      padding: 4px 8px
    }

    .auth-panel { 
      padding: 12px; 
      border-bottom: 1px solid #eee; 
      background: #f9f9f9 
    }

    a {
      color: blue;
      text-decoration: none;
    }

    a:visited {
      color: blue; 
    }

    a:hover {
      color: red; 
      text-decoration: underline;
    }
</style>
