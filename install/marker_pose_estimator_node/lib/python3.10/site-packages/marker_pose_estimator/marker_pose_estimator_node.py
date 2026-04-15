#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MARKER POSE ESTIMATOR NODE
Оценивает 6DOF позы маркеров относительно камеры с синхронизацией сенсоров
"""

import cv2
import numpy as np
import yaml
import threading
from typing import Optional
from collections import deque
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from rclpy.time import Time

from geometry_msgs.msg import Vector3, Pose, Point, Quaternion, TransformStamped
from std_msgs.msg import Float64
from tf2_ros import TransformBroadcaster
from drone_msgs.msg import ArucoDetectionArray, MarkerPose, MarkerPoseArray


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
# Math helpers
# ─────────────────────────────────────────────────────────────────────────────

def euler_to_rotation_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]], dtype=np.float64)
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]], dtype=np.float64)
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]], dtype=np.float64)
    return Rz @ Ry @ Rx


def rotation_matrix_to_quaternion(R: np.ndarray) -> np.ndarray:
    """Преобразует матрицу поворота в кватернион [x, y, z, w]"""
    trace = np.trace(R)
    if trace > 0:
        s = 0.5 / np.sqrt(trace + 1.0)
        w = 0.25 / s
        x = (R[2, 1] - R[1, 2]) * s
        y = (R[0, 2] - R[2, 0]) * s
        z = (R[1, 0] - R[0, 1]) * s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s
    return np.array([x, y, z, w])


def make_marker_object_points(marker_length: float) -> np.ndarray:
    """3D углы маркера в его системе координат (Z=0 plane)"""
    half = marker_length / 2.0
    return np.array([
        [-half, half, 0.0],
        [half, half, 0.0],
        [half, -half, 0.0],
        [-half, -half, 0.0],
    ], dtype=np.float64)


# ─────────────────────────────────────────────────────────────────────────────
# Node
# ─────────────────────────────────────────────────────────────────────────────

class MarkerPoseEstimatorNode(Node):

    def __init__(self):
        super().__init__('marker_pose_estimator_node')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('camera_params_file', '/home/drone/drone_ws/src/config/camera_params.yaml')
        self.declare_parameter('aruco_whitelist_file', '/home/drone/drone_ws/src/config/aruco_whitelist_field.yaml')
        self.declare_parameter('camera_mount_rotation', 'down')

        cam_file = self.get_parameter('camera_params_file').value
        aruco_file = self.get_parameter('aruco_whitelist_file').value
        camera_mount = self.get_parameter('camera_mount_rotation').value

        # ── TF Broadcasting параметры ──────────────────────────────────────
        self.declare_parameter('send_tf', True)
        self.declare_parameter('frame_id_prefix', 'aruco_')
        self.send_tf = self.get_parameter('send_tf').value
        self.frame_id_prefix = self.get_parameter('frame_id_prefix').value

        # ── Runtime state ──────────────────────────────────────────────────
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._altitude = None
        self._last_imu_time = None
        self._last_altitude_time = None
        self._sensor_buffer = deque(maxlen=50)
        self._max_time_diff = 0.050  # FIXED: 50мс для более надежной синхронизации
        self._imu_lock = threading.Lock()

        # ── Загрузка конфигов ──────────────────────────────────────────────
        self._load_camera_params(cam_file)
        self._load_sensor_offsets(cam_file)
        aruco_cfg = self._load_yaml(aruco_file)
        
        self.marker_length = float(aruco_cfg['marker_length'])
        self.obj_points = make_marker_object_points(self.marker_length)
        
        # Трансформация камеры
        self._R_cam_to_body = self._get_camera_transform(camera_mount)

        # ── TF Broadcaster ─────────────────────────────────────────────────
        if self.send_tf:
            self.tf_broadcaster = TransformBroadcaster(self)
            self.get_logger().info(f'TF broadcasting enabled with prefix: {self.frame_id_prefix}')
        else:
            self.tf_broadcaster = None
            self.get_logger().info('TF broadcasting disabled')

        # ── QoS ────────────────────────────────────────────────────────────
        rel_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST, depth=10
        )

        # ── Подписки / издатели ────────────────────────────────────────────
        self.create_subscription(ArucoDetectionArray, '/aruco/detections', self.detections_callback, rel_qos)
        self.create_subscription(Vector3, '/uav/ATTITUDE', self.attitude_callback, rel_qos)
        self.create_subscription(Float64, '/uav/altitude', self.altitude_callback, rel_qos)
        
        self.pub_poses = self.create_publisher(MarkerPoseArray, '/aruco/marker_poses', rel_qos)

        self.get_logger().info('marker_pose_estimator_node ready')

    # ───────────────────────────────────────────────────────────────────────
    # Camera transform
    # ───────────────────────────────────────────────────────────────────────

    def _get_camera_transform(self, mount_type: str) -> np.ndarray:
        """Возвращает матрицу трансформации камеры в body frame"""
        
        # Стандартная система координат камеры OpenCV:
        # X = right, Y = down, Z = forward
        
        # Body frame дрона (NED или FRD):
        # X = forward, Y = right, Z = down
        
        if mount_type == 'down':
            # Оригинальная версия
            return np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=np.float64)
        
        elif mount_type == 'down_v2':
            return np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]], dtype=np.float64)
        
        elif mount_type == 'down_v3':
            return np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64)
        
        elif mount_type == 'down_correct':
            # Камера смотрит вниз: X_cam=forward, Y_cam=right, Z_cam=down
            # Body: X_body=forward, Y_body=right, Z_body=up
            return np.array([[1, 0, 0], [0, 1, 0], [0, 0, -1]], dtype=np.float64)
        
        elif mount_type == 'down_cw90':
            # Камера повернута на 90° по часовой стрелке
            return np.array([[0, 1, 0], [-1, 0, 0], [0, 0, -1]], dtype=np.float64)
        
        elif mount_type == 'down_180':
            # Камера повернута на 180°
            return np.array([[-1, 0, 0], [0, -1, 0], [0, 0, -1]], dtype=np.float64)
        
        elif mount_type == 'down_ccw90':
            # Камера повернута на 270° (90° против часовой)
            return np.array([[0, -1, 0], [1, 0, 0], [0, 0, -1]], dtype=np.float64)
        
        elif mount_type == 'none':
            self.get_logger().warn('Camera transform disabled for debugging')
            return np.eye(3, dtype=np.float64)
        
        else:
            self.get_logger().warn(f'Unknown camera mount type: {mount_type}, using "down"')
            return self._get_camera_transform('down')

    # ───────────────────────────────────────────────────────────────────────
    # Config loaders
    # ───────────────────────────────────────────────────────────────────────

    @staticmethod
    def _load_yaml(path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _load_camera_params(self, path: str) -> None:
        d = self._load_yaml(path)
        self._K_new = np.array(d['camera_matrix']['data'], dtype=np.float64).reshape(3, 3)
    
    def _load_sensor_offsets(self, path: str) -> None:
        """Загружает параметры смещения датчиков"""
        d = self._load_yaml(path)
        
        # Проверяем наличие секции sensor_offsets
        if 'sensor_offsets' not in d:
            self.get_logger().warn('No sensor_offsets in config, using zero offsets')
            self._camera_offset = np.zeros(3, dtype=np.float64)
            self._rangefinder_offset = np.zeros(3, dtype=np.float64)
            self._enable_offset_compensation = False
            self._enable_tilt_compensation = False
            return
        
        offsets = d['sensor_offsets']
        
        # Загружаем смещение камеры
        cam_offset = offsets.get('camera_to_body', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        self._camera_offset = np.array([
            cam_offset['x'],
            cam_offset['y'],
            cam_offset['z']
        ], dtype=np.float64)
        
        # Загружаем смещение дальномера
        rf_offset = offsets.get('rangefinder_to_body', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        self._rangefinder_offset = np.array([
            rf_offset['x'],
            rf_offset['y'],
            rf_offset['z']
        ], dtype=np.float64)
        
        # Флаги компенсации
        self._enable_offset_compensation = offsets.get('enable_offset_compensation', True)
        self._enable_tilt_compensation = offsets.get('enable_tilt_compensation', True)
        
        # Вычисляем относительное смещение дальномера от камеры
        self._rangefinder_to_camera_offset = self._rangefinder_offset - self._camera_offset
        
        self.get_logger().info(
            f'Sensor offsets loaded: '
            f'camera={self._camera_offset}, '
            f'rangefinder={self._rangefinder_offset}, '
            f'relative={self._rangefinder_to_camera_offset}, '
            f'offset_comp={self._enable_offset_compensation}, '
            f'tilt_comp={self._enable_tilt_compensation}'
        )

    # ───────────────────────────────────────────────────────────────────────
    # Sensor synchronization
    # ───────────────────────────────────────────────────────────────────────

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
            
            if self._last_imu_time and \
               (current_time - self._last_imu_time).nanoseconds / 1e9 < self._max_time_diff:
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
            
            img_time_sec = image_timestamp.sec + image_timestamp.nanosec / 1e9
            
            best_match = None
            min_diff = float('inf')
            
            for data in self._sensor_buffer:
                data_time_sec = data.timestamp.nanoseconds / 1e9
                diff = abs(img_time_sec - data_time_sec)
                
                if diff < min_diff:
                    min_diff = diff
                    best_match = data
            
            if min_diff > self._max_time_diff:
                return None
            
            return best_match

    # ───────────────────────────────────────────────────────────────────────
    # Pose estimation
    # ───────────────────────────────────────────────────────────────────────

    def detections_callback(self, msg: ArucoDetectionArray) -> None:
        # ── Получаем синхронизированные данные сенсоров ────────────────────
        sensor_data = self._get_synchronized_sensor_data(msg.header.stamp)
        if sensor_data is None:
            self.get_logger().warn('No synchronized sensor data', throttle_duration_sec=1.0)
            return
        
        if sensor_data.altitude is None:
            self.get_logger().warn('No altitude data available', throttle_duration_sec=1.0)
            return

        # Нулевые коэффициенты искажений — изображение уже rectified
        dist_zero = np.zeros((4, 1), dtype=np.float64)
        
        # ── ОПТИМИЗАЦИЯ: Вычисляем один раз за кадр ───────────────────────
        # Матрица поворота дрона (body frame → world frame)
        R_body_world = euler_to_rotation_matrix(
            sensor_data.roll, 
            sensor_data.pitch, 
            sensor_data.yaw
        )
        
        # Корректируем высоту дальномера с учетом наклона
        if self._enable_tilt_compensation:
            # Вектор "вниз" в body frame
            down_vector_body = np.array([0.0, 0.0, 1.0])
            # Трансформируем в мировую систему координат
            down_vector_world = R_body_world @ down_vector_body
            # Вертикальная компонента (проекция на ось Z)
            vertical_scale = down_vector_world[2]
            
            # Корректируем высоту
            if abs(vertical_scale) > 0.1:  # Защита от деления на ноль
                corrected_altitude = sensor_data.altitude * vertical_scale
            else:
                corrected_altitude = sensor_data.altitude
                self.get_logger().warn(
                    f'Large tilt detected (vertical_scale={vertical_scale:.2f}), '
                    f'altitude correction may be inaccurate',
                    throttle_duration_sec=2.0
                )
        else:
            corrected_altitude = sensor_data.altitude
        # ───────────────────────────────────────────────────────────────────
        
        marker_poses = []
        transforms = []  # НОВОЕ: список TF трансформаций
        
        for detection in msg.detections:
            # Преобразуем углы обратно в формат OpenCV
            corners_flat = np.array(detection.corners, dtype=np.float64)
            img_pts = corners_flat.reshape(4, 2)
            
            # solvePnP для оценки позы
            ok, rvec, tvec = cv2.solvePnP(
                self.obj_points, img_pts,
                self._K_new, dist_zero,
                flags=cv2.SOLVEPNP_IPPE_SQUARE
            )
            
            if not ok:
                continue
            
            # ═══════════════════════════════════════════════════════════════
            # TF BROADCASTING (маркер в camera frame, БЕЗ инверсии)
            # ═══════════════════════════════════════════════════════════════
            if self.send_tf:
                transform = TransformStamped()
                transform.header.stamp = msg.header.stamp
                transform.header.frame_id = msg.header.frame_id  # camera frame
                transform.child_frame_id = f'{self.frame_id_prefix}{detection.marker_id}'
                
                # Позиция маркера в camera frame (оригинальный tvec)
                transform.transform.translation.x = float(tvec[0])
                transform.transform.translation.y = float(tvec[1])
                transform.transform.translation.z = float(tvec[2])
                
                # Ориентация маркера из rvec (axis-angle → quaternion)
                angle = np.linalg.norm(rvec)
                if angle > 0:
                    axis = rvec.flatten() / angle
                    qw = np.cos(angle / 2)
                    qx = axis[0] * np.sin(angle / 2)
                    qy = axis[1] * np.sin(angle / 2)
                    qz = axis[2] * np.sin(angle / 2)
                else:
                    qw, qx, qy, qz = 1.0, 0.0, 0.0, 0.0
                
                transform.transform.rotation.x = qx
                transform.transform.rotation.y = qy
                transform.transform.rotation.z = qz
                transform.transform.rotation.w = qw
                
                transforms.append(transform)
            # ═══════════════════════════════════════════════════════════════
            
            # ── ДОБАВЛЕНО: Проверка reprojection error ─────────────────────
            # Проецируем 3D точки обратно на изображение
            projected_pts, _ = cv2.projectPoints(
                self.obj_points, rvec, tvec, self._K_new, dist_zero
            )
            projected_pts = projected_pts.reshape(-1, 2)
            
            # Вычисляем среднюю ошибку репроекции
            reprojection_error = np.mean(np.linalg.norm(img_pts - projected_pts, axis=1))
            
            # Отклоняем измерения с большой ошибкой (порог 2 пикселя)
            if reprojection_error > 2.0:
                self.get_logger().warn(
                    f'Marker {detection.marker_id}: high reprojection error {reprojection_error:.2f}px, rejecting',
                    throttle_duration_sec=1.0
                )
                continue
            # ───────────────────────────────────────────────────────────────
            
            # Преобразуем rvec в матрицу поворота
            R_cm, _ = cv2.Rodrigues(rvec.flatten())
            
            # solvePnP дает нам трансформацию: маркер → камера
            # tvec - позиция маркера в системе координат камеры
            # R_cm - ориентация маркера в системе координат камеры
            
            # Шаг 1: Трансформируем из системы камеры в body frame
            t_marker_in_body = self._R_cam_to_body @ tvec.reshape(3, 1)
            R_marker_in_body = self._R_cam_to_body @ R_cm
            
            # Шаг 2: Инвертируем - получаем позицию body относительно маркера
            # В системе координат маркера
            R_body_in_marker = R_marker_in_body.T
            t_body_in_marker = -R_body_in_marker @ t_marker_in_body
            
            t_relative = t_body_in_marker.flatten()
            
            # ═══════════════════════════════════════════════════════════════
            # КАЛИБРОВКА: Компенсация смещения датчиков
            # ═══════════════════════════════════════════════════════════════
            
            # Шаг 1: Компенсация смещения камеры относительно центра дрона
            # t_relative сейчас - это позиция центра дрона относительно маркера,
            # но вычислена она от камеры. Нужно учесть смещение камеры.
            if self._enable_offset_compensation:
                # Трансформируем смещение камеры в систему координат маркера
                camera_offset_in_marker = R_body_in_marker @ self._camera_offset.reshape(3, 1)
                t_relative = t_relative - camera_offset_in_marker.flatten()
            
            # Шаг 2: Компенсация смещения дальномера
            # (corrected_altitude уже вычислен вне цикла)
            if self._enable_offset_compensation:
                # Смещение дальномера относительно камеры в body frame
                # Трансформируем в систему координат маркера
                rf_offset_in_marker = R_body_in_marker @ self._rangefinder_to_camera_offset.reshape(3, 1)
                
                # Применяем смещение к высоте
                # Используем только Z-компоненту смещения для высоты
                altitude_offset = rf_offset_in_marker[2, 0]
                corrected_altitude += altitude_offset
            
            # Финальная позиция с скорректированной высотой
            t_relative = np.array([
                t_relative[0],
                t_relative[1],
                corrected_altitude
            ])
            
            # ═══════════════════════════════════════════════════════════════
            
            # Создаем сообщение с позой
            marker_pose = MarkerPose()
            marker_pose.marker_id = detection.marker_id
            marker_pose.pose = Pose()
            marker_pose.pose.position = Point(
                x=float(t_relative[0]),
                y=float(t_relative[1]),
                z=float(t_relative[2])
            )
            
            # Преобразуем матрицу поворота в кватернион
            quat = rotation_matrix_to_quaternion(R_marker_in_body)
            marker_pose.pose.orientation = Quaternion(
                x=float(quat[0]),
                y=float(quat[1]),
                z=float(quat[2]),
                w=float(quat[3])
            )
            
            marker_poses.append(marker_pose)
        
        if not marker_poses:
            return
        
        # ── Публикация TF трансформаций ────────────────────────────────────
        if self.send_tf and transforms:
            self.tf_broadcaster.sendTransform(transforms)
            self.get_logger().debug(
                f'Published TF for {len(transforms)} markers',
                throttle_duration_sec=1.0
            )
        
        # ── Публикация MarkerPoseArray ─────────────────────────────────────
        pose_array = MarkerPoseArray()
        pose_array.header = msg.header
        pose_array.poses = marker_poses
        self.pub_poses.publish(pose_array)
        
        self.get_logger().info(
            f'Estimated poses for {len(marker_poses)} markers: {[p.marker_id for p in marker_poses]}',
            throttle_duration_sec=1.0
        )


# ───────────────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = MarkerPoseEstimatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
