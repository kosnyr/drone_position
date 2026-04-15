#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ─── Нода дальномера ───────────────────────────────────────────────
    rangefinder_node = Node(
        package='rangefinder',
        executable='rangefinder',
        name='rangefinder'
    )

    aruco_detector_node = Node(
        package='aruco_detector',
        executable='aruco_detector',
        name='aruco_detector'
    )

    global_position_node = Node(
        package='global_position',
        executable='global_position',
        name='global_position'
    )

    image_preprocessor_node = Node(
        package='image_preprocessor',
        executable='image_preprocessor',
        name='image_preprocessor'
    )

    marker_pose_estimator_node = Node(
        package='marker_pose_estimator',
        executable='marker_pose_estimator',
        name='marker_pose_estimator',
        parameters=[{
        'camera_mount_rotation': 'down_correct'  
        }]
    )

    position_fusion_node = Node(
        package='position_fusion',
        executable='position_fusion',
        name='position_fusion'
    )

    # ─── Нода пересчета высоты с учетом углов Эйлера ───────────────────────────────────────────────
    altitude_node = Node(
        package='altitude',
        executable='altitude',
        name='altitude'
    )

    # ─── Нода PX4 ──────────────────────────────────────────────────────────────
    px4_node = Node(
        package='px4',
        executable='px4',
        name='px4'
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
        image_preprocessor_node,
        rangefinder_node,
        altitude_node,
        marker_pose_estimator_node,
        position_fusion_node,
        aruco_detector_node,
        global_position_node,
    ])
