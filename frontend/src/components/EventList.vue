<template>
    <div v-if="events.length > 0" class="scrollable-container">
        <EventBox v-for="event in props.events"
        :key="event.id":event="event" />
    </div>
    <div v-if="events.length === 0">
        <p>No events found! Try adjusting your search or filters.</p>
    </div>
</template>

<script setup lang="ts">
    import type { Event } from '@/types/Event';
    import EventBox from './EventBox.vue';
    const props = defineProps<{
        events: Event[];
    }>();
</script>

<style scoped>
    .scrollable-container {
        height: 70vh;
        width: 40vw;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 2rem;
        padding-top: 0px;
        padding-bottom: 0px;
    }
</style>