<template>
    <div id="map">
        <!--Contain markers, coordinates obtained from reverse geocoding-->
    </div>
</template>
<script setup lang="ts">
  import { onMounted } from 'vue';

  declare global {
    interface Window { initMap: () => void; }
  }

  const api_key = import.meta.env.VITE_API_KEY;

  onMounted(() => {
    window.initMap = () => {
      const downtown: google.maps.LatLngLiteral = { lat: 43.0747, lng: -89.3842 };

      const map = new google.maps.Map(document.getElementById('map') as HTMLElement, {
        center: downtown,
        zoom: 14
      });
    };

    const s = document.createElement('script');
    s.src = `https://maps.googleapis.com/maps/api/js?key=${api_key}&callback=initMap`;
    s.async = true;
    document.head.appendChild(s);
  });
</script>

<style scoped>
  #map {
    width: 25rem;
    height: 25rem;
    background-color: darkslategray;
    margin-bottom: 4rem;
  }
</style>