<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEyeTestStore } from '../stores/useEyeTestStore';
import { BookOpen, Check, X } from 'lucide-vue-next';

const router = useRouter();
const store = useEyeTestStore();

const score = ref(null);

// Standard pixel sizes for Near Vision (approximate for mobile screens)
const textBlocks = [
    { sizePx: 12, jaeger: 'J1', label: 'J1 (Eng kichik)' },
    { sizePx: 14, jaeger: 'J2', label: 'J2 (Normal)' },
    { sizePx: 16, jaeger: 'J3', label: 'J3 (Gazeta)' },
    { sizePx: 20, jaeger: 'J5', label: 'J5' },
    { sizePx: 24, jaeger: 'J7', label: 'J7' },
    { sizePx: 32, jaeger: 'J10', label: 'J10 (Yirik)' }
];

const selectedLevel = ref(null);

const completeTest = () => {
    if (!selectedLevel.value) return;
    
    // Logic: If they can read J2 (index 1) or J1 (index 0), it's good.
    const result = textBlocks[selectedLevel.value];
    
    store.saveResult('nearVision', {
        score: result.jaeger,
        details: `Eng kichik o'qilgan matn: ${result.label}`
    });
    router.push('/test/red-desaturation');
};

const selectLevel = (index) => {
    selectedLevel.value = index;
};
</script>

<template>
  <div class="min-h-screen bg-amber-50 flex flex-col items-center justify-center p-4">
    <div class="max-w-xl w-full bg-white rounded-3xl shadow-xl overflow-hidden p-8">
         <div class="text-center mb-6">
            <h1 class="text-3xl font-extrabold text-slate-900 flex items-center justify-center gap-2 mb-4">
                <BookOpen class="w-8 h-8 text-amber-700" />
                Yaqindan Ko'rish (O'qish)
            </h1>
            <p class="text-slate-600 mt-2 text-lg font-medium leading-relaxed">
                Telefonni ko'zingizdan <b>35-40 sm</b> masofada ushlab turing. 
                <br>Qaysi eng kichik matnni qiynalmasdan o'qiy oldingiz?
            </p>
         </div>

         <div class="space-y-6 mb-8 text-left">
             <div 
                v-for="(block, index) in textBlocks" 
                :key="index"
                class="p-4 border rounded-xl hover:border-brand-blue/50 transition cursor-pointer"
                :class="selectedLevel === index ? 'border-brand-blue bg-blue-50 ring-2 ring-blue-100' : 'border-slate-100'"
                @click="selectLevel(index)"
             >
                <div class="flex justify-between items-center mb-2">
                    <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ block.label }}</span>
                    <div v-if="selectedLevel === index" class="bg-brand-blue text-white p-1 rounded-full">
                        <Check class="w-3 h-3" />
                    </div>
                </div>
                <p 
                    class="text-slate-800 leading-relaxed font-serif"
                    :style="{ fontSize: block.sizePx + 'px' }"
                >
                    Quyosh charaqlab turgan paytda, ko'm-ko'k osmonga qarab, tabiatning naqadar go'zal ekanligini his qilish insonga o'zgacha zavq bag'ishlaydi.
                </p>
             </div>
         </div>

         <button 
            @click="completeTest"
            :disabled="selectedLevel === null"
            class="w-full py-4 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-bold transition flex items-center justify-center gap-2"
         >
            Natijani Saqlash
            <Check class="w-5 h-5" />
         </button>
    </div>
  </div>
</template>
