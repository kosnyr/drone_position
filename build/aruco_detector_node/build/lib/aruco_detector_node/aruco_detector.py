#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FISHEYE ARUCO POSITIONING NODE
Fisheye camera + ArUco markers → absolute drone position on field
Высота вычисляется с помощью дальномера и углов Эйлера
"""

import cv2
import numpy as np
import yaml
import threading
from typing import Optional, Tuple, List, Dict
from collections import deque
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from rclpy.time import Time

from sensor_msgs.msg import Image
from geometry_msgs.msg import Vector3, PointStamped, Point
from std_msgs.msg import Float64
from cv_bridge import CvBridge, CvBridgeError


# ─────────────────────────────────────────────────────────────────────────────
# Data structures for sensor synchronization
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SensorData:
    """Синхронизированные данные от сенсоров"""
    timestamp: Time
    roll: float
    pitch: float
    yaw: float
    altitude: float


# ─────────────────────────────────────────────────────────────────────────────
# Kalman Filter for position smoothing
# ─────────────────────────────────────────────────────────────────────────────

class KalmanFilter3D:
    """Simple Kalman filter for 3D position tracking"""
    
    def __init__(self, process_noise: float = 0.01, measurement_noise: float = 0.1):
        # State: [x, y, z, vx, vy, vz]
        self.state = np.zeros(6)
        self.P = np.eye(6) * 1.0  # Covariance matrix
        
        # Process noise
        self.Q = np.eye(6) * process_noise
        
        # Measurement noise
        self.R = np.eye(3) * measurement_noise
        
        # State transition matrix (constant velocity model)
        self.F = np.eye(6)
        
        # Measurement matrix (we only measure position)
        self.H = np.zeros((3, 6))
        self.H[0, 0] = 1.0
        self.H[1, 1] = 1.0
        self.H[2, 2] = 1.0
        
        self.initialized = False
        self.last_time = None
    
    def predict(self, dt: float):
        """Predict step with time delta"""
        # Update state transition matrix with dt
        self.F[0, 3] = dt
        self.F[1, 4] = dt
        self.F[2, 5] = dt
        
        # Predict state
        self.state = self.F @ self.state
        
        # Predict covariance
        self.P = self.F @ self.P @ self.F.T + self.Q
    
    def update(self, measurement: np.ndarray):
        """Update step with new measurement [x, y, z]"""
        if not self.initialized:
            # Initialize state with first measurement
            self.state[0:3] = measurement
            self.initialized = True
            return self.state[0:3]
        
        # Innovation
        y = measurement - self.H @ self.state
        
        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R
        
        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Update state
        self.state = self.state + K @ y
        
        # Update covariance
        self.P = (np.eye(6) - K @ self.H) @ self.P
        
        return self.state[0:3]
    
    def process(self, measurement: np.ndarray, timestamp: float) -> np.ndarray:
        """Process measurement with timestamp"""
        if self.last_time is not None:
            dt = timestamp - self.last_time
            if dt > 0 and dt < 1.0:  # Sanity check
                self.predict(dt)
        
        self.last_time = timestamp
        return self.update(measurement)


# ─────────────────────────────────────────────────────────────────────────────
# Math helpers
# ─────────────────────────────────────────────────────────────────────────────

def euler_to_rotation_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cr, sr = np.cos(roll),  np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw),   np.sin(yaw)
    Rx = np.array([[1,  0,   0 ], [0,  cr, -sr], [0, sr, cr]], dtype=np.float64)
    Ry = np.array([[cp, 0,   sp], [0,   1,   0], [-sp, 0, cp]], dtype=np.float64)
    Rz = np.array([[cy, -sy, 0 ], [sy, cy,   0], [0,   0,  1]], dtype=np.float64)
    return Rz @ Ry @ Rx


def make_marker_object_points(marker_length: float) -> np.ndarray:
    """
    3D corners of a marker in its own coordinate frame (Z=0 plane).
    Order: top-left, top-right, bottom-right, bottom-left  (OpenCV convention).
    """
    half = marker_length / 2.0
    return np.array([
        [-half,  half, 0.0],
        [ half,  half, 0.0],
        [ half, -half, 0.0],
        [-half, -half, 0.0],
    ], dtype=np.float64)


# ─────────────────────────────────────────────────────────────────────────────
# Node
# ─────────────────────────────────────────────────────────────────────────────

class aruco_detector_node(Node):

    def __init__(self):
        super().__init__('aruco_detector_node')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('camera_params_file',   '/home/drone/drone_ws/src/config/camera_params.yaml')
        self.declare_parameter('aruco_whitelist_file', '/home/drone/drone_ws/src/config/aruco_whitelist_field.yaml')
        self.declare_parameter('field_config_file', '/home/drone/drone_ws/src/config/field.yaml')
        self.declare_parameter('balance',      0.0)
        self.declare_parameter('use_whitelist', True)
        self.declare_parameter('camera_mount_rotation', 'down')  # 'down', 'forward', 'custom'

        cam_file    = self.get_parameter('camera_params_file').value
        aruco_file  = self.get_parameter('aruco_whitelist_file').value
        field_file  = self.get_parameter('field_config_file').value
        self.balance      = float(self.get_parameter('balance').value)
        use_whitelist     = self.get_parameter('use_whitelist').value
        camera_mount      = self.get_parameter('camera_mount_rotation').value

        # ── Runtime state (инициализируем ДО первой загрузки) ─────────────
        self.bridge      = CvBridge()
        self._roll       = 0.0
        self._pitch      = 0.0
        self._yaw        = 0.0
        self._altitude   = None  # высота от дальномера
        self._last_imu_time = None
        self._last_altitude_time = None
        self._sensor_buffer = deque(maxlen=50)  # Буфер синхронизированных данных
        self._max_time_diff = 0.05  # 50мс максимальная разница для синхронизации
        self._imu_lock   = threading.Lock()
        self._map1       = None
        self._map2       = None
        self._K_new      = None
        self._cam_params: Optional[dict] = None
        
        # Kalman filter для каждого маркера
        self._kalman_filters: Dict[int, KalmanFilter3D] = {}
        
        # Параметры для outlier rejection
        self._last_positions: Dict[int, np.ndarray] = {}
        self._last_timestamps: Dict[int, float] = {}
        self._max_velocity = 3.0  # максимальная скорость дрона в м/с
        self._base_position_jump = 0.3  # базовый порог для медленных движений
        
        # Трансформация камеры в зависимости от установки
        self._R_cam_to_body = self._get_camera_transform(camera_mount)

        # ── Загрузка конфигов ──────────────────────────────────────────────
        self._load_camera_params(cam_file)                        # заполняет self._cam_params

        aruco_cfg = self._load_yaml(aruco_file)
        
        # Загружаем карту поля
        self.field_map = self._load_field_map(field_file)
        self.get_logger().info(f'Loaded {len(self.field_map)} markers from field map')
        
        self.target_width   = self._cam_params['target_width']
        self.target_height  = self._cam_params['target_height']
        self.marker_length  = float(aruco_cfg['marker_length'])
        aruco_dict_name     = aruco_cfg['aruco_dict']
        self.allowed_ids    = (
            set(aruco_cfg['allowed_marker_ids']) if use_whitelist else None
        )
        


        # 3D точки маркера для solvePnP
        self.obj_points = make_marker_object_points(self.marker_length)

        self._init_aruco_detector(aruco_dict_name)

        # ── QoS ───────────────────────────────────────────────────────────
        img_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST, depth=1
        )
        rel_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST, depth=10
        )

        # ── Подписки / издатели ───────────────────────────────────────────
        self.create_subscription(Image,   '/camera/image_raw',    self.image_callback,    img_qos)
        self.create_subscription(Vector3, '/uav/ATTITUDE',        self.attitude_callback, rel_qos)
        self.create_subscription(Float64, '/uav/altitude',        self.altitude_callback, rel_qos)

        # Публикуем абсолютную позицию на поле (объединяем функционал global_position_node)
        self.pub_pose_field = self.create_publisher(PointStamped, '/uav/global_position', rel_qos)

        self.get_logger().info('aruco_detector_node ready')

    # ─────────────────────────────────────────────────────────────────────
    # Camera transform
    # ─────────────────────────────────────────────────────────────────────
    
    def _get_camera_transform(self, mount_type: str) -> np.ndarray:
        """
        Возвращает матрицу трансформации камеры в body frame
        
        Args:
            mount_type: 'down', 'down_v2', 'down_v3', 'none' (для отладки)
        """
        if mount_type == 'down':
            # Вариант 1: Камера смотрит вниз, поворот 90° вокруг X
            return np.array([
                [ 1,  0,  0],
                [ 0,  0,  1],
                [ 0, -1,  0]
            ], dtype=np.float64)
        elif mount_type == 'down_v2':
            # Вариант 2: Камера смотрит вниз, поворот 90° вокруг Y
            return np.array([
                [ 0,  0, -1],
                [ 0,  1,  0],
                [ 1,  0,  0]
            ], dtype=np.float64)
        elif mount_type == 'down_v3':
            # Вариант 3: Камера смотрит вниз, Z вниз
            return np.array([
                [ 1,  0,  0],
                [ 0,  1,  0],
                [ 0,  0,  1]
            ], dtype=np.float64)
        elif mount_type == 'none':
            # Без трансформации (для отладки)
            self.get_logger().warn('Camera transform disabled for debugging')
            return np.eye(3, dtype=np.float64)
        else:
            self.get_logger().warn(f'Unknown camera mount type: {mount_type}, using "down"')
            return self._get_camera_transform('down')

    # ─────────────────────────────────────────────────────────────────────
    # Config loaders
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _load_yaml(path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _load_camera_params(self, path: str) -> None:
        d = self._load_yaml(path)
        for key in ('target_width', 'target_height'):
            if key not in d:
                raise KeyError(
                    f"'{key}' is required in {path} but was not found"
                )
        self._cam_params = {
            'width':         d['image_width'],
            'height':        d['image_height'],
            'target_width':  d['target_width'],
            'target_height': d['target_height'],
            'K': np.array(d['camera_matrix']['data'],          dtype=np.float64).reshape(3, 3),
            'D': np.array(d['distortion_coefficients']['data'], dtype=np.float64).reshape(1, 4),
            'R': np.array(d['rectification_matrix']['data'],   dtype=np.float64).reshape(3, 3),
        }
    
    def _load_field_map(self, path: str) -> Dict[int, np.ndarray]:
        """Загружает карту маркеров на поле"""
        d = self._load_yaml(path)
        result: Dict[int, np.ndarray] = {}
        
        # Читаем параметры из конфига
        marker_size = d.get('marker_size', 0.2)
        marker_origin = d.get('marker_origin', 'center')
        
        # Вычисляем смещение
        offset = marker_size / 2.0 if marker_origin == 'corner' else 0.0
        
        for m in d.get('markers', []):
            p = m['position']
            result[int(m['id'])] = np.array([
                p['x'] - offset,
                p['y'] - offset,
                p['z']
            ], dtype=np.float64)
        
        self.get_logger().info(
            f"Marker origin: {marker_origin}, offset: {offset}m"
        )
        
        return result

    # ─────────────────────────────────────────────────────────────────────
    # Undistort maps (lazy init при первом кадре нужного размера)
    # ─────────────────────────────────────────────────────────────────────

    def _init_undistort_maps(self, width: int, height: int) -> None:
        scale_x = width  / self._cam_params['width']
        scale_y = height / self._cam_params['height']
        K_sc = self._cam_params['K'].copy()
        K_sc[0, 0] *= scale_x;  K_sc[1, 1] *= scale_y
        K_sc[0, 2] *= scale_x;  K_sc[1, 2] *= scale_y

        self._K_new = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
            K_sc, self._cam_params['D'], (width, height),
            self._cam_params['R'], balance=self.balance
        )
        self._map1, self._map2 = cv2.fisheye.initUndistortRectifyMap(
            K_sc, self._cam_params['D'], self._cam_params['R'],
            self._K_new, (width, height), cv2.CV_16SC2
        )
        self.get_logger().info(
            f'Undistort maps initialised for {width}×{height}'
        )

    # ─────────────────────────────────────────────────────────────────────
    # ArUco detector
    # ─────────────────────────────────────────────────────────────────────

    def _init_aruco_detector(self, dict_name: str) -> None:
        _dicts = {
            'DICT_4X4_250':  cv2.aruco.DICT_4X4_250,
            'DICT_5X5_250':  cv2.aruco.DICT_5X5_250,
        }
        aruco_dict = cv2.aruco.getPredefinedDictionary(
            _dicts.get(dict_name, cv2.aruco.DICT_4X4_250)
        )
        params = cv2.aruco.DetectorParameters()
        params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR
        self.aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, params)

    def _estimate_pose(
        self, corners_list: list, ids_flat: np.ndarray
    ) -> List[Tuple[np.ndarray, np.ndarray, int]]:
        """
        Возвращает список (rvec, tvec, marker_id) для маркеров из белого списка.
        Использует cv2.solvePnP вместо удалённого estimatePoseSingleMarkers.
        """
        # нулевые коэффициенты искажений — изображение уже rectified
        dist_zero = np.zeros((4, 1), dtype=np.float64)
        poses = []
        for corners, mid in zip(corners_list, ids_flat):
            mid = int(mid)
            if self.allowed_ids and mid not in self.allowed_ids:
                continue
            img_pts = corners[0].astype(np.float64)          # shape (4, 2)
            ok, rvec, tvec = cv2.solvePnP(
                self.obj_points, img_pts,
                self._K_new, dist_zero,
                flags=cv2.SOLVEPNP_IPPE_SQUARE
            )
            if not ok:
                continue
            poses.append((rvec.flatten(), tvec.flatten(), mid))
        return poses

    # ─────────────────────────────────────────────────────────────────────
    # Callbacks
    # ─────────────────────────────────────────────────────────────────────

    def attitude_callback(self, msg: Vector3) -> None:
        """Сохраняем IMU с timestamp"""
        with self._imu_lock:
            self._roll, self._pitch, self._yaw = msg.x, msg.y, msg.z
            self._last_imu_time = self.get_clock().now()

    def altitude_callback(self, msg: Float64) -> None:
        """Сохраняем altitude с timestamp и создаем синхронизированный пакет"""
        with self._imu_lock:
            self._altitude = msg.data
            current_time = self.get_clock().now()
            self._last_altitude_time = current_time
            
            # Проверяем, что IMU данные свежие
            if self._last_imu_time and \
               (current_time - self._last_imu_time).nanoseconds / 1e9 < self._max_time_diff:
                
                # Создаем синхронизированный пакет данных
                sensor_data = SensorData(
                    timestamp=current_time,
                    roll=self._roll,
                    pitch=self._pitch,
                    yaw=self._yaw,
                    altitude=self._altitude
                )
                self._sensor_buffer.append(sensor_data)
    
    def _get_synchronized_sensor_data(self, image_timestamp) -> Optional[SensorData]:
        """Находит ближайшие по времени данные сенсоров"""
        with self._imu_lock:
            if not self._sensor_buffer:
                return None
            
            # Конвертируем ROS timestamp в секунды
            img_time_sec = image_timestamp.sec + image_timestamp.nanosec / 1e9
            
            # Ищем ближайшие данные
            best_match = None
            min_diff = float('inf')
            
            for data in self._sensor_buffer:
                data_time_sec = data.timestamp.nanoseconds / 1e9
                diff = abs(img_time_sec - data_time_sec)
                
                if diff < min_diff:
                    min_diff = diff
                    best_match = data
            
            # Проверяем, что разница не слишком большая
            if min_diff > self._max_time_diff:
                return None
            
            return best_match

    def image_callback(self, msg: Image) -> None:
        # ── Декод ──────────────────────────────────────────────────────
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge error: {e}')
            return

        # ── Ресайз ─────────────────────────────────────────────────────
        h, w = frame.shape[:2]
        if w != self.target_width or h != self.target_height:
            frame = cv2.resize(frame, (self.target_width, self.target_height))

        # ── Undistort (lazy init) ───────────────────────────────────────
        if self._map1 is None:
            self._init_undistort_maps(self.target_width, self.target_height)
        undistorted = cv2.remap(frame, self._map1, self._map2, cv2.INTER_CUBIC)

        # ── Детекция маркеров ──────────────────────────────────────────
        gray = cv2.cvtColor(undistorted, cv2.COLOR_BGR2GRAY)
        try:
            corners, ids, _ = self.aruco_detector.detectMarkers(gray)
        except cv2.error as e:
            self.get_logger().warn(f'ArUco detection error: {e}', throttle_duration_sec=1.0)
            return
        if ids is None:
            return

        # ── Оценка поз (новый API) ─────────────────────────────────────
        poses = self._estimate_pose(corners, ids.flatten())
        if not poses:
            return

        # ── Получаем синхронизированные данные сенсоров ────────────────
        sensor_data = self._get_synchronized_sensor_data(msg.header.stamp)
        if sensor_data is None:
            self.get_logger().warn('No synchronized sensor data', throttle_duration_sec=1.0)
            return
        
        roll, pitch, yaw = sensor_data.roll, sensor_data.pitch, sensor_data.yaw
        altitude = sensor_data.altitude

        # Если нет данных о высоте, пропускаем
        if altitude is None:
            self.get_logger().warn('No altitude data available', throttle_duration_sec=1.0)
            return

        R_b2w = euler_to_rotation_matrix(roll, pitch, yaw)
        
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        # ── Обработка всех видимых маркеров с взвешенным усреднением ────
        weighted_positions = []
        weights = []
        valid_markers = []

        for rvec, tvec, mid in poses:
            # Проверяем, есть ли маркер в карте поля
            if mid not in self.field_map:
                self.get_logger().warn(
                    f'Marker {mid} not in field map, skipping',
                    throttle_duration_sec=2.0
                )
                continue
            
            R_cm, _ = cv2.Rodrigues(rvec)
            
            # Инвертируем: позиция камеры относительно маркера
            R_mc = R_cm.T
            t_cam_in_marker = -R_mc @ tvec.reshape(3, 1)
            
            # Преобразуем из системы камеры в body frame дрона
            t_body_in_marker = self._R_cam_to_body @ t_cam_in_marker
            
            # Ориентация маркера в body frame
            R_marker_in_body = self._R_cam_to_body @ R_cm
            
            # Позиция дрона в системе координат маркера
            t_drone_in_marker = R_marker_in_body.T @ t_body_in_marker
            t_relative = t_drone_in_marker.flatten()
            
            # Используем высоту от дальномера
            t_relative = np.array([
                t_relative[0],
                t_relative[1],
                altitude
            ])
            
            # Позиция маркера на поле
            marker_world_pos = self.field_map[mid]
            
            # АБСОЛЮТНАЯ позиция дрона = позиция маркера + относительная позиция
            t_absolute = marker_world_pos + t_relative
            
            # ── Outlier rejection с учетом времени ────────────────────
            if mid in self._last_positions and mid in self._last_timestamps:
                dt = timestamp - self._last_timestamps[mid]
                if dt > 0 and dt < 1.0:
                    position_diff = np.linalg.norm(t_absolute - self._last_positions[mid])
                    max_jump = self._base_position_jump + self._max_velocity * dt
                    
                    if position_diff > max_jump:
                        self.get_logger().warn(
                            f'Marker {mid}: position jump {position_diff:.2f}m > {max_jump:.2f}m, rejecting',
                            throttle_duration_sec=1.0
                        )
                        continue
            
            # Обновляем timestamp
            self._last_timestamps[mid] = timestamp
            
            # ── Kalman filtering ───────────────────────────────────────
            if mid not in self._kalman_filters:
                self._kalman_filters[mid] = KalmanFilter3D(
                    process_noise=0.02,
                    measurement_noise=0.05
                )
            
            t_filtered = self._kalman_filters[mid].process(t_absolute, timestamp)
            self._last_positions[mid] = t_filtered
            
            # Вес зависит от расстояния до маркера (ближе = больше вес)
            distance = np.linalg.norm(tvec)
            weight = 1.0 / (distance + 0.1)
            
            weighted_positions.append(t_filtered)
            weights.append(weight)
            valid_markers.append(mid)
        
        # Если нет валидных маркеров, выходим
        if not weighted_positions:
            return
        
        # Нормализуем веса и вычисляем взвешенную среднюю
        weights = np.array(weights)
        weights /= weights.sum()
        final_position = np.average(weighted_positions, axis=0, weights=weights)
        
        # Публикуем абсолютную позицию на поле
        # Используем PointStamped (только позиция без ориентации)
        field_msg = PointStamped()
        field_msg.header = msg.header
        field_msg.header.frame_id = 'field'
        field_msg.point = Point(
            x=float(final_position[0]),
            y=float(final_position[1]),
            z=float(final_position[2])
        )
        
        self.pub_pose_field.publish(field_msg)
        
        # Логируем для отладки
        self.get_logger().info(
            f'Fused {len(valid_markers)} markers {valid_markers}, '
            f'pos: [{final_position[0]:.2f}, {final_position[1]:.2f}, {final_position[2]:.2f}]',
            throttle_duration_sec=1.0
        )


# ─────────────────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = aruco_detector_node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
