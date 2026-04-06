#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLOBAL POSITION NODE
Преобразует позицию дрона относительно маркеров в абсолютную позицию на поле
"""

import numpy as np
import yaml
from typing import Dict

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import PoseStamped, Point, Quaternion


class GlobalPositionNode(Node):

    def __init__(self):
        super().__init__('global_position_node')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('field_config_file', '/home/drone/drone_ws/src/config/field.yaml')
        field_file = self.get_parameter('field_config_file').value

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

        # Абсолютная поза на поле
        self.pub_pose_field = self.create_publisher(
            PoseStamped, 
            '/aruco/drone_pose_field', 
            rel_qos
        )

        # Буфер для накопления измерений от разных маркеров
        self.measurements: Dict[int, tuple] = {}  # marker_id -> (pose, timestamp)
        self.measurement_timeout = 0.1  # секунды

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
        for m in d.get('markers', []):
            p = m['position']
            result[int(m['id'])] = np.array([p['x'], p['y'], p['z']], dtype=np.float64)
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

        # Публикуем абсолютную позицию
        field_msg = PoseStamped()
        field_msg.header = msg.header
        field_msg.header.frame_id = 'field'
        field_msg.pose.position = Point(
            x=float(drone_world[0]),
            y=float(drone_world[1]),
            z=float(drone_world[2])
        )
        # Ориентация остаётся той же
        field_msg.pose.orientation = msg.pose.orientation

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
