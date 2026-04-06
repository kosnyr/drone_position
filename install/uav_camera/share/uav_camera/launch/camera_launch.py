from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='uav_camera',
            executable='camera_publisher',
            name='camera_publisher',
            parameters=[{
                'camera_device': '/dev/video0',
                'frame_width': 640,
                'frame_height': 480,
                'fps': 30
            }]
        )
    ])