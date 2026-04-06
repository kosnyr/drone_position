#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArUco Visualization Node with Web Streaming
ROS 2 нода для веб-визуализации детекции ArUco маркеров
"""

import cv2
import numpy as np
import yaml
import threading
from flask import Flask, Response, render_template_string

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError


# ═════════════════════════════════════════════════════════════════════════════
# КОНСТАНТЫ
# ═════════════════════════════════════════════════════════════════════════════

CAMERA_PARAMS_PATH = '/home/drone/drone_ws/src/config/camera_params.yaml'
BALANCE = 0.0
ARUCO_DICT = cv2.aruco.DICT_4X4_250
WHITELIST = list(range(135, 160))  # 135-159


# ═════════════════════════════════════════════════════════════════════════════
# HTML ШАБЛОН
# ═════════════════════════════════════════════════════════════════════════════

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ArUco Detection Visualization</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #1e1e1e;
            color: #fff;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        h1 { 
            color: #4CAF50; 
            margin-bottom: 10px;
            font-size: 32px;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
        }
        .info {
            background: #2d2d2d;
            padding: 12px 20px;
            margin: 12px 0;
            border-radius: 8px;
            font-size: 17px;
        }
        .marker-count {
            color: #4CAF50;
            font-weight: bold;
            font-size: 22px;
        }
        .feeds {
            display: flex;
            gap: 16px;
            justify-content: center;
            align-items: flex-start;
            flex-wrap: wrap;
            margin: 16px 0;
        }
        .feed-box {
            flex: 1 1 45%;
            min-width: 280px;
        }
        .feed-box h2 {
            font-size: 15px;
            margin: 0 0 8px 0;
            color: #aaa;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .feed-box.raw h2   { color: #f0a000; }
        .feed-box.fixed h2 { color: #4CAF50; }
        .feed-box img {
            width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.6);
        }
        .feed-box.raw   img { border: 3px solid #f0a000; }
        .feed-box.fixed img { border: 3px solid #4CAF50; }
        .legend { 
            font-size: 15px; 
            color: #bbb; 
            margin-top: 16px;
        }
        .legend span { 
            margin: 0 12px;
            display: inline-block;
        }
        .status {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 6px;
        }
        .status.green { background: #4CAF50; }
        .status.yellow { background: #f0a000; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 ArUco Marker Detection Visualization</h1>

        <div class="info">
            <p>Dictionary: DICT_4X4_250 &nbsp;|&nbsp; Valid IDs: 135–159</p>
            <p class="marker-count" id="marker-info">Waiting for data...</p>
        </div>

        <div class="feeds">
            <div class="feed-box raw">
                <h2>📷 Raw Fisheye</h2>
                <img src="{{ url_for('video_feed_raw') }}" alt="Raw feed">
            </div>
            <div class="feed-box fixed">
                <h2>✅ Undistorted + Detection</h2>
                <img src="{{ url_for('video_feed') }}" alt="Undistorted feed">
            </div>
        </div>

        <div class="info legend">
            <span><span class="status green"></span>Green = Valid marker (135–159)</span>
            <span><span class="status yellow"></span>Yellow = Out of whitelist</span>
        </div>
    </div>

    <script>
        setInterval(function() {
            fetch('/marker_info')
                .then(r => r.text())
                .then(data => {
                    document.getElementById('marker-info').innerText = data;
                })
                .catch(err => {
                    document.getElementById('marker-info').innerText = 'Connection error';
                });
        }, 1000);
    </script>
</body>
</html>
"""


# ═════════════════════════════════════════════════════════════════════════════
# НОДА ВИЗУАЛИЗАЦИИ
# ═════════════════════════════════════════════════════════════════════════════

class ArucoVisualizationNode(Node):

    def __init__(self):
        super().__init__('aruco_visualization_node')

        self.bridge = CvBridge()
        self.latest_frame = None
        self.raw_frame    = None
        self.frame_lock = threading.Lock()
        self.markers_info = "No markers detected"

        # ── Загрузка параметров камеры и инициализация undistort-карт ────
        self._map1, self._map2, self._dst_size = self._init_undistort_maps(CAMERA_PARAMS_PATH)

        # ── ArUco детектор ────────────────────────────────────────────────
        aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        parameters = cv2.aruco.DetectorParameters()
        parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR
        self.detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

        # ── QoS ───────────────────────────────────────────────────────────
        img_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST, depth=1
        )

        # ── Подписки / издатели ───────────────────────────────────────────
        self.create_subscription(Image, '/camera/image_raw', self.image_callback, img_qos)
        self.pub_debug_image = self.create_publisher(Image, '/aruco/debug_image', img_qos)
        self.pub_markers_info = self.create_publisher(String, '/aruco/markers_info', 10)

        self.get_logger().info('ArUco Visualization Node started')
        self.get_logger().info('Web interface: http://0.0.0.0:5000')

    # ─────────────────────────────────────────────────────────────────────
    # Undistort
    # ─────────────────────────────────────────────────────────────────────

    def _init_undistort_maps(self, path: str):
        with open(path, 'r') as f:
            d = yaml.safe_load(f)

        src_w = int(d['image_width'])
        src_h = int(d['image_height'])
        dst_w = int(d.get('target_width',  src_w))
        dst_h = int(d.get('target_height', src_h))

        K = np.array(d['camera_matrix']['data'],           dtype=np.float64).reshape(3, 3)
        D = np.array(d['distortion_coefficients']['data'], dtype=np.float64).reshape(1, 4)
        R = np.array(d['rectification_matrix']['data'],    dtype=np.float64).reshape(3, 3)

        # Масштабируем K под целевое разрешение
        K_sc = K.copy()
        K_sc[0, 0] *= dst_w / src_w;  K_sc[1, 1] *= dst_h / src_h
        K_sc[0, 2] *= dst_w / src_w;  K_sc[1, 2] *= dst_h / src_h

        K_new = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
            K_sc, D, (dst_w, dst_h), R, balance=BALANCE
        )
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(
            K_sc, D, R, K_new, (dst_w, dst_h), cv2.CV_16SC2
        )

        self.get_logger().info(
            f'Undistort maps ready: {src_w}×{src_h} → {dst_w}×{dst_h}, balance={BALANCE}'
        )
        return map1, map2, (dst_w, dst_h)

    # ─────────────────────────────────────────────────────────────────────
    # Callback
    # ─────────────────────────────────────────────────────────────────────

    def image_callback(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge error: {e}')
            return

        # Ресайз до целевого разрешения если нужно
        if (frame.shape[1], frame.shape[0]) != self._dst_size:
            frame = cv2.resize(frame, self._dst_size)

        # Сохраняем сырой кадр до undistort
        with self.frame_lock:
            self.raw_frame = frame.copy()

        # ── Fisheye undistort ─────────────────────────────────────────────
        frame = cv2.remap(frame, self._map1, self._map2, cv2.INTER_LINEAR)

        # ── Детекция маркеров ─────────────────────────────────────────────
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)

        markers_list = []
        if ids is not None:
            for i, marker_id in enumerate(ids.flatten()):
                marker_id = int(marker_id)
                valid = marker_id in WHITELIST

                # Цвет рамки: зелёный — валидный, жёлтый — вне списка
                color = (0, 255, 0) if valid else (0, 255, 255)
                
                # Отрисовка маркера
                cv2.aruco.drawDetectedMarkers(frame, [corners[i]], np.array([[marker_id]]))

                # Подпись в центре маркера
                corner = corners[i][0]
                cx = int(corner[:, 0].mean())
                cy = int(corner[:, 1].mean())
                label = f"ID:{marker_id}" + (" ✓" if valid else " ⚠")
                cv2.putText(frame, label, (cx - 30, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                if valid:
                    self.get_logger().info(f'✓ Marker ID: {marker_id}')
                    markers_list.append(f'{marker_id}✓')
                else:
                    self.get_logger().warn(f'⚠ Marker ID: {marker_id} (out of whitelist)')
                    markers_list.append(f'{marker_id}⚠')

            self.markers_info = f"Found {len(ids)} markers: {', '.join(markers_list)}"
            info_msg = String()
            info_msg.data = self.markers_info
            self.pub_markers_info.publish(info_msg)
        else:
            self.markers_info = "No markers detected"

        # Счётчик маркеров на кадре
        cv2.putText(frame, f"Markers: {len(ids) if ids is not None else 0}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Сохранение кадра для веб-стриминга
        with self.frame_lock:
            self.latest_frame = frame.copy()

        # Публикация отладочного изображения
        try:
            debug_msg = self.bridge.cv2_to_imgmsg(frame, 'bgr8')
            debug_msg.header = msg.header
            self.pub_debug_image.publish(debug_msg)
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge error: {e}')

    def get_latest_frame(self):
        with self.frame_lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def get_raw_frame(self):
        with self.frame_lock:
            return self.raw_frame.copy() if self.raw_frame is not None else None


# ═════════════════════════════════════════════════════════════════════════════
# FLASK ПРИЛОЖЕНИЕ
# ═════════════════════════════════════════════════════════════════════════════

app = Flask(__name__)
node_instance = None


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/marker_info')
def marker_info():
    if node_instance:
        return node_instance.markers_info
    return "Node not initialized"


def generate_frames():
    while True:
        if node_instance:
            frame = node_instance.get_latest_frame()
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        threading.Event().wait(0.033)  # ~30 FPS


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_raw_frames():
    while True:
        if node_instance:
            frame = node_instance.get_raw_frame()
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        threading.Event().wait(0.033)


@app.route('/video_feed_raw')
def video_feed_raw():
    return Response(generate_raw_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def run_flask():
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main(args=None):
    global node_instance

    rclpy.init(args=args)
    node_instance = ArucoVisualizationNode()

    # Запуск Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    try:
        rclpy.spin(node_instance)
    except KeyboardInterrupt:
        pass
    finally:
        node_instance.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
