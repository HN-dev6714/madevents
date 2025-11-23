<template>
  <main>
    <NavBar />
    <div class="container">
    <div class="left-column">
      <SearchBar :events="list"/>
    </div>
    <div class="right-column">
      <Map></Map>
      <WeekDisplay :days="weekDates"></WeekDisplay>
    </div>
    <!--Map component, that takes in all events and displays them-->
    <!--Calendar.vue with EventBox.vue that have all matching dates-->
    </div>
  </main>
</template>
<script setup lang="ts">
    import NavBar from '@/components/NavBar.vue'
    import SearchBar from '@/components/SearchBar.vue'
    import type { Event } from '@/types/Event.ts'
    import Map from '@/components/Map.vue'
    import WeekDisplay from '@/components/WeekDisplay.vue'
    import { computed } from 'vue'

    // TODO: Move this to shared types
    interface IDay {
        weekDay: ("Su" | "M" | "Tu" | "W" | "Th" | "F" | "Sa" | undefined),
        showStar: boolean
    }

    const DAY_MAP: Record<number, IDay['weekDay']> = {
        0: 'Su',
        1: 'M',
        2: 'Tu',
        3: 'W',
        4: 'Th',
        5: 'F',
        6: 'Sa'
    } as const;

    const list: Event[] = [
      {
        id: 1,
        name: "Farmer's market",
        description: "Market happening every Saturday",
        latitude: -0.1,
        longitude: 0.1,
        datetime: new Date(new Date().setDate(new Date().getDate() - new Date().getDay() + 6)).toISOString(),
      },
      {
        id: 2,
        name: "Party at the Parthenon",
        description: "Hosted by none other than Zeus",
        latitude: 17,
        longitude: 38,
        datetime: new Date(new Date().setDate(new Date().getDate() - new Date().getDay() + 3)).toISOString(),
      },
      {
        id: 3,
        name: "Farm",
        description: "Farm happening every Saturday",
        latitude: -0.1,
        longitude: 0.1,
        datetime: new Date(new Date().setDate(new Date().getDate() - new Date().getDay() + 1)).toISOString(),
      },
      {
        id: 4,
        name: "Moses Parting",
        description: "Moses parting the red sea",
        latitude: 17,
        longitude: 38,
        datetime: new Date(new Date().setDate(new Date().getDate() - new Date().getDay() + 4)).toISOString(),
      }
    ]

    const weekDates = computed(() => {
        const today = new Date();
        const currentDayOfWeek = today.getDay();
        const days: IDay[] = [];

        const sunday = new Date(today);
        sunday.setDate(today.getDate() - currentDayOfWeek);
        sunday.setHours(0, 0, 0, 0);

        for (let i = 0; i < 7; i++) {
            const currDay = new Date(sunday);
            currDay.setDate(sunday.getDate() + i);
            currDay.setHours(0, 0, 0, 0);

            const showStar = list.some(ev => {
                const evDate = new Date(ev.datetime);
                evDate.setHours(0, 0, 0, 0);
                return evDate.getTime() === currDay.getTime();
            });

            days.push({ weekDay: DAY_MAP[currDay.getDay()], showStar });
        }

        return days;
    });
</script>
<style scoped>
  .container {
      display: flex; /* Makes the child elements flex items arranged in a row by default */
      justify-content: space-between; /* Distributes space evenly, pushing columns to edges if needed */
  }

  .left-column {
      flex: 2;
      padding: 4rem;
      padding-top: 2rem;
  }

  .right-column {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 2rem;
  }

  /* Add media queries for responsiveness to stack columns on smaller screens */
  @media (max-width: 600px) {
      .container {
          flex-direction: column; /* Stacks columns vertically on small screens */
      }
  }
</style>