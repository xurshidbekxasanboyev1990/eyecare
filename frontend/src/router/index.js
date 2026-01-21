import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: () => import('../views/HomeView.vue')
        },
        {
            path: '/test/visual-acuity',
            name: 'visual-acuity',
            component: () => import('../views/VisualAcuityView.vue')
        },
        {
            path: '/test/color-blindness',
            name: 'color-blindness',
            component: () => import('../views/ColorBlindnessView.vue')
        },
        {
            path: '/test/amsler',
            name: 'amsler',
            component: () => import('../views/AmslerGridView.vue')
        },
        {
            path: '/test/contrast',
            name: 'contrast',
            component: () => import('../views/ContrastSensitivityView.vue')
        },
        {
            path: '/results',
            name: 'results',
            component: () => import('../views/ResultsView.vue')
        },
        {
            path: '/test/astigmatism',
            name: 'astigmatism',
            component: () => import('../views/AstigmatismView.vue')
        },
        {
            path: '/test/duochrome',
            name: 'duochrome',
            component: () => import('../views/DuochromeView.vue')
        },
        {
            path: '/test/perimetry',
            name: 'perimetry',
            component: () => import('../views/PerimetryView.vue')
        },
        {
            path: '/test/near-vision',
            name: 'near-vision',
            component: () => import('../views/NearVisionView.vue')
        },
        {
            path: '/test/red-desaturation',
            name: 'red-desaturation',
            component: () => import('../views/RedDesaturationView.vue')
        },
        {
            path: '/test/dry-eye',
            name: 'dry-eye',
            component: () => import('../views/DryEyeView.vue')
        }
    ]
});

export default router;
