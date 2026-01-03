import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import uuid
import hashlib
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# 配置日志，确保在控制台能看到 INFO 级别的输出
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI_Service")

# 1. 初始化线程池
executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() + 1)

# 2. 全局单例
detector = None

# 3. 关键点配置
PARTS_CONFIG = {
    "left_eye": [33, 133, 160, 159, 158, 144, 145, 153, 154, 155],
    "right_eye": [362, 263, 387, 386, 385, 373, 374, 380, 381, 382],
    "left_eyebrow": [70, 63, 105, 66, 107, 55, 65, 52, 53, 46],
    "right_eyebrow": [336, 296, 334, 293, 300, 276, 283, 282, 295, 285],
    "lips": [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308],
    "nose": [1, 2, 98, 327, 168]
}

def init_detector():
    global detector
    model_path = 'face_landmarker.task'
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        num_faces=1
    )
    detector = vision.FaceLandmarker.create_from_options(options)
    logger.info("MediaPipe FaceLandmarker 单例初始化完成")

def _sync_process_logic(img_bytes: bytes, upload_root: str):
    """
    同步处理逻辑：运行在线程池中
    """
    # 计算图像 MD5
    img_md5 = hashlib.md5(img_bytes).hexdigest()
    cache_rel_dir = os.path.join("makeup_parts", img_md5)
    cache_full_dir = os.path.join(upload_root, cache_rel_dir)

    # --- 核心：缓存校验逻辑 ---
    if os.path.exists(cache_full_dir):
        logger.info(f"🚀 [Cache Hit] 命中缓存，直接返回路径: {img_md5}")
        return {
            name: f"/static/makeup_parts/{img_md5}/{name}.png".replace("\\", "/") 
            for name in PARTS_CONFIG.keys()
        }, img_md5

    # --- 缓存未命中，开始 AI 处理 ---
    logger.info(f"⚙️ [Processing] 正在处理新图片，MD5: {img_md5}")
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None: return None
    
    h, w, _ = img.shape
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    res = detector.detect(mp_image)
    
    if not res.face_landmarks:
        logger.warning(f"❌ [Failed] 未能识别到面部: {img_md5}")
        return None

    face_landmarks = res.face_landmarks[0]
    os.makedirs(cache_full_dir, exist_ok=True)

    result_urls = {}
    for part_name, indices in PARTS_CONFIG.items():
        # 1. 创建 Mask
        mask = np.zeros((h, w), dtype=np.uint8)
        points = np.array([(int(face_landmarks[idx].x * w), int(face_landmarks[idx].y * h)) for idx in indices], np.int32)
        cv2.fillPoly(mask, [points], 255)

        # 2. 边缘羽化 (让妆容边缘不再生硬)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)

        # 3. 提取带 Alpha 通道的图像
        bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        bgra[:, :, 3] = mask 

        # 4. 裁剪
        x, y, bw, bh = cv2.boundingRect(points)
        margin = 10 # 适当留白防止羽化部分被切
        y1, y2 = max(0, y-margin), min(h, y+bh+margin)
        x1, x2 = max(0, x-margin), min(w, x+bw+margin)
        cropped = bgra[y1:y2, x1:x2]
        
        file_name = f"{part_name}.png"
        cv2.imwrite(os.path.join(cache_full_dir, file_name), cropped)
        result_urls[part_name] = f"/static/makeup_parts/{img_md5}/{file_name}".replace("\\", "/")

    return result_urls, img_md5

async def extract_face_parts_async(img_bytes: bytes, upload_root: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _sync_process_logic, img_bytes, upload_root)

