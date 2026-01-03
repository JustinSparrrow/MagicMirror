<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

const props = defineProps({ makeupData: Object });
const emit = defineEmits(['onProgress']);

const videoRef = ref(null);
const canvasRef = ref(null);
let faceLandmarker = null;
let animationId = null;
let partImages = {};

// 1. 预加载图片并上报进度
const preloadImages = () => {
  const baseUrl = "http://localhost:8000";
  const parts = ['left_eye_path', 'right_eye_path', 'left_eyebrow_path', 'right_eyebrow_path', 'lips_path', 'nose_path'];
  let loaded = 0;

  parts.forEach(key => {
    if (props.makeupData[key]) {
      const img = new Image();
      img.onload = () => {
        loaded++;
        emit('onProgress', { percent: 80 + Math.floor((loaded / parts.length) * 20), text: '正在渲染妆容图层...' });
      };
      img.src = baseUrl + props.makeupData[key];
      partImages[key] = img;
    }
  });
};

// 2. 初始化 MediaPipe (使用本地路径)
const initMediaPipe = async () => {
  emit('onProgress', { percent: 40, text: '启动 AI 追踪引擎...' });
  
  const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm"
  );
  
  emit('onProgress', { percent: 55, text: '正在加载本地模型文件...' });

  faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
    baseOptions: {
      // 核心修改：改为本地根路径，读取 public 文件夹下的文件
      modelAssetPath: `/face_landmarker.task`, 
      delegate: "GPU"
    },
    runningMode: "VIDEO",
    numFaces: 1
  });

  emit('onProgress', { percent: 75, text: '正在开启摄像头...' });
  renderLoop();
};

const renderLoop = () => {
  if (!videoRef.value || !canvasRef.value) return;
  const ctx = canvasRef.value.getContext("2d");

  const process = async () => {
    if (videoRef.value.readyState >= 2) {
      const results = faceLandmarker.detectForVideo(videoRef.value, Date.now());
      ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
      ctx.drawImage(videoRef.value, 0, 0, canvasRef.value.width, canvasRef.value.height);

      if (results.faceLandmarks && results.faceLandmarks.length > 0) {
        drawMakeup(ctx, results.faceLandmarks[0]);
      }
    }
    animationId = requestAnimationFrame(process);
  };
  process();
};

// 3. 动态缩放渲染算法
const drawMakeup = (ctx, landmarks) => {
  const mapping = {
    lips_path: { center: 13, wIdx: [61, 291], hIdx: [0, 17], scale: 1.1 },
    left_eye_path: { center: 468, wIdx: [33, 133], hIdx: [159, 145], scale: 1.1 },
    right_eye_path: { center: 473, wIdx: [362, 263], hIdx: [386, 374], scale: 1.1 },
    left_eyebrow_path: { center: 105, wIdx: [70, 107], hIdx: null, scale: 1.15, yShift: 0.05 },
    right_eyebrow_path: { center: 334, wIdx: [336, 285], hIdx: null, scale: 1.15, yShift: 0.05 },
    // 鼻子：中心点改为 6(鼻梁)，高度参考 168(眉心) 到 2(鼻底)
    nose_path: { center: 6, wIdx: [102, 331], hIdx: [168, 2], scale: 1.4, yShift: 0.15 }
  };

  Object.keys(mapping).forEach(key => {
    const img = partImages[key];
    if (!img || !img.complete) return;

    const cfg = mapping[key];
    const cp = landmarks[cfg.center];
    const wp1 = landmarks[cfg.wIdx[0]];
    const wp2 = landmarks[cfg.wIdx[1]];

    // 计算宽度
    const dx = (wp2.x - wp1.x) * canvasRef.value.width;
    const dy = (wp2.y - wp1.y) * canvasRef.value.height;
    const targetWidth = Math.sqrt(dx * dx + dy * dy) * cfg.scale;

    // 计算高度 (非等比缩放)
    let targetHeight;
    if (cfg.hIdx) {
      const hp1 = landmarks[cfg.hIdx[0]];
      const hp2 = landmarks[cfg.hIdx[1]];
      const hx = (hp2.x - hp1.x) * canvasRef.value.width;
      const hy = (hp2.y - hp1.y) * canvasRef.value.height;
      targetHeight = Math.sqrt(hx * hx + hy * hy) * cfg.scale;
    } else {
      targetHeight = targetWidth * (img.height / img.width);
    }

    const angle = Math.atan2(dy, dx);

    ctx.save();
    ctx.translate(cp.x * canvasRef.value.width, cp.y * canvasRef.value.height);
    ctx.rotate(angle);
    ctx.globalAlpha = 0.95; 
    
    const yOff = cfg.yShift ? targetHeight * cfg.yShift : 0;
    ctx.drawImage(img, -targetWidth / 2, -targetHeight / 2 + yOff, targetWidth, targetHeight);
    ctx.restore();
  });
};

onMounted(async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
    videoRef.value.srcObject = stream;
    preloadImages();
    await initMediaPipe();
    emit('onProgress', { percent: 100, text: '加载完成！' });
  } catch (err) {
    emit('onProgress', { percent: 0, text: '摄像头开启失败' });
  }
});

onUnmounted(() => {
  cancelAnimationFrame(animationId);
  if (videoRef.value?.srcObject) {
    videoRef.value.srcObject.getTracks().forEach(t => t.stop());
  }
});
</script>

<template>
  <div class="canvas-container">
    <video ref="videoRef" autoplay playsinline style="display: none;"></video>
    <canvas ref="canvasRef" width="640" height="480"></canvas>
  </div>
</template>

<style scoped>
.canvas-container { border-radius: 20px; overflow: hidden; background: #000; line-height: 0; }
canvas { width: 100%; transform: scaleX(-1); }
</style>