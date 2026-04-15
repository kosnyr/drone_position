#!/usr/bin/env python3
"""
Проверка разрешения и частоты кадров камеры.
Выводит размеры кадра и средний FPS.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import time


class CameraInfoChecker(Node):
    def __init__(self):
        super().__init__('camera_info_checker')
        self.bridge = CvBridge()
        self.sub = self.create_subscription(Image, '/camera/image_raw', self.callback, 10)

        self.last_log = time.time()
        self.frame_count = 0
        self.resolution = None

        self.get_logger().info("Camera Info Checker started. Listening on /camera/image_raw...")

    def callback(self, msg: Image):
        # Конвертируем в OpenCV только чтобы узнать размеры, не нагружая процессор
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"CV Bridge error: {e}")
            return

        h, w = cv_img.shape[:2]
        self.resolution = (w, h)

        self.frame_count += 1
        now = time.time()
        dt = now - self.last_log
        if dt >= 2.0:
            fps = self.frame_count / dt
            self.get_logger().info(
                f"Resolution: {w} x {h} | FPS: {fps:.1f} (frames: {self.frame_count})"
            )
            self.frame_count = 0
            self.last_log = now


def main(args=None):
    rclpy.init(args=args)
    node = CameraInfoChecker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()