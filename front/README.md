# Magic Mirror Frontend
这是“魔镜”项目的浏览器端实现，基于 Vue 3 和 MediaPipe 开发。它能够实时追踪用户面部坐标，并将后端提取的五官妆容素材精准地“贴”在用户脸上，实现低延迟、高保真的虚拟试妆体验。

## ✨ 核心工程特性
- 边缘计算实时渲染：利用浏览器端 MediaPipe Face Landmarker (WASM) 实现 478 个面部关键点实时追踪，确保 AR 覆盖达到 30FPS 以上。
- 非等比缩放算法 (Non-uniform Scaling)：基于面部关键点距离动态计算妆容图片的横向与纵向缩放比例，完美适配不同脸型。
- 工程化鉴权体系：集成 Axios 拦截器，自动为所有 API 请求注入 JWT Bearer Token，实现无感权限校验。
- 加载性能优化：
    - 模型本地化：通过静态资源预加载 face_landmarker.task，避免跨洋请求谷歌 CDN，加载速度提升 10 倍。
    - 分阶段进度监控：实现完整的 Loading 状态机，向用户实时反馈 AI 引擎初始化、模型下载及资源加载进度。
- 响应式画廊模式：支持妆容历史库预览、一键换妆及物理联动删除。

## 🛠 技术栈
框架: Vue 3 (Composition API)
构建工具: Vite 5+
AI 引擎: @mediapipe/tasks-vision (WebAssembly)
网络请求: Axios + 自定义拦截器
路由管理: Vue Router 4
样式方案: 原生 CSS 变量 + 响应式 Grid 布局

## 🚀 环境搭建与快速启动
1. 克隆项目并进入目录
```bash
cd magic-mirror/front
```

2. 安装依赖
```
npm install
```

3. 配置本地 AI 模型
为了获得最佳加载速度，请确保 face_landmarker.task 文件已放置在 public 目录下：
```Text
文件路径应为: front/public/face_landmarker.task
```

4. 配置环境变量
在 front/ 目录下创建 .env.development 文件：
```lni
# 后端 API 地址
VITE_API_BASE_URL=http://localhost:8000/api/v1
# 后端静态资源根地址（用于拼接图片 URL）
VITE_IMAGE_BASE_URL=http://localhost:8000
```

5. 启动开发服务器
```bash
npm run dev
```

启动后，在浏览器访问 http://localhost:5173。

## 📂 项目结构说明
```Text
front/
├── src/
│   ├── api/            # Axios 实例与拦截器配置
│   ├── components/     # 核心组件 (MagicMirror.vue 实时渲染引擎)
│   ├── router/         # 路由配置与登录守卫
│   ├── views/          # 页面级组件 (Home 主页、Login 登录页)
│   ├── App.vue         # 根容器
│   └── main.js         # 入口文件
├── public/             # 存放 AI 模型文件 (.task)
├── .env.development    # 环境配置文件
└── package.json        # 项目依赖
```

## 🧠 核心算法解析
### 1. 坐标映射 (Coordinate Mapping)
MediaPipe 返回的是 0-1 之间的归一化坐标。我们将其通过以下公式转化为 Canvas 像素坐标：
$$ X_{pixel}=X_{normalized}×Canvas_{Width}$$
​
### 2. 纵横比适配
为了防止妆容在不同脸型上出现过度拉伸，系统计算了面部的物理比例系数：
- 宽度参考点：鼻翼两侧 (102, 331) 或 嘴角 (61, 291)。
- 高度参考点：眉心到鼻底 (168, 2)。
- 旋转角：通过 Math.atan2(dy, dx) 计算面部倾斜度，实时同步图片旋转。

## ⚠️ 开发者注意事项
- 摄像头权限：浏览器要求在 localhost 或 HTTPS 环境下才允许调用摄像头。
- 浏览器兼容性：建议使用最新版 Chrome 或 Edge，以获得完整的 WebAssembly 硬件加速支持。
- 后端连接：若手机端预览，需将 .env 中的 localhost 改为电脑的局域网 IP 地址。

---
*Magic Mirror Project - 重新定义数字美妆。*