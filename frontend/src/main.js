import { createApp, ref } from "https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js";

const API_BASE_URL = "http://127.0.0.1:8000";

createApp({
  setup() {
    const hotelName = ref("");
    const results = ref([]);
    const message = ref("Search for a hotel to view available stays.");
    const isLoading = ref(false);

    async function search() {
      const query = hotelName.value.trim();
      results.value = [];
      if (!query) {
        message.value = "Enter a hotel name before searching.";
        return;
      }

      isLoading.value = true;
      message.value = "";
      try {
        const response = await fetch(`${API_BASE_URL}/api/hotels?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error("The search service is unavailable.");
        const data = await response.json();
        results.value = data.results;
        message.value = data.count
          ? `${data.count} available stay${data.count === 1 ? "" : "s"} found.`
          : `No hotels or available stays match “${query}”.`;
      } catch (error) {
        message.value = error.message;
      } finally {
        isLoading.value = false;
      }
    }

    return { hotelName, results, message, isLoading, search };
  },
  template: `
    <section class="search-card" aria-labelledby="page-title">
      <p class="eyebrow">LOCAL TRAVEL SEARCH</p>
      <h1 id="page-title">Reservation Lite</h1>
      <p class="intro">Find available hotel stays from our local travel catalog.</p>
      <form class="search-form" @submit.prevent="search">
        <label for="hotel-name">Hotel name</label>
        <div class="input-row">
          <input id="hotel-name" v-model="hotelName" type="search" placeholder="Try Harbor or Maple" autocomplete="off" />
          <button type="submit" :disabled="isLoading">{{ isLoading ? "Searching…" : "Search" }}</button>
        </div>
      </form>
      <p class="message" role="status">{{ message }}</p>
      <div v-if="results.length" class="table-wrap">
        <table>
          <thead><tr><th>Hotel</th><th>Location</th><th>Check-in</th><th>Check-out</th><th>Available rooms</th><th>Price/night</th></tr></thead>
          <tbody>
            <tr v-for="stay in results" :key="stay.hotelId + stay.checkIn">
              <td>{{ stay.hotelName }}</td><td>{{ stay.city }}, {{ stay.country }}</td><td>{{ stay.checkIn }}</td><td>{{ stay.checkOut }}</td><td>{{ stay.availableRooms }}</td><td>\${{ stay.pricePerNight.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  `,
}).mount("#app");
