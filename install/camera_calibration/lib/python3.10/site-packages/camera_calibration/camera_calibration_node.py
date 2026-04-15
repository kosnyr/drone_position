#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║         УЛУЧШЕННАЯ КАЛИБРОВКА FISHEYE КАМЕРЫ (v5.0)                      ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Улучшения v5.0:                                                          ║
║    • Вывод картинки через HTTP MJPEG (http://localhost:8080/)             ║
║    • Убраны зависимости tkinter и Pillow                                  ║
║  Прежние улучшения:                                                       ║
║    • Доска 9x6 (можно задать свои размеры)                               ║
║    • Использование findChessboardCornersSB (OpenCV >=4.5)                ║
║    • 5 коэффициентов дисторсии (модель equidistant)                      ║
║    • Начальное приближение K + флаг USE_INTRINSIC_GUESS                  ║
║    • Минимум 30 кадров (рекомендуется 40+)                               ║
║    • Параметр balance при undistortion = 0 (для визуальной проверки)     ║
║    • Сохранение в формате camera_info (совместимо с image_preprocessor)  ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import numpy as np
import os
import threading
import queue
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# ═══════════════════════════════════════════════════════════════
# НАСТРОЙКИ (ИЗМЕНИТЕ ПОД СВОЮ ДОСКУ)
# ═══════════════════════════════════════════════════════════════
BOARD_W        = 4          # количество внутренних углов по горизонтали
BOARD_H        = 6           # количество внутренних углов по вертикали
SQUARE_SIZE_MM = 48         # размер клетки в миллиметрах

MIN_FRAMES     = 30          # минимальное количество кадров (рекомендуется 40)

HTTP_PORT      = 8080        # порт HTTP-стрима
JPEG_QUALITY   = 80          # качество JPEG (0-100)

# Путь сохранения YAML
SAVE_PATH = os.path.expanduser("~/drone_ws/src/drone_vision/config/camera_params_improved.yaml")

# Использовать ли SB детектор (OpenCV >=4.5)
USE_SB_DETECTOR = True

# ═══════════════════════════════════════════════════════════════
# ОБЩЕЕ СОСТОЯНИЕ
# ═══════════════════════════════════════════════════════════════
class State:
    def __init__(self):
        self.frame_q  = queue.Queue(maxsize=1)
        self.result_q = queue.Queue(maxsize=1)

        self.latest_result = None
        self.result_lock   = threading.Lock()

        self.capture_lock = threading.Lock()
        self.objpoints    = []
        self.imgpoints    = []
        self.img_size     = None

        self.flash      = 0
        self.calibrated = False
        self.quit_flag  = False

        # MJPEG буфер
        self.latest_jpeg = None
        self.jpeg_lock   = threading.Lock()

S = State()

# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ОЧЕРЕДЕЙ
# ═══════════════════════════════════════════════════════════════
def _qput(q, item):
    try:
        q.get_nowait()
    except queue.Empty:
        pass
    q.put(item)

def _qget_latest(q):
    result = None
    while True:
        try:
            result = q.get_nowait()
        except queue.Empty:
            break
    return result

# ═══════════════════════════════════════════════════════════════
# ROS2 НОДА
# ═══════════════════════════════════════════════════════════════
class CalibrationNode(Node):
    def __init__(self):
        super().__init__("calibration_node_improved")
        self.bridge = CvBridge()

        square_size_m = SQUARE_SIZE_MM / 1000.0
        self.OBJP = np.zeros((BOARD_W * BOARD_H, 1, 3), dtype=np.float64)
        self.OBJP[:, 0, :2] = np.mgrid[0:BOARD_W, 0:BOARD_H].T.reshape(-1, 2)
        self.OBJP *= square_size_m

        self.create_subscription(Image, "/camera/image_raw", self._cb, 10)

        self.get_logger().info("=" * 60)
        self.get_logger().info("  УЛУЧШЕННАЯ КАЛИБРОВКА FISHEYE v5.0")
        self.get_logger().info(f"  Доска: {BOARD_W}x{BOARD_H}, клетка {SQUARE_SIZE_MM} мм")
        self.get_logger().info(f"  Минимум кадров: {MIN_FRAMES}")
        self.get_logger().info(f"  Стрим: http://localhost:{HTTP_PORT}/")
        self.get_logger().info("  Enter=захват  d=удалить  c=калибровать  q=выход")
        self.get_logger().info("=" * 60)

    def _cb(self, msg: Image):
        if S.calibrated or S.quit_flag:
            return
        try:
            frame_bgr = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(str(e), throttle_duration_sec=5.0)
            return

        with S.capture_lock:
            if S.img_size is None:
                S.img_size = (frame_bgr.shape[1], frame_bgr.shape[0])
        _qput(S.frame_q, frame_bgr)

    def do_capture(self):
        with S.result_lock:
            result = S.latest_result
        if result is None or not result['found']:
            self.get_logger().warn("Доска не найдена — захват невозможен")
            return

        with S.capture_lock:
            S.objpoints.append(self.OBJP.copy())
            S.imgpoints.append(result['corners'])
            S.flash = 5
            n = len(S.objpoints)

        self.get_logger().info(f"[ЗАХВАТ] #{n}  ({n}/{MIN_FRAMES})")
        if n >= MIN_FRAMES:
            self.get_logger().info("  Достаточно кадров. Введи c для калибровки.")

    def do_delete(self):
        with S.capture_lock:
            if not S.objpoints:
                self.get_logger().warn("Нечего удалять")
                return
            S.objpoints.pop()
            S.imgpoints.pop()
            n = len(S.objpoints)
        self.get_logger().info(f"[УДАЛЕНО] Остаток: {n}/{MIN_FRAMES}")

    def do_calibrate(self):
        with S.capture_lock:
            n         = len(S.objpoints)
            objpoints = list(S.objpoints)
            imgpoints = list(S.imgpoints)
            img_size  = S.img_size

        if n < MIN_FRAMES:
            self.get_logger().warn(f"Мало кадров: {n}/{MIN_FRAMES}")
            return

        self.get_logger().info(f"[КАЛИБРОВКА] Запуск по {n} кадрам...")

        K = np.array([[img_size[0], 0, img_size[0]/2.0],
                      [0, img_size[1], img_size[1]/2.0],
                      [0, 0, 1]], dtype=np.float64)
        D = np.zeros((5, 1), dtype=np.float64)

        flags = (cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC |
                 cv2.fisheye.CALIB_CHECK_COND |
                 cv2.fisheye.CALIB_FIX_SKEW |
                 cv2.fisheye.CALIB_USE_INTRINSIC_GUESS)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)

        try:
            rms, K, D, _, _ = cv2.fisheye.calibrate(
                objpoints, imgpoints, img_size, K, D,
                flags=flags, criteria=criteria
            )
        except cv2.error as e:
            self.get_logger().error(f"Ошибка калибровки: {e}")
            return

        quality = (
            "ОТЛИЧНО"   if rms < 0.3 else
            "ХОРОШО"    if rms < 0.5 else
            "ПРИЕМЛЕМО" if rms < 1.0 else
            "ПЛОХО"
        )
        d = D.flatten()
        self.get_logger().info("=" * 60)
        self.get_logger().info(f"  RMS: {rms:.4f} px  [{quality}]")
        self.get_logger().info(f"  fx={K[0,0]:.2f}  fy={K[1,1]:.2f}  cx={K[0,2]:.2f}  cy={K[1,2]:.2f}")
        self.get_logger().info(f"  k1={d[0]:.4f}  k2={d[1]:.4f}  k3={d[2]:.4f}  k4={d[3]:.4f}  k5={d[4]:.4f}")
        self.get_logger().info("=" * 60)

        yp = _save_results(K, D, rms, n, img_size)
        self.get_logger().info(f"[OK] YAML → {yp}")

        S.calibrated = True


# ═══════════════════════════════════════════════════════════════
# WORKER-ПОТОК — ПОИСК ШАХМАТНОЙ ДОСКИ
# ═══════════════════════════════════════════════════════════════
def chessboard_worker(stop_event: threading.Event):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    flags = (cv2.CALIB_CB_ADAPTIVE_THRESH +
             cv2.CALIB_CB_NORMALIZE_IMAGE +
             cv2.CALIB_CB_FAST_CHECK)

    while not stop_event.is_set():
        try:
            frame = S.frame_q.get(timeout=0.1)
        except queue.Empty:
            continue

        if S.calibrated or S.quit_flag:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if USE_SB_DETECTOR and hasattr(cv2, 'findChessboardCornersSB'):
            found, corners = cv2.findChessboardCornersSB(gray, (BOARD_W, BOARD_H), flags)
        else:
            found, corners = cv2.findChessboardCorners(gray, (BOARD_W, BOARD_H), flags)

        if found:
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            vis = frame.copy()
            cv2.drawChessboardCorners(vis, (BOARD_W, BOARD_H), corners, True)
        else:
            vis = frame.copy()

        _qput(S.result_q, {
            'found':   found,
            'corners': corners if found else None,
            'vis':     vis,
        })


# ═══════════════════════════════════════════════════════════════
# RENDER-ПОТОК — РИСУЕТ ОВЕРЛЕЙ И КОДИРУЕТ JPEG
# ═══════════════════════════════════════════════════════════════
def render_worker():
    """Берёт кадры из result_q, рисует HUD, кодирует в JPEG → S.latest_jpeg."""
    while not S.quit_flag and not S.calibrated:
        new_result = _qget_latest(S.result_q)
        if new_result is not None:
            with S.result_lock:
                S.latest_result = new_result

        with S.result_lock:
            result = S.latest_result

        if result is None:
            time.sleep(0.033)
            continue

        with S.capture_lock:
            n     = len(S.objpoints)
            flash = S.flash
            if S.flash > 0:
                S.flash -= 1

        frame = result['vis'].copy()
        found = result['found']
        h, w  = frame.shape[:2]

        # Вспышка при захвате
        if flash > 0:
            white = np.ones_like(frame, dtype=np.uint8) * 255
            frame = cv2.addWeighted(frame, 0.25, white, 0.75, 0)

        # Рамка: зелёная — доска найдена
        color = (0, 220, 0) if found else (50, 50, 50)
        cv2.rectangle(frame, (2, 2), (w - 2, h - 2), color, 2)

        # Счётчик кадров
        cv2.putText(frame, f"{n}/{MIN_FRAMES}", (10, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)

        # Статус доски
        board_str = "ДОСКА НАЙДЕНА — нажми Enter" if found else "Доска не найдена"
        cv2.putText(frame, board_str, (10, h - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

        # Прогресс-бар
        bar_x0, bar_x1 = 10, w - 10
        bar_y0, bar_y1 = h - 22, h - 10
        pct      = min(n / MIN_FRAMES, 1.0)
        fill_col = (0, 255, 128) if pct >= 1.0 else (0, 180, 60)
        cv2.rectangle(frame, (bar_x0, bar_y0), (bar_x1, bar_y1), (50, 50, 50), -1)
        if pct > 0:
            cv2.rectangle(frame,
                          (bar_x0, bar_y0),
                          (bar_x0 + int((bar_x1 - bar_x0) * pct), bar_y1),
                          fill_col, -1)

        ok, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if ok:
            with S.jpeg_lock:
                S.latest_jpeg = buf.tobytes()

        time.sleep(0.033)  # ~30 FPS


# ═══════════════════════════════════════════════════════════════
# HTTP MJPEG СЕРВЕР
# ═══════════════════════════════════════════════════════════════
_INDEX_HTML = f"""\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Fisheye Calibration v5.0</title>
  <style>
    body  {{ background: #111; color: #eee; font-family: monospace;
             display: flex; flex-direction: column; align-items: center;
             margin: 0; padding: 16px; }}
    h2    {{ margin: 0 0 12px; color: #0f0; }}
    img   {{ max-width: 100%; border: 2px solid #333; border-radius: 4px; }}
    p     {{ color: #888; font-size: 13px; margin-top: 10px; }}
  </style>
</head>
<body>
  <h2>Fisheye Calibration v5.0</h2>
  <img src="/stream" alt="MJPEG stream">
  <p>Управление в терминале:&nbsp;
     <b>Enter</b>=захват &nbsp; <b>d</b>=удалить &nbsp;
     <b>c</b>=калибровать &nbsp; <b>q</b>=выход</p>
</body>
</html>
""".encode()

class _MJPEGHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # заглушаем access-логи в консоль

    def do_GET(self):
        if self.path == '/':
            self._serve_index()
        elif self.path == '/stream':
            self._serve_stream()
        else:
            self.send_error(404)

    def _serve_index(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(_INDEX_HTML))
        self.end_headers()
        self.wfile.write(_INDEX_HTML)

    def _serve_stream(self):
        self.send_response(200)
        self.send_header('Content-Type',
                         'multipart/x-mixed-replace; boundary=frame')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        try:
            while not S.quit_flag and not S.calibrated:
                with S.jpeg_lock:
                    jpeg = S.latest_jpeg
                if jpeg is None:
                    time.sleep(0.05)
                    continue
                try:
                    self.wfile.write(
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' +
                        jpeg +
                        b'\r\n'
                    )
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    break
                time.sleep(0.033)
        except Exception:
            pass


def run_http_server(node: CalibrationNode):
    server = HTTPServer(('0.0.0.0', HTTP_PORT), _MJPEGHandler)
    server.timeout = 0.5
    node.get_logger().info(f"[HTTP] http://localhost:{HTTP_PORT}/  (MJPEG поток)")
    while not S.quit_flag and not S.calibrated:
        server.handle_request()
    server.server_close()


# ═══════════════════════════════════════════════════════════════
# ПОТОК КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════════════
def keyboard_loop(node: CalibrationNode):
    print("Готово. Введи команду (Enter / d / c / q):")
    while not S.quit_flag and not S.calibrated:
        try:
            cmd = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            S.quit_flag = True
            break

        if S.quit_flag or S.calibrated:
            break

        if cmd == "q":
            print("Выход...")
            S.quit_flag = True
            rclpy.shutdown()
            break
        elif cmd == "d":
            node.do_delete()
        elif cmd == "c":
            node.do_calibrate()
        else:
            node.do_capture()


# ═══════════════════════════════════════════════════════════════
# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# ═══════════════════════════════════════════════════════════════
def _save_results(K, D, rms, n_frames, img_size):
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]
    d = D.flatten()
    while len(d) < 5:
        d = np.append(d, 0.0)

    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

    with open(SAVE_PATH, "w") as f:
        f.write(f"# fisheye Kannala-Brandt  RMS={rms:.4f} px\n\n")
        f.write(f"image_width: {img_size[0]}\nimage_height: {img_size[1]}\n")
        f.write(f"camera_name: fisheye_camera\n")
        f.write(f"distortion_model: equidistant\n\n")
        f.write(f"target_width: {img_size[0]}\ntarget_height: {img_size[1]}\n\n")
        f.write(f"distortion_coefficients:\n  rows: 1\n  cols: 5\n")
        f.write(f"  data: [{d[0]:.8f}, {d[1]:.8f}, {d[2]:.8f}, {d[3]:.8f}, {d[4]:.8f}]\n\n")
        f.write(f"camera_matrix:\n  rows: 3\n  cols: 3\n")
        f.write(f"  data: [{fx:.6f}, 0.0, {cx:.6f},\n")
        f.write(f"         0.0, {fy:.6f}, {cy:.6f},\n")
        f.write(f"         0.0, 0.0, 1.0]\n\n")
        f.write(f"rectification_matrix:\n  rows: 3\n  cols: 3\n")
        f.write(f"  data: [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]\n\n")
        f.write(f"projection_matrix:\n  rows: 3\n  cols: 4\n")
        f.write(f"  data: [{fx:.6f}, 0.0, {cx:.6f}, 0.0,\n")
        f.write(f"         0.0, {fy:.6f}, {cy:.6f}, 0.0,\n")
        f.write(f"         0.0, 0.0, 1.0, 0.0]\n")
    return SAVE_PATH


# ═══════════════════════════════════════════════════════════════
# ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════
def main(args=None):
    rclpy.init(args=args)
    node = CalibrationNode()

    stop_event = threading.Event()

    t_spin = threading.Thread(target=rclpy.spin, args=(node,), daemon=True, name="ros_spin")
    t_spin.start()

    t_chess = threading.Thread(target=chessboard_worker, args=(stop_event,), daemon=True, name="chess_worker")
    t_chess.start()

    t_render = threading.Thread(target=render_worker, daemon=True, name="render")
    t_render.start()

    t_kb = threading.Thread(target=keyboard_loop, args=(node,), daemon=True, name="keyboard")
    t_kb.start()

    # Главный поток — HTTP сервер (блокирующий)
    run_http_server(node)

    stop_event.set()
    S.quit_flag = True
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == "__main__":
    main()
