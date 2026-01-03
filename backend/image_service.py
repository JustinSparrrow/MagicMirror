import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import uuid

# 全局初始化模型，避免重复加载
model_path = 'face_landmarker.task' 
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)

PARTS_CONFIG = {
    "left_eye": [33, 133, 160, 159, 158, 144, 145, 153, 154, 155],
    "right_eye": [362, 263, 387, 386, 385, 373, 374, 380, 381, 382],
    "left_eyebrow": [70, 63, 105, 66, 107, 55, 65, 52, 53, 46],
    "right_eyebrow": [336, 296, 334, 293, 300, 276, 283, 282, 295, 285],
    "lips": [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308],
    "nose": [1, 2, 98, 327, 168]
}

def process_face_parts(img_bytes, upload_root, parts_dir):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None: return None
    
    h, w, _ = img.shape
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    detection_result = detector.detect(mp_image)
    
    if not detection_result.face_landmarks:
        return None

    face_landmarks = detection_result.face_landmarks[0]
    task_id = str(uuid.uuid4())
    task_relative_path = os.path.join(parts_dir, task_id)
    task_full_path = os.path.join(upload_root, task_relative_path)
    os.makedirs(task_full_path, exist_ok=True)

    result_paths = {}

    for part_name, indices in PARTS_CONFIG.items():
        points = [(int(face_landmarks[idx].x * w), int(face_landmarks[idx].y * h)) for idx in indices]
        points_arr = np.array(points, dtype=np.int32)

        bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [points_arr], 255)
        bgra[:, :, 3] = 0
        bgra[mask == 255, 3] = 255

        x, y, bw, bh = cv2.boundingRect(points_arr)
        cropped_part = bgra[max(0,y):min(h,y+bh), max(0,x):min(w,x+bw)]

        file_name = f"{part_name}.png"
        file_save_path = os.path.join(task_full_path, file_name)
        cv2.imwrite(file_save_path, cropped_part)
        
        # 返回存储的相对路径，方便数据库记录
        result_paths[part_name] = f"/static/{task_id}/{file_name}".replace("\\", "/")

    return result_paths, task_id

