<script setup lang="ts">
import { ref, onMounted } from 'vue'

const message = ref('Loading...')

onMounted(async () => {
  console.log("Hello world!");
})
</script>

<template>
  <div style="padding: 2rem">
    {{ message }}
  </div>
</template>
