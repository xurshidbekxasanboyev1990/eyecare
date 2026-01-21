<script setup>
import { onMounted, ref } from 'vue';
import { useEyeTestStore } from '../stores/useEyeTestStore';
import { useRouter } from 'vue-router';
import { Download, Share2, RefreshCw, Home, Send, Loader2 } from 'lucide-vue-next';

const store = useEyeTestStore();
const router = useRouter();
const isTelegram = ref(false);
const isSending = ref(false);

const checkTelegram = () => {
    if (window.Telegram?.WebApp) {
        isTelegram.value = true;
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
    }
};

const sendToBot = async () => {
    isSending.value = true;
    
    // 1. Generate Diagnosis
    const r = store.results;
    let diagnoses = [];
    let recs = [];
    let exercises = [];

    // Simple Logic
    // Acuity
    if (r.visualAcuity.score && r.visualAcuity.score !== '20/20' && r.visualAcuity.score !== '20/15') {
        diagnoses.push(`Ko'rish o'tkirligi pasaygan (${r.visualAcuity.score})`);
        recs.push("Okulist ko'rigidan o'tib, ko'zoynak tanlash maslahat beriladi.");
    }

    // Color
    if (r.colorBlindness.score !== 'Normal') {
        diagnoses.push("Rang ajratishda nuqsonlar (Daltonizm ehtimoli)");
    }

    // Amsler
    if (r.amslerGrid.hasDistortion) {
        diagnoses.push("Makula degeneratsiyasi belgilari (Amsler)");
        recs.push("Zudlik bilan to'r parda tekshiruvi zarur!");
    }

    // Dry Eye
    if (parseFloat(r.dryEye.score) < 10) {
        diagnoses.push("Quruq ko'z sindromi");
        recs.push("Sun'iy ko'z yoshi tomchilaridan foydalanish.");
        exercises.push("20-20-20 qoidasi: Har 20 daqiqada 20 soniya uzoqqa qarash.");
    }

    // Astigmatism
    if (r.astigmatism.hasIssue) {
        diagnoses.push("Astigmatizm belgilari");
    }

    if (diagnoses.length === 0) {
        diagnoses.push("Ko'rish qobiliyati me'yorda.");
        recs.push("Yilda bir marta profilaktik ko'rikdan o'ting.");
    }

    const payload = {
        diag: diagnoses.join('\n'),
        color_res: r.colorBlindness.score || "Topshirilmagan",
        exercise: exercises.length > 0 ? exercises.join('\n') : "Ko'z gimnastikasi mashqlari.",
        meds: recs.join('\n'),
        full_data: r // Sending raw data for AI analysis if needed
    };

    // Send to Telegram
    if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.sendData(JSON.stringify(payload));
    } else {
        alert("Bu funksiya faqat Telegram ichida ishlaydi!");
        console.log(payload);
    }
    isSending.value = false;
};

onMounted(() => {
    checkTelegram();
});

const restart = () => {
    store.resetTests();
    router.push('/');
};

