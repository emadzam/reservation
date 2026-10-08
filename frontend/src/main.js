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
    const resultSource = ref(null);
    const savedProviderIds = ref([]);
    const pendingIds = ref([]);
    const feedback = ref("");
    const chatQuestion = ref("");
    const chatState = ref("idle");
    const chatResult = ref(null);
    const chatMessage = ref("");
    const message = ref("Enter a five-digit U.S. ZIP code to find nearby hotels.");

    async function fetchJson(path, options) {
      const response = await fetch(`${API_BASE_URL}${path}`, options);
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "The request could not be completed.");
      return body;
    }

    async function search() {
      const zip = zipCode.value.trim();
      hotels.value = [];
      searchCenter.value = null;
      selectedIndex.value = null;
      feedback.value = "";
      if (!/^\d{5}$/.test(zip)) {
        state.value = "invalid";
        message.value = "Enter a five-digit U.S. ZIP code.";
        clearMap();
        return;
      }
      state.value = "loading";
      message.value = `Checking saved hotels for ${zip}…`;
      try {
        const local = await fetchJson(`/api/saved-hotels?zip=${encodeURIComponent(zip)}`);
        savedProviderIds.value = local.savedProviderIds || [];
        if (local.count) {
          hotels.value = local.hotels.map((hotel) => ({ ...hotel, saved: true }));
          searchCenter.value = local.searchCenter;
          resultSource.value = "local";
          state.value = "results";
          message.value = `${local.count} locally saved hotel${local.count === 1 ? "" : "s"} matched ZIP ${zip}. These are not a complete area listing.`;
        } else {
          message.value = `Finding live hotels near ${zip}…`;
          const live = await fetchJson(`/api/nearby-hotels?zip=${encodeURIComponent(zip)}`);
          hotels.value = live.hotels.map((hotel) => ({ ...hotel, saved: savedProviderIds.value.includes(hotel.id) }));
          searchCenter.value = live.searchCenter;
          resultSource.value = "api";
          state.value = live.count ? "results" : "empty";
          message.value = live.count ? `${live.count} API hotel${live.count === 1 ? "" : "s"} found within 5 km of ${zip}.` : `No hotels were found within 5 km of ${zip}.`;
        }
      } catch (error) {
        state.value = "failure";
        resultSource.value = null;
        message.value = error.message || "Local hotel storage is unavailable. Please try again.";
        clearMap();
        return;
      }
      await nextTick();
      renderMap();
    }

    function isPending(hotel) { return pendingIds.value.includes(hotel.id); }
    function isSaved(hotel) { return hotel.saved || savedProviderIds.value.includes(hotel.id); }

    async function addToLocal(hotel) {
      if (!hotel.id || isPending(hotel)) return;
      const context = searchCenter.value;
      if (!context) return;
      pendingIds.value = [...pendingIds.value, hotel.id];
      feedback.value = "";
      try {
        await fetchJson("/api/saved-hotels", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            hotel_id: hotel.id, name: hotel.name, address: hotel.address,
            latitude: hotel.latitude, longitude: hotel.longitude,
            zip: zipCode.value.trim(), search_latitude: context.latitude,
            search_longitude: context.longitude, search_locality: context.locality || null,
          }),
        });
        hotel.saved = true;
        savedProviderIds.value = [...new Set([...savedProviderIds.value, hotel.id])];
        feedback.value = `${hotel.name} was saved locally with simulated classroom nights.`;
      } catch (error) {
        feedback.value = error.message || "The hotel could not be saved locally.";
      } finally {
        pendingIds.value = pendingIds.value.filter((id) => id !== hotel.id);
      }
    }

    async function removeFromLocal(hotel) {
      if (!hotel.id || isPending(hotel)) return;
      pendingIds.value = [...pendingIds.value, hotel.id];
      feedback.value = "";
      try {
        await fetchJson(`/api/saved-hotels/${encodeURIComponent(hotel.id)}`, { method: "DELETE" });
        savedProviderIds.value = savedProviderIds.value.filter((id) => id !== hotel.id);
        await search();
        feedback.value = `${hotel.name} was removed from local storage.`;
      } catch (error) {
        feedback.value = error.message || "The saved hotel could not be removed.";
      } finally {
        pendingIds.value = pendingIds.value.filter((id) => id !== hotel.id);
      }
    }

    async function askHotelQuestion() {
      const question = chatQuestion.value.trim();
      if (question.length < 3) {
        chatState.value = "failure";
        chatMessage.value = "Ask a hotel question using at least three characters.";
        return;
      }
      chatState.value = "loading";
      chatMessage.value = "Checking the saved local hotel data…";
      chatResult.value = null;
      try {
        chatResult.value = await fetchJson("/api/hotel-chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question }),
        });
        chatState.value = chatResult.value.status;
        chatMessage.value = chatResult.value.status === "insufficient_data" ? "Insufficient local data" : chatResult.value.status === "no_matches" ? "No matching local records" : "Grounded answer from saved local records";
      } catch (error) {
        chatState.value = "failure";
        chatMessage.value = error.message || "The hotel chatbot is unavailable. Please try again.";
      }
    }

    function formatRecords(records) { return JSON.stringify(records, null, 2); }

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

    return { zipCode, hotels, selectedIndex, state, message, feedback, resultSource, chatQuestion, chatState, chatResult, chatMessage, search, selectHotel, addToLocal, removeFromLocal, askHotelQuestion, formatRecords, isPending, isSaved };
  },
  template: `
    <main class="search-card" aria-labelledby="page-title">
      <p class="eyebrow">ASSIGNMENT 2 · PART 2</p>
      <h1 id="page-title">Nearby Hotel Search</h1>
      <p class="intro">Search a saved local shortlist first, then live hotel locations within 5 km of an exact U.S. ZIP code.</p>
      <form class="search-form" @submit.prevent="search" novalidate>
        <label for="zip-code">U.S. ZIP code</label>
        <div class="input-row"><input id="zip-code" v-model="zipCode" type="text" inputmode="numeric" autocomplete="postal-code" maxlength="5" placeholder="e.g. 02108" :aria-invalid="state === 'invalid'" aria-describedby="search-status" /><button type="submit" :disabled="state === 'loading'">{{ state === 'loading' ? 'Searching…' : 'Search' }}</button></div>
      </form>
      <p id="search-status" class="message" :class="state" role="status" aria-live="polite">{{ message }}</p>
      <p v-if="feedback" class="feedback" role="status" aria-live="polite">{{ feedback }}</p>
      <section class="chat-panel" aria-labelledby="chat-title">
        <h2 id="chat-title">Ask about saved hotels</h2>
        <p>Answers use only locally saved hotels and simulated classroom nightly data. The chatbot cannot change the database or make bookings.</p>
        <form class="chat-form" @submit.prevent="askHotelQuestion">
          <label for="hotel-question">Hotel question</label>
          <textarea id="hotel-question" v-model="chatQuestion" maxlength="500" placeholder="Example: Which saved hotel has rooms available on October 12?" :disabled="chatState === 'loading'"></textarea>
          <button type="submit" :disabled="chatState === 'loading'">{{ chatState === 'loading' ? 'Checking…' : 'Ask question' }}</button>
        </form>
        <p v-if="chatMessage" class="chat-message" :class="chatState" role="status" aria-live="polite">{{ chatMessage }}</p>
        <div v-if="chatResult" class="chat-result">
          <p class="answer">{{ chatResult.answer }}</p>
          <details v-if="chatResult.proposedSql"><summary>Show checked SQL and retrieved records</summary><p><strong>Proposed SQL</strong></p><pre>{{ chatResult.proposedSql }}</pre><p><strong>Retrieved records</strong></p><pre>{{ formatRecords(chatResult.records) }}</pre></details>
        </div>
      </section>
      <section v-if="state === 'results' || state === 'empty'" class="results-layout" aria-label="Nearby hotels and map">
        <section class="hotel-list" aria-labelledby="hotel-list-title">
          <div class="section-heading"><h2 id="hotel-list-title">Hotels</h2><span v-if="resultSource" class="source-label">{{ resultSource === 'local' ? 'Saved locally' : 'API results' }}</span></div>
          <p v-if="resultSource === 'local'" class="local-note">Showing only hotels you previously saved for this ZIP, not a complete list of nearby hotels.</p>
          <p v-if="!hotels.length" class="empty-state">No nearby hotels to show.</p>
          <article v-for="(hotel, index) in hotels" :key="hotel.id || hotel.latitude + ',' + hotel.longitude" class="hotel-card" :class="{ selected: selectedIndex === index }">
            <button class="hotel-select" @click="selectHotel(index)" :aria-pressed="selectedIndex === index"><strong>{{ hotel.name }}</strong><span>{{ hotel.address }}</span><small>{{ hotel.latitude.toFixed(5) }}, {{ hotel.longitude.toFixed(5) }}</small></button>
            <p v-if="resultSource === 'local'" class="simulated-data"><strong>Simulated classroom data</strong><br><span v-for="night in hotel.nights" :key="night.stayDate">{{ night.stayDate }}: &#36;{{ (night.nightlyRateCents / 100).toFixed(2) }}, {{ night.roomsAvailable }} rooms<br></span></p>
            <div class="hotel-actions">
              <span v-if="isSaved(hotel)" class="saved-label">Saved locally</span>
              <button v-if="!isSaved(hotel)" class="secondary-action" @click="addToLocal(hotel)" :disabled="isPending(hotel) || !hotel.id">{{ !hotel.id ? 'Provider ID unavailable' : isPending(hotel) ? 'Saving…' : 'Add to Local' }}</button>
              <button v-else class="remove-action" @click="removeFromLocal(hotel)" :disabled="isPending(hotel)">{{ isPending(hotel) ? 'Removing…' : 'Remove from Local' }}</button>
            </div>
          </article>
        </section>
        <section class="map-panel" aria-labelledby="map-title"><h2 id="map-title">Map</h2><div id="hotel-map" aria-label="Map of nearby hotel locations"></div><p class="map-note">Select a hotel in either view to highlight it in the other.</p></section>
      </section>
    </main>
  `,
}).mount("#app");

function escapeHtml(value) {
  return String(value ?? "Unavailable").replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
}
