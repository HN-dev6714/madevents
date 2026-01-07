<template>
  <div id="map">
    <!--Contain markers, coordinates obtained from reverse geocoding-->
  </div>
</template>
<script setup lang="ts">
  import { onMounted } from 'vue'
  import type { Event } from '@/types/Event.ts'
  import { openEventInfoWindow } from '@/types/Event.ts'
  import { mapState } from '@/composables/mapState'

  const { infowindow, geocoder, initializeMapTools } = mapState()

  declare global {
    interface Window {
      initMap: () => void
    }
  }

  defineEmits<{
    (e: 'marker-created', eventId: number, marker: google.maps.marker.AdvancedMarkerElement): void
  }>()

  const map_id = import.meta.env.VITE_MAP_ID
  const api_key = import.meta.env.VITE_API_KEY

  const props = defineProps<{
    events: Event[]
  }>()

  function addMarker(
    map: google.maps.Map,
    geocoder: google.maps.Geocoder | undefined,
    event: Event,
    infowindow: google.maps.InfoWindow | undefined,
  ) {
    const latLng = { lat: parseFloat(event.latitude), lng: parseFloat(event.longitude) }

    if (!geocoder || !infowindow) return;

    const marker = new google.maps.marker.AdvancedMarkerElement({
      position: latLng,
      map: map,
      title: event.name,
    })

    marker.addListener('click', () => openEventInfoWindow(
      event, infowindow, geocoder
    )
    /**() => {
      infowindow.close()

      geocoder
        .geocode({ location: latLng })
        .then((response) => {
          if (response.results[0]) {
            const content = `
              <h3>${event.name}</h3>
              <p>Address: ${response.results[0].formatted_address}</p>
              <p>Description: ${event.description}</p>
            `
            infowindow.setContent(content)
            infowindow.open(map, marker)
          } else {
            infowindow.setContent(`<h3>${event.name}</h3><p>Address not found.</p>`)
            infowindow.open(map, marker)
          }
        })
        .catch(() => {
          infowindow.setContent(`<h3>${event.name}</h3><p>Geocoding failed.</p>`)
          infowindow.open(map, marker)
        })
    }*/)

    event.marker = marker
  }

  onMounted(() => {
    window.initMap = () => {
      const downtown: google.maps.LatLngLiteral = { lat: 43.0747, lng: -89.3842 }

      const map = new google.maps.Map(document.getElementById('map') as HTMLElement, {
        center: downtown,
        zoom: 14,
        mapId: map_id,
      })

      initializeMapTools(map)

      const currentInfowindow = infowindow.value
      const currentGeocoder = geocoder.value
      
      if(infowindow.value && geocoder.value){
        props.events.forEach((event) => {
        addMarker(map, currentGeocoder, event, currentInfowindow)
      })
      }
    }

    const s = document.createElement('script')
    s.src = `https://maps.googleapis.com/maps/api/js?key=${api_key}&callback=initMap&libraries=marker&v=beta&map_id=${map_id}`
    s.async = true
    document.head.appendChild(s)
  })
</script>

<style scoped>
  #map {
    width: 25rem;
    height: 25rem;
    background-color: darkslategray;
    margin-bottom: 4rem;
  }
</style>
