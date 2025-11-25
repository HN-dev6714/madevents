<template>
  <div class="week-container">
    <div v-for="day in days" :key="day.weekDay" class="week-item">
      <div>{{ day.weekDay ? day.weekDay : 'NA' }}</div>
      <div v-if="day.showStar">&#9733;</div>
    </div>
  </div>
</template>
<script setup lang="ts">
  interface IDay {
    weekDay: 'Su' | 'M' | 'Tu' | 'W' | 'Th' | 'F' | 'Sa' | undefined
    showStar: boolean
  }

  interface IWeekDisplay {
    days: IDay[]
  }

  defineProps<IWeekDisplay>()
</script>
<style scoped>
  .week-container {
    display: flex;
    flex-wrap: nowrap;
    width: 100%;
    height: 5rem;
    background: #ccc;
  }

  .week-item {
    flex: 1;
    padding: 1rem;
    text-align: center;
    box-sizing: border-box;
    transition: background-color 0.3s ease;
    cursor: default;
  }

  .week-item:hover {
    background: darkgray;
  }
</style>
