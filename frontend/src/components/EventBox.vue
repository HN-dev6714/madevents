<template>
    <div class="full-box">
        <h2>{{  event.name }}</h2>
        <h3> {{ event.datetime }}</h3>
        <p>{{ event.latitude }},{{ event.longitude }}</p>
        <p> {{ event.description }}</p>
    </div>
</template>

<script setup lang="ts">
    import type { Event } from '@/types/Event';

    defineProps<{
        event: Event;
    }>();

</script>

<style>

</style>