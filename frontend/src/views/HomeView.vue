<template>
  <main>
    <NavBar />
    <div class="container">
    <div class="left-column">
      <SearchBar :events="list"/>
    </div>
    <div class="right-column">
      <Map ref="mapRef" :events="list"></Map>
      <WeekDisplay :days="weekDates"></WeekDisplay>
    </div>
    </div>
  </main>
</template>
<script setup lang="ts">
    import NavBar from '@/components/NavBar.vue'
    import SearchBar from '@/components/SearchBar.vue'
    import type { Event } from '@/types/Event.ts'
    import Map from '@/components/Map.vue'
    import WeekDisplay from '@/components/WeekDisplay.vue'
    import { computed, onMounted } from 'vue'
    import client from '@/api/client'

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

    onMounted(async () => {
      try {
        const response = await client.get<Event>('/events');
        console.log(response.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    });

       const list: Event[] = [
      {
      id: 1,
      name: "NEEDTOBREATH",
      description: "The barely elegant acousitc tour",
      latitude: "43.0831",
      longitude: "-89.3731",
      datetime: new Date(new Date().setDate(new Date().getDate() - new Date().getDay() + 6)).toISOString(),
      address: "brease stevens field, Madison"
      },
      {
      id: 2,
      name: "LOLO: U TOUR ME ON",
      description: "Music tour",
      latitude: "43.0831",
      longitude: "-89.3731",
      datetime: new Date(new Date().setDate(new Date().getDate() - new Date().getDay() + 3)).toISOString(),
      address: "brease stevens field" 
      },
      {
      id: 3,
      name: "MSO After Dark",
      description: "Fall Crafting Festival",
      latitude: "43.0440",
      longitude: "-89.3807",
      datetime: new Date(new Date().setDate(new Date().getDate() - new Date().getDay() + 1)).toISOString(),
      address: "456 Country Rd, Springfield"
      },
      {
      id: 4,
      name: "Bridal & Wedding Expo",
      description: "Wisconsin Bridal and Wedding Expo",
      latitude: "43.0440",
      longitude: "-89.3807",
      datetime: new Date(new Date().setDate(new Date().getDate() - new Date().getDay() + 4)).toISOString(),
      address: "Alliant Energy Center, Madison"
      },
      {
      id: 5,
      name: "Womens Basketball",
      description: "Wisconsin Badgers Women'S Basketball",
      latitude: "43.0687", 
      longitude: " -89.4077",
      datetime: new Date(new Date().setDate(new Date().getDate() - new Date().getDay() + 7)).toISOString(),
      address: "Camp Randall Stadium, Madison"
      }
    ]

    //
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
      display: flex; 
      justify-content: space-between;
  }

  .left-column {
      flex: 2;
      padding: 4rem;
      padding-top: 2rem;
      padding-bottom: 0rem;
  }

  .right-column {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 4rem;
  }

  /* Add media queries for responsiveness to stack columns on smaller screens */
  @media (max-width: 600px) {
      .container {
          flex-direction: column; /* Stacks columns vertically on small screens */
      }
  }
</style>