<template>
  <nav class="nav">
    <div class="left">
      <a href="/">Home</a>
      <a href="#">Add Event</a>
    </div>
    <div class="right">
      <span v-if="currentUser">Signed in: {{ currentUser }}</span>
      <span v-else>Not signed in</span>
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
      align-items:center;
      padding: 8px 12px; 
      border-bottom:1px solid #eee 
    }

    .nav .left a { 
      margin-right:12px; 
      text-decoration: none; 
    }

    .nav button { 
      margin-left:12px; 
      padding:4px 8px
    }

    .auth-panel { 
      padding:12px; 
      border-bottom:1px solid #eee; 
      background:#f9f9f9 
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

    a:active {
      color: green;
    }
</style>
