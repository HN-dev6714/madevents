<template>
    <div class="search-container">
        <input v-model="searchText" 
            placeholder="Event name"
            class="search-bar"
        />
        <EventList :events="filteredEvents" />
    </div>
</template>

<script setup lang="ts">
    import EventList from './EventList.vue';
    import type { Event } from '@/types/Event';
    import { ref, computed} from 'vue';

    const props = defineProps<{
        events: Event[];
    }>();

    const searchText = ref("");

    const filteredEvents = computed(() => {
        if (!props.events || !Array.isArray(props.events)) {
             return [];
        }

        if(!searchText.value || searchText.value.toLowerCase().trim() === ""){
            return props.events;
        }
        const lower = searchText.value.toLowerCase();

        return props.events.filter(event =>
           event.name.trim().toLowerCase().includes(lower)
        );
    });
</script>

<style style scoped>
    .search-bar {
        margin-bottom: 1rem;
        padding: 1rem;
        font-size: 1rem;
        width: 94%;
    }
    .search-container {
        max-width: 40rem;
    }
</style>