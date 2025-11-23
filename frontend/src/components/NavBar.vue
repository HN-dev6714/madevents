<template>
  <nav class="nav">
    <h1>MadEvents</h1>
    <div class="right">
      <span v-if="currentUser">Hello, {{ currentUser }}!</span>
      <button v-if="!currentUser" @click="togglePanel" class="sign-in-button">
        {{ showPanel ? 'Close' : 'Sign In' }}
      </button>
      <button v-if="currentUser" @click="executeLogout" class="sign-in-button">
        Logout
      </button>
    </div>
  </nav>

  <Teleport to="body">
    <!-- NEW: Transition Wrapper -->
    <Transition name="modal">
      <div v-if="showPanel && !currentUser" class="auth-overlay" @click.self="togglePanel">
        <div class="auth-modal">
          <!-- Pass the close event handler -->
          <Auth @close="showPanel = false" />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// ERROR CHECK: Make sure this path is exactly where you saved Auth.vue
import Auth from './Auth.vue' 
import { useAuth } from '@/composables/useAuth'

const { currentUser, logout } = useAuth()
const showPanel = ref(false)

function executeLogout() {
  logout()
  showPanel.value = false
}

function togglePanel() {
  console.log("Toggling panel. Current state:", showPanel.value); // Debugging line
  showPanel.value = !showPanel.value;
}
</script>

<style scoped>
/* KEEP YOUR EXISTING NAV STYLES HERE */
.nav { 
  display: flex; 
  justify-content: space-between; 
  align-items: center;
  padding: 8px 12px; 
  border-bottom:1px solid #eee;
  background-color: #c42116;
  position: sticky;
  top: 0; 
  z-index: 1000;
}

h1 { margin: 4px; color: white; }
.nav .right { display: flex; gap: 15px; align-items: center; color: white; }

.sign-in-button {
    background: none;
    color: white;
    border: 1px solid white;
    border-radius: 4px;
    padding: 6px 12px;
    font: inherit;
    cursor: pointer;
}

/* OVERLAY STYLES */
.auth-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;    /* Changed from 100vw to avoid scrollbar issues */
  height: 100%;   /* Changed from 100vh */
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;  /* Very high z-index */
  backdrop-filter: blur(2px);
}

.auth-modal {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  min-width: 300px;
  z-index: 10000; /* Ensure modal is above overlay */
}


/* 1. Active state for entering and leaving */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

/* 2. Starting state for enter, Ending state for leave */
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

/* Optional: Add a nice pop effect to the inner white box */
.modal-enter-active .auth-modal,
.modal-leave-active .auth-modal {
  transition: transform 0.2s ease-out;
}

.modal-enter-from .auth-modal,
.modal-leave-to .auth-modal {
  transform: scale(0.9); /* Starts slightly smaller */
}
</style>