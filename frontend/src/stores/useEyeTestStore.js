import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useEyeTestStore = defineStore('eyeTest', () => {
    // State
    const results = ref({
        visualAcuity: { score: null, details: [] }, // 20/20, 20/40 etc.
        colorBlindness: { score: null, details: [] },
        amslerGrid: { hasDistortion: false, details: '' },
        contrastSensitivity: { score: null, details: [] },
        perimetry: { score: null, details: [] },
        astigmatism: { hasIssue: false, details: '' },
        duochrome: { preference: null, details: '' },
        nearVision: { score: null, details: [] },
        redDesaturation: { hasIssue: false, details: '' },
        dryEye: { holdTime: 0, details: '' },
    });

    const currentTestIndex = ref(0);
    const tests = [
        { id: 'visual-acuity', name: "Ko'rish O'Tkirligi", path: '/test/visual-acuity' },
        { id: 'color-blindness', name: "Rang Ajratish", path: '/test/color-blindness' },
        { id: 'amsler', name: "Amsler Panjarasi", path: '/test/amsler' },
        { id: 'contrast', name: "Kontrast Sezgirlik", path: '/test/contrast' },
        { id: 'astigmatism', name: "Astigmatizm", path: '/test/astigmatism' },
        { id: 'duochrome', name: "Duoxrom (Aniqlik)", path: '/test/duochrome' },
        { id: 'near-vision', name: "Yaqindan Ko'rish", path: '/test/near-vision' },
        { id: 'red-desaturation', name: "Qizil Rang (Nerv)", path: '/test/red-desaturation' },
        { id: 'dry-eye', name: "Quruq Ko'z (Blink)", path: '/test/dry-eye' },
        // { id: 'perimetry', name: "Perimetriya", path: '/test/perimetry' }, // Webda qiyin, lekin qo'shish mumkin
    ];

    // Actions
    function saveResult(testId, data) {
        if (results.value[testId]) {
            results.value[testId] = data;
        }
    }

    function resetTests() {
        results.value = {
            visualAcuity: { score: null, details: [] },
            colorBlindness: { score: null, details: [] },
            amslerGrid: { hasDistortion: false, details: '' },
            contrastSensitivity: { score: null, details: [] },
            perimetry: { score: null, details: [] }, // Added state here too
            astigmatism: { hasIssue: false, details: '' },
            duochrome: { preference: null, details: '' },
            nearVision: { score: null, details: [] },
            redDesaturation: { hasIssue: false, details: '' },
            dryEye: { holdTime: 0, details: '' },
        };
        currentTestIndex.value = 0;
    }

    return {
        pxPerCm,
        setCalibration,
        results,
        tests,
        currentTestIndex,
        saveResult,
        resetTests
    };
});
