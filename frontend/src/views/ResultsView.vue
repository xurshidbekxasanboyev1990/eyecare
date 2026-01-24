<script setup>
import { onMounted, ref, computed } from 'vue';
import { useEyeTestStore } from '../stores/useEyeTestStore';
import { useRouter } from 'vue-router';
import { Download, Share2, RefreshCw, Home, Loader2, Eye, ShieldCheck, MapPin, Phone, Clock, Stethoscope } from 'lucide-vue-next';
import { useStorage } from '@vueuse/core';
import html2pdf from 'html2pdf.js';

const store = useEyeTestStore();
const router = useRouter();
const isGeneratingPdf = ref(false);
const pdfContent = ref(null);

// Load doctors from admin settings
const doctors = useStorage('eyecareDoctors', []);
const showDoctorSettings = useStorage('eyecareShowDoctorOnResults', true);

const activeDoctors = computed(() => {
    return doctors.value.filter(d => d.isActive);
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

const analysis = computed(() => {
    // Generate Summary based on scores
    const issues = [];
    const r = store.results;
    
    // 1. Acuity
    if (r.visualAcuity.score && parseInt(r.visualAcuity.score.split('/')[1]) > 20) {
        issues.push("Uzoqni ko'rishda pasayish (Miyopiya)");
    }
    
    // 2. Color
    if (r.colorBlindness.score && (r.colorBlindness.score.includes('qiyinchilik') || r.colorBlindness.score.includes('buzilishi'))) {
        issues.push("Rang ajratishda og'ishlar");
    }
    
    // 3. Amsler
    if (r.amslerGrid.hasDistortion) {
        issues.push("Makula sohasida o'zgarishlar ehtimoli");
    }
    
    // 4. Astigmatism
    if (r.astigmatism.hasIssue) {
        issues.push("Astigmatizm alomatlari");
    }
    
    // 5. Dry Eye
    if (parseFloat(r.dryEye.score) < 10) {
        issues.push("Quruq ko'z sindromi");
    }
    
    if (issues.length === 0) {
        return "Sizning ko'z salomatligingiz a'lo darajada! Barcha testlar natijalari me'yor doirasida. Har 6 oyda profilaktik tekshiruvdan o'tish tavsiya etiladi.";
    } else {
        return `Dastlabki tahlil natijasida quyidagi ehtimoliy muammolar aniqlandi: ${issues.join(', ')}. Ushbu natijalar asosida oftalmolog ko'rigidan o'tish tavsiya etiladi.`;
    }
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 pb-20">
    <div ref="pdfContent" class="max-w-3xl mx-auto bg-white min-h-screen shadow-2xl relative">
        <!-- Header -->
        <div class="bg-slate-900 text-white p-8 relative overflow-hidden">
             <div class="relative z-10 flex justify-between items-start">
                 <div>
                     <h1 class="text-3xl font-extrabold mb-1">EyeCare</h1>
                     <p class="text-slate-400 font-medium">Professional Ko'z Tekshiruvi</p>
                 </div>
                 <div class="text-right">
                     <p class="text-sm opacity-60">Sana</p>
                     <p class="font-mono font-bold">{{ formatDate() }}</p>
                 </div>
             </div>
             
             <!-- Tahlil Badge -->
             <div class="mt-8 bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
                 <div class="flex items-start gap-3">
                     <div class="p-2 bg-blue-500 rounded-lg shrink-0">
                         <ShieldCheck class="w-6 h-6 text-white" />
                     </div>
                     <div>
                         <h3 class="font-bold text-lg mb-1">Tahlil Xulosasi</h3>
                         <p class="text-sm text-slate-200 leading-relaxed font-medium">
                             {{ analysis }}
                         </p>
                     </div>
                 </div>
             </div>
        </div>

        <!-- Results Grid -->
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
        
        <!-- Doctor Recommendation Section -->
        <div v-if="showDoctorSettings && activeDoctors.length > 0" class="bg-gradient-to-br from-blue-50 to-indigo-50 p-8 border-t border-slate-100">
            <div class="flex items-center gap-3 mb-6">
                <div class="p-3 bg-brand-blue rounded-xl">
                    <Stethoscope class="w-6 h-6 text-white" />
                </div>
                <div>
                    <h3 class="text-xl font-extrabold text-slate-800">Tavsiya Etilgan Shifokorlar</h3>
                    <p class="text-slate-500 font-medium">Professional tekshiruv uchun</p>
                </div>
            </div>
            
            <div class="space-y-4">
                <div 
                    v-for="doctor in activeDoctors" 
                    :key="doctor.id" 
                    class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100"
                >
                    <div class="flex flex-col md:flex-row gap-6">
                        <div class="w-24 h-24 bg-slate-100 rounded-2xl flex items-center justify-center shrink-0">
                            <Eye class="w-12 h-12 text-slate-400" />
                        </div>
                        <div class="flex-1">
                            <h4 class="text-2xl font-extrabold text-slate-800 mb-1">{{ doctor.name }}</h4>
                            <p class="text-brand-blue font-bold mb-4">{{ doctor.specialty }} | {{ doctor.experience }}</p>
                            
                            <div class="space-y-2 text-slate-600">
                                <div v-if="doctor.clinic || doctor.address" class="flex items-center gap-2">
                                    <MapPin class="w-4 h-4 text-slate-400" />
                                    <span>{{ doctor.clinic }}{{ doctor.clinic && doctor.address ? ', ' : '' }}{{ doctor.address }}</span>
                                </div>
                                <div v-if="doctor.phone" class="flex items-center gap-2">
                                    <Phone class="w-4 h-4 text-slate-400" />
                                    <span class="font-medium">{{ doctor.phone }}</span>
                                </div>
                                <div v-if="doctor.workHours" class="flex items-center gap-2">
                                    <Clock class="w-4 h-4 text-slate-400" />
                                    <span>{{ doctor.workHours }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div v-if="doctor.phone" class="mt-6 pt-6 border-t border-slate-100 flex flex-col sm:flex-row gap-3">
                        <a :href="'tel:' + doctor.phone.replace(/[^+\d]/g, '')" class="flex-1 py-3 bg-brand-blue hover:bg-blue-600 text-white font-bold rounded-xl text-center transition">
                            Qo'ng'iroq Qilish
                        </a>
                        <button class="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition">
                            Xaritada Ko'rish
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="bg-slate-900 text-white p-6 text-center">
            <p class="text-slate-400 font-medium mb-2">Ushbu natijalar tashxis hisoblanmaydi.</p>
            <p class="text-sm text-slate-500">Aniq tashxis uchun mutaxassis shifokorga murojaat qiling.</p>
        </div>
    </div>
    
    <!-- Action Buttons (Outside PDF) -->
    <div class="max-w-3xl mx-auto p-6 space-y-4">
        <button 
            @click="downloadPdf" 
            :disabled="isGeneratingPdf"
            class="w-full py-5 bg-gradient-to-r from-brand-blue to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-bold rounded-2xl shadow-xl shadow-blue-200 transition flex items-center justify-center gap-3 text-lg disabled:opacity-50"
        >
            <Loader2 v-if="isGeneratingPdf" class="w-6 h-6 animate-spin" />
            <Download v-else class="w-6 h-6" />
            {{ isGeneratingPdf ? 'PDF Tayyorlanmoqda...' : 'Natijalarni PDF Yuklash' }}
        </button>
        
        <div class="grid grid-cols-2 gap-4">
            <button @click="restart" class="py-4 bg-white border-2 border-slate-200 text-slate-700 hover:bg-slate-50 hover:border-slate-300 font-bold rounded-xl transition flex items-center justify-center gap-2">
                <RefreshCw class="w-5 h-5" />
                Qayta Topshirish
            </button>
            <button @click="router.push('/')" class="py-4 bg-white border-2 border-slate-200 text-slate-700 hover:bg-slate-50 hover:border-slate-300 font-bold rounded-xl transition flex items-center justify-center gap-2">
                <Home class="w-5 h-5" />
                Bosh Sahifa
            </button>
        </div>
    </div>
  </div>
</template>
