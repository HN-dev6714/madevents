<template>
    <div class="full-box" @click="marker()">
        <h2>{{  event.name }}</h2>
        <h3> {{ convertToFriendlyDate(event.datetime) }}</h3>
       <p>{{ description }}</p>
    </div>
</template>

<script setup lang="ts">
    import type { Event } from '@/types/Event';
    import { computed } from 'vue';

    const convertToFriendlyDate = (date: string) => {
        const toDate = new Date(date);
        return `${(toDate).toLocaleDateString()} - ${(toDate).toLocaleTimeString().replace(/(.*)\D\d+/, '$1')}`;
    }

    const description = computed(() => {
        if (props.event.description && props.event.description.trim() !== "") {
            return props.event.description
        }
        else {
            return "There is no description for this event."
        }
    });

    const props = defineProps<{
        event: Event;
    }>();

    function marker(){
        console.log("HEY!")
    }
</script>

<style style scoped>
    .full-box {
        border: 2px solid black;
        margin-top: 2rem;
        margin-bottom: 2rem;
        border-radius: 4px;
        padding: 1rem;
        transition: background-color 0.3s ease; 
    }

    .full-box:hover{
        background: darkgray;
    }

</style>