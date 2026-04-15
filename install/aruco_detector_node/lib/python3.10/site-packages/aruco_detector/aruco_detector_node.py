#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARUCO DETECTOR NODE (REFACTORED)
Детектирует ArUco маркеры на исправленных изображениях
"""

import cv2
import numpy as np
import yaml

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from drone_msgs.msg import ArucoDetection, ArucoDetectionArray


class ArucoDetectorNode(Node):

    def __init__(self):
        super().__init__('aruco_detector_node')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('aruco_whitelist_file', '/home/drone/drone_ws/src/config/aruco_whitelist_field.yaml')
        self.declare_parameter('use_whitelist', True)

        aruco_file = self.get_parameter('aruco_whitelist_file').value
        use_whitelist = self.get_parameter('use_whitelist').value

        # ── Runtime state ──────────────────────────────────────────────────
        self.bridge = CvBridge()

        # ── Загрузка конфигов ──────────────────────────────────────────────
        aruco_cfg = self._load_yaml(aruco_file)
        
        aruco_dict_name = aruco_cfg['aruco_dict']
        detector_params = aruco_cfg.get('detector_parameters', None)
        self.allowed_ids = (
            set(aruco_cfg['allowed_marker_ids']) if use_whitelist else None
        )

        self._init_aruco_detector(aruco_dict_name, detector_params)

        # ── QoS ────────────────────────────────────────────────────────────
        img_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST, depth=1
        )
        rel_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST, depth=10
        )

        # ── Подписки / издатели ────────────────────────────────────────────
        self.create_subscription(Image, '/camera/image_undistorted', self.image_callback, img_qos)
        self.pub_detections = self.create_publisher(ArucoDetectionArray, '/aruco/detections', rel_qos)

        self.get_logger().info('aruco_detector_node ready (refactored)')

    # ───────────────────────────────────────────────────────────────────────
    # Config loaders
    # ───────────────────────────────────────────────────────────────────────

    @staticmethod
    def _load_yaml(path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    # ───────────────────────────────────────────────────────────────────────
    # ArUco detector
    # ───────────────────────────────────────────────────────────────────────

    def _init_aruco_detector(self, dict_name: str, detector_params: dict = None) -> None:
        """Инициализация ArUco детектора с настраиваемыми параметрами"""
        _dicts = {
            'DICT_4X4_250': cv2.aruco.DICT_4X4_250,
            'DICT_5X5_250': cv2.aruco.DICT_5X5_250,
        }
        aruco_dict = cv2.aruco.getPredefinedDictionary(
            _dicts.get(dict_name, cv2.aruco.DICT_4X4_250)
        )
        
        # Создаем параметры детектора
        params = cv2.aruco.DetectorParameters()
        
        # Применяем параметры из конфига (если есть)
        if detector_params:
            # Адаптивная пороговая обработка
            if 'adaptiveThreshWinSizeMin' in detector_params:
                params.adaptiveThreshWinSizeMin = detector_params['adaptiveThreshWinSizeMin']
            if 'adaptiveThreshWinSizeMax' in detector_params:
                params.adaptiveThreshWinSizeMax = detector_params['adaptiveThreshWinSizeMax']
            if 'adaptiveThreshWinSizeStep' in detector_params:
                params.adaptiveThreshWinSizeStep = detector_params['adaptiveThreshWinSizeStep']
            
            # Уточнение углов
            if 'cornerRefinementMethod' in detector_params:
                method_map = {
                    'CORNER_REFINE_NONE': cv2.aruco.CORNER_REFINE_NONE,
                    'CORNER_REFINE_SUBPIX': cv2.aruco.CORNER_REFINE_SUBPIX,
                    'CORNER_REFINE_CONTOUR': cv2.aruco.CORNER_REFINE_CONTOUR,
                    'CORNER_REFINE_APRILTAG': cv2.aruco.CORNER_REFINE_APRILTAG,
                }
                method_name = detector_params['cornerRefinementMethod']
                params.cornerRefinementMethod = method_map.get(
                    method_name, cv2.aruco.CORNER_REFINE_SUBPIX
                )
            if 'cornerRefinementMaxIterations' in detector_params:
                params.cornerRefinementMaxIterations = detector_params['cornerRefinementMaxIterations']
            if 'cornerRefinementMinAccuracy' in detector_params:
                params.cornerRefinementMinAccuracy = detector_params['cornerRefinementMinAccuracy']
            
            # Ограничения размера маркера
            if 'minMarkerPerimeterRate' in detector_params:
                params.minMarkerPerimeterRate = detector_params['minMarkerPerimeterRate']
            if 'maxMarkerPerimeterRate' in detector_params:
                params.maxMarkerPerimeterRate = detector_params['maxMarkerPerimeterRate']
            
            self.get_logger().info(
                f'ArUco detector initialized with custom parameters: '
                f'cornerRefinement={detector_params.get("cornerRefinementMethod", "default")}, '
                f'adaptiveThresh=[{params.adaptiveThreshWinSizeMin}, {params.adaptiveThreshWinSizeMax}], '
                f'markerPerimeter=[{params.minMarkerPerimeterRate:.2f}, {params.maxMarkerPerimeterRate:.2f}]'
            )
        else:
            # Параметры по умолчанию (базовые)
            params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR
            self.get_logger().info('ArUco detector initialized with default parameters')
        
        self.aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, params)

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

        # ── Детекция маркеров ──────────────────────────────────────────────
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        try:
            corners, ids, _ = self.aruco_detector.detectMarkers(gray)
        except cv2.error as e:
            self.get_logger().warn(f'ArUco detection error: {e}', throttle_duration_sec=1.0)
            return
        
        if ids is None:
            return

        # ── Фильтрация по whitelist и создание сообщений ───────────────────
        detections = []
        for corner, mid in zip(corners, ids.flatten()):
            mid = int(mid)
            if self.allowed_ids and mid not in self.allowed_ids:
                continue
            
            # Преобразуем углы в плоский массив [x1, y1, x2, y2, x3, y3, x4, y4]
            corners_flat = corner[0].flatten().astype(np.float32)
            
            detection = ArucoDetection()
            detection.marker_id = mid
            detection.corners = corners_flat.tolist()
            detections.append(detection)

        if not detections:
            return

        # ── Публикация ─────────────────────────────────────────────────────
        detection_array = ArucoDetectionArray()
        detection_array.header = msg.header
        detection_array.detections = detections
        self.pub_detections.publish(detection_array)
        
        self.get_logger().info(
            f'Detected {len(detections)} markers: {[d.marker_id for d in detections]}',
            throttle_duration_sec=1.0
        )


# ───────────────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = ArucoDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
