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


def euler_to_rotation_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """Матрица поворота из углов Эйлера (ZYX convention)"""
    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)
    
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    
    return Rz @ Ry @ Rx


class AltitudeEstimatorNode(Node):

    def __init__(self):
        super().__init__('altitude_estimator_node')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('max_tilt_angle', 30.0)  # градусы, максимальный наклон для валидных измерений
        self.declare_parameter('filter_alpha', 0.3)  # 0-1, меньше = больше сглаживание

        self.max_tilt = np.radians(self.get_parameter('max_tilt_angle').value)
        self.alpha = self.get_parameter('filter_alpha').value

        # ── Состояние ──────────────────────────────────────────────────────
        self._lock = threading.Lock()
        self._range_distance = None
        self._roll = 0.0
        self._pitch = 0.0
        self._last_range_time = None
        self._last_attitude_time = None
        self._filtered_altitude = None

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

            # Вычисляем скорректированную высоту
            altitude = self._calculate_altitude(
                self._range_distance,
                self._roll,
                self._pitch
            )

            if altitude is not None:
                # Применяем экспоненциальный фильтр
                if self._filtered_altitude is None:
                    self._filtered_altitude = altitude
                else:
                    self._filtered_altitude = (
                        self.alpha * altitude + 
                        (1 - self.alpha) * self._filtered_altitude
                    )
                
                alt_msg = Float64()
                alt_msg.data = self._filtered_altitude
                self.pub_altitude.publish(alt_msg)

    # ─────────────────────────────────────────────────────────────────────
    # Altitude calculation
    # ─────────────────────────────────────────────────────────────────────

    def _calculate_altitude(self, distance: float, roll: float, pitch: float) -> float:
        """
        Правильный расчет высоты с учетом наклона
        
        Луч дальномера направлен вдоль оси Z дрона (вниз в системе дрона).
        При наклоне дрона нужно найти вертикальную составляющую.
        
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

        # Вектор луча дальномера в системе дрона: [0, 0, distance]
        # (направлен вниз по оси Z)
        ray_body = np.array([0, 0, distance])
        
        # Матрица поворота от системы дрона к мировой
        R = euler_to_rotation_matrix(roll, pitch, 0)  # yaw не влияет на высоту
        
        # Преобразуем вектор в мировую систему
        ray_world = R @ ray_body
        
        # Вертикальная составляющая (Z в мировой системе)
        altitude = abs(ray_world[2])

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
