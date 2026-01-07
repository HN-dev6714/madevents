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

export function openEventInfoWindow(
  event: Event,
  infowindow: google.maps.InfoWindow | undefined,
  geocoder: google.maps.Geocoder | undefined
){
  if (!event.marker || !infowindow || !geocoder) return

  const map = event.marker.map;
  const latLng = event.marker.position as google.maps.LatLng;

  infowindow.close();

  geocoder
    .geocode({ location: latLng })
    .then((response) => {
      if (response.results[0]) {
        const content = `
          <h3>${event.name}</h3>
          <p>Address: ${response.results[0].formatted_address}</p>
          <p>Description: ${event.description}</p>
        `;
        infowindow.setContent(content);
        infowindow.open(map, event.marker);
      } else {
        infowindow.setContent(`<h3>${event.name}</h3><p>Address not found.</p>`);
        infowindow.open(map, event.marker);
      }
    })
    .catch(() => {
      infowindow.setContent(`<h3>${event.name}</h3><p>Geocoding failed.</p>`);
      infowindow.open(map, event.marker);
    });
}