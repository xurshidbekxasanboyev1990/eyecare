<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { FaceMesh } from '@mediapipe/face_mesh';
import { Camera } from '@mediapipe/camera_utils';
import { Camera as CameraIcon, CheckCircle2, AlertTriangle, XCircle } from 'lucide-vue-next';

const props = defineProps({
  targetDistance: {
    type: Number,
    default: 40 // cm
  },
  tolerance: {
    type: Number,
    default: 5 // +/- cm
  }
});

const videoRef = ref(null);
const canvasRef = ref(null);
const distance = ref(0);
const isCameraActive = ref(false);
const permissionGranted = ref(false);
const isLoading = ref(true);

let camera = null;
let faceMesh = null;

// Approximate constants for distance calculation
// Average Inter-pupillary distance (IPD) is ~6.3cm (63mm)
const AVG_IPD_CM = 6.3;
// Focal length approximation (varies by device, but ~500-600 for 640px width is common for webcams)
// We might need a calibration factor.
const FOCAL_LENGTH = 600; 

const status = computed(() => {
    if (distance.value === 0) return 'no-face';
    const diff = distance.value - props.targetDistance;
    if (Math.abs(diff) <= props.tolerance) return 'good';
    if (diff > 0) return 'too-far';
    return 'too-close';
});

const statusColor = computed(() => {
    switch (status.value) {
        case 'good': return 'border-green-500 bg-green-500/10 text-green-700';
        case 'too-far': return 'border-orange-500 bg-orange-500/10 text-orange-700';
        case 'too-close': return 'border-red-500 bg-red-500/10 text-red-700';
        default: return 'border-slate-300 bg-slate-900/50 text-white';
    }
});

const message = computed(() => {
    switch (status.value) {
        case 'good': return "Masofa To'g'ri";
        case 'too-far': return "Yaqinroq keling";
        case 'too-close': return "Uzoqlashing";
        case 'no-face': return "Yuz topilmadi";
        default: return "Kamera ishlamoqda...";
    }
});

const onResults = (results) => {
    if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
        const landmarks = results.multiFaceLandmarks[0];
        
        // Key landmarks for eyes (iris centers are not always available in standard mesh, use pupil approximation)
        // Left Eye: 33, Right Eye: 263 (Corners) or 468, 473 (Iris - if refined mesh)
        // Using standard mesh corners for stability: 
        // Left Eye Outer: 33, Right Eye Outer: 263
        // Actually, let's use pupils if available, or inner corners: 133 (left inner), 362 (right inner)
        
        // Let's use Index 33 (Left Eye outer) and 263 (Right Eye outer) for "Outer Canthal Distance" ~9-10cm? No, that varies.
        // Let's use Mesh approx centers. 
        // 159 (Left Eye Top), 145 (Left Eye Bottom) -> Center approx
        // 386 (Right Eye Top), 374 (Right Eye Bottom) -> Center approx
        
        // Simple approach: Distance between landmark 33 and 263 (Outer corners)
        // Average outer canthal distance is approx 9-10cm? 
        // IPD (Pupil to pupil) is better. 
        // Left Pupil approx: 468, Right Pupil approx: 473 (These exist in refined mesh). 
        // If not refined, let's use 159/145 mid and 386/374 mid.
        
        // Let's try simple IPD approx using corners 33 and 263 which is wider.
        // Or assume 468/473 works (refine_landmarks: true).
        
        const leftEye = landmarks[468] || landmarks[159]; // Fallback if iris not present
        const rightEye = landmarks[473] || landmarks[386];
        
        if (leftEye && rightEye) {
            const dx = (rightEye.x - leftEye.x) * videoRef.value.videoWidth;
            const dy = (rightEye.y - leftEye.y) * videoRef.value.videoHeight;
            const pixelDist = Math.sqrt(dx*dx + dy*dy);
            
            // D = (F * Real_Width) / Pixel_Width
            // Adjust focal length or multiplier to match ~40cm on typical laptop/phone
            // Empirically, at 40cm, pixelDist might be around 100px on 640w.
            // 40 = (X * 6.3) / 100 => X = 635. So FOCAL_LENGTH ~640 is capable.
            
            const estimatedDist = (FOCAL_LENGTH * AVG_IPD_CM) / pixelDist;
            
            // Smoothing
            distance.value = Math.round(distance.value * 0.7 + estimatedDist * 0.3);
        }
    } else {
        // distance.value = 0; // Don't reset immediately to avoid flickering, maybe?
    }
    isLoading.value = false;
};

const initCamera = () => {
    faceMesh = new FaceMesh({locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
    }});
    
    faceMesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: true, // Needed for iris
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
    });
    
    faceMesh.onResults(onResults);
    
    if (videoRef.value) {
        camera = new Camera(videoRef.value, {
            onFrame: async () => {
                await faceMesh.send({image: videoRef.value});
            },
            width: 640,
            height: 480
        });
        
        camera.start()
            .then(() => {
                isCameraActive.value = true;
                permissionGranted.value = true;
            })
            .catch(err => {
                console.error("Camera error:", err);
                permissionGranted.value = false;
                isLoading.value = false;
            });
    }
};

onMounted(() => {
    initCamera();
});

onUnmounted(() => {
    if (camera) camera.stop();
    if (faceMesh) faceMesh.close();
});
</script>

<template>
  <!-- Loading State -->
  <div v-if="isLoading" class="fixed top-24 right-4 z-50 bg-white/80 backdrop-blur p-3 rounded-xl shadow-lg border border-slate-200 flex items-center gap-2">
      <div class="w-4 h-4 border-2 border-brand-blue border-t-transparent rounded-full animate-spin"></div>
      <span class="text-xs font-bold text-slate-600">Kamera yuklanmoqda...</span>
  </div>

  <!-- Main Interface -->
  <!-- We use opacity-0 instead of v-if/v-show so the video element exists in DOM and has dimensions for initialization -->
  <div class="fixed z-50 transition-all duration-300 pointer-events-none"
       :class="[
          'top-24 right-4 w-36 sm:w-48',
          permissionGranted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'
       ]"> 
       
       <div class="relative bg-white/90 backdrop-blur rounded-2xl overflow-hidden shadow-2xl border-4 transition-colors duration-300" 
            :class="statusColor">
            
            <video ref="videoRef" class="w-full aspect-[4/3] object-cover scale-x-[-1] opacity-80" autoplay playsinline></video>
            
            <div class="absolute inset-0 flex flex-col items-center justify-end pb-2 bg-gradient-to-t from-black/60 to-transparent">
                 <div class="flex items-center gap-1 mb-1">
                    <CheckCircle2 v-if="status === 'good'" class="w-5 h-5 text-green-400 animate-pulse" />
                    <AlertTriangle v-else-if="status === 'too-close' || status === 'too-far'" class="w-5 h-5 text-orange-400" />
                    <CameraIcon v-else class="w-5 h-5 text-white/70" />
                    
                    <span class="text-2xl font-black text-white font-mono tracking-tighter">
                        {{ distance > 0 ? distance : '--' }} <span class="text-xs font-sans font-medium opacity-80">sm</span>
                    </span>
                 </div>
                 
                 <div class="px-2 py-1 rounded-full text-[10px] uppercase font-bold tracking-widest text-white/90 bg-black/40 backdrop-blur-sm border border-white/10">
                     {{ message }}
                 </div>
            </div>
       </div>

       <!-- Target Indicator -->
       <div class="mt-2 flex justify-center">
          <div class="bg-slate-800 text-white text-[10px] py-1 px-3 rounded-full shadow-lg opacity-80 font-medium">
             Nominal: {{ targetDistance }} sm
          </div>
       </div>
  </div>
  
  <div v-if="!permissionGranted && !isLoading" class="fixed top-24 right-4 z-50">
       <div class="bg-red-50 border border-red-200 p-3 rounded-xl shadow-lg w-48 text-center">
            <XCircle class="w-6 h-6 text-red-500 mx-auto mb-2" />
            <p class="text-xs text-red-700 font-bold">Kamera ruxsati berilmadi</p>
       </div>
  </div>
</template>