const formatDate = () => {
    return new Date().toLocaleDateString('uz-UZ', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-4">
    <div class="max-w-3xl mx-auto">
        <header class="text-center mb-12">
            <h1 class="text-4xl md:text-5xl font-extrabold text-slate-900 mb-3">Umumiy Natijalar</h1>
            <p class="text-lg text-slate-500">{{ formatDate() }} holatiga ko'ra</p>
        </header>
        
        <div class="bg-white shadow-xl rounded-3xl overflow-hidden mb-8">
            <div class="p-8 grid gap-8">
                <!-- Visual Acuity -->
                <div class="flex items-center justify-between border-b pb-6 last:border-0 last:pb-0">
                    <div>
                        <h3 class="font-bold text-slate-800 text-2xl mb-2">Ko'rish O'tkirligi</h3>
                        <p class="text-lg text-slate-500">Snellen Testi</p>
                    </div>
                    <div class="text-right">
                        <div class="text-4xl font-extrabold text-brand-blue">
                             {{ store.results.visualAcuity.score || '-' }}
                        </div>
                        <p class="text-sm text-slate-400 font-medium">Norma: 20/20</p>
                    </div>
                </div>

                <!-- Color Blindness -->
                <div class="flex items-center justify-between border-b pb-6 last:border-0 last:pb-0">
                     <div>
                        <h3 class="font-bold text-slate-800 text-2xl mb-2">Rang Ajratish</h3>
                        <p class="text-lg text-slate-500">Ishihara Plitalari</p>
                    </div>
                     <div class="text-right">
                        <div class="text-3xl font-extrabold" 
                            :class="store.results.colorBlindness.score === 'Normal' ? 'text-green-500' : 'text-orange-500'">
                             {{ store.results.colorBlindness.score || '-' }}
                        </div>
                        <p class="text-sm text-slate-400 font-medium">{{ store.results.colorBlindness.details }}</p>
                    </div>
                </div>

                <!-- Amsler -->
                <div class="flex items-center justify-between border-b pb-6 last:border-0 last:pb-0">
                     <div>
                        <h3 class="font-bold text-slate-800 text-2xl mb-2">Amsler Panjarasi</h3>
                        <p class="text-lg text-slate-500">Makula holati</p>
                    </div>
                     <div class="text-right">
                        <div class="text-3xl font-extrabold text-slate-700">
                             {{ store.results.amslerGrid.score || '-' }}
                        </div>
                         <p class="text-sm text-slate-400 font-medium">{{ store.results.amslerGrid.details }}</p>
                    </div>
                </div>

                <!-- Astigmatism -->
                <div class="flex items-center justify-between border-b pb-6 last:border-0 last:pb-0">
                     <div>
                        <h3 class="font-bold text-slate-800 text-2xl mb-2">Astigmatizm</h3>
                        <p class="text-lg text-slate-500">Soat Ciferblati Testi</p>
                    </div>
                     <div class="text-right">
                        <div class="text-3xl font-extrabold" 
                            :class="store.results.astigmatism.hasIssue ? 'text-orange-500' : 'text-green-500'">
                             {{ store.results.astigmatism.score || '-' }}
                        </div>
                         <p class="text-sm text-slate-400 font-medium">{{ store.results.astigmatism.details }}</p>
                    </div>
                </div>

                 <!-- Duochrome -->
                 <div class="flex items-center justify-between border-b pb-6 last:border-0 last:pb-0">
                     <div>
                        <h3 class="font-bold text-slate-800 text-2xl mb-2">Duoxrom Balans</h3>
                        <p class="text-lg text-slate-500">Qizil/Yashil Fon</p>
                    </div>
                     <div class="text-right">
                        <div class="text-3xl font-extrabold text-slate-700">
                             {{ store.results.duochrome.score === 'equal' ? 'Normal' : (store.results.duochrome.score || '-') }}
                        </div>
                         <p class="text-sm text-slate-400 font-medium">{{ store.results.duochrome.details }}</p>
                    </div>
                </div>

                <!-- Near Vision -->
                <div class="flex items-center justify-between border-b pb-6 last:border-0 last:pb-0">
                     <div>
                        <h3 class="font-bold text-slate-800 text-2xl mb-2">Yaqindan O'qish</h3>
                        <p class="text-lg text-slate-500">Jaeger Matnlari</p>
                    </div>
                     <div class="text-right">
                        <div class="text-3xl font-extrabold text-slate-700">
                             {{ store.results.nearVision.score || '-' }}
                        </div>
                         <p class="text-sm text-slate-400 font-medium">{{ store.results.nearVision.details ? store.results.nearVision.details.split(': ')[1] : '' }}</p>
                    </div>
                </div>

                <!-- Red Desaturation -->
                <div class="flex items-center justify-between border-b pb-6 last:border-0 last:pb-0">
                     <div>
                        <h3 class="font-bold text-slate-800 text-2xl mb-2">Rang To'yinganligi</h3>
                        <p class="text-lg text-slate-500">Nerv O'tkazuvchanligi</p>
                    </div>
                     <div class="text-right">
                        <div class="text-3xl font-extrabold"
                            :class="store.results.redDesaturation.hasIssue ? 'text-red-500' : 'text-green-500'">
                             {{ store.results.redDesaturation.score || '-' }}
                        </div>
                    </div>
                </div>

                 <!-- Perimetry -->
                 <div class="flex items-center justify-between border-b pb-6 last:border-0 last:pb-0">
                     <div>
                        <h3 class="font-bold text-slate-800 text-2xl mb-2">Perimetriya</h3>
                        <p class="text-lg text-slate-500">Ko'rish Maydoni</p>
                    </div>
                     <div class="text-right">
                        <div class="text-3xl font-extrabold" 
                            :class="store.results.perimetry.score === 'Normal' ? 'text-green-500' : 'text-red-500'">
                             {{ store.results.perimetry.score || '-' }}
                        </div>
                         <p class="text-sm text-slate-400 font-medium">{{ store.results.perimetry.details }}</p>
                    </div>
                </div>

                 <!-- Dry Eye -->
                 <div class="flex items-center justify-between border-b pb-6 last:border-0 last:pb-0">      
                <div>
                <h3 class="font-bold text-slate-800 text-2xl mb-2">Quruq Ko'z (TBUT)</h3>
                <p class="text-lg text-slate-500">Yoshi pardasi barqarorligi</p>
            </div>
                <div class="text-right">
                <div class="text-3xl font-extrabold"
                    :class="parseFloat(store.results.dryEye.score) >= 10 ? 'text-green-500' : 'text-orange-500'">
                        {{ store.results.dryEye.score || '-' }}
                </div>
                    <p class="text-sm text-slate-400 font-medium">{{ store.results.dryEye.details }}</p>       
            </div>
            </div>

            <!-- Contrast -->
            <div class="flex items-center justify-between">
                     <div>
                        <h3 class="font-bold text-slate-800 text-2xl mb-2">Kontrast Sezgirlik</h3>
                        <p class="text-lg text-slate-500">Pelli-Robson shkalasi bo'yicha</p>
                    </div>
                     <div class="text-right">
                        <div class="text-4xl font-extrabold text-indigo-600">
                             {{ store.results.contrastSensitivity.score || '-' }}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="bg-slate-50 p-6 text-center text-lg text-slate-500 border-t border-slate-100 font-medium">
                Ushbu natijalar tashxis hisoblanmaydi. Aniq tashxis uchun oftalmologga murojaat qiling.
            </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button @click="restart" class="bg-white border-2 border-slate-200 text-slate-700 hover:bg-slate-50 hover:border-slate-300 py-6 px-6 rounded-2xl font-bold flex items-center justify-center gap-3 text-lg transition">
                 <RefreshCw class="w-6 h-6" />
                 Qayta Topshirish
            </button>
            
            <button v-if="isTelegram" @click="sendToBot" 
              class="bg-brand-blue text-white hover:bg-blue-600 py-6 px-6 rounded-2xl font-bold shadow-lg shadow-blue-200 flex items-center justify-center gap-3 text-lg transition animate-pulse"
              :disabled="isSending">
                <component :is="isSending ? Loader2 : Send" class="w-6 h-6" :class="{ 'animate-spin': isSending }" />
                {{ isSending ? 'Yuborilmoqda...' : 'Botga Yuborish' }}
            </button>
            
            <button v-else class="bg-slate-800 text-white hover:bg-slate-700 py-6 px-6 rounded-2xl font-bold shadow-lg flex items-center justify-center gap-3 text-lg transition">
                 <Download class="w-6 h-6" />
                 PDF Yuklab Olish (Demo)
            </button>
        </div>
    </div>
  </div>
</template>
