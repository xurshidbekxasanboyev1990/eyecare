<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEyeTestStore } from '../stores/useEyeTestStore';
import { ArrowUp, ArrowRight, ArrowDown, ArrowLeft, Sun, ScanEye, CheckCircle2 } from 'lucide-vue-next';

const router = useRouter();
const store = useEyeTestStore();

const levels = [
  { size: 200, label: '20/200' }, // Huge
  { size: 100, label: '20/100' },
  { size: 70, label: '20/70' },
  { size: 50, label: '20/50' },
  { size: 40, label: '20/40' }, // Driver's license req usually
  { size: 30, label: '20/30' },
  { size: 20, label: '20/20' }, // Normal
  { size: 15, label: '20/15' }, // Superior
];

const currentLevelIndex = ref(0);
const currentDirection = ref(0); // 0: up, 1: right, 2: down, 3: left
const mistakes = ref(0);
const maxMistakes = 2; 

const testType = ref('snellen'); // 'snellen' (E) or 'landolt' (C)

const isTestStarted = ref(false);

// Standard approximated sizes in pixels for different viewing contexts (mobile/desktop)
// Assumes user holds phone at ~40-50cm
const levelSizes = computed(() => {
    // Base size for 20/200 roughly 40-50mm on screen
    // We'll use a standard scaling factor.
    // 20/200 -> 150px
    // 20/20 -> 15px
    const baseScale = 0.75; // Adjust this multiplier for general fit
    return levels.map(l => ({
        ...l,
        pixelSize: l.size * baseScale
    }));
});

const generateDirection = () => {
  currentDirection.value = Math.floor(Math.random() * 4);
};

const start = () => {
    isTestStarted.value = true;
    generateDirection();
};

const checkAnswer = (direction) => {
    if (direction === currentDirection.value) {
        // Correct
        if (currentLevelIndex.value < levels.length - 1) {
            currentLevelIndex.value++;
            generateDirection();
        } else {
            // Finished all levels
            finishTest(levels[currentLevelIndex.value].label);
        }
    } else {
        // Incorrect
        mistakes.value++;
        if (mistakes.value > maxMistakes) {
            const resultLabel = currentLevelIndex.value > 0 ? levels[currentLevelIndex.value - 1].label : ' < 20/200';
            finishTest(resultLabel);
        } else {
            generateDirection();
        }
    }
};

const finishTest = (scoreLabel) => {
    store.saveResult('visualAcuity', { 
        score: scoreLabel, 
        details: `Optotip: ${testType.value === 'snellen' ? 'Snellen E' : 'Landolt C'}` 
    });
    router.push('/test/color-blindness');
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
    <!-- Pre-Check Modal Removed -->

    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        <h1 class="text-3xl font-extrabold mb-4 text-slate-800">Ko'rish O'tkirligi</h1>
        
        <div v-if="!isTestStarted">
            <p class="text-slate-600 mb-8 text-lg font-medium leading-relaxed">
                Qurilmani ko'zingizdan <b>40-50 sm (bir qo'l)</b> masofada tuting.
                <br>Bir ko'zingizni yoping va ekrandagi harf/belgi yo'nalishini toping.
            </p>

            
            <div class="flex justify-center gap-4 mb-8">
                <button 
                    @click="testType = 'snellen'"
                    class="p-4 rounded-xl border-2 transition-all flex flex-col items-center gap-2 w-32"
                    :class="testType === 'snellen' ? 'border-brand-blue bg-blue-50 text-brand-blue' : 'border-slate-100 text-slate-400'"
                >
                    <span class="font-serif font-black text-3xl">E</span>
                    <span class="text-xs font-bold">Snellen</span>
                </button>
                 <button 
                    @click="testType = 'landolt'"
                    class="p-4 rounded-xl border-2 transition-all flex flex-col items-center gap-2 w-32"
                    :class="testType === 'landolt' ? 'border-brand-blue bg-blue-50 text-brand-blue' : 'border-slate-100 text-slate-400'"
                >
                    <span class="font-sans font-bold text-3xl border-4 border-current rounded-full w-8 h-8 border-r-transparent rotate-45 inline-block"></span>
                    <span class="text-xs font-bold">Landolt</span>
                </button>
            </div>

            <button @click="start" class="bg-brand-blue text-white w-full py-3 rounded-xl font-bold hover:bg-blue-600 transition">
                Boshlash
            </button>
        </div>

        <div v-else>
            <div class="h-64 flex items-center justify-center mb-8 border-b border-gray-100 overflow-hidden relative">
                <!-- Snellen E -->
                <div 
                    v-if="testType === 'snellen'"
                    class="font-serif font-black leading-none select-none transition-all duration-300"
                    :style="{ fontSize: levelSizes[currentLevelIndex].pixelSize + 'px', transform: 'rotate(' + (currentDirection * 90) + 'deg)' }"
                >
                    E
                </div>

                <!-- Landolt C -->
                <div 
                    v-else
                    class="border-[1em] border-black rounded-full border-r-transparent select-none transition-all duration-300 box-border"
                    :style="{ 
                        width: levelSizes[currentLevelIndex].pixelSize + 'px', 
                        height: levelSizes[currentLevelIndex].pixelSize + 'px',
                        borderWidth: (levelSizes[currentLevelIndex].pixelSize / 5) + 'px',
                        transform: 'rotate(' + (currentDirection * 90) + 'deg)' 
                    }"
                ></div>
            </div>

            <p class="text-xl text-slate-500 mb-6 font-medium">
                {{ testType === 'snellen' ? 'E harfining' : 'Doira yorig\'ining' }} ochiq tomoni qayerda?
            </p>

            <div class="grid grid-cols-3 gap-4 auto-rows-fr max-w-[200px] mx-auto">
                <div></div>
                <button @click="checkAnswer(0)" class="aspect-square bg-slate-100 hover:bg-slate-200 rounded-lg flex items-center justify-center active:scale-95 transition">
                    <ArrowUp class="w-6 h-6 text-slate-700"/>
                </button>
                <div></div>

                <button @click="checkAnswer(3)" class="aspect-square bg-slate-100 hover:bg-slate-200 rounded-lg flex items-center justify-center active:scale-95 transition">
                    <ArrowLeft class="w-6 h-6 text-slate-700"/>
                </button>
                <div class="aspect-square flex items-center justify-center bg-slate-50 rounded-full text-xs text-slate-400 font-mono">
                   {{ levels[currentLevelIndex].label }}
                </div>
                <button @click="checkAnswer(1)" class="aspect-square bg-slate-100 hover:bg-slate-200 rounded-lg flex items-center justify-center active:scale-95 transition">
                    <ArrowRight class="w-6 h-6 text-slate-700"/>
                </button>

                <div></div>
                <button @click="checkAnswer(2)" class="aspect-square bg-slate-100 hover:bg-slate-200 rounded-lg flex items-center justify-center active:scale-95 transition">
                    <ArrowDown class="w-6 h-6 text-slate-700"/>
                </button>
                <div></div>
            </div>
            
             <div class="mt-6 text-slate-400 text-xs text-center border-t pt-2">
                Xatolar: {{ mistakes }} / {{ maxMistakes + 1 }}
             </div>
        </div>
    </div>
  </div>
</template>
