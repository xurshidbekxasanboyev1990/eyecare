<script setup>
import { RouterView, useRoute } from 'vue-router';
import { computed } from 'vue';
import { useEyeTestStore } from './stores/useEyeTestStore';
import DistanceCheck from './components/DistanceCheck.vue';

const route = useRoute();
const store = useEyeTestStore();

const isTestRoute = computed(() => route.path.startsWith('/test/'));

const progress = computed(() => {
    // Find index of current test path in store.tests
    const idx = store.tests.findIndex(t => t.path === route.path);
    if (idx === -1) return 0;
    return ((idx + 1) / store.tests.length) * 100;
});
const currentTestNumber = computed(() => {
    const idx = store.tests.findIndex(t => t.path === route.path);
    return idx !== -1 ? idx + 1 : 0;
});

const targetDistance = computed(() => {
    if (route.path.includes('near-vision')) return 35; // Standard reading distance
    if (route.path.includes('amsler')) return 30; // Standard Amsler grid distance
    if (route.path.includes('visual-acuity')) return 50; 
    return 45; // Default for others
});
</script>

<template>
  <DistanceCheck v-if="isTestRoute" :target-distance="targetDistance" :tolerance="5" />
  
  <div v-if="isTestRoute" class="fixed top-0 left-0 w-full h-1 bg-gray-200 z-50">
      <div 
        class="h-full bg-brand-blue transition-all duration-500 ease-out"
        :style="{ width: progress + '%' }"
      ></div>
  </div>
  
  <div v-if="isTestRoute" class="fixed top-4 right-4 z-40 bg-white/80 backdrop-blur px-3 py-1 rounded-full text-xs font-bold text-slate-500 border border-slate-200 shadow-sm">
      Test: {{ currentTestNumber }} / {{ store.tests.length }}
  </div>

  <RouterView />
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
