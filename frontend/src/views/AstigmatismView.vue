<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEyeTestStore } from '../stores/useEyeTestStore';
import { CheckCircle, AlertTriangle } from 'lucide-vue-next';

const router = useRouter();
const store = useEyeTestStore();

const clockSize = 340; // Fixed size nicely fitting mobile screens

const completeTest = (hasIssue) => {
    store.saveResult('astigmatism', { 
        hasIssue, 
        score: hasIssue ? 'Musbat' : 'Manfiy',
        details: hasIssue ? 'Ayrim chiziqlar qalinroq yoki qoraroq ko\'rindi' : 'Barcha chiziqlar bir xil'
    });
    router.push('/test/duochrome');
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
    <div class="max-w-3xl w-full bg-white rounded-3xl shadow-xl overflow-hidden p-8 text-center">
        <h1 class="text-3xl font-extrabold text-slate-800 mb-4">Astigmatizm Testi</h1>
        <p class="text-slate-600 mb-8 max-w-lg mx-auto text-lg font-medium leading-relaxed">
            <b>Bir ko'zingizni yoping</b> va rasmdagi chiziqlarga qarang.
            <br>Barcha chiziqlar bir xil qalinlikdami va qoralikdami?
        </p>

        <div class="flex justify-center mb-10 overflow-hidden py-4">
            <!-- Programmatic Clock Dial -->
            <div 
                class="relative bg-white rounded-full flex items-center justify-center select-none"
                :style="{ width: clockSize + 'px', height: clockSize + 'px' }"
            >
                
                <!-- Lines -->
                <div v-for="i in 12" :key="i" 
                    class="absolute w-[3px] h-full bg-transparent flex flex-col justify-between"
                    :style="{ transform: `rotate(${i * 15}deg)` }"
                >
                    <!-- Typical block dial looks like 3 distinct input lines per angle or just single thick ones. Using simple thick lines. -->
                    <div class="w-full h-[15%] bg-black"></div>
                    <div class="w-full h-[15%] bg-black"></div>
                </div>

                <!-- Center Crosshair/Dot -->
                <div class="absolute w-[10px] h-[10px] bg-black rounded-full z-10"></div>
                
                <!-- Numbers (Optional, usually 1-12 clock) -->
                 <div v-for="n in 12" :key="n"
                    class="absolute text-xl font-bold text-slate-400"
                    :style="{ 
                        transform: `rotate(${n * 30}deg) translate(0, -${clockSize * 0.4}px) rotate(-${n * 30}deg)`
                    }"
                 >
                 </div>
            </div>
        </div>

        <h3 class="text-lg font-medium text-slate-700 mb-6 font-bold">Nimanidir farqini sezdingizmi? (Masalan, 12-6 chizig'i boshqalardan ko'ra qoraroqmi?)</h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg mx-auto">
            <button 
                @click="completeTest(false)"
                class="flex items-center justify-center gap-3 p-4 rounded-xl border-2 border-slate-100 hover:border-brand-blue hover:bg-brand-light-blue transition-all"
            >
                <CheckCircle class="w-6 h-6 text-green-500" />
                Yo'q, hammasi bir xil
            </button>
            <button 
                @click="completeTest(true)"
                class="flex items-center justify-center gap-3 p-4 rounded-xl border-2 border-slate-100 hover:border-orange-400 hover:bg-orange-50 transition-all text-left"
            >
                <AlertTriangle class="w-6 h-6 text-orange-500" />
                Ha, ayrimlari qoraroq/qalinroq
            </button>
        </div>
    </div>
  </div>
</template>
