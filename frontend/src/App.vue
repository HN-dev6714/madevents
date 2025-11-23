<template>
  <router-view />
</template>
<script lang="ts">
  import { useAuthStore } from '@/stores/authStore';
  import { onMounted } from 'vue';

  //const auth = useAuthStore();
  //onMounted(() => {
    //auth.checkSession();
  //});
</script>
