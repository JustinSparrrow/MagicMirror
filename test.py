import cv2
import numpy as np
import mediapipe as mp
import time
import threading
from HandTrackingModule import HandDetector

# 调用关键点检测模型
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

try:
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=3,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("Mediapipe Face Mesh initialized successfully.")
except Exception as e:
    print("Error initializing Mediapipe Face Mesh:", e)

# mediapipe提供的绘制模块
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# 定义左右眼、左右眉毛、嘴唇和鼻子的连接
LEFT_EYE = mp_face_mesh.FACEMESH_LEFT_EYE
RIGHT_EYE = mp_face_mesh.FACEMESH_RIGHT_EYE
LEFT_EYEBROW = mp_face_mesh.FACEMESH_LEFT_EYEBROW
RIGHT_EYEBROW = mp_face_mesh.FACEMESH_RIGHT_EYEBROW
LIPS = mp_face_mesh.FACEMESH_LIPS
NOSE = mp_face_mesh.FACEMESH_NOSE

# 加载替换图片
left_eye_img = cv2.imread('images/left_eye.png', cv2.IMREAD_UNCHANGED)
right_eye_img = cv2.imread('images/right_eye.png', cv2.IMREAD_UNCHANGED)
left_eyebrow_img = cv2.imread('images/left_eyebrow.png', cv2.IMREAD_UNCHANGED)
right_eyebrow_img = cv2.imread('images/right_eyebrow.png', cv2.IMREAD_UNCHANGED)
lips_img = cv2.imread('imagesps.png', cv2.IMREAD_UNCHANGED)
nose_img = cv2.imread('images[表情]se.png', cv2.IMREAD_UNCHANGED)

# 添加alpha通道的函数
def add_alpha_channel(image):
    b_channel, g_channel, r_channel = cv2.split(image)
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255  # 创建一个全白的Alpha通道
    return cv2.merge((b_channel, g_channel, r_channel, alpha_channel))

# 检查并添加Alpha通道
def ensure_alpha_channel(image):
    if image is not None and image.shape[2] != 4:
        return add_alpha_channel(image)
    return image

left_eye_img = ensure_alpha_channel(left_eye_img)
right_eye_img = ensure_alpha_channel(right_eye_img)
left_eyebrow_img = ensure_alpha_channel(left_eyebrow_img)
right_eyebrow_img = ensure_alpha_channel(right_eyebrow_img)
lips_img = ensure_alpha_channel(lips_img)
nose_img = ensure_alpha_channel(nose_img)

