<template>
    <div class="full-bar">
        <input v-model="searchText" 
            placeholder="Type event name..."
            class="search-bar"
        />
        <EventList :events="filteredEvents" />
    </div>
</template>

<script setup lang="ts">
    import EventList from './EventList.vue';
    import type { Event } from '@/types/Event';
    import { ref, computed, reactive} from 'vue';

    const props = defineProps<{
        events: Event[];
    }>();

    const searchText = ref("");

    const filteredEvents = computed(() => {
        if (!props.events || !Array.isArray(props.events)) {
             return [];
        }

        if(!searchText.value){
            return props.events;
        }
        const lower = searchText.value.toLowerCase();

        return props.events.filter(event =>
           event.name.toLowerCase().includes(lower)
        );
    });
</script>

<style>

</style>