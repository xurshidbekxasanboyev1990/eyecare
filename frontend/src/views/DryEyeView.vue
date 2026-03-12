<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useEyeTestStore } from '../stores/useEyeTestStore';
import { Eye, Timer, Play, CheckCircle, AlertTriangle } from 'lucide-vue-next';

const router = useRouter();
const store = useEyeTestStore();

const isStarted = ref(false);
const isFinished = ref(false);
const startTime = ref(0);
const duration = ref(0);
const timerInterval = ref(null);

const startTest = () => {
  isStarted.value = true;
  startTime.value = Date.now();
  
  timerInterval.value = setInterval(() => {
    duration.value = (Date.now() - startTime.value) / 1000;
  }, 100);
};

const handleBlink = () => {
    if (!isStarted.value || isFinished.value) return;

    clearInterval(timerInterval.value);
    isFinished.value = true;
    
    // Save result
    // Normal TBUT (Tear Break-up Time) is > 10 seconds
    const resultDetails = duration.value < 10 
        ? 'Quruq ko\'z sindromi ehtimoli bor (<10s)' 
        : 'Me\'yorida (>10s)';
    
    // Ensure accurate storage format for ResultsView: it parses parseFloat(score)
    store.saveResult('dryEye', { 
        score: duration.value.toFixed(1) + ' sekund', 
        details: resultDetails 
    });
};

const next = () => {
  // Dry Eye is usually the last one or close to it, check logic
  router.push('/results');
};

const restart = () => {
    isStarted.value = false;
    isFinished.value = false;
    duration.value = 0;
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
      <div class="mb-6 flex justify-center">
        <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
           <Eye class="w-8 h-8 text-brand-blue" />
        </div>
      </div>

      <h1 class="text-3xl font-extrabold mb-4 text-slate-800">Quruq Ko'z Testi</h1>
      
      <div v-if="!isStarted">
        <p class="text-slate-600 mb-6 text-lg font-medium">
            Bu test "Ko'z yoshi pardasining buzilish vaqti" (TBUT) ga asoslangan.
        </p>
        <div class="bg-blue-50 p-6 rounded-xl text-left mb-8 space-y-4">
             <div class="flex gap-3">
                <span class="font-bold text-brand-blue text-lg">1.</span>
                <p class="text-base text-slate-800 font-medium">Oddiy holatda o'tiring va ko'zingizni bir necha marta pirpirating.</p>
             </div>
             <div class="flex gap-3">
                <span class="font-bold text-brand-blue text-lg">2.</span>
                <p class="text-base text-slate-800 font-medium">"Boshlash" tugmasini bosgach, ko'zingizni ochib, imkon qadar <b>pirpiratmasdan</b> turing.</p>
             </div>
             <div class="flex gap-3">
                <span class="font-bold text-brand-blue text-lg">3.</span>
                <p class="text-base text-slate-800 font-medium">Ko'zingizda noqulaylik sezilib (achishish), pirpiratishingiz bilan "Pirpiratdim" tugmasini bosing.</p>
             </div>
        </div>

        <button @click="startTest" class="w-full bg-brand-blue text-white py-4 rounded-xl font-bold hover:bg-blue-600 transition flex items-center justify-center gap-2">
            <Play class="w-5 h-5" /> Testni Boshlash
        </button>
      </div>

      <div v-else-if="!isFinished" class="py-8">
         <div class="text-6xl font-mono font-bold text-slate-800 mb-8 tabular-nums">
             {{ duration.toFixed(1) }}<span class="text-2xl text-slate-400">s</span>
         </div>
         
         <p class="text-slate-500 mb-8 animate-pulse">
             Ko'zingizni ochiq holda saqlang...
         </p>

         <button @click="handleBlink" class="w-full bg-orange-500 text-white py-6 rounded-xl font-bold hover:bg-orange-600 transition text-lg shadow-lg shadow-orange-200">
             KO'ZIMNI PIRPIRATDIM!
         </button>
      </div>

      <div v-else>
         <div class="mb-6">
             <div v-if="duration >= 10" class="flex flex-col items-center">
                 <CheckCircle class="w-16 h-16 text-green-500 mb-4" />
                 <h2 class="text-xl font-bold text-slate-800">Natija: Yaxshi</h2>
                 <p class="text-green-600 mt-2">Siz {{ duration.toFixed(1) }} soniya bardosh berdingiz.</p>
             </div>
             <div v-else class="flex flex-col items-center">
                 <AlertTriangle class="w-16 h-16 text-orange-500 mb-4" />
                 <h2 class="text-xl font-bold text-slate-800">Quruq Ko'z Belgilari</h2>
                 <p class="text-orange-600 mt-2">Siz faqat {{ duration.toFixed(1) }} soniya bardosh berdingiz. (Me'yor > 10s)</p>
             </div>
         </div>

         <div class="flex flex-col gap-3">
             <button @click="next" class="w-full bg-brand-blue text-white py-3 rounded-xl font-bold hover:bg-blue-600 transition">
                 Natijalarni ko'rish
             </button>
             <button @click="restart" class="w-full text-slate-500 py-3 rounded-xl font-medium hover:bg-slate-100 transition">
                 Qayta urinish
             </button>
         </div>
      </div>

    </div>
  </div>
</template>
