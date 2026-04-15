// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from drone_msgs:msg/ArucoDetectionArray.idl
// generated code does not contain a copyright notice

#ifndef DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION_ARRAY__BUILDER_HPP_
#define DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "drone_msgs/msg/detail/aruco_detection_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace drone_msgs
{

namespace msg
{

namespace builder
{

class Init_ArucoDetectionArray_detections
{
public:
  explicit Init_ArucoDetectionArray_detections(::drone_msgs::msg::ArucoDetectionArray & msg)
  : msg_(msg)
  {}
  ::drone_msgs::msg::ArucoDetectionArray detections(::drone_msgs::msg::ArucoDetectionArray::_detections_type arg)
  {
    msg_.detections = std::move(arg);
    return std::move(msg_);
  }

private:
  ::drone_msgs::msg::ArucoDetectionArray msg_;
};

class Init_ArucoDetectionArray_header
{
public:
  Init_ArucoDetectionArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ArucoDetectionArray_detections header(::drone_msgs::msg::ArucoDetectionArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ArucoDetectionArray_detections(msg_);
  }

private:
  ::drone_msgs::msg::ArucoDetectionArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::drone_msgs::msg::ArucoDetectionArray>()
{
  return drone_msgs::msg::builder::Init_ArucoDetectionArray_header();
}

}  // namespace drone_msgs

#endif  // DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION_ARRAY__BUILDER_HPP_
