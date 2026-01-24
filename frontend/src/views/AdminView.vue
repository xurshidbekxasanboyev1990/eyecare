<script setup>
import { ref, reactive, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useStorage } from '@vueuse/core';
import { 
    Settings, Eye, User, Phone, MapPin, Clock, Save, ArrowLeft, 
    Stethoscope, Bell, Palette, Monitor, Shield, Database, 
    ToggleLeft, ToggleRight, ChevronRight, CheckCircle, Camera,
    FileText, Globe, MessageSquare, Smartphone, Trash2, Plus, Edit3
} from 'lucide-vue-next';

const router = useRouter();

// Admin Authentication
const isAuthenticated = ref(false);
const adminPassword = ref('');
const loginError = ref('');
const ADMIN_PASSWORD = 'eyecare2026'; // Default password

const login = () => {
    if (adminPassword.value === ADMIN_PASSWORD) {
        isAuthenticated.value = true;
        loginError.value = '';
    } else {
        loginError.value = "Noto'g'ri parol";
    }
};

// Settings with persistence
const appSettings = useStorage('eyecareAppSettings', {
    // General
    appName: 'EyeCare',
    appVersion: '1.2',
    language: 'uz',
    
    // Distance Check
    enableDistanceCheck: true,
    defaultDistance: 45,
    distanceTolerance: 5,
    
    // Tests
    enabledTests: {
        visualAcuity: true,
        colorBlindness: true,
        amsler: true,
        contrast: true,
        astigmatism: true,
        duochrome: true,
        nearVision: true,
        redDesaturation: true,
        perimetry: true,
        dryEye: true
    },
    
    // Test Distances
    testDistances: {
        visualAcuity: 50,
        nearVision: 35,
        amsler: 30,
        default: 45
    },
    
    // UI Settings
    theme: 'light',
    primaryColor: '#007AFF',
    showProgressBar: true,
    showTestCounter: true,
    
    // PDF Settings
    pdfEnabled: true,
    clinicLogo: '',
    
    // Notifications
    enableNotifications: false,
    reminderDays: 180
});

const doctors = useStorage('eyecareDoctors', [
    {
        id: 1,
        name: 'Dr. Abdullayev Jasur',
        specialty: 'Oftalmolog',
        experience: '15 yillik tajriba',
        clinic: '"Salomatlik" Klinikasi',
        address: 'Toshkent sh., Chilonzor t., 12-mavze',
        phone: '+998 71 123-45-67',
        workHours: 'Dush-Juma: 09:00 - 18:00',
        isActive: true
    }
]);

const showDoctorSettings = useStorage('eyecareShowDoctorOnResults', true);

// Doctor management
const editingDoctor = ref(null);
const showDoctorForm = ref(false);
const newDoctor = ref({
    name: '',
    specialty: 'Oftalmolog',
    experience: '',
    clinic: '',
    address: '',
    phone: '',
    workHours: 'Dush-Juma: 09:00 - 18:00',
    isActive: true
});

const addDoctor = () => {
    const doctor = {
        ...newDoctor.value,
        id: Date.now()
    };
    doctors.value.push(doctor);
    resetDoctorForm();
};

const editDoctor = (doctor) => {
    editingDoctor.value = { ...doctor };
    showDoctorForm.value = true;
};

const updateDoctor = () => {
    const index = doctors.value.findIndex(d => d.id === editingDoctor.value.id);
    if (index !== -1) {
        doctors.value[index] = { ...editingDoctor.value };
    }
    editingDoctor.value = null;
    showDoctorForm.value = false;
};

const deleteDoctor = (id) => {
    if (confirm("Bu shifokorni o'chirishni tasdiqlaysizmi?")) {
        doctors.value = doctors.value.filter(d => d.id !== id);
    }
};

const toggleDoctorActive = (id) => {
    const doctor = doctors.value.find(d => d.id === id);
    if (doctor) {
        doctor.isActive = !doctor.isActive;
    }
};

const resetDoctorForm = () => {
    newDoctor.value = {
        name: '',
        specialty: 'Oftalmolog',
        experience: '',
        clinic: '',
        address: '',
        phone: '',
        workHours: 'Dush-Juma: 09:00 - 18:00',
        isActive: true
    };
    showDoctorForm.value = false;
    editingDoctor.value = null;
};

const botSettings = useStorage('eyecareBotSettings', {
    // Telegram Bot
    enabled: false,
    botToken: '',
    adminChatId: '',
    welcomeMessage: "Assalomu alaykum! EyeCare ko'z tekshiruvi botiga xush kelibsiz.",
    
    // Auto-responses
    autoReply: true,
    replyDelay: 1000,
    
    // Features
    sendResults: true,
    sendReminders: false,
    reminderTime: '09:00',
    
    // Commands
    commands: {
        start: true,
        help: true,
        test: true,
        results: true,
        doctor: true
    }
});

// Active tab
const activeTab = ref('general');

const tabs = [
    { id: 'general', name: 'Umumiy', icon: Settings },
    { id: 'tests', name: 'Testlar', icon: Eye },
    { id: 'distance', name: 'Masofa', icon: Camera },
    { id: 'doctor', name: 'Shifokor', icon: Stethoscope },
    { id: 'ui', name: 'Interfeys', icon: Palette },
    { id: 'pdf', name: 'PDF Hisobot', icon: FileText },
    { id: 'bot', name: 'Telegram Bot', icon: MessageSquare },
];

const testNames = {
    visualAcuity: "Ko'rish O'tkirligi",
    colorBlindness: "Rang Ajratish",
    amsler: "Amsler Panjarasi",
    contrast: "Kontrast Sezgirlik",
    astigmatism: "Astigmatizm",
    duochrome: "Duoxrom",
    nearVision: "Yaqindan Ko'rish",
    redDesaturation: "Qizil Desaturatsiya",
    perimetry: "Perimetriya",
    dryEye: "Quruq Ko'z"
};

const saved = ref(false);
const saveSettings = () => {
    saved.value = true;
    setTimeout(() => saved.value = false, 2000);
};

const enabledTestsCount = () => {
    return Object.values(appSettings.value.enabledTests).filter(v => v).length;
};
</script>

<template>
  <!-- Login Screen -->
  <div v-if="!isAuthenticated" class="min-h-screen bg-slate-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl p-8 w-full max-w-sm">
        <div class="text-center mb-8">
            <div class="w-16 h-16 bg-brand-blue rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Shield class="w-8 h-8 text-white" />
            </div>
            <h1 class="text-2xl font-extrabold text-slate-800">Admin Panel</h1>
            <p class="text-slate-500 mt-2">Sozlamalarga kirish uchun parolni kiriting</p>
        </div>
        
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">Parol</label>
                <input 
                    v-model="adminPassword"
                    type="password"
                    placeholder="••••••••"
                    class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none transition"
                    @keyup.enter="login"
                />
            </div>
            
            <p v-if="loginError" class="text-red-500 text-sm font-medium">{{ loginError }}</p>
            
            <button 
                @click="login"
                class="w-full py-3 bg-brand-blue hover:bg-blue-600 text-white font-bold rounded-xl transition"
            >
                Kirish
            </button>
            
            <button 
                @click="router.push('/')"
                class="w-full py-3 text-slate-500 hover:text-slate-700 font-medium transition flex items-center justify-center gap-2"
            >
                <ArrowLeft class="w-4 h-4" />
                Bosh sahifaga qaytish
            </button>
        </div>
    </div>
  </div>

  <!-- Admin Panel -->
  <div v-else class="min-h-screen bg-slate-100">
    <!-- Header -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <div class="flex items-center gap-4">
                <button @click="router.push('/')" class="p-2 hover:bg-slate-100 rounded-lg transition">
                    <ArrowLeft class="w-5 h-5 text-slate-600" />
                </button>
                <div>
                    <h1 class="text-xl font-extrabold text-slate-800">Admin Panel</h1>
                    <p class="text-sm text-slate-500">EyeCare sozlamalari</p>
                </div>
            </div>
            
            <button 
                @click="saveSettings"
                class="px-6 py-2.5 bg-brand-blue hover:bg-blue-600 text-white font-bold rounded-xl transition flex items-center gap-2"
            >
                <Save class="w-4 h-4" />
                <span v-if="saved">Saqlandi!</span>
                <span v-else>Saqlash</span>
            </button>
        </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 py-8 flex gap-8">
        <!-- Sidebar -->
        <aside class="w-64 shrink-0">
            <nav class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                <button 
                    v-for="tab in tabs" 
                    :key="tab.id"
                    @click="activeTab = tab.id"
                    class="w-full px-4 py-3 flex items-center gap-3 text-left transition border-l-4"
                    :class="activeTab === tab.id 
                        ? 'bg-blue-50 border-brand-blue text-brand-blue' 
                        : 'border-transparent hover:bg-slate-50 text-slate-600'"
                >
                    <component :is="tab.icon" class="w-5 h-5" />
                    <span class="font-medium">{{ tab.name }}</span>
                </button>
            </nav>
        </aside>

        <!-- Content -->
        <main class="flex-1">
            <!-- General Settings -->
            <div v-if="activeTab === 'general'" class="space-y-6">
                <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                    <h2 class="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <Settings class="w-5 h-5 text-brand-blue" />
                        Umumiy Sozlamalar
                    </h2>
                    
                    <div class="grid gap-6">
                        <div>
                            <label class="block text-sm font-bold text-slate-700 mb-2">Ilova nomi</label>
                            <input 
                                v-model="appSettings.appName"
                                type="text"
                                class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                            />
                        </div>
                        
                        <div>
                            <label class="block text-sm font-bold text-slate-700 mb-2">Versiya</label>
                            <input 
                                v-model="appSettings.appVersion"
                                type="text"
                                class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                            />
                        </div>
                        
                        <div>
                            <label class="block text-sm font-bold text-slate-700 mb-2">Til</label>
                            <select 
                                v-model="appSettings.language"
                                class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                            >
                                <option value="uz">O'zbekcha</option>
                                <option value="ru">Русский</option>
                                <option value="en">English</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tests Settings -->
            <div v-if="activeTab === 'tests'" class="space-y-6">
                <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                    <h2 class="text-lg font-bold text-slate-800 mb-2 flex items-center gap-2">
                        <Eye class="w-5 h-5 text-brand-blue" />
                        Testlarni Boshqarish
                    </h2>
                    <p class="text-slate-500 mb-6">Faol testlar: {{ enabledTestsCount() }}/10</p>
                    
                    <div class="space-y-3">
                        <div 
                            v-for="(enabled, key) in appSettings.enabledTests" 
                            :key="key"
                            class="flex items-center justify-between p-4 bg-slate-50 rounded-xl"
                        >
                            <span class="font-medium text-slate-700">{{ testNames[key] }}</span>
                            <button 
                                @click="appSettings.enabledTests[key] = !appSettings.enabledTests[key]"
                                class="transition"
                            >
                                <ToggleRight v-if="appSettings.enabledTests[key]" class="w-8 h-8 text-brand-blue" />
                                <ToggleLeft v-else class="w-8 h-8 text-slate-300" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Distance Settings -->
            <div v-if="activeTab === 'distance'" class="space-y-6">
                <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                    <h2 class="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <Camera class="w-5 h-5 text-brand-blue" />
                        Masofa Nazorati
                    </h2>
                    
                    <div class="space-y-6">
                        <div class="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                            <div>
                                <h3 class="font-bold text-slate-800">Masofa tekshiruvini yoqish</h3>
                                <p class="text-sm text-slate-500">Kamera orqali masofani nazorat qilish</p>
                            </div>
                            <button @click="appSettings.enableDistanceCheck = !appSettings.enableDistanceCheck">
                                <ToggleRight v-if="appSettings.enableDistanceCheck" class="w-8 h-8 text-brand-blue" />
                                <ToggleLeft v-else class="w-8 h-8 text-slate-300" />
                            </button>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-bold text-slate-700 mb-2">Standart masofa (sm)</label>
                            <input 
                                v-model.number="appSettings.defaultDistance"
                                type="number"
                                class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                            />
                        </div>
                        
                        <div>
                            <label class="block text-sm font-bold text-slate-700 mb-2">Tolerans (+/- sm)</label>
                            <input 
                                v-model.number="appSettings.distanceTolerance"
                                type="number"
                                class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                            />
                        </div>
                        
                        <div class="border-t pt-6">
                            <h3 class="font-bold text-slate-800 mb-4">Testlar uchun maxsus masofalar</h3>
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-sm font-medium text-slate-600 mb-1">Ko'rish o'tkirligi</label>
                                    <input 
                                        v-model.number="appSettings.testDistances.visualAcuity"
                                        type="number"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                                    />
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-slate-600 mb-1">Yaqindan ko'rish</label>
                                    <input 
                                        v-model.number="appSettings.testDistances.nearVision"
                                        type="number"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                                    />
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-slate-600 mb-1">Amsler</label>
                                    <input 
                                        v-model.number="appSettings.testDistances.amsler"
                                        type="number"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                                    />
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-slate-600 mb-1">Boshqalar (default)</label>
                                    <input 
                                        v-model.number="appSettings.testDistances.default"
                                        type="number"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Doctor Settings -->
            <div v-if="activeTab === 'doctor'" class="space-y-6">
                <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                    <div class="flex items-center justify-between mb-6">
                        <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
                            <Stethoscope class="w-5 h-5 text-brand-blue" />
                            Tavsiya Etilgan Shifokorlar
                        </h2>
                        <button 
                            @click="showDoctorForm = true; editingDoctor = null"
                            class="px-4 py-2 bg-brand-blue hover:bg-blue-600 text-white font-bold rounded-xl transition flex items-center gap-2"
                        >
                            <Plus class="w-4 h-4" />
                            Yangi Qo'shish
                        </button>
                    </div>
                    
                    <div class="flex items-center justify-between p-4 bg-slate-50 rounded-xl mb-6">
                        <div>
                            <h3 class="font-bold text-slate-800">Natijalarda ko'rsatish</h3>
                            <p class="text-sm text-slate-500">Shifokor ma'lumotlarini natijalar sahifasida ko'rsatish</p>
                        </div>
                        <button @click="showDoctorSettings = !showDoctorSettings">
                            <ToggleRight v-if="showDoctorSettings" class="w-8 h-8 text-brand-blue" />
                            <ToggleLeft v-else class="w-8 h-8 text-slate-300" />
                        </button>
                    </div>

                    <!-- Doctor List -->
                    <div class="space-y-3">
                        <div 
                            v-for="doctor in doctors" 
                            :key="doctor.id"
                            class="p-4 border rounded-xl transition"
                            :class="doctor.isActive ? 'border-green-200 bg-green-50/50' : 'border-slate-200 bg-slate-50 opacity-60'"
                        >
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 mb-1">
                                        <h3 class="font-bold text-slate-800">{{ doctor.name }}</h3>
                                        <span v-if="doctor.isActive" class="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-bold rounded-full">Faol</span>
                                    </div>
                                    <p class="text-sm text-brand-blue font-medium">{{ doctor.specialty }} | {{ doctor.experience }}</p>
                                    <p class="text-sm text-slate-500 mt-1">{{ doctor.clinic }}</p>
                                    <div class="flex items-center gap-4 mt-2 text-sm text-slate-600">
                                        <span class="flex items-center gap-1">
                                            <MapPin class="w-3 h-3" />
                                            {{ doctor.address }}
                                        </span>
                                    </div>
                                    <div class="flex items-center gap-4 mt-1 text-sm text-slate-600">
                                        <span class="flex items-center gap-1">
                                            <Phone class="w-3 h-3" />
                                            {{ doctor.phone }}
                                        </span>
                                        <span class="flex items-center gap-1">
                                            <Clock class="w-3 h-3" />
                                            {{ doctor.workHours }}
                                        </span>
                                    </div>
                                </div>
                                <div class="flex items-center gap-2">
                                    <button 
                                        @click="toggleDoctorActive(doctor.id)"
                                        class="p-2 hover:bg-slate-200 rounded-lg transition"
                                        :title="doctor.isActive ? 'Faolsizlantirish' : 'Faollashtirish'"
                                    >
                                        <ToggleRight v-if="doctor.isActive" class="w-5 h-5 text-green-600" />
                                        <ToggleLeft v-else class="w-5 h-5 text-slate-400" />
                                    </button>
                                    <button 
                                        @click="editDoctor(doctor)"
                                        class="p-2 hover:bg-blue-100 rounded-lg transition"
                                    >
                                        <Edit3 class="w-5 h-5 text-blue-600" />
                                    </button>
                                    <button 
                                        @click="deleteDoctor(doctor.id)"
                                        class="p-2 hover:bg-red-100 rounded-lg transition"
                                    >
                                        <Trash2 class="w-5 h-5 text-red-500" />
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div v-if="doctors.length === 0" class="text-center py-12 text-slate-400">
                            <Stethoscope class="w-12 h-12 mx-auto mb-4 opacity-50" />
                            <p>Hech qanday shifokor qo'shilmagan</p>
                        </div>
                    </div>
                </div>

                <!-- Add/Edit Doctor Modal -->
                <div v-if="showDoctorForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
                    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
                        <div class="p-6 border-b border-slate-100">
                            <h3 class="text-xl font-bold text-slate-800">
                                {{ editingDoctor ? "Shifokorni Tahrirlash" : "Yangi Shifokor Qo'shish" }}
                            </h3>
                        </div>
                        
                        <div class="p-6 space-y-4">
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-sm font-bold text-slate-700 mb-2">Ism *</label>
                                    <input 
                                        v-model="editingDoctor ? editingDoctor.name : newDoctor.name"
                                        type="text"
                                        placeholder="Dr. Ism Familiya"
                                        class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                                    />
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-700 mb-2">Mutaxassislik</label>
                                    <input 
                                        v-model="editingDoctor ? editingDoctor.specialty : newDoctor.specialty"
                                        type="text"
                                        placeholder="Oftalmolog"
                                        class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                                    />
                                </div>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-2">Tajriba</label>
                                <input 
                                    v-model="editingDoctor ? editingDoctor.experience : newDoctor.experience"
                                    type="text"
                                    placeholder="10 yillik tajriba"
                                    class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                                />
                            </div>
                            
                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-2">Klinika nomi</label>
                                <input 
                                    v-model="editingDoctor ? editingDoctor.clinic : newDoctor.clinic"
                                    type="text"
                                    placeholder="Klinika nomi"
                                    class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                                />
                            </div>
                            
                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-2">Manzil</label>
                                <input 
                                    v-model="editingDoctor ? editingDoctor.address : newDoctor.address"
                                    type="text"
                                    placeholder="Shahar, tuman, manzil"
                                    class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                                />
                            </div>
                            
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-sm font-bold text-slate-700 mb-2">Telefon</label>
                                    <input 
                                        v-model="editingDoctor ? editingDoctor.phone : newDoctor.phone"
                                        type="text"
                                        placeholder="+998 XX XXX-XX-XX"
                                        class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                                    />
                                </div>
                                <div>
                                    <label class="block text-sm font-bold text-slate-700 mb-2">Ish vaqti</label>
                                    <input 
                                        v-model="editingDoctor ? editingDoctor.workHours : newDoctor.workHours"
                                        type="text"
                                        placeholder="Dush-Juma: 09:00 - 18:00"
                                        class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                                    />
                                </div>
                            </div>
                        </div>
                        
                        <div class="p-6 border-t border-slate-100 flex gap-3">
                            <button 
                                @click="resetDoctorForm"
                                class="flex-1 py-3 border border-slate-200 text-slate-700 font-bold rounded-xl hover:bg-slate-50 transition"
                            >
                                Bekor qilish
                            </button>
                            <button 
                                @click="editingDoctor ? updateDoctor() : addDoctor()"
                                class="flex-1 py-3 bg-brand-blue hover:bg-blue-600 text-white font-bold rounded-xl transition"
                            >
                                {{ editingDoctor ? "Saqlash" : "Qo'shish" }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- UI Settings -->
            <div v-if="activeTab === 'ui'" class="space-y-6">
                <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                    <h2 class="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <Palette class="w-5 h-5 text-brand-blue" />
                        Interfeys Sozlamalari
                    </h2>
                    
                    <div class="space-y-6">
                        <div>
                            <label class="block text-sm font-bold text-slate-700 mb-2">Mavzu</label>
                            <select 
                                v-model="appSettings.theme"
                                class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                            >
                                <option value="light">Yorug'</option>
                                <option value="dark">Qorong'i</option>
                                <option value="auto">Avtomatik</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-bold text-slate-700 mb-2">Asosiy rang</label>
                            <div class="flex items-center gap-4">
                                <input 
                                    v-model="appSettings.primaryColor"
                                    type="color"
                                    class="w-12 h-12 rounded-lg cursor-pointer border-0"
                                />
                                <input 
                                    v-model="appSettings.primaryColor"
                                    type="text"
                                    class="flex-1 px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none font-mono"
                                />
                            </div>
                        </div>
                        
                        <div class="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                            <div>
                                <h3 class="font-bold text-slate-800">Progress bar ko'rsatish</h3>
                                <p class="text-sm text-slate-500">Yuqorida test jarayonini ko'rsatish</p>
                            </div>
                            <button @click="appSettings.showProgressBar = !appSettings.showProgressBar">
                                <ToggleRight v-if="appSettings.showProgressBar" class="w-8 h-8 text-brand-blue" />
                                <ToggleLeft v-else class="w-8 h-8 text-slate-300" />
                            </button>
                        </div>
                        
                        <div class="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                            <div>
                                <h3 class="font-bold text-slate-800">Test hisoblagichini ko'rsatish</h3>
                                <p class="text-sm text-slate-500">"Test: 3/10" ko'rinishida</p>
                            </div>
                            <button @click="appSettings.showTestCounter = !appSettings.showTestCounter">
                                <ToggleRight v-if="appSettings.showTestCounter" class="w-8 h-8 text-brand-blue" />
                                <ToggleLeft v-else class="w-8 h-8 text-slate-300" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- PDF Settings -->
            <div v-if="activeTab === 'pdf'" class="space-y-6">
                <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                    <h2 class="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <FileText class="w-5 h-5 text-brand-blue" />
                        PDF Hisobot Sozlamalari
                    </h2>
                    
                    <div class="space-y-6">
                        <div class="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                            <div>
                                <h3 class="font-bold text-slate-800">PDF yuklashni yoqish</h3>
                                <p class="text-sm text-slate-500">Natijalarni PDF formatida yuklash imkoniyati</p>
                            </div>
                            <button @click="appSettings.pdfEnabled = !appSettings.pdfEnabled">
                                <ToggleRight v-if="appSettings.pdfEnabled" class="w-8 h-8 text-brand-blue" />
                                <ToggleLeft v-else class="w-8 h-8 text-slate-300" />
                            </button>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-bold text-slate-700 mb-2">Klinika logotipi (URL)</label>
                            <input 
                                v-model="appSettings.clinicLogo"
                                type="text"
                                placeholder="https://example.com/logo.png"
                                class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bot Settings -->
            <div v-if="activeTab === 'bot'" class="space-y-6">
                <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                    <h2 class="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <MessageSquare class="w-5 h-5 text-brand-blue" />
                        Telegram Bot Sozlamalari
                    </h2>
                    
                    <div class="space-y-6">
                        <div class="flex items-center justify-between p-4 bg-blue-50 rounded-xl border border-blue-100">
                            <div>
                                <h3 class="font-bold text-slate-800">Telegram botni yoqish</h3>
                                <p class="text-sm text-slate-500">Bot orqali test natijalarini yuborish</p>
                            </div>
                            <button @click="botSettings.enabled = !botSettings.enabled">
                                <ToggleRight v-if="botSettings.enabled" class="w-8 h-8 text-brand-blue" />
                                <ToggleLeft v-else class="w-8 h-8 text-slate-300" />
                            </button>
                        </div>
                        
                        <div v-if="botSettings.enabled" class="space-y-4 pt-4 border-t">
                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-2">Bot Token</label>
                                <input 
                                    v-model="botSettings.botToken"
                                    type="password"
                                    placeholder="123456789:ABCdefGHI..."
                                    class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none font-mono"
                                />
                                <p class="text-xs text-slate-400 mt-1">@BotFather dan olingan token</p>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-2">Admin Chat ID</label>
                                <input 
                                    v-model="botSettings.adminChatId"
                                    type="text"
                                    placeholder="123456789"
                                    class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none font-mono"
                                />
                            </div>
                            
                            <div>
                                <label class="block text-sm font-bold text-slate-700 mb-2">Xush kelibsiz xabari</label>
                                <textarea 
                                    v-model="botSettings.welcomeMessage"
                                    rows="3"
                                    class="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none resize-none"
                                ></textarea>
                            </div>
                            
                            <div class="grid grid-cols-2 gap-4 pt-4">
                                <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                                    <span class="text-sm font-medium text-slate-700">Natijalarni yuborish</span>
                                    <button @click="botSettings.sendResults = !botSettings.sendResults">
                                        <ToggleRight v-if="botSettings.sendResults" class="w-6 h-6 text-brand-blue" />
                                        <ToggleLeft v-else class="w-6 h-6 text-slate-300" />
                                    </button>
                                </div>
                                
                                <div class="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                                    <span class="text-sm font-medium text-slate-700">Eslatmalar</span>
                                    <button @click="botSettings.sendReminders = !botSettings.sendReminders">
                                        <ToggleRight v-if="botSettings.sendReminders" class="w-6 h-6 text-brand-blue" />
                                        <ToggleLeft v-else class="w-6 h-6 text-slate-300" />
                                    </button>
                                </div>
                            </div>
                            
                            <div class="pt-4 border-t">
                                <h4 class="font-bold text-slate-800 mb-3">Bot buyruqlari</h4>
                                <div class="grid grid-cols-3 gap-2">
                                    <div v-for="(enabled, cmd) in botSettings.commands" :key="cmd" 
                                         class="flex items-center gap-2 p-2 bg-slate-50 rounded-lg">
                                        <input type="checkbox" v-model="botSettings.commands[cmd]" class="rounded" />
                                        <span class="text-sm font-mono text-slate-600">/{{ cmd }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
  </div>
</template>
