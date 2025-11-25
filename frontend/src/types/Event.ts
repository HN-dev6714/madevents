export interface Event {
  id: number
  name: string
  description: string
  latitude: string
  longitude: string
  address: string
  datetime: string
  marker?: google.maps.marker.AdvancedMarkerElement
}
