#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAGE PREPROCESSOR NODE
Исправляет искажения fisheye-камеры и публикует rectified изображения
"""

import cv2
import numpy as np
import yaml
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class ImagePreprocessorNode(Node):

    def __init__(self):
        super().__init__('image_preprocessor_node')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('camera_params_file', '/home/drone/drone_ws/src/config/camera_params.yaml')
        self.declare_parameter('balance', 0.0)

        cam_file = self.get_parameter('camera_params_file').value
        self.balance = float(self.get_parameter('balance').value)

        # ── Runtime state ──────────────────────────────────────────────────
        self.bridge = CvBridge()
        self._map1 = None
        self._map2 = None
        self._K_new = None
        self._cam_params: Optional[dict] = None

        # ── Загрузка конфигов ──────────────────────────────────────────────
        self._load_camera_params(cam_file)

        self.target_width = self._cam_params['target_width']
        self.target_height = self._cam_params['target_height']

        # ── QoS ────────────────────────────────────────────────────────────
        img_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST, depth=1
        )

        # ── Подписки / издатели ────────────────────────────────────────────
        self.create_subscription(Image, '/camera/image_raw', self.image_callback, img_qos)
        self.pub_undistorted = self.create_publisher(Image, '/camera/image_undistorted', img_qos)

        self.get_logger().info('image_preprocessor_node ready')

    # ───────────────────────────────────────────────────────────────────────
    # Config loaders
    # ───────────────────────────────────────────────────────────────────────

    @staticmethod
    def _load_yaml(path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _load_camera_params(self, path: str) -> None:
        d = self._load_yaml(path)
        for key in ('target_width', 'target_height'):
            if key not in d:
                raise KeyError(f"'{key}' is required in {path} but was not found")
        self._cam_params = {
            'width': d['image_width'],
            'height': d['image_height'],
            'target_width': d['target_width'],
            'target_height': d['target_height'],
            'K': np.array(d['camera_matrix']['data'], dtype=np.float64).reshape(3, 3),
            'D': np.array(d['distortion_coefficients']['data'], dtype=np.float64).reshape(1, 4),
            'R': np.array(d['rectification_matrix']['data'], dtype=np.float64).reshape(3, 3),
        }

    # ───────────────────────────────────────────────────────────────────────
    # Undistort maps (lazy init при первом кадре нужного размера)
    # ───────────────────────────────────────────────────────────────────────

    def _init_undistort_maps(self, width: int, height: int) -> None:
        scale_x = width / self._cam_params['width']
        scale_y = height / self._cam_params['height']
        K_sc = self._cam_params['K'].copy()
        K_sc[0, 0] *= scale_x
        K_sc[1, 1] *= scale_y
        K_sc[0, 2] *= scale_x
        K_sc[1, 2] *= scale_y

        self._K_new = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
            K_sc, self._cam_params['D'], (width, height),
            self._cam_params['R'], balance=self.balance
        )
        self._map1, self._map2 = cv2.fisheye.initUndistortRectifyMap(
            K_sc, self._cam_params['D'], self._cam_params['R'],
            self._K_new, (width, height), cv2.CV_16SC2
        )
        self.get_logger().info(f'Undistort maps initialized for {width}×{height}')

    # ───────────────────────────────────────────────────────────────────────
    # Callbacks
    # ───────────────────────────────────────────────────────────────────────

    def image_callback(self, msg: Image) -> None:
        # ── Декод ──────────────────────────────────────────────────────────
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge error: {e}')
            return

        # ── Ресайз ─────────────────────────────────────────────────────────
        h, w = frame.shape[:2]
        if w != self.target_width or h != self.target_height:
            frame = cv2.resize(frame, (self.target_width, self.target_height))

        # ── Undistort (lazy init) ──────────────────────────────────────────
        if self._map1 is None:
            self._init_undistort_maps(self.target_width, self.target_height)
        undistorted = cv2.remap(frame, self._map1, self._map2, cv2.INTER_CUBIC)

        # ── Публикация ─────────────────────────────────────────────────────
        try:
            undistorted_msg = self.bridge.cv2_to_imgmsg(undistorted, 'bgr8')
            undistorted_msg.header = msg.header
            self.pub_undistorted.publish(undistorted_msg)
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge error: {e}')


# ───────────────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = ImagePreprocessorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
