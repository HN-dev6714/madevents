<template>
    <div class="scrollable-container">
        <EventBox v-for="event in props.events"
        :key="event.id":event="event" />
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
        height: 34rem;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 2rem;
        padding-top: 0px;
        padding-bottom: 0px;
    }
</style>