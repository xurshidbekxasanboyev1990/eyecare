<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEyeTestStore } from '../stores/useEyeTestStore';

const router = useRouter();
const store = useEyeTestStore();

const letterSize = 64; // Approx 4rem (text-6xl)

const contrastLevels = [
    { opacity: 1.0, label: '100% (Normal)' },
    { opacity: 0.5, label: '50%' },
    { opacity: 0.25, label: '25%' },
    { opacity: 0.1, label: '10%' },
    { opacity: 0.05, label: '5%' },
    { opacity: 0.025, label: '2.5% (A\'lo)' },
    { opacity: 0.012, label: '1.2% (Super)' }
];

const letters = ['C', 'O', 'H', 'Z', 'K', 'S'];

const generateTest = () => {
    return contrastLevels.map((level, index) => ({
        ...level,
        letter: letters[Math.floor(Math.random() * letters.length)],
        id: index
    }));
};

const activeTests = ref(generateTest());

const completeTest = (canSeeAll) => {
    // Logic: user selects the last row they can see
    // For simplicity: "Did you see standard gray text?"
    // Better UI: Show one by one.
};

const handleSelection = (levelIndex) => {
    // contrastLevels are Top (100%) to Bottom (1%). Higher index = Better sensitivity.
    const result = contrastLevels[levelIndex];
    
    // We want to save a score like "1.65 logCS" or just the % string
    store.saveResult('contrastSensitivity', { 
        score: result.label.split(' ')[0], // "2.5%"
        details: `Eng past kontrast: ${result.label}` 
    });
    router.push('/test/astigmatism');
};

</script>

<template>
  <div class="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-4">
    <div class="max-w-2xl w-full text-center">
        <h1 class="text-3xl font-extrabold text-white mb-4">Kontrast Sezgirlik</h1>
        <p class="text-slate-300 mb-12 text-xl font-medium">
            Quyidagi qatorlardan qaysi birini <b>eng oxirgi bo'lib</b> aniq o'qiy oldingiz?
            <br><span class="text-sm font-normal opacity-80">(Oxirgi ko'ringan qatorni bosing)</span>
        </p>

        <div class="space-y-6 bg-white rounded-3xl p-8 mb-8">
            <div 
                v-for="(test, index) in activeTests" 
                :key="test.id"
                @click="handleSelection(index)"
                class="cursor-pointer hover:bg-slate-50 p-4 rounded-xl transition flex items-center justify-between group"
            >
                <span class="text-sm text-slate-400 font-mono w-16 text-left">Level {{ index + 1 }}</span>
                
                <div class="flex-1 text-center">
                    <span 
                        class="font-sans font-bold select-none" 
                        :style="{ 
                            fontSize: letterSize + 'px',
                            color: `rgba(0,0,0, ${test.opacity})` 
                        }"
                    >
                        {{ test.letter }} R K Z
                    </span>
                </div>

                <div class="w-16 opacity-0 group-hover:opacity-100 text-brand-blue font-bold text-sm">
                    Tanlash
                </div>
            </div>
        </div>
        
        <p class="text-xs text-slate-500">
            Tanlash uchun eng xira ko'ringan qatorni bosing.
        </p>
    </div>
  </div>
</template>
