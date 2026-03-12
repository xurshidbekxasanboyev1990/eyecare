<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEyeTestStore } from '../stores/useEyeTestStore';
import IshiharaPlate from '../components/IshiharaPlate.vue';

const router = useRouter();
const store = useEyeTestStore();

const plates = [
    // 1. Demonstration (12) - Everyone sees this
    { 
        id: 1, 
        number: '12', 
        correctAnswer: '12', 
        options: ['12', '8', '3', 'Ko\'rinmayapti'],
        description: 'Namuna'
    },
    // 2. Normal: 8, Red-Green Blind: 3
    { 
        id: 2, 
        number: '8', 
        correctAnswer: '8', 
        options: ['8', '3', '0', 'Ko\'rinmayapti'],
        description: 'Qizil-yashil sinov' 
    },
    // 3. Normal: 29, RG Blind: 70
    { 
        id: 3, 
        number: '29', 
        correctAnswer: '29', 
        options: ['29', '70', '19', 'Ko\'rinmayapti'],
        description: 'Qizil-yashil sinov'
    },
    // 4. Normal: 5, RG Blind: 2
    { 
        id: 4, 
        number: '5', 
        correctAnswer: '5', 
        options: ['5', '2', '6', 'Ko\'rinmayapti'],
        description: 'Qizil-yashil sinov'
    },
    // 5. Normal: 74, RG Blind: 21
    { 
        id: 5, 
        number: '74', 
        correctAnswer: '74', 
        options: ['74', '21', '71', 'Ko\'rinmayapti'],
        description: 'Qizil-yashil sinov'
    }
];

const currentIndex = ref(0);
const score = ref(0);
const answers = ref([]);

const currentPlate = computed(() => plates[currentIndex.value]);
// Standard fixed size for Ishihara plate (fits well on mobile)
const plateSize = 300; 
const progress = computed(() => ((currentIndex.value) / plates.length) * 100);

const submitAnswer = (selectedOption) => {
    const isCorrect = selectedOption === currentPlate.value.correctAnswer;
    if (isCorrect) score.value++;
    
    answers.value.push({
        plateId: currentPlate.value.id,
        isCorrect,
        selected: selectedOption
    });

    if (currentIndex.value < plates.length - 1) {
        currentIndex.value++;
    } else {
        finishTest();
    }
};

const finishTest = () => {
    const resultDetails = `To'g'ri javoblar: ${score.value}/${plates.length}`;
    let finalScore = 'Normal';
    
    // Logic: If user missed the first one (12), possible malingering or total blindness.
    // If they got '12' but missed others -> Color Blindness.
    
    // Strictness: Allow 1 mistake (except plate 1)
    if (score.value >= plates.length - 1) {
        finalScore = 'Normal';
    } else {
        finalScore = 'Rang ajratish buzilishi ehtimoli';
    }

    store.saveResult('colorBlindness', { 
        score: finalScore, 
        details: resultDetails,
        rawMatches: answers.value
    });
    
    router.push('/test/amsler');
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
    <div class="w-full max-w-2xl bg-white rounded-3xl shadow-xl overflow-hidden">
        <!-- Progress Bar -->
        <div class="h-2 bg-slate-100">
            <div class="h-full bg-brand-blue transition-all duration-300" :style="{ width: progress + '%' }"></div>
        </div>

        <div class="p-8 md:p-12 text-center">
            <h1 class="text-3xl font-extrabold text-slate-800 mb-4">Rang Ajratish Testi (Ishihara)</h1>
            <p class="text-slate-500 mb-8 text-lg font-medium">
                Rasmda qanday sonni ko'ryapsiz?
                <br><span class="text-sm font-normal text-slate-400">Rasm: {{ currentIndex + 1 }} / {{ plates.length }}</span>
            </p>

            <div class="flex justify-center mb-10">
                <!-- Programmable Canvas Plate -->
                <IshiharaPlate 
                    :key="currentPlate.id"
                    :number="currentPlate.number" 
                    :size="plateSize" 
                />
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-lg mx-auto">
                <button 
                    v-for="option in currentPlate.options" 
                    :key="option"
                    @click="submitAnswer(option)"
                    class="py-4 px-6 rounded-xl border-2 border-slate-100 text-slate-700 font-bold text-lg hover:border-brand-blue hover:bg-brand-light-blue hover:text-brand-blue transition-all active:scale-95"
                >
                    {{ option }}
                </button>
            </div>
        </div>
    </div>
  </div>
</template>