# 手势识别线程
class HandRecognitionThread(threading.Thread):
    def __init__(self, frame, detector):
        threading.Thread.__init__(self)
        self.frame = frame
        self.detector = detector

    def run(self):
        self.frame = self.detector.findHands(self.frame)
        lmList, bbox = self.detector.findPosition(self.frame)
        if lmList:
            x_1, y_1 = bbox["bbox"][0], bbox["bbox"][1]
            x1, x2, x3, x4, x5 = self.detector.fingersUp()

            if (x2 == 1 and x3 == 1) and (x4 == 0 and x5 == 0 and x1 == 0):
                cv2.putText(self.frame, "2_TWO", (x_1, y_1), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
            elif (x2 == 1 and x3 == 1 and x4 == 1) and (x1 == 0 and x5 == 0):
                cv2.putText(self.frame, "3_THREE", (x_1, y_1), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
            elif (x2 == 1 and x3 == 1 and x4 == 1 and x5 == 1) and (x1 == 0):
                cv2.putText(self.frame, "4_FOUR", (x_1, y_1), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
            elif x1 == 1 and x2 == 1 and x3 == 1 and x4 == 1 and x5 == 1:
                cv2.putText(self.frame, "5_FIVE", (x_1, y_1), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
            elif x2 == 1 and (x1 == 0, x3 == 0, x4 == 0, x5 == 0):
                cv2.putText(self.frame, "1_ONE", (x_1, y_1), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
            elif x1 and (x2 == 0 and x3 == 0 and x4 == 0 and x5 == 0):
                cv2.putText(self.frame, "GOOD!", (x_1, y_1), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

# 面部识别线程
class FaceMeshThread(threading.Thread):
    def __init__(self, frame):
        threading.Thread.__init__(self)
        self.frame = frame

    def run(self):
        # 将BGR图像转为RGB图像
        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                # 使用模型获取关键点
        results = face_mesh.process(frame_rgb)

        # 如果检测到关键点
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 获取关键点坐标
                h, w, c = self.frame.shape
                landmarks = [(int(pt.x * w), int(pt.y * h)) for pt in face_landmarks.landmark]

                # 绘制左右眼、左右眉毛、嘴唇和鼻子
                mp_drawing.draw_landmarks(image=self.frame, landmark_list=face_landmarks,
                                          connections=LEFT_EYE,
                                          landmark_drawing_spec=None,
                                          connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
                mp_drawing.draw_landmarks(image=self.frame, landmark_list=face_landmarks,
                                          connections=RIGHT_EYE,
                                          landmark_drawing_spec=None,
                                          connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

                mp_drawing.draw_landmarks(image=self.frame, landmark_list=face_landmarks,
                                          connections=LEFT_EYEBROW,
                                          landmark_drawing_spec=None,
                                          connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

                mp_drawing.draw_landmarks(image=self.frame, landmark_list=face_landmarks,
                                          connections=RIGHT_EYEBROW,
                                          landmark_drawing_spec=None,
                                          connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

                mp_drawing.draw_landmarks(image=self.frame, landmark_list=face_landmarks,
                                          connections=LIPS,
                                          landmark_drawing_spec=None,
                                          connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

                mp_drawing.draw_landmarks(image=self.frame, landmark_list=face_landmarks,
                                          connections=NOSE,
                                          landmark_drawing_spec=None,
                                          connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

                 # 获取左眼区域并替换
                if left_eye_img is not None:
                    left_eye_points = [landmarks[i] for i in [33, 133, 160, 159, 158, 144, 145, 153, 154, 155]]
                    left_eye_x = min([pt[0] for pt in left_eye_points])
                    left_eye_y = min([pt[1] for pt in left_eye_points])
                    left_eye_w = max([pt[0] for pt in left_eye_points]) - left_eye_x
                    left_eye_h = max([pt[1] for pt in left_eye_points]) - left_eye_y
                    left_eye_resized = cv2.resize(left_eye_img, (left_eye_w, left_eye_h))
                    overlay_image_alpha(frame, left_eye_resized[:, :, :3], left_eye_x, left_eye_y, left_eye_resized[:, :, 3] / 255.0)
                else:
                    print('no left eye img.')

                # 获取右眼区域并替换
                if right_eye_img is not None:
                    right_eye_points = [landmarks[i] for i in [362, 263, 387, 386, 385, 373, 374, 380, 381, 382]]
                    right_eye_x = min([pt[0] for pt in right_eye_points])
                    right_eye_y = min([pt[1] for pt in right_eye_points])
                    right_eye_w = max([pt[0] for pt in right_eye_points]) - right_eye_x
                    right_eye_h = max([pt[1] for pt in right_eye_points]) - right_eye_y
                    right_eye_resized = cv2.resize(right_eye_img, (right_eye_w, right_eye_h))
                    overlay_image_alpha(frame, right_eye_resized[:, :, :3], right_eye_x, right_eye_y, right_eye_resized[:, :, 3] / 255.0)
                else:
                    print('no right eye img.')

                # 获取左眉毛区域并替换
                if left_eyebrow_img is not None:
                    left_eyebrow_points = [landmarks[i] for i in [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]]
                    left_eyebrow_x = min([pt[0] for pt in left_eyebrow_points])
                    left_eyebrow_y = min([pt[1] for pt in left_eyebrow_points])
                    left_eyebrow_w = max([pt[0] for pt in left_eyebrow_points]) - left_eyebrow_x
                    left_eyebrow_h = max([pt[1] for pt in left_eyebrow_points]) - left_eyebrow_y
                    left_eyebrow_resized = cv2.resize(left_eyebrow_img, (left_eyebrow_w, left_eyebrow_h))
                    overlay_image_alpha(frame, left_eyebrow_resized[:, :, :3], left_eyebrow_x, left_eyebrow_y, left_eyebrow_resized[:, :, 3] / 255.0)
                else:
                    print('no left eyebrow img.')

                # 获取右眉毛区域并替换
                if right_eyebrow_img is not None:
                    right_eyebrow_points = [landmarks[i] for i in [336, 296, 334, 293, 300, 276, 283, 282, 295, 285]]
                    right_eyebrow_x = min([pt[0] for pt in right_eyebrow_points])
                    right_eyebrow_y = min([pt[1] for pt in right_eyebrow_points])
                    right_eyebrow_w = max([pt[0] for pt in right_eyebrow_points]) - right_eyebrow_x
                    right_eyebrow_h = max([pt[1] for pt in right_eyebrow_points]) - right_eyebrow_y
                    right_eyebrow_resized = cv2.resize(right_eyebrow_img, (right_eyebrow_w, right_eyebrow_h))
                    overlay_image_alpha(frame, right_eyebrow_resized[:, :, :3], right_eyebrow_x, right_eyebrow_y, right_eyebrow_resized[:, :, 3] / 255.0)
                else:
                    print('no right eyebrow img.')

                # 获取嘴唇区域并替换
                if lips_img is not None:
                    lips_points = [landmarks[i] for i in [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308]]
                    lips_x = min([pt[0] for pt in lips_points])
                    lips_y = min([pt[1] for pt in lips_points])
                    lips_w = max([pt[0] for pt in lips_points]) - lips_x
                    lips_h = max([pt[1] for pt in lips_points]) - lips_y
                    lips_resized = cv2.resize(lips_img, (lips_w, lips_h))
                    overlay_image_alpha(frame, lips_resized[:, :, :3], lips_x, lips_y, lips_resized[:, :, 3] / 255.0)
                else:
                    print('no lips img.')

                # 获取鼻子区域并替换
                if nose_img is not None:
                    nose_points = [landmarks[i] for i in [1, 2, 98, 327, 168]]
                    nose_x = min([pt[0] for pt in nose_points])
                    nose_y = min([pt[1] for pt in nose_points])
                    nose_w = max([pt[0] for pt in nose_points]) - nose_x
                    nose_h = max([pt[1] for pt in nose_points]) - nose_y
                    nose_resized = cv2.resize(nose_img, (nose_w, nose_h))
                    overlay_image_alpha(frame, nose_resized[:, :, :3], nose_x, nose_y, nose_resized[:, :, 3] / 255.0)
                else:
                    print('no nose img.')

# 叠加带Alpha通道的图像
def overlay_image_alpha(img, overlay_img, x, y, alpha_mask):
    h, w = overlay_img.shape[0], overlay_img.shape[1]

    for c in range(3):
        img[y:y+h, x:x+w, c] = img[y:y+h, x:x+w, c] * (1 - alpha_mask) + overlay_img[:, :, c] * alpha_mask

cap = cv2.VideoCapture(0)

# 初始化手势检测
detector = HandDetector(detectionCon=0.7, maxHands=2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 创建并启动手势识别和面部识别线程
    hand_thread = HandRecognitionThread(frame, detector)
    face_thread = FaceMeshThread(frame)
    hand_thread.start()
    face_thread.start()

    # 等待线程完成
    hand_thread.join()
    face_thread.join()

    # 显示结果
    cv2.imshow('Hand and Face Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()