#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLOBAL POSITION NODE
Преобразует позицию дрона относительно маркеров в абсолютную позицию на поле
Усредняет данные от нескольких маркеров и применяет фильтр Калмана
"""

import numpy as np
import yaml
from typing import Dict
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import PoseStamped, PointStamped


# ─────────────────────────────────────────────────────────────────────────────
# Quaternion math helpers
# ─────────────────────────────────────────────────────────────────────────────

def quaternion_multiply(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    """Multiply two quaternions [x, y, z, w]"""
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    return np.array([
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
        w1*w2 - x1*x2 - y1*y2 - z1*z2
    ])


def quaternion_slerp(q1: np.ndarray, q2: np.ndarray, t: float) -> np.ndarray:
    """Spherical linear interpolation between two quaternions"""
    dot = np.dot(q1, q2)
    
    # If dot < 0, negate q2 to take shorter path
    if dot < 0.0:
        q2 = -q2
        dot = -dot
    
    # If quaternions are very close, use linear interpolation
    if dot > 0.9995:
        result = q1 + t * (q2 - q1)
        return result / np.linalg.norm(result)
    
    # Calculate angle between quaternions
    theta_0 = np.arccos(np.clip(dot, -1.0, 1.0))
    theta = theta_0 * t
    
    q3 = q2 - q1 * dot
    q3 = q3 / np.linalg.norm(q3)
    
    return q1 * np.cos(theta) + q3 * np.sin(theta)


def average_quaternions_weighted(quaternions: list, weights: list) -> np.ndarray:
    """
    Weighted average of quaternions using iterative method
    Based on: Markley et al. "Averaging Quaternions"
    """
    if len(quaternions) == 1:
        q = quaternions[0].copy()
        # Ensure w is positive for consistent representation
        if q[3] < 0:
            q = -q
        return q
    
    # Normalize weights
    weights = np.array(weights)
    weights = weights / np.sum(weights)
    
    # Start with first quaternion (ensure positive w)
    q_avg = quaternions[0].copy()
    if q_avg[3] < 0:
        q_avg = -q_avg
    
    # Iterative refinement
    for _ in range(10):  # Usually converges in 2-3 iterations
        error_vectors = []
        for q, w in zip(quaternions, weights):
            # Ensure shortest path and positive w
            if np.dot(q_avg, q) < 0:
                q = -q
            
            # Compute error quaternion
            q_error = quaternion_multiply(q, np.array([
                -q_avg[0], -q_avg[1], -q_avg[2], q_avg[3]
            ]))
            
            # Extract rotation vector (small angle approximation)
            if q_error[3] < 0:
                q_error = -q_error
            
            error_vectors.append(w * q_error[:3])
        
        # Average error vector
        e_avg = np.sum(error_vectors, axis=0)
        
        # Check convergence
        if np.linalg.norm(e_avg) < 1e-6:
            break
        
        # Update average quaternion
        angle = np.linalg.norm(e_avg)
        if angle > 1e-10:
            axis = e_avg / angle
            half_angle = angle / 2
            q_delta = np.array([
                axis[0] * np.sin(half_angle),
                axis[1] * np.sin(half_angle),
                axis[2] * np.sin(half_angle),
                np.cos(half_angle)
            ])
            q_avg = quaternion_multiply(q_delta, q_avg)
            q_avg = q_avg / np.linalg.norm(q_avg)
    
    # Final normalization: ensure w is positive for consistent output
    if q_avg[3] < 0:
        q_avg = -q_avg
    
    return q_avg


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


class GlobalPositionNode(Node):

    def __init__(self):
        super().__init__('global_position')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('field_config_file', '/home/drone/drone_ws/src/config/field.yaml')
        self.declare_parameter('measurement_timeout', 0.1)
        
        field_file = self.get_parameter('field_config_file').value
        self.measurement_timeout = self.get_parameter('measurement_timeout').value

        # ── Загрузка карты поля ────────────────────────────────────────────
        self.field_map: Dict[int, np.ndarray] = self._load_field_map(field_file)
        self.get_logger().info(
            f'Field map loaded: {len(self.field_map)} markers'
        )

        # ── QoS ────────────────────────────────────────────────────────────
        rel_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST, depth=10
        )

        # ── Подписки / издатели ────────────────────────────────────────────
        self.create_subscription(
            PoseStamped, 
            '/aruco/drone_pose_marker', 
            self.marker_pose_callback, 
            rel_qos
        )

        # Абсолютная поза на поле (только координаты)
        self.pub_pose_field = self.create_publisher(
            PointStamped, 
            '/aruco/drone_pose_field', 
            rel_qos
        )

        # Буфер для накопления измерений от разных маркеров
        self.measurements: Dict[int, tuple] = {}  # marker_id -> (pose, timestamp)
        
        # Kalman filter for position smoothing
        self.kalman_filter = KalmanFilter3D(process_noise=0.01, measurement_noise=0.05)

        self.get_logger().info('GlobalPositionNode ready')

    # ─────────────────────────────────────────────────────────────────────
    # Config loader
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _load_yaml(path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _load_field_map(self, path: str) -> Dict[int, np.ndarray]:
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
    # Callback
    # ─────────────────────────────────────────────────────────────────────

    def marker_pose_callback(self, msg: PoseStamped) -> None:
        """
        Получает позицию дрона относительно маркера и вычисляет абсолютную позицию
        """
        # Извлекаем ID маркера из frame_id (формат: 'marker_{id}')
        frame_id = msg.header.frame_id
        if not frame_id.startswith('marker_'):
            self.get_logger().warn(f'Invalid frame_id: {frame_id}')
            return

        try:
            marker_id = int(frame_id.split('_')[1])
        except (IndexError, ValueError):
            self.get_logger().warn(f'Cannot parse marker_id from: {frame_id}')
            return

        # Проверяем, есть ли маркер в карте поля
        if marker_id not in self.field_map:
            self.get_logger().warn(f'Marker {marker_id} not in field map')
            return

        # Позиция маркера на поле
        marker_world = self.field_map[marker_id]

        # Позиция дрона относительно маркера (уже в мировой системе координат)
        drone_relative = np.array([
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z
        ], dtype=np.float64)

        # Абсолютная позиция дрона на поле
        drone_world = marker_world + drone_relative
        
        # Debug для маркера 136
        if marker_id == 136:
            self.get_logger().info(
                f'M136: marker_pos=[{marker_world[0]:.3f},{marker_world[1]:.3f},{marker_world[2]:.3f}] '
                f'drone_rel=[{drone_relative[0]:.3f},{drone_relative[1]:.3f},{drone_relative[2]:.3f}] '
                f'drone_world=[{drone_world[0]:.3f},{drone_world[1]:.3f},{drone_world[2]:.3f}]',
                throttle_duration_sec=0.5
            )
        
        # Сохраняем измерение в буфер (без ориентации из ArUco)
        current_time = time.time()
        self.measurements[marker_id] = (drone_world, current_time)
        
        # Удаляем устаревшие измерения
        self._cleanup_old_measurements(current_time)
        
        # Если есть хотя бы одно измерение, вычисляем усредненную позицию
        if len(self.measurements) > 0:
            self._publish_fused_position(msg.header)

    def _cleanup_old_measurements(self, current_time: float) -> None:
        """Удаляет устаревшие измерения из буфера"""
        to_remove = []
        for marker_id, (_, timestamp) in self.measurements.items():
            if current_time - timestamp > self.measurement_timeout:
                to_remove.append(marker_id)
        
        for marker_id in to_remove:
            del self.measurements[marker_id]

    def _publish_fused_position(self, header) -> None:
        """Вычисляет взвешенное усреднение позиций и публикует результат"""
        if len(self.measurements) == 0:
            return
        
        positions = []
        weights = []
        
        for marker_id, (position, _) in self.measurements.items():
            positions.append(position)
            
            # Вес обратно пропорционален расстоянию до маркера
            distance = np.linalg.norm(position[:2])  # XY distance
            weight = 1.0 / (distance + 0.1)  # +0.1 чтобы избежать деления на 0
            weights.append(weight)
        
        # Нормализуем веса
        weights = np.array(weights)
        weights = weights / np.sum(weights)
        
        # Взвешенное усреднение позиций
        avg_position = np.average(positions, axis=0, weights=weights)
        
        # Применяем фильтр Калмана к позиции
        timestamp = time.time()
        filtered_position = self.kalman_filter.process(avg_position, timestamp)
        
        # Публикуем только координаты (без ориентации)
        field_msg = PointStamped()
        field_msg.header = header
        field_msg.header.frame_id = 'field'
        field_msg.point.x = float(filtered_position[0])
        field_msg.point.y = float(filtered_position[1])
        field_msg.point.z = float(filtered_position[2])

        self.pub_pose_field.publish(field_msg)


# ─────────────────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = GlobalPositionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
