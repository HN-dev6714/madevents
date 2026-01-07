import { ref } from 'vue'

const infowindow = ref<google.maps.InfoWindow>()
const geocoder = ref<google.maps.Geocoder>()

export function mapState() {
  const initializeMapTools = (map: google.maps.Map) => {
    if (!infowindow.value) {
      infowindow.value = new google.maps.InfoWindow()
    }
    if (!geocoder.value) {
      geocoder.value = new google.maps.Geocoder()
    }
  }

  return {
    infowindow,
    geocoder,
    initializeMapTools
  }
}