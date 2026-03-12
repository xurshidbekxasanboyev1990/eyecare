<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useEyeTestStore } from '../stores/useEyeTestStore';
import { Play, RotateCcw } from 'lucide-vue-next';

const router = useRouter();
const store = useEyeTestStore();

const isStarted = ref(false);
const showDot = ref(false);
const dotPosition = ref({ top: '50%', left: '50%' });
const score = ref(0);
const totalAttempts = 10;
const currentAttempt = ref(0);
const misses = ref(0);

let timer = null;

const startTest = () => {
    isStarted.value = true;
    currentAttempt.value = 0;
    score.value = 0;
    misses.value = 0;
    scheduleDot();
};

const scheduleDot = () => {
    if (currentAttempt.value >= totalAttempts) {
        finishTest();
        return;
    }

    showDot.value = false;
    
    // Random delay between 1s and 3s
    const delay = Math.random() * 2000 + 1000;
    
    timer = setTimeout(() => {
        // Random position (peripheral)
        // Avoid center (30% to 70% range in middle)
        let top, left;
        do {
            top = Math.random() * 90 + 5; // 5% to 95%
            left = Math.random() * 90 + 5;
        } while (top > 30 && top < 70 && left > 30 && left < 70); // Keep away from center fixation

        dotPosition.value = { top: `${top}%`, left: `${left}%` };
        showDot.value = true;
        currentAttempt.value++;

        // Dot visible for only 0.5s typical perimetry flash
        setTimeout(() => {
            if (showDot.value) {
                // If still visible (user didn't click), count as miss? 
                // Actually usually we wait for user response or timeout.
                // Let's make it auto-fail if not clicked within 1.5s window?
                // Visual field tests usually flash briefly. 
                // Let's keep it simple: Flash for 0.4s. User has to click ANYWHERE while it's visible or shortly after.
                
                // For web simplicity: User clicks button "I saw it" whenever.
                showDot.value = false;
                scheduleDot(); // Missed it (implied if we auto-schedule, but we need a verified input way)
                               // Actually, let's make user Click the SCREEN when they see it.
            }
        }, 400); // 400ms flash

    }, delay);
};

// Capturing user reaction
const handleScreenClick = () => {
    if (!isStarted.value) return;
    
    if (showDot.value) {
        // User caught it!
        score.value++;
        showDot.value = false;
        // Proceed immediately or wait for flash timer end? Better proceed.
        clearTimeout(timer);
        scheduleDot();
    } else {
        // False positive? Ignored for simplicity
    }
};

const finishTest = () => {
    isStarted.value = false;
    const resultScore = Math.round((score.value / totalAttempts) * 100); // 90
    
    store.saveResult('perimetry', {
        score: resultScore, // Store number for result view
        details: `Aniqlangan signallar: ${score.value}/${totalAttempts}`
    });
    router.push('/test/dry-eye');
};

onUnmounted(() => {
    clearTimeout(timer);
});
</script>

<template>
  <div 
    class="min-h-screen bg-black flex flex-col items-center justify-center relative overflow-hidden cursor-crosshair select-none"
    @mousedown="handleScreenClick"
  >
    <!-- Center Fixation Cross -->
    <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div class="w-8 h-8 relative">
            <div class="absolute top-1/2 left-0 w-full h-1 bg-red-600 -translate-y-1/2"></div>
            <div class="absolute left-1/2 top-0 h-full w-1 bg-red-600 -translate-x-1/2"></div>
        </div>
    </div>

    <!-- The Flash Dot -->
    <div 
        v-if="showDot"
        class="absolute w-3 h-3 bg-white rounded-full shadow-[0_0_10px_rgba(255,255,255,0.8)]"
        :style="dotPosition"
    ></div>

    <!-- UI Overlay -->
    <div v-if="!isStarted" class="z-50 bg-white/10 backdrop-blur-md p-8 rounded-3xl text-center max-w-lg shadow-2xl border border-white/20">
        <h1 class="text-3xl font-extrabold text-white mb-6">Perimetriya (Ko'rish Maydoni)</h1>
        <p class="text-slate-200 mb-8 text-lg font-medium leading-relaxed">
            Glaukomani aniqlash uchun test.
            <br>Diqqatingizni faqat <b>markaziy qizil xochga</b> qarating. 
            Ekranning chetida oq nuqta paydo bo'lganda, ekranning <b>istalgan joyiga bosing</b>.
        </p>
        <button 
            @click.stop="startTest"
            class="flex items-center justify-center gap-3 w-full py-4 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold transition text-lg"
        >
            <Play class="fill-current w-5 h-5" />
            Boshlash
        </button>
    </div>

    <!-- Progress info (Optional) -->
    <div v-if="isStarted" class="absolute top-4 right-4 text-white/30 text-xs font-mono">
        Progress: {{ currentAttempt }} / {{ totalAttempts }}
    </div>

  </div>
</template>
