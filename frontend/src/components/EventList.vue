<template>
    <div class="full-list">
        <EventBox v-for="event in props.events"
        :key="event.id":event="event" />
    </div>
</template>

<script setup lang="ts">
    import type { Event } from '@/types/Event';
    import EventBox from './EventBox.vue';
    // TODO: Replace events with list
    const props = defineProps<{
        events: Event[];
    }>();

</script>

<style>

</style>