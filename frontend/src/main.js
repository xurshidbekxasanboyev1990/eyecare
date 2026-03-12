import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.config.errorHandler = (err) => {
    console.error("Global Error Handler:", err);
    // alert("Dasturda xatolik yuz berdi: " + err.message);
};

app.mount('#app')
