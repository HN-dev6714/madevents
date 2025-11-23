<template>
  <main>
    <NavBar />
    <div style="padding:2rem">
      <h1>MADEVENTS</h1>
      <SearchBar :events="list"/>
    </div>
    <!--Map component, that takes in all events and displays them-->
    <!--Calendar.vue with EventBox.vue that have all matching dates-->
  </main>
</template>

<script setup lang="ts">

    import NavBar from '@/components/NavBar.vue'
    import SearchBar from '@/components/SearchBar.vue'
    import type { Event } from '@/types/Event.ts'

    const list: Event[] = [
        {
            id: 1,
            name: "Farmer's market",
            description: "Market happening every Saturday",
            latitude: -0.1,
            longitude: 0.1,
            datetime: new Date().toISOString(),
        },
        {
            id: 2,
            name: "Party at the Parthenon",
            description: "Hosted by none other than Zeus",
            latitude: 17,
            longitude: 38,
            datetime: new Date().toISOString(),
        },
        {
            id: 3,
            name: "Farm",
            description: "farm happening every Saturday",
            latitude: -0.1,
            longitude: 0.1,
            datetime: new Date().toISOString(),
        },
        {
            id: 4,
            name: "Part",
            description: "moses parting the red sea",
            latitude: 17,
            longitude: 38,
            datetime: new Date().toISOString(),
        }
    ]
</script>

<style>

</style>