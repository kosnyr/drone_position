#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FISHEYE ARUCO POSITIONING NODE
Fisheye camera + ArUco markers → absolute drone position on field
"""

import cv2
import numpy as np
import yaml
import threading
from typing import Optional, Tuple, List, Dict

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Image
from geometry_msgs.msg import Vector3, PoseStamped, Point, Quaternion
from std_msgs.msg import Header
from cv_bridge import CvBridge, CvBridgeError


# ─────────────────────────────────────────────────────────────────────────────
# Math helpers
# ─────────────────────────────────────────────────────────────────────────────

def euler_to_rotation_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cr, sr = np.cos(roll),  np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw),   np.sin(yaw)
    Rx = np.array([[1,  0,   0 ], [0,  cr, -sr], [0, sr, cr]], dtype=np.float64)
    Ry = np.array([[cp, 0,   sp], [0,   1,   0], [-sp, 0, cp]], dtype=np.float64)
    Rz = np.array([[cy, -sy, 0 ], [sy, cy,   0], [0,   0,  1]], dtype=np.float64)
    return Rz @ Ry @ Rx


def rotation_matrix_to_quaternion(R: np.ndarray) -> Tuple[float, float, float, float]:
    trace = R[0, 0] + R[1, 1] + R[2, 2]
    if trace > 0:
        s = 0.5 / np.sqrt(trace + 1.0)
        w = 0.25 / s
        x, y, z = (R[2,1]-R[1,2])*s, (R[0,2]-R[2,0])*s, (R[1,0]-R[0,1])*s
    elif R[0,0] > R[1,1] and R[0,0] > R[2,2]:
        s = 2.0 * np.sqrt(1.0 + R[0,0] - R[1,1] - R[2,2])
        w, x, y, z = (R[2,1]-R[1,2])/s, 0.25*s, (R[0,1]+R[1,0])/s, (R[0,2]+R[2,0])/s
    elif R[1,1] > R[2,2]:
        s = 2.0 * np.sqrt(1.0 + R[1,1] - R[0,0] - R[2,2])
        w, x, y, z = (R[0,2]-R[2,0])/s, (R[0,1]+R[1,0])/s, 0.25*s, (R[1,2]+R[2,1])/s
    else:
        s = 2.0 * np.sqrt(1.0 + R[2,2] - R[0,0] - R[1,1])
        w, x, y, z = (R[1,0]-R[0,1])/s, (R[0,2]+R[2,0])/s, (R[1,2]+R[2,1])/s, 0.25*s
    return float(x), float(y), float(z), float(w)


def make_marker_object_points(marker_length: float) -> np.ndarray:
    """
    3D corners of a marker in its own coordinate frame (Z=0 plane).
    Order: top-left, top-right, bottom-right, bottom-left  (OpenCV convention).
    """
    half = marker_length / 2.0
    return np.array([
        [-half,  half, 0.0],
        [ half,  half, 0.0],
        [ half, -half, 0.0],
        [-half, -half, 0.0],
    ], dtype=np.float64)


# ─────────────────────────────────────────────────────────────────────────────
# Node
# ─────────────────────────────────────────────────────────────────────────────

class aruco_detector_node(Node):

    def __init__(self):
        super().__init__('aruco_detector_node')

        # ── Параметры ──────────────────────────────────────────────────────
        self.declare_parameter('camera_params_file',   '/home/drone/drone_ws/src/config/camera_params.yaml')
        self.declare_parameter('aruco_whitelist_file', '/home/drone/drone_ws/src/config/aruco_whitelist_field.yaml')
        self.declare_parameter('balance',      0.0)
        self.declare_parameter('use_whitelist', True)

        cam_file    = self.get_parameter('camera_params_file').value
        aruco_file  = self.get_parameter('aruco_whitelist_file').value
        self.balance      = float(self.get_parameter('balance').value)
        use_whitelist     = self.get_parameter('use_whitelist').value

        # ── Runtime state (инициализируем ДО первой загрузки) ─────────────
        self.bridge      = CvBridge()
        self._roll       = 0.0
        self._pitch      = 0.0
        self._yaw        = 0.0
        self._imu_lock   = threading.Lock()
        self._map1       = None
        self._map2       = None
        self._K_new      = None
        self._cam_params: Optional[dict] = None

        # ── Загрузка конфигов ──────────────────────────────────────────────
        self._load_camera_params(cam_file)                        # заполняет self._cam_params

        aruco_cfg = self._load_yaml(aruco_file)
        self.target_width   = self._cam_params['target_width']
        self.target_height  = self._cam_params['target_height']
        self.marker_length  = float(aruco_cfg['marker_length'])
        aruco_dict_name     = aruco_cfg['aruco_dict']
        self.allowed_ids    = (
            set(aruco_cfg['allowed_marker_ids']) if use_whitelist else None
        )

        # 3D точки маркера для solvePnP
        self.obj_points = make_marker_object_points(self.marker_length)

        self._init_aruco_detector(aruco_dict_name)

        # ── QoS ───────────────────────────────────────────────────────────
        img_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST, depth=1
        )
        rel_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST, depth=10
        )

        # ── Подписки / издатели ───────────────────────────────────────────
        self.create_subscription(Image,   '/camera/image_raw',       self.image_callback,    img_qos)
        self.create_subscription(Vector3, '/uav/attitude/euler',      self.attitude_callback, rel_qos)

        # Поза относительно ближайшего маркера
        self.pub_pose_marker = self.create_publisher(PoseStamped, '/aruco/drone_pose_marker', rel_qos)

        self.get_logger().info('aruco_detector_node ready')

    # ─────────────────────────────────────────────────────────────────────
    # Config loaders
    # ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _load_yaml(path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _load_camera_params(self, path: str) -> None:
        d = self._load_yaml(path)
        for key in ('target_width', 'target_height'):
            if key not in d:
                raise KeyError(
                    f"'{key}' is required in {path} but was not found"
                )
        self._cam_params = {
            'width':         d['image_width'],
            'height':        d['image_height'],
            'target_width':  d['target_width'],
            'target_height': d['target_height'],
            'K': np.array(d['camera_matrix']['data'],          dtype=np.float64).reshape(3, 3),
            'D': np.array(d['distortion_coefficients']['data'], dtype=np.float64).reshape(1, 4),
            'R': np.array(d['rectification_matrix']['data'],   dtype=np.float64).reshape(3, 3),
        }

    # ─────────────────────────────────────────────────────────────────────
    # Undistort maps (lazy init при первом кадре нужного размера)
    # ─────────────────────────────────────────────────────────────────────

    def _init_undistort_maps(self, width: int, height: int) -> None:
        scale_x = width  / self._cam_params['width']
        scale_y = height / self._cam_params['height']
        K_sc = self._cam_params['K'].copy()
        K_sc[0, 0] *= scale_x;  K_sc[1, 1] *= scale_y
        K_sc[0, 2] *= scale_x;  K_sc[1, 2] *= scale_y

        self._K_new = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
            K_sc, self._cam_params['D'], (width, height),
            self._cam_params['R'], balance=self.balance
        )
        self._map1, self._map2 = cv2.fisheye.initUndistortRectifyMap(
            K_sc, self._cam_params['D'], self._cam_params['R'],
            self._K_new, (width, height), cv2.CV_16SC2
        )
        self.get_logger().info(
            f'Undistort maps initialised for {width}×{height}'
        )

    # ─────────────────────────────────────────────────────────────────────
    # ArUco detector
    # ─────────────────────────────────────────────────────────────────────

    def _init_aruco_detector(self, dict_name: str) -> None:
        _dicts = {
            'DICT_4X4_250':  cv2.aruco.DICT_4X4_250,
            'DICT_5X5_250':  cv2.aruco.DICT_5X5_250,
        }
        aruco_dict = cv2.aruco.getPredefinedDictionary(
            _dicts.get(dict_name, cv2.aruco.DICT_4X4_250)
        )
        params = cv2.aruco.DetectorParameters()
        params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR
        self.aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, params)

    def _estimate_pose(
        self, corners_list: list, ids_flat: np.ndarray
    ) -> List[Tuple[np.ndarray, np.ndarray, int]]:
        """
        Возвращает список (rvec, tvec, marker_id) для маркеров из белого списка.
        Использует cv2.solvePnP вместо удалённого estimatePoseSingleMarkers.
        """
        # нулевые коэффициенты искажений — изображение уже rectified
        dist_zero = np.zeros((4, 1), dtype=np.float64)
        poses = []
        for corners, mid in zip(corners_list, ids_flat):
            mid = int(mid)
            if self.allowed_ids and mid not in self.allowed_ids:
                continue
            img_pts = corners[0].astype(np.float64)          # shape (4, 2)
            ok, rvec, tvec = cv2.solvePnP(
                self.obj_points, img_pts,
                self._K_new, dist_zero,
                flags=cv2.SOLVEPNP_IPPE_SQUARE
            )
            if not ok:
                continue
            poses.append((rvec.flatten(), tvec.flatten(), mid))
        return poses

    # ─────────────────────────────────────────────────────────────────────
    # Callbacks
    # ─────────────────────────────────────────────────────────────────────

    def attitude_callback(self, msg: Vector3) -> None:
        with self._imu_lock:
            self._roll, self._pitch, self._yaw = msg.x, msg.y, msg.z

    def image_callback(self, msg: Image) -> None:
        # ── Декод ──────────────────────────────────────────────────────
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge error: {e}')
            return

        # ── Ресайз ─────────────────────────────────────────────────────
        h, w = frame.shape[:2]
        if w != self.target_width or h != self.target_height:
            frame = cv2.resize(frame, (self.target_width, self.target_height))

        # ── Undistort (lazy init) ───────────────────────────────────────
        if self._map1 is None:
            self._init_undistort_maps(self.target_width, self.target_height)
        undistorted = cv2.remap(frame, self._map1, self._map2, cv2.INTER_LINEAR)

        # ── Детекция маркеров ──────────────────────────────────────────
        gray = cv2.cvtColor(undistorted, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.aruco_detector.detectMarkers(gray)
        if ids is None:
            return

        # ── Оценка поз (новый API) ─────────────────────────────────────
        poses = self._estimate_pose(corners, ids.flatten())
        if not poses:
            return

        # ── IMU snapshot ───────────────────────────────────────────────
        with self._imu_lock:
            roll, pitch, yaw = self._roll, self._pitch, self._yaw
        R_b2w = euler_to_rotation_matrix(roll, pitch, yaw)

        # ── Публикация: поза относительно каждого маркера ─────────────
        for rvec, tvec, mid in poses:
            R_cm, _ = cv2.Rodrigues(rvec)
            R_mc    = R_cm.T
            t_mc    = (-R_mc @ tvec.reshape(3, 1)).flatten()  # cam в системе маркера

            # Преобразуем в мировую систему координат (с учётом ориентации дрона)
            t_world  = R_b2w @ t_mc
            R_world  = R_b2w @ R_mc
            qx, qy, qz, qw = rotation_matrix_to_quaternion(R_world)

            marker_msg = PoseStamped()
            marker_msg.header          = msg.header
            marker_msg.header.frame_id = f'marker_{mid}'
            marker_msg.pose.position    = Point(
                x=float(t_world[0]),
                y=float(t_world[1]),
                z=float(t_world[2])
            )
            marker_msg.pose.orientation = Quaternion(x=qx, y=qy, z=qz, w=qw)
            self.pub_pose_marker.publish(marker_msg)


# ─────────────────────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = aruco_detector_node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
