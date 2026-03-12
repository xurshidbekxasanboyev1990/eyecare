<script setup>
import { useRouter } from 'vue-router';
import { useEyeTestStore } from '../stores/useEyeTestStore';

const router = useRouter();
const store = useEyeTestStore();

const completeTest = (preference) => {
    let details = '';
    if (preference === 'red') details = 'Qizil fon aniqroq (Ehtimoliy miyopiya)';
    else if (preference === 'green') details = 'Yashil fon aniqroq (Ehtimoliy gipermetropiya)';
    else details = 'Ikkisi ham bir xil (Normal balans)';

    store.saveResult('duochrome', { 
        preference, 
        score: preference, 
        details 
    });
    router.push('/test/near-vision');
};
</script>

<template>
  <div class="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-4">
    <div class="max-w-4xl w-full bg-slate-800 rounded-3xl shadow-2xl overflow-hidden text-center pb-8">
        <div class="p-6 text-white border-b border-slate-700">
             <h1 class="text-3xl font-extrabold mb-4">Duoxrom Testi</h1>
             <p class="text-slate-300 text-lg font-medium">
                 Qaysi fondagi doiralar <b>aniqroq va o'tkirroq</b> ko'rinyapti?
             </p>
        </div>

        <div class="flex flex-col md:flex-row h-[400px]">
            <!-- Red Side -->
            <div class="flex-1 bg-[#EE0000] flex items-center justify-center relative group cursor-pointer hover:opacity-95 transition" @click="completeTest('red')">
                <div class="absolute top-4 left-4 bg-white/20 text-white px-3 py-1 rounded-full text-sm">Qizil</div>
                <div class="grid grid-cols-4 gap-4">
                    <!-- Landolt C or Circles -->
                    <div class="w-12 h-12 rounded-full border-[6px] border-black"></div>
                    <div class="w-10 h-10 rounded-full border-[5px] border-black"></div>
                    <div class="w-8 h-8 rounded-full border-[4px] border-black"></div>
                    <div class="w-6 h-6 rounded-full border-[3px] border-black"></div>
                </div>
            </div>

            <!-- Green Side -->
            <div class="flex-1 bg-[#00AA00] flex items-center justify-center relative group cursor-pointer hover:opacity-95 transition" @click="completeTest('green')">
                 <div class="absolute top-4 right-4 bg-white/20 text-white px-3 py-1 rounded-full text-sm">Yashil</div>
                 <div class="grid grid-cols-4 gap-4">
                    <div class="w-12 h-12 rounded-full border-[6px] border-black"></div>
                    <div class="w-10 h-10 rounded-full border-[5px] border-black"></div>
                    <div class="w-8 h-8 rounded-full border-[4px] border-black"></div>
                    <div class="w-6 h-6 rounded-full border-[3px] border-black"></div>
                </div>
            </div>
        </div>

        <div class="flex justify-center gap-6 mt-8">
            <button @click="completeTest('red')" class="px-6 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 font-bold">
                Qizil Taraf Aniqroq
            </button>
             <button @click="completeTest('equal')" class="px-6 py-3 bg-slate-600 text-white rounded-xl hover:bg-slate-500 font-bold">
                Bir Xil
            </button>
            <button @click="completeTest('green')" class="px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 font-bold">
                Yashil Taraf Aniqroq
            </button>
        </div>
    </div>
  </div>
</template>
