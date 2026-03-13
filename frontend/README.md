# 👁️ EyeCare Frontend - PWA

Ko'z salomatligi tekshirish platformasi uchun Progressive Web App.

## 🛠️ Texnologiyalar

- **Vue 3** - Composition API
- **Vite** - Build tool
- **Pinia** - State management
- **Vue Router** - Routing
- **TailwindCSS** - Styling
- **PWA** - Offline support

## 📦 O'rnatish

```bash
# Dependencies o'rnatish
npm install

# Development server
npm run dev

# Production build
npm run build

# Preview build
npm run preview
```

## 🌐 Kirish

- **Local:** http://localhost:5173
- **Network:** http://[your-ip]:5173

## 📁 Loyiha Strukturasi

```
frontend/
├── src/
│   ├── components/           # UI Komponentlar
│   │   ├── tests/            # Ko'z testlari
│   │   │   ├── VisualAcuityTest.vue
│   │   │   ├── ColorBlindnessTest.vue
│   │   │   ├── ContrastSensitivityTest.vue
│   │   │   ├── AstigmatismTest.vue
│   │   │   ├── AmslerGridTest.vue
│   │   │   ├── NearVisionTest.vue
│   │   │   ├── DryEyeTest.vue
│   │   │   ├── EyeFatigueTest.vue
│   │   │   ├── LightSensitivityTest.vue
│   │   │   └── PeripheralVisionTest.vue
│   │   ├── DistanceDetector.vue
│   │   ├── PdfGenerator.vue
│   │   └── ...
│   │
│   ├── views/                # Sahifalar
│   │   ├── HomeView.vue
│   │   ├── TestView.vue
│   │   ├── ResultsView.vue
│   │   ├── HistoryView.vue
│   │   ├── ProfileView.vue
│   │   ├── DoctorsView.vue
│   │   └── AdminView.vue
│   │
│   ├── stores/               # Pinia stores
│   │   ├── test.js
│   │   └── user.js
│   │
│   ├── router/               # Vue Router
│   │   └── index.js
│   │
│   ├── assets/               # Statik resurslar
│   │   └── css/
│   │
│   ├── App.vue               # Root component
│   └── main.js               # Entry point
│
├── public/                   # Public statik fayllar
│   ├── pwa-192x192.png
│   └── pwa-512x512.png
│
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## 🧪 Ko'z Testlari (10 ta)

| # | Test | Tavsif |
|---|------|--------|
| 1 | Ko'rish o'tkirligi | Snellen chart |
| 2 | Rang ko'rish | Ishihara plitalari |
| 3 | Kontrast sezgirligi | Turli kontrastlar |
| 4 | Astigmatizm | Radial chiziqlar |
| 5 | Amsler panjarasi | Makula degeneratsiyasi |
| 6 | Yaqin ko'rish | O'qish qobiliyati |
| 7 | Quruq ko'z | Simptomlar testi |
| 8 | Ko'z charchoqi | Charchoq darajasi |
| 9 | Yorug'lik sezgirligi | Fotofobiya |
| 10 | Periferik ko'rish | Yon ko'rish |

## 📱 PWA Xususiyatlari

- ✅ Offline ishlash
- ✅ Qurilmaga o'rnatish
- ✅ Push bildirishnomalar
- ✅ Kamera orqali masofa aniqlash
- ✅ Responsive dizayn

## 🔧 Konfiguratsiya

### Vite Config (`vite.config.js`)

```javascript
export default defineConfig({
  plugins: [vue(), VitePWA(...)],
  server: {
    host: '0.0.0.0',
    port: 5173
  }
})
```

### Tailwind Config (`tailwind.config.js`)

```javascript
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        primary: '#007AFF',
        secondary: '#5856D6'
      }
    }
  }
}
```

## 🔗 Backend API

Frontend quyidagi backend API ga ulanadi:

- **Development:** http://localhost:8000/api/v1
- **Production:** https://api.eyecare.uz/api/v1

## 📞 Aloqa

- Telegram: @eyecare_support
- Email: support@eyecare.uz

