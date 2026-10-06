import { createApp, nextTick, ref } from "https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js";

const API_BASE_URL = "http://127.0.0.1:8000";
let map;
let markers = [];

createApp({
  setup() {
    const zipCode = ref("");
    const hotels = ref([]);
    const searchCenter = ref(null);
    const selectedIndex = ref(null);
    const state = ref("idle");
    const message = ref("Enter a five-digit U.S. ZIP code to find nearby hotels.");

    async function search() {
      const zip = zipCode.value.trim();
      hotels.value = [];
      searchCenter.value = null;
      selectedIndex.value = null;
      if (!/^\d{5}$/.test(zip)) {
        state.value = "invalid";
        message.value = "Enter a five-digit U.S. ZIP code.";
        clearMap();
        return;
      }
      state.value = "loading";
      message.value = `Finding hotels near ${zip}…`;
      try {
        const response = await fetch(`${API_BASE_URL}/api/nearby-hotels?zip=${encodeURIComponent(zip)}`);
        const body = await response.json().catch(() => ({}));
        if (!response.ok) {
          state.value = response.status === 404 ? "unresolved" : "failure";
          message.value = body.detail || "The hotel search service is unavailable. Please try again.";
          clearMap();
          return;
        }
        hotels.value = body.hotels;
        searchCenter.value = body.searchCenter;
        state.value = body.count ? "results" : "empty";
        message.value = body.count ? `${body.count} hotel${body.count === 1 ? "" : "s"} found within 5 km of ${zip}.` : `No hotels were found within 5 km of ${zip}.`;
      } catch {
        state.value = "failure";
        message.value = "The hotel search service is unavailable. Please try again.";
        clearMap();
      }
      if (state.value === "results" || state.value === "empty") {
        await nextTick();
        renderMap();
      }
    }

    function selectHotel(index) {
      selectedIndex.value = index;
      markers.forEach((marker, markerIndex) => marker.setIcon(markerIcon(markerIndex === index)));
      if (markers[index]) markers[index].openPopup();
    }

    function markerIcon(selected) {
      return L.divIcon({ className: "hotel-marker", html: `<span class="${selected ? "selected" : ""}">●</span>`, iconSize: [24, 24], iconAnchor: [12, 12] });
    }

    function renderMap() {
      clearMap();
      if (!searchCenter.value) return;
      map = L.map("hotel-map", { scrollWheelZoom: false }).setView([searchCenter.value.latitude, searchCenter.value.longitude], 13);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap contributors" }).addTo(map);
      L.circle([searchCenter.value.latitude, searchCenter.value.longitude], { radius: 5000, color: "#176a57", fillColor: "#176a57", fillOpacity: 0.06 }).addTo(map);
      markers = hotels.value.map((hotel, index) => L.marker([hotel.latitude, hotel.longitude], { icon: markerIcon(false) }).addTo(map).bindPopup(`<strong>${escapeHtml(hotel.name)}</strong><br>${escapeHtml(hotel.address)}`).on("click", () => selectHotel(index)));
      if (markers.length) map.fitBounds(L.featureGroup(markers).getBounds().pad(0.25));
    }

    function clearMap() {
      markers = [];
      if (map) { map.remove(); map = undefined; }
    }

    return { zipCode, hotels, selectedIndex, state, message, search, selectHotel };
  },
  template: `
    <main class="search-card" aria-labelledby="page-title">
      <p class="eyebrow">ASSIGNMENT 2 · PART 1</p>
      <h1 id="page-title">Nearby Hotel Search</h1>
      <p class="intro">Search live hotel locations within 5 km of an exact U.S. ZIP code.</p>
      <form class="search-form" @submit.prevent="search" novalidate>
        <label for="zip-code">U.S. ZIP code</label>
        <div class="input-row"><input id="zip-code" v-model="zipCode" type="text" inputmode="numeric" autocomplete="postal-code" maxlength="5" placeholder="e.g. 02108" :aria-invalid="state === 'invalid'" aria-describedby="search-status" /><button type="submit" :disabled="state === 'loading'">{{ state === 'loading' ? 'Searching…' : 'Search' }}</button></div>
      </form>
      <p id="search-status" class="message" :class="state" role="status" aria-live="polite">{{ message }}</p>
      <section v-if="state === 'results' || state === 'empty'" class="results-layout" aria-label="Nearby hotels and map">
        <section class="hotel-list" aria-labelledby="hotel-list-title"><h2 id="hotel-list-title">Hotels</h2><p v-if="!hotels.length" class="empty-state">No nearby hotels to show.</p><button v-for="(hotel, index) in hotels" :key="hotel.id || hotel.latitude + ',' + hotel.longitude" class="hotel-card" :class="{ selected: selectedIndex === index }" @click="selectHotel(index)"><strong>{{ hotel.name }}</strong><span>{{ hotel.address }}</span><small>{{ hotel.latitude.toFixed(5) }}, {{ hotel.longitude.toFixed(5) }}</small></button></section>
        <section class="map-panel" aria-labelledby="map-title"><h2 id="map-title">Map</h2><div id="hotel-map" aria-label="Map of nearby hotel locations"></div><p class="map-note">Select a hotel in either view to highlight it in the other.</p></section>
      </section>
    </main>
  `,
}).mount("#app");

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
}
