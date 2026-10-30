<template>
  <!-- One page of BeamNG.Earth's settings in the pause menu: its BeamNG.Earth tab lists the pages down the side
       (index.js registerModTab / registerModButton, the way BeamMP adds its tab: the user, 2026-10-28) and shows the
       page picked here; EarthSettingsSide.vue is the tab's second card. -->
  <EarthSettingsBody :page="page" />
</template>

<script setup>
import { onMounted, onUnmounted } from "vue"
import EarthSettingsBody from "./EarthSettingsBody.vue"
import { startPolling, stopPolling } from "./earthSettingsStore.js"

defineProps({
  page: { type: String, default: "Graphics" },     // the page's name (earthSettingsStore.js settingsSchema)
})

onMounted(startPolling)
onUnmounted(stopPolling)
</script>
