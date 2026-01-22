<script setup>
import { onMounted, ref } from 'vue';
import { useEyeTestStore } from '../stores/useEyeTestStore';
import { useRouter } from 'vue-router';
import { Download, Share2, RefreshCw, Home, Loader2, Eye, ShieldCheck } from 'lucide-vue-next';
import html2pdf from 'html2pdf.js';

const store = useEyeTestStore();
const router = useRouter();
const isGeneratingPdf = ref(false);
const pdfContent = ref(null);

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

const downloadPdf = () => {
    isGeneratingPdf.value = true;
    const element = pdfContent.value;
    
    // Hidden PDF container is displayed for capture
    element.style.display = 'block';

    const opt = {
        margin:       10,
        filename:     `EyeCare-Natijalar-${new Date().toISOString().slice(0,10)}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(element).save().then(() => {
        element.style.display = 'none';
        isGeneratingPdf.value = false;
    });
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-4">
    <div class="max-w-3xl mx-auto">
        <!-- PDF Template (Hidden by default) -->
        <div ref="pdfContent" style="display: none;" class="bg-white p-8 max-w-[210mm] mx-auto">
            <div class="flex items-center justify-between border-b-2 border-slate-800 pb-4 mb-8">
                <div class="flex items-center gap-3">
                    <div class="bg-brand-blue p-2 rounded-lg">
                         <Eye class="w-8 h-8 text-white" />
                    </div>
                    <div>
                        <h1 class="text-2xl font-extrabold text-slate-900">EyeCare AI</h1>
                        <p class="text-xs text-slate-500">Professional Ko'z Tekshiruvi</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="font-bold text-slate-900">Natijalar Varaqasi</p>
                    <p class="text-sm text-slate-500">{{ formatDate() }}</p>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4 mb-8">
                 <div class="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <p class="text-sm text-slate-500 mb-1">Ko'rish O'tkirligi</p>
                    <p class="text-3xl font-extrabold text-brand-blue">{{ store.results.visualAcuity.score || '-' }}</p>
                    <p class="text-xs text-slate-400 mt-1">Norma: 20/20</p>
                 </div>
                 <div class="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <p class="text-sm text-slate-500 mb-1">Rang Ajratish</p>
                    <p class="text-2xl font-extrabold" :class="store.results.colorBlindness.score === 'Normal' ? 'text-green-600' : 'text-orange-600'">
                        {{ store.results.colorBlindness.score || '-' }}
                    </p>
                 </div>
                 <div class="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <p class="text-sm text-slate-500 mb-1">Amsler Panjarasi</p>
                    <p class="text-xl font-bold text-slate-800">{{ store.results.amslerGrid.score || '-' }}</p>
                 </div>
                 <div class="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <p class="text-sm text-slate-500 mb-1">Astigmatizm</p>
                    <p class="text-xl font-bold text-slate-800">{{ store.results.astigmatism.score || '-' }}</p>
                 </div>
                 <div class="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <p class="text-sm text-slate-500 mb-1">Duoxrom</p>
                    <p class="text-xl font-bold text-slate-800">{{ store.results.duochrome.score || '-' }}</p>
                 </div>
                 <div class="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <p class="text-sm text-slate-500 mb-1">Yaqindan O'qish</p>
                    <p class="text-xl font-bold text-slate-800">{{ store.results.nearVision.score || '-' }}</p>
                 </div>
            </div>

             <div class="border-t border-slate-200 pt-6">
                <h3 class="font-bold text-slate-900 mb-4 flex items-center gap-2">
                    <ShieldCheck class="w-5 h-5 text-green-600" />
                    AI Xulosasi
                </h3>
                <p class="text-sm text-slate-600 leading-relaxed">
                    Ushbu test natijalari sun'iy intellekt algoritmlari asosida yaratildi. 
                    Agar natijalarda og'ishlar kuzatilsa, iltimos, chuqurlashtirilgan tekshiruv uchun oftalmolog shifokorga murojaat qiling.
                    <br><br>
                    <b>DIQQAT:</b> Ushbu hujjat tibbiy tashxis hisoblanmaydi.
                </p>
            </div>
            
            <div class="mt-12 text-center text-xs text-slate-400">
                &copy; 2026 EyeCare AI Project. Created by Xurshidbek Xasanboyev.
            </div>
        </div>

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
                         <p class="text-sm text-slate-400 font-medium">{{ typeof store.results.nearVision.details === 'string' && store.results.nearVision.details.includes(':') ? store.results.nearVision.details.split(': ')[1] : store.results.nearVision.details }}</p>
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
            
            <button @click="downloadPdf" class="bg-slate-800 text-white hover:bg-slate-700 py-6 px-6 rounded-2xl font-bold shadow-lg flex items-center justify-center gap-3 text-lg transition">
                 <Download class="w-6 h-6" />
                 PDF Yuklab Olish (Demo)
            </button>
        </div>
    </div>
  </div>
</template>
