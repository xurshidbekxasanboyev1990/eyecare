import { createRouter, createWebHistory } from 'vue-router';
import ColorBlindnessView from '../views/ColorBlindnessView.vue';
import HomeView from '../views/HomeView.vue';
import ResultsView from '../views/ResultsView.vue';
import VisualAcuityView from '../views/VisualAcuityView.vue';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/test/visual-acuity',
            name: 'visual-acuity',
            component: VisualAcuityView
        },
        {
            path: '/test/color-blindness',
            name: 'color-blindness',
            component: ColorBlindnessView
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
            component: ResultsView
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
        },
        {
            path: '/admin',
            name: 'admin',
            component: () => import('../views/AdminView.vue')
        }
    ]
});

export default router;
