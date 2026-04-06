#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Vector3
 
class AttitudeProvider(Node):
    def __init__(self):
        super().__init__('attitude_provider')
 
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
 
        self.sub = self.create_subscription(
            Float64MultiArray,
            '/uav/ATTITUDE',
            self.callback,
            qos
        )
 
        # Публикует [roll, pitch, yaw] в радианах
        self.pub = self.create_publisher(Vector3, '/uav/attitude/euler', qos)
 
        # Таймер для публикации нулевых углов если нет данных от PX4
        self.last_msg_time = self.get_clock().now()
        self.timeout = 1.0  # секунды
        self.timer = self.create_timer(0.1, self.check_timeout)
 
        self.get_logger().info('AttitudeProvider started')
 
    def callback(self, msg: Float64MultiArray):
        # MAVLinkForwarder порядок: [pitch, roll, yaw, ...]
        out = Vector3()
        out.x = msg.data[1]  # roll
        out.y = msg.data[0]  # pitch
        out.z = msg.data[2]  # yaw
        self.pub.publish(out)
        
        # Обновляем время последнего сообщения
        self.last_msg_time = self.get_clock().now()
 
    def check_timeout(self):
        """Публикует нулевые углы если нет данных от PX4"""
        elapsed = (self.get_clock().now() - self.last_msg_time).nanoseconds / 1e9
        
        if elapsed > self.timeout:
            # Публикуем нулевые углы
            out = Vector3()
            out.x = 0.0  # roll
            out.y = 0.0  # pitch
            out.z = 0.0  # yaw
            self.pub.publish(out)
 
def main(args=None):
    rclpy.init(args=args)
    node = AttitudeProvider()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
 
if __name__ == '__main__':
    main()
