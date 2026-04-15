#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from pymavlink import mavutil
import signal
import sys
from geometry_msgs.msg import Vector3


class MAVLinkForwarder(Node):
    def __init__(self):
        super().__init__('mavlink_forwarder')

        # Configuration parameters
        self.declare_parameter('device', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 57600)
        self.declare_parameter('connection_timeout', 30)
        self.declare_parameter('publish_rate', 20.0)  # Hz

        # Configure QoS for real-time data
        qos_profile = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)

        # Publisher for Euler angles
        self.attitude_pub = self.create_publisher(Vector3, '/uav/ATTITUDE', qos_profile)

        # Rate limiting
        self.publish_rate = self.get_parameter('publish_rate').value
        self.min_publish_interval = 1.0 / self.publish_rate
        self.last_publish_time = 0.0
        self.last_attitude_msg = None

        self.connect_mavlink()
        self.timer = self.create_timer(0.001, self.process_mavlink_messages)

        # Signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)

    def connect_mavlink(self):
        device = self.get_parameter('device').value
        baudrate = self.get_parameter('baudrate').value
        timeout = self.get_parameter('connection_timeout').value

        try:
            self.master = mavutil.mavlink_connection(
                device,
                baud=baudrate,
                source_system=1,
                source_component=1,
                autoreconnect=True
            )

            if not self.master.wait_heartbeat(timeout=timeout):
                raise ConnectionError("Heartbeat timeout")

            self.get_logger().info("Connected to PX4", throttle_duration_sec=5)

        except Exception as e:
            self.get_logger().error(f"Connection failed: {str(e)}")
            sys.exit(1)

    def process_mavlink_messages(self):
        try:
            msg = self.master.recv_match(blocking=False, timeout=0.01)
            if msg:
                self.handle_mavlink_message(msg)
        except Exception as e:
            self.get_logger().error(f"Error processing message: {str(e)}", throttle_duration_sec=5.0)

    def handle_mavlink_message(self, msg):
        msg_type = msg.get_type()

        try:
            if msg_type == "ATTITUDE":
                # Rate limiting: publish at max publish_rate Hz
                current_time = self.get_clock().now().nanoseconds / 1e9
                
                if current_time - self.last_publish_time >= self.min_publish_interval:
                    euler_msg = Vector3()
                    euler_msg.x = msg.roll
                    euler_msg.y = msg.pitch
                    euler_msg.z = msg.yaw
                    self.attitude_pub.publish(euler_msg)
                    self.last_publish_time = current_time
                else:
                    # Cache the message for next publish cycle
                    self.last_attitude_msg = msg

        except Exception as e:
            self.get_logger().error(f"Error handling {msg_type}: {str(e)}", throttle_duration_sec=1)

    def signal_handler(self, sig, frame):
        self.get_logger().info("Shutting down gracefully...")
        self.destroy_node()
        rclpy.shutdown()
        sys.exit(0)


def main(args=None):
    rclpy.init(args=args)
    forwarder = MAVLinkForwarder()

    try:
        rclpy.spin(forwarder)
    except KeyboardInterrupt:
        pass
    finally:
        forwarder.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()