<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
  number: { type: [Number, String], required: true },
  size: { type: Number, default: 300 }
});

const canvasRef = ref(null);

// Ishihara colors
const bgColors = ['#8FB996', '#6C8E74', '#A8D5BA', '#B5D8C1', '#D6EADF', '#90B493', '#7A9E7E']; // Greens/Teals
const numberColors = ['#E88D67', '#D9734E', '#F0A07C', '#D66D4F', '#C45A3E']; // Oranges/Reds

// Helper to get random color
const randomColor = (palette) => palette[Math.floor(Math.random() * palette.length)];

// Helper to check overlap
const checkOverlap = (circle, circles) => {
    for (let c of circles) {
        const dx = circle.x - c.x;
        const dy = circle.y - c.y;
        const distance = Math.sqrt(dx*dx + dy*dy);
        if (distance < circle.r + c.r + 1) return true; // +1 padding
    }
    return false;
};

// Main draw function
const drawPlate = () => {
    const canvas = canvasRef.value;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = props.size;
    const h = props.size;
    const radius = w / 2;
    
    // Resize canvas
    canvas.width = w;
    canvas.height = h;

    // 1. Create a mask for the number
    const maskCanvas = document.createElement('canvas');
    maskCanvas.width = w;
    maskCanvas.height = h;
    const maskCtx = maskCanvas.getContext('2d');
    maskCtx.font = `bold ${w * 0.55}px sans-serif`;
    maskCtx.textAlign = 'center';
    maskCtx.textBaseline = 'middle';
    maskCtx.fillStyle = '#000';
    maskCtx.fillText(props.number.toString(), w/2, h/2);
    
    // Get mask data
    const maskData = maskCtx.getImageData(0, 0, w, h).data;
    const isInsideNumber = (x, y) => {
        const idx = (Math.floor(y) * w + Math.floor(x)) * 4;
        return maskData[idx+3] > 100; // Alpha > 100
    };

    // 2. Circle Packing
    const circles = [];
    const minR = w * 0.015; // Increased min size slightly
    const maxR = w * 0.035; // Increased max size slightly
    
    // Reduce counts for performance on mobile
    const targetCircles = 600; 
    const maxAttempts = 3000;

    ctx.clearRect(0, 0, w, h);

    // Use a non-blocking generation if possible, but for simplicity here we just reduce the load
    // For very smooth UI, we should use requestAnimationFrame chaining, but reducing count is simpler safe fix first.
    
    let attempts = 0;
    while (circles.length < targetCircles && attempts < maxAttempts) {
        attempts++;
        const r = minR + Math.random() * (maxR - minR);
        // Random position in circle
        const angle = Math.random() * Math.PI * 2;
        // Weighted radius to distribute evenly
        const dist = Math.sqrt(Math.random()) * (radius - r);
        const x = w/2 + Math.cos(angle) * dist;
        const y = h/2 + Math.sin(angle) * dist;
        
        const circle = { x, y, r };
        
        if (!checkOverlap(circle, circles)) {
            // Decide color based on mask
            const isNumber = isInsideNumber(x, y);
            const color = isNumber ? randomColor(numberColors) : randomColor(bgColors);
            
            // Draw
            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.fill();
            
            circles.push({ ...circle, isNumber });
        }
    }
};

onMounted(drawPlate);
watch(() => [props.number, props.size], drawPlate);

</script>

<template>
  <canvas ref="canvasRef"></canvas>
</template>
