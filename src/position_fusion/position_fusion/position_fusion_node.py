#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSITION FUSION NODE
Слияние данных от нескольких маркеров с фильтрацией Калмана
"""

import numpy as np
import yaml
from typing import Dict

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import PointStamped, Point
from drone_msgs.msg import MarkerPoseArray

# Import from drone_utils ROS2 package
from drone_utils.kalman_filter import KalmanFilter3D
from drone_utils.aperiodic_filter import AdaptiveAperiodicFilter


# ─────────────────────────────────────────────────────────────────────────────
# Node
# ─────────────────────────────────────────────────────────────────────────────

class PositionFusionNode(Node):

    def __init__(self):
        super().__init__('position_fusion_node')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('field_config_file', '/home/drone/drone_ws/src/config/field.yaml')

        field_file = self.get_parameter('field_config_file').value

        # ── Runtime state ──────────────────────────────────────────────────
        # Kalman filter для каждого маркера
        self._kalman_filters: Dict[int, KalmanFilter3D] = {}
        
        # Апериодический фильтр для финальной позиции
        self._aperiodic_filter = AdaptiveAperiodicFilter(
            time_constant_slow=0.15,   # Сглаживание при медленном движении
            time_constant_fast=0.05,   # Быстрая реакция при быстром движении
            velocity_threshold=0.5,    # Порог переключения (м/с)
            gain=1.0
        )
        self._last_fused_time = None
        
        # Параметры для outlier rejection
        self._last_positions: Dict[int, np.ndarray] = {}
        self._last_timestamps: Dict[int, float] = {}
        self._max_velocity = 5.0  # INCREASED: максимальная скорость дрона в м/с
        self._base_position_jump = 0.5  # INCREASED: базовый порог для медленных движений

        # ── Загрузка конфигов ──────────────────────────────────────────────
        self.field_map = self._load_field_map(field_file)
        self.get_logger().info(f'Loaded {len(self.field_map)} markers from field map')

        # ── QoS ────────────────────────────────────────────────────────────
        rel_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST, depth=10
        )

        # ── Подписки / издатели ────────────────────────────────────────────
        self.create_subscription(MarkerPoseArray, '/aruco/marker_poses', self.poses_callback, rel_qos)
        self.pub_global_position = self.create_publisher(PointStamped, '/uav/global_position', rel_qos)

        self.get_logger().info('position_fusion_node ready')

    # ───────────────────────────────────────────────────────────────────────
    # Config loaders
    # ───────────────────────────────────────────────────────────────────────

    @staticmethod
    def _load_yaml(path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

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

    # ───────────────────────────────────────────────────────────────────────
    # Position fusion
    # ───────────────────────────────────────────────────────────────────────

    def poses_callback(self, msg: MarkerPoseArray) -> None:
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        weighted_positions = []
        weights = []
        valid_markers = []

        for marker_pose in msg.poses:
            mid = marker_pose.marker_id
            
            # Проверяем, есть ли маркер в карте поля
            if mid not in self.field_map:
                self.get_logger().warn(
                    f'Marker {mid} not in field map, skipping',
                    throttle_duration_sec=2.0
                )
                continue
            
            # Относительная позиция дрона от маркера
            t_relative = np.array([
                marker_pose.pose.position.x,
                marker_pose.pose.position.y,
                marker_pose.pose.position.z
            ])
            
            # Позиция маркера на поле
            marker_world_pos = self.field_map[mid]
            
            # АБСОЛЮТНАЯ позиция дрона = позиция маркера + относительная позиция
            t_absolute = marker_world_pos + t_relative
            
            # ── Outlier rejection с учетом времени ─────────────────────────
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
            
            # ── Kalman filtering ────────────────────────────────────────────
            if mid not in self._kalman_filters:
                self._kalman_filters[mid] = KalmanFilter3D(
                    process_noise=0.02,
                    measurement_noise=0.05
                )
            
            t_filtered = self._kalman_filters[mid].process(t_absolute, timestamp)
            self._last_positions[mid] = t_filtered
            
            # Вес зависит от расстояния до маркера (ближе = больше вес)
            horizontal_distance = np.linalg.norm(t_relative[:2])
            weight = 1.0 / (horizontal_distance + 0.1)
            
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
        
        # Применяем апериодический фильтр к финальной позиции
        if self._last_fused_time is not None:
            dt = timestamp - self._last_fused_time
            if dt > 0 and dt < 1.0:  # Sanity check
                final_position = self._aperiodic_filter.update(final_position, dt)
        else:
            # Первая итерация - инициализируем фильтр
            final_position = self._aperiodic_filter.update(final_position, 0.033)  # ~30Hz
        
        self._last_fused_time = timestamp

        self._cleanup_stale_filters(timestamp)
        
        # Публикуем абсолютную позицию на поле
        field_msg = PointStamped()
        field_msg.header = msg.header
        field_msg.header.frame_id = 'field'
        field_msg.point = Point(
            x=float(final_position[0]),
            y=float(final_position[1]),
            z=float(final_position[2])
        )
        
        self.pub_global_position.publish(field_msg)
        
        # Логируем для отладки
        self.get_logger().info(
            f'Fused {len(valid_markers)} markers {valid_markers}, '
            f'pos: [{final_position[0]:.2f}, {final_position[1]:.2f}, {final_position[2]:.2f}]',
            throttle_duration_sec=1.0
        )

    def _cleanup_stale_filters(self, current_timestamp: float, max_age: float = 5.0) -> None:
        """Удаляет Kalman-фильтры для маркеров, не обновлявшихся >5 секунд"""
        stale_ids = [
            mid for mid, ts in self._last_timestamps.items()
            if current_timestamp - ts > max_age
        ]
        for mid in stale_ids:
            self._last_timestamps.pop(mid, None)
            self._last_positions.pop(mid, None)
            self._kalman_filters.pop(mid, None)
            self.get_logger().debug(f'Removed stale Kalman filter for marker {mid}')


# ───────────────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = PositionFusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

