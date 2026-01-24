<script setup>
import { useRouter } from 'vue-router';
import { Eye, ArrowRight, Activity, ShieldCheck, Zap, Maximize, Contrast, Palette, BookOpen, Sun, AlertCircle, Settings } from 'lucide-vue-next';

const router = useRouter();

const startTest = () => {
  router.push('/test/visual-acuity');
};

const tests = [
  { icon: Eye, name: "Ko'rish O'tkirligi", desc: "Uzoqni ko'rish qobiliyatini tekshirish" },
  { icon: Palette, name: "Rang Ajratish", desc: "Daltonizm va ranglarni sezish" },
  { icon: ShieldCheck, name: "Amsler Panjarasi", desc: "Makula degeneratsiyasini aniqlash" },
  { icon: Contrast, name: "Kontrast", desc: "Yorug'lik va soyani ajratish" },
  { icon: Maximize, name: "Astigmatizm", desc: "Ko'z shox pardasining egriligi" },
  { icon: Sun, name: "Duoxrom", desc: "Optik kuch balansi (Miyopiya/Gipermetropiya)" },
  { icon: BookOpen, name: "Yaqindan Ko'rish", desc: "O'qish qobiliyati (Presbiopiya)" },
  { icon: Activity, name: "Qizil Desaturatsiya", desc: "Ko'rish nervi o'tkazuvchanligi" },
  { icon: Zap, name: "Perimetriya", desc: "Periferik (yon) ko'rish maydoni" },
  { icon: AlertCircle, name: "Quruq Ko'z (TBUT)", desc: "Ko'z yoshi pardasi barqarorligi" }
];
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <!-- Navbar -->
    <nav class="sticky top-0 z-30 bg-white/80 backdrop-blur border-b border-slate-200 px-6 py-4 flex justify-between items-center">
      <div class="flex items-center gap-2">
        <div class="bg-brand-blue p-2 rounded-lg">
          <Eye class="w-6 h-6 text-white" />
        </div>
        <span class="text-xl font-bold text-slate-800">EyeCare</span>
      </div>
      <button class="text-slate-600 hover:text-brand-blue font-medium transition">
        v1.2
      </button>
    </nav>

    <!-- Hero Section -->
    <header class="container mx-auto px-6 py-12 md:py-20 flex flex-col md:flex-row items-center gap-12">
      <div class="flex-1 text-center md:text-left space-y-8">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-100 text-blue-700 font-bold text-sm mx-auto md:mx-0">
          <ShieldCheck class="w-4 h-4" />
          <span>Professional Oftalmologik Tizim</span>
        </div>
        
        <h1 class="text-5xl md:text-7xl font-extrabold text-slate-900 leading-tight tracking-tight">
            Ko'z Diagnostikasi <br><span class="text-brand-blue">Professional</span> Tizim
        </h1>
        
        <p class="text-xl text-slate-600 max-w-xl mx-auto md:mx-0 font-medium leading-relaxed">
            Avtomatik masofa nazorati va 10 turdagi professional testlar yordamida ko'z salomatligingizni uyingizda tekshiring.
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center md:justify-start pt-4">
          <button 
            @click="startTest"
            class="px-8 py-5 bg-brand-blue hover:bg-blue-600 text-white font-bold rounded-2xl shadow-xl shadow-blue-200 transition-all transform hover:-translate-y-1 flex items-center justify-center gap-3 text-xl"
          >
            To'liq Tekshiruvni Boshlash
            <ArrowRight class="w-6 h-6" />
          </button>
        </div>
      </div>

      <div class="flex-1 w-full max-w-lg relative">
         <!-- Abstract decoration -->
         <div class="absolute -inset-4 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-full blur-3xl opacity-50 z-0"></div>
         
         <div class="relative z-10 grid grid-cols-2 gap-4">
               <div class="bg-white p-6 rounded-3xl shadow-lg flex flex-col items-center text-center gap-3 border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-700">
                    <div class="bg-blue-50 p-3 rounded-2xl"><Eye class="w-8 h-8 text-brand-blue" /></div>
                    <span class="font-bold text-slate-800">O'tkirlik</span>
               </div>
               <div class="bg-white p-6 rounded-3xl shadow-lg flex flex-col items-center text-center gap-3 border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100 mt-8">
                    <div class="bg-amber-50 p-3 rounded-2xl"><Activity class="w-8 h-8 text-amber-600" /></div>
                    <span class="font-bold text-slate-800">Color Blind</span>
               </div>
               <div class="bg-white p-6 rounded-3xl shadow-lg flex flex-col items-center text-center gap-3 border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
                    <div class="bg-green-50 p-3 rounded-2xl"><ShieldCheck class="w-8 h-8 text-green-600" /></div>
                    <span class="font-bold text-slate-800">Masofa</span>
               </div>
               <div class="bg-white p-6 rounded-3xl shadow-lg flex flex-col items-center text-center gap-3 border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300 mt-8">
                    <div class="bg-indigo-50 p-3 rounded-2xl"><ArrowRight class="w-8 h-8 text-indigo-600" /></div>
                    <span class="font-bold text-slate-800">Perimetriya</span>
               </div>
         </div>
      </div>
    </header>

    <!-- Tests Grid -->
    <section class="container mx-auto px-6 py-16">
        <h2 class="text-3xl font-extrabold text-slate-900 text-center mb-12">Mavjud Testlar (10 ta)</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <div v-for="test in tests" :key="test.name" class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-blue/30 transition group">
                <div class="bg-slate-50 w-12 h-12 rounded-xl flex items-center justify-center mb-4 group-hover:bg-blue-50 transition">
                    <component :is="test.icon" class="w-6 h-6 text-slate-600 group-hover:text-brand-blue transition" />
                </div>
                <h3 class="font-bold text-slate-800 mb-1 text-sm">{{ test.name }}</h3>
                <p class="text-xs text-slate-500 leading-snug">{{ test.desc }}</p>
            </div>
        </div>
    </section>

    <footer class="bg-white py-8 border-t border-slate-100">
      <div class="container mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <p class="text-slate-500 font-medium">&copy; 2026 EyeCare Project. Powered by Vue 3.</p>
          <button 
              @click="router.push('/admin')"
              class="text-slate-400 hover:text-brand-blue text-sm font-medium transition flex items-center gap-1"
          >
              <Settings class="w-4 h-4" />
              Admin Panel
          </button>
      </div>
    </footer>
  </div>
</template>
