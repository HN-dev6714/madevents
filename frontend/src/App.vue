<script setup lang="ts">
import { ref, onMounted } from 'vue'

const message = ref('Loading...')

onMounted(async () => {
  try {
    const res = await fetch('http://localhost:8000/api/hello')
    if (!res.ok) {
      throw new Error(await res.text())
    }
    const data = await res.json()
    message.value = data?.message ?? JSON.stringify(data)
  } catch (err) {
    message.value = `Error fetching API: ${err}`
  }
})
</script>

<template>
  <div style="padding: 2rem">
    {{ message }}
  </div>
</template>
