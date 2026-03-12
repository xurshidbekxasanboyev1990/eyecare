<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useEyeTestStore } from '../stores/useEyeTestStore';
import { AlertCircle, ThumbsUp } from 'lucide-vue-next';

const router = useRouter();
const store = useEyeTestStore();

const circleSize = 250; // Fixed size nicely fitting mobile screens

const completeTest = (hasIssue) => {
    store.saveResult('redDesaturation', { 
        hasIssue, 
        score: hasIssue ? 'Muammo aniqlandi' : 'Me\'yorda',
        details: hasIssue ? 'Qizil rang bir ko\'zda xiraroq ko\'rindi (Desaturatsiya)' : 'Ikki ko\'zda ham bir xil yorqinlik' 
    });
    router.push('/test/perimetry');
};
</script>

<template>
  <div class="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-4">
    <div class="max-w-2xl w-full bg-slate-800 rounded-3xl shadow-2xl p-8 text-center border border-slate-700">
        <h1 class="text-3xl font-extrabold text-white mb-4">Qizil Rang To'yinganligi</h1>
        <p class="text-slate-300 mb-8 max-w-lg mx-auto text-lg font-medium leading-relaxed">
            Ko'rish nervi faoliyatini tekshirish.
            <br>Navbat bilan har bir ko'zingizni yoping va qizil doiraga qarang.
        </p>

        <div class="flex justify-center mb-10">
            <div 
                class="bg-[#DD0000] rounded-full shadow-[0_0_50px_rgba(221,0,0,0.4)] flex items-center justify-center animate-pulse"
                :style="{ width: circleSize + 'px', height: circleSize + 'px' }"
            >
                <span class="text-white/20 font-bold text-xl">RED</span>
            </div>
        </div>

        <h3 class="text-xl font-bold text-slate-100 mb-6">
            Bir ko'zingizda qizil rang boshqasiga qaraganda <span class="text-red-400">ochroq, xiraroq yoki jigarrangroq</span> ko'rindimi?
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button 
                @click="completeTest(false)"
                class="flex items-center justify-center gap-3 p-4 rounded-xl border-2 border-green-900 bg-green-900/20 text-green-400 hover:bg-green-900/40 transition-all font-medium"
            >
                <ThumbsUp class="w-6 h-6" />
                Yo'q, ikkalasi ham bir xil yorqin
            </button>
            <button 
                @click="completeTest(true)"
                class="flex items-center justify-center gap-3 p-4 rounded-xl border-2 border-red-900 bg-red-900/20 text-red-400 hover:bg-red-900/40 transition-all font-medium"
            >
                <AlertCircle class="w-6 h-6" />
                Ha, farq bor (xiraroq)
            </button>
        </div>
    </div>
  </div>
</template>
