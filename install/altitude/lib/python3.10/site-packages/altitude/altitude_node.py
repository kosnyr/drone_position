#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALTITUDE ESTIMATOR NODE
Вычисляет точную высоту дрона используя дальномер и углы Эйлера
"""

import numpy as np
import threading

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Range
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float64


class AltitudeEstimatorNode(Node):

    def __init__(self):
        super().__init__('altitude_estimator_node')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('max_tilt_angle', 30.0)  # градусы, максимальный наклон для валидных измерений

        self.max_tilt = np.radians(self.get_parameter('max_tilt_angle').value)

        # ── Состояние ──────────────────────────────────────────────────────
        self._lock = threading.Lock()
        self._range_distance = None
        self._roll = 0.0
        self._pitch = 0.0
        self._last_range_time = None
        self._last_attitude_time = None

        # ── QoS ────────────────────────────────────────────────────────────
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # ── Подписки ───────────────────────────────────────────────────────
        self.create_subscription(Range, '/rangefinder/range', self.range_callback, qos)
        self.create_subscription(Vector3, '/uav/ATTITUDE', self.attitude_callback, qos)

        # ── Издатели ───────────────────────────────────────────────────────
        self.pub_altitude = self.create_publisher(Float64, '/uav/altitude', qos)
        self.pub_altitude_raw = self.create_publisher(Float64, '/uav/altitude_raw', qos)

        self.get_logger().info('AltitudeEstimatorNode ready')

    # ─────────────────────────────────────────────────────────────────────
    # Callbacks
    # ─────────────────────────────────────────────────────────────────────

    def attitude_callback(self, msg: Vector3):
        """Получает углы Эйлера (roll, pitch, yaw)"""
        with self._lock:
            self._roll = msg.x
            self._pitch = msg.y
            self._last_attitude_time = self.get_clock().now()

    def range_callback(self, msg: Range):
        """Получает расстояние от дальномера и вычисляет высоту"""
        with self._lock:
            self._range_distance = msg.range
            self._last_range_time = self.get_clock().now()
            
            # Проверяем валидность данных
            if self._range_distance is None or self._range_distance <= 0:
                return
            
            # Публикуем сырое расстояние
            raw_msg = Float64()
            raw_msg.data = self._range_distance
            self.pub_altitude_raw.publish(raw_msg)

            # Вычисляем скорректированную высоту
            altitude = self._calculate_altitude(
                self._range_distance,
                self._roll,
                self._pitch
            )

            if altitude is not None:
                alt_msg = Float64()
                alt_msg.data = altitude
                self.pub_altitude.publish(alt_msg)

    # ─────────────────────────────────────────────────────────────────────
    # Altitude calculation
    # ─────────────────────────────────────────────────────────────────────

    def _calculate_altitude(self, distance: float, roll: float, pitch: float) -> float:
        """
        Вычисляет истинную высоту с учетом наклона дрона
        
        Args:
            distance: расстояние от дальномера (м)
            roll: угол крена (радианы)
            pitch: угол тангажа (радианы)
            
        Returns:
            Высота над поверхностью (м) или None если данные невалидны
        """
        # Проверяем, что наклон не слишком большой
        total_tilt = np.sqrt(roll**2 + pitch**2)
        if total_tilt > self.max_tilt:
            self.get_logger().warn(
                f'Tilt angle too large: {np.degrees(total_tilt):.1f}° > {np.degrees(self.max_tilt):.1f}°',
                throttle_duration_sec=1.0
            )
            return None

        # Вычисляем вертикальную составляющую
        # h = d * cos(pitch) * cos(roll)
        altitude = distance * np.cos(pitch) * np.cos(roll)

        # Дополнительная проверка на разумность
        if altitude < 0 or altitude > 100:  # 100м - максимальная разумная высота
            self.get_logger().warn(
                f'Invalid altitude calculated: {altitude:.2f}m',
                throttle_duration_sec=1.0
            )
            return None

        return altitude


# ─────────────────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = AltitudeEstimatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
