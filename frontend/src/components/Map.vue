<template>
    <div class="map">
        <img :src="`https://maps.googleapis.com/maps/api/staticmap?center=Madison,WI&zoom=14&size=400x400&key=${api_key}&signature=${signature}`" />
        <!--Contain markers, coordinates obtained from reverse geocoding-->
    </div>
</template>
<script setup lang="ts">
    const api_key: string = import.meta.env.VITE_API_KEY;
    const signature: string = import.meta.env.SIGNATURE;
</script>
<style scoped>
  .map {
    width: 25rem;
    height: 25rem;
    background-color: darkslategray;
    margin-bottom: 4rem;
  }
</style>