#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VL53L1X RANGEFINDER NODE
Публикует данные дальномера VL53L1X в ROS2
"""

import board
import busio
import adafruit_vl53l1x
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Range


class RangefinderNode(Node):

    def __init__(self):
        super().__init__('rangefinder_node')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('i2c_address', 0x29)
        self.declare_parameter('update_rate', 20.0)  # Hz
        self.declare_parameter('min_range', 0.0)     # meters
        self.declare_parameter('max_range', 4.0)     # meters
        self.declare_parameter('fov', 0.471)         # radians (~27 degrees)

        i2c_address = self.get_parameter('i2c_address').value
        update_rate = self.get_parameter('update_rate').value
        self.min_range = self.get_parameter('min_range').value
        self.max_range = self.get_parameter('max_range').value
        self.fov = self.get_parameter('fov').value

        # ── Инициализация сенсора ──────────────────────────────────────────
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = adafruit_vl53l1x.VL53L1X(i2c, address=i2c_address)
            self.sensor.start_ranging()
            self.get_logger().info(f'VL53L1X initialized at 0x{i2c_address:02x}')
        except Exception as e:
            self.get_logger().error(f'Failed to initialize VL53L1X: {e}')
            raise

        # ── QoS ────────────────────────────────────────────────────────────
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # ── Издатель ───────────────────────────────────────────────────────
        self.pub_range = self.create_publisher(Range, '/rangefinder/range', qos)

        # ── Таймер ─────────────────────────────────────────────────────────
        timer_period = 1.0 / update_rate
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info('RangefinderNode ready')

    def timer_callback(self):
        """Читает данные с дальномера и публикует в ROS2"""
        try:
            if self.sensor.data_ready:
                # Читаем расстояние в см и конвертируем в метры
                distance_cm = self.sensor.distance
                
                # CRITICAL FIX: Проверяем что distance не None
                if distance_cm is None:
                    self.get_logger().warn('Sensor returned None distance', throttle_duration_sec=2.0)
                    return
                
                distance_m = distance_cm / 100.0
                
                # Проверяем валидность диапазона
                if distance_m < self.min_range or distance_m > self.max_range:
                    self.get_logger().warn(
                        f'Distance {distance_m:.2f}m out of range [{self.min_range}, {self.max_range}]',
                        throttle_duration_sec=2.0
                    )
                    return
                
                self.sensor.clear_interrupt()

                # Создаем сообщение Range
                msg = Range()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.header.frame_id = 'rangefinder_link'
                msg.radiation_type = Range.INFRARED
                msg.field_of_view = self.fov
                msg.min_range = self.min_range
                msg.max_range = self.max_range
                msg.range = float(distance_m)

                self.pub_range.publish(msg)

        except Exception as e:
            self.get_logger().error(f'Error reading sensor: {e}', throttle_duration_sec=1.0)

    def destroy_node(self):
        """Останавливаем сенсор при завершении"""
        try:
            self.sensor.stop_ranging()
            self.get_logger().info('VL53L1X stopped')
        except:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = RangefinderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
