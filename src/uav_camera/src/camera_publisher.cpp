#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <opencv2/videoio.hpp>
#include <iostream>

class CameraPublisher : public rclcpp::Node {
public:
    CameraPublisher() : Node("camera_publisher")
    {
        // Параметры
        this->declare_parameter("frame_width", 640);
        this->declare_parameter("frame_height", 480);
        this->declare_parameter("fps", 30);

        int width  = this->get_parameter("frame_width").as_int();
        int height = this->get_parameter("frame_height").as_int();
        int fps    = this->get_parameter("fps").as_int();

        // Создаем publisher
        publisher_ = this->create_publisher<sensor_msgs::msg::Image>("/camera/image_raw", 10);

        // GStreamer pipeline через libcamera
        std::string pipeline =
            "libcamerasrc ! "
            "video/x-raw,width=" + std::to_string(width) +
            ",height=" + std::to_string(height) +
            ",framerate=" + std::to_string(fps) + "/1 ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink drop=true max-buffers=1";

        RCLCPP_INFO(this->get_logger(), "Opening pipeline: %s", pipeline.c_str());

        cap_.open(pipeline, cv::CAP_GSTREAMER);

        if (!cap_.isOpened()) {
            RCLCPP_ERROR(this->get_logger(), "Failed to open camera via GStreamer pipeline");
            rclcpp::shutdown();
            return;
        }

        RCLCPP_INFO(this->get_logger(),
            "Camera opened: %dx%d @ %d fps", width, height, fps);

        // Таймер публикации
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(1000 / fps),
            std::bind(&CameraPublisher::publish_frame, this));
    }

    ~CameraPublisher()
    {
        if (cap_.isOpened()) {
            cap_.release();
        }
    }

private:
    void publish_frame()
    {
        cv::Mat frame;

        if (!cap_.read(frame)) {
            RCLCPP_WARN(this->get_logger(), "Failed to capture frame");
            return;
        }

        if (frame.empty()) {
            RCLCPP_WARN(this->get_logger(), "Empty frame received");
            return;
        }

        auto msg = cv_bridge::CvImage(
            std_msgs::msg::Header(), "bgr8", frame).toImageMsg();

        msg->header.stamp    = this->now();
        msg->header.frame_id = "camera_frame";

        publisher_->publish(*msg);
    }

    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    cv::VideoCapture cap_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<CameraPublisher>();

    if (rclcpp::ok()) {
        rclcpp::spin(node);
    }

    rclcpp::shutdown();
    return 0;
}