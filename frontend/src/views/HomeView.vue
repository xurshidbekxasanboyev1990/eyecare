<script setup>
import { useRouter } from 'vue-router';
import { Eye, ArrowRight, Activity, ShieldCheck } from 'lucide-vue-next';

const router = useRouter();

const startTest = () => {
  router.push('/test/visual-acuity');
};
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50 flex flex-col">
    <!-- Navbar -->
    <nav class="container mx-auto px-6 py-4 flex justify-between items-center">
      <div class="flex items-center gap-2">
        <div class="bg-brand-blue p-2 rounded-lg">
          <Eye class="w-6 h-6 text-white" />
        </div>
        <span class="text-xl font-bold text-gray-800">EyeCare AI</span>
      </div>
      <button class="text-gray-600 hover:text-brand-blue font-medium transition">
        Haqida
      </button>
    </nav>

    <!-- Hero Section -->
    <main class="flex-1 container mx-auto px-6 flex flex-col md:flex-row items-center justify-center gap-12 py-10">
      <div class="flex-1 space-y-8 text-center md:text-left">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-100 text-blue-700 font-bold text-sm">
          <ShieldCheck class="w-5 h-5" />
          <span>Professional ko'z tekshiruvi v1.0</span>
        </div>
        
        <h1 class="text-5xl md:text-7xl font-extrabold text-slate-900 leading-tight">
            Ko'z salomatligingiz — <span class="text-brand-blue">Birinchi o'rinda</span>
        </h1>
        
        <p class="text-xl md:text-2xl text-slate-600 max-w-xl mx-auto md:mx-0 font-medium leading-relaxed">
            Sun'iy intellekt yordamida 10 xil turdagi professional ko'z testlaridan o'ting. 
            Tez, aniq va uyingizdan chiqmasdan.
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center md:justify-start pt-4">
          <button 
            @click="startTest"
            class="px-8 py-5 bg-brand-blue hover:bg-blue-600 text-white font-bold rounded-2xl shadow-xl shadow-blue-200 transition-all transform hover:-translate-y-1 flex items-center justify-center gap-3 text-xl"
          >
            Tekshiruvni Boshlash
            <ArrowRight class="w-6 h-6" />
          </button>
        </div>

        <div class="pt-8 grid grid-cols-3 gap-6 border-t border-gray-200 mt-8">
          <div>
            <h3 class="font-extrabold text-3xl text-slate-800">10+</h3>
            <p class="text-base text-slate-500 font-medium">Tibbiy Testlar</p>
          </div>
          <div>
            <h3 class="font-extrabold text-3xl text-slate-800">100%</h3>
            <p class="text-base text-slate-500 font-medium">Avtomatlashgan</p>
          </div>
          <div>
            <h3 class="font-extrabold text-3xl text-slate-800">AI</h3>
            <p class="text-base text-slate-500 font-medium">Tahlil Tizimi</p>
          </div>
        </div>
      </div>

      <div class="flex-1 w-full max-w-lg">
          <div class="bg-white p-8 rounded-3xl shadow-2xl border border-slate-100 grid grid-cols-2 gap-4">
               <div class="bg-blue-50 p-4 rounded-2xl flex flex-col items-center justify-center text-center gap-2 aspect-square">
                    <Eye class="w-10 h-10 text-brand-blue" />
                    <span class="font-bold text-slate-700">O'tkirlik</span>
               </div>
               <div class="bg-amber-50 p-4 rounded-2xl flex flex-col items-center justify-center text-center gap-2 aspect-square">
                    <Activity class="w-10 h-10 text-amber-600" />
                    <span class="font-bold text-slate-700">Ranglar</span>
               </div>
               <div class="bg-green-50 p-4 rounded-2xl flex flex-col items-center justify-center text-center gap-2 aspect-square">
                    <ShieldCheck class="w-10 h-10 text-green-600" />
                    <span class="font-bold text-slate-700">Amsler</span>
               </div>
               <div class="bg-indigo-50 p-4 rounded-2xl flex flex-col items-center justify-center text-center gap-2 aspect-square">
                    <ArrowRight class="w-10 h-10 text-indigo-600" />
                    <span class="font-bold text-slate-700">Perimetriya</span>
               </div>
          </div>
      </div>
    </main>

    <footer class="py-6 text-center text-slate-400 text-sm">
      &copy; 2026 EyeCare AI. Barcha huquqlar himoyalangan.
    </footer>
  </div>
</template>
