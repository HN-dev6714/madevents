<template>
  <main>
    <NavBar />
    <div style="padding:2rem">
      <p>Hello world</p>
      <SearchBar :events="events"/>
    </div>
    <!--Insert NavBar (home and addevents)-->
    <!--Map component, that takes in all events and displays them-->
    <!--Calendar.vue with EventBox.vue that have all matching dates-->
    <!--SearchBar.vue-->
    <!--EventBox.vue of all events if search bar is empty-->
    <!--If search bar activated, filter name-->
  </main>
</template>

<script setup lang="ts">

    import NavBar from '@/components/NavBar.vue'
    import SearchBar from '@/components/SearchBar.vue'
    import type { Event } from '@/types/Event';

    const props = defineProps<{
        events: Event[];
    }>();

</script>

<style>

</style>