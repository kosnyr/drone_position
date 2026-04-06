#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ─── Нода глобальной позиции ───────────────────────────────────────────────
    global_position_node = Node(
        package='global_position_node',
        executable='global_position',
        name='global_position'
    )

    # ─── Нода PX4 ──────────────────────────────────────────────────────────────
    px4_node = Node(
        package='px4',
        executable='px4',
        name='px4'
    )

    # ─── Нода детектора ArUco ──────────────────────────────────────────────────
    aruco_detector_node = Node(
        package='aruco_detector_node',
        executable='aruco_detector',
        name='aruco_detector'
    )

    # ─── Лаунч камеры  ────────────────────────
    camera_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('uav_camera'),  
                'launch',
                'camera_launch.py'                        
            ])
        )
    )

    return LaunchDescription([
        camera_launch,
        px4_node,
        aruco_detector_node,
        global_position_node,
    ])
