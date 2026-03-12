<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
  number: {
    type: [String, Number],
    required: true
  },
  // 'red-green' is standard. Can be expanded for tritanopia etc.
  type: {
    type: String,
    default: 'red-green' 
  },
  size: {
    type: Number,
    default: 300
  }
});

const canvasRef = ref(null);

// Palettes for Red-Green blindness (Protan/Deutero)
// People with color blindness see these as similar.
// Normal vision sees distinct colors.
const palettes = {
  'red-green': {
    figure: ['#E95D46', '#D6513B', '#C84C38', '#E66C55'], // Red/Orange shades
    background: ['#88A34F', '#7A9148', '#6D8240', '#95B258', '#A2C162'] // Green/Yellow-Green
  }
};

const randomColor = (colors) => colors[Math.floor(Math.random() * colors.length)];
const randomRange = (min, max) => Math.random() * (max - min) + min;

// Circle Packing Algorithm with Shape Detection
const generatePlate = () => {
    const canvas = canvasRef.value;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    
    const width = props.size;
    const height = props.size;
    const radius = width / 2;
    const centerX = width / 2;
    const centerY = height / 2;

    canvas.width = width;
    canvas.height = height;

    // 1. Draw the number temporarily to create a "map" of where the figure is
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = width;
    tempCanvas.height = height;
    const tCtx = tempCanvas.getContext('2d', { willReadFrequently: true });
    
    tCtx.font = `bold ${width * 0.6}px sans-serif`;
    tCtx.textAlign = 'center';
    tCtx.textBaseline = 'middle';
    tCtx.fillStyle = '#000000';
    tCtx.fillText(props.number.toString(), centerX, centerY + (width * 0.05)); // Slight offset

    // Get pixel data to check collision with text
    const imgData = tCtx.getImageData(0, 0, width, height).data;

    const isInsideText = (x, y) => {
        const index = (Math.floor(y) * width + Math.floor(x)) * 4;
        return imgData[index + 3] > 128; // Alpha > 128 means part of text
    };

    // 2. Generate Dots
    ctx.clearRect(0, 0, width, height);
    
    // Draw background circle (plate boundary) for visual guide if needed, usually invisible
    
    const dots = [];
    const minDotSize = width * 0.015;
    const maxDotSize = width * 0.045;
    const totalDots = 2500; // Attempt count

    const palette = palettes[props.type];

    for (let i = 0; i < totalDots; i++) {
        const r = randomRange(minDotSize, maxDotSize);
        // Random point in circle
        const angle = Math.random() * Math.PI * 2;
        const dist = Math.sqrt(Math.random()) * (radius - r - 5); // -5 padding
        const x = centerX + Math.cos(angle) * dist;
        const y = centerY + Math.sin(angle) * dist;

        // Overlap check
        let overlapping = false;
        for (const dot of dots) {
            const dx = dot.x - x;
            const dy = dot.y - y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < (dot.r + r + 1.5)) { // 1.5px spacing
                overlapping = true;
                break;
            }
        }

        if (!overlapping) {
            const isFigure = isInsideText(x, y);
            
            // Logic:
            // Normal plate: Figure is one color set, Background is another.
            // Determine color based on position
            const color = isFigure 
                ? randomColor(palette.figure) 
                : randomColor(palette.background);

            dots.push({ x, y, r, color });
        }
    }

    // 3. Render Dots
    dots.forEach(dot => {
        ctx.beginPath();
        ctx.arc(dot.x, dot.y, dot.r, 0, Math.PI * 2);
        ctx.fillStyle = dot.color;
        ctx.fill();
    });
};

onMounted(generatePlate);
watch(() => props.number, generatePlate);

</script>

<template>
  <div class="inline-block rounded-full bg-white shadow-inner p-4">
      <canvas ref="canvasRef" class="w-full h-full rounded-full"></canvas>
  </div>
</template>
