// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from drone_msgs:msg/ArucoDetection.idl
// generated code does not contain a copyright notice

#ifndef DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION__BUILDER_HPP_
#define DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "drone_msgs/msg/detail/aruco_detection__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace drone_msgs
{

namespace msg
{

namespace builder
{

class Init_ArucoDetection_corners
{
public:
  explicit Init_ArucoDetection_corners(::drone_msgs::msg::ArucoDetection & msg)
  : msg_(msg)
  {}
  ::drone_msgs::msg::ArucoDetection corners(::drone_msgs::msg::ArucoDetection::_corners_type arg)
  {
    msg_.corners = std::move(arg);
    return std::move(msg_);
  }

private:
  ::drone_msgs::msg::ArucoDetection msg_;
};

class Init_ArucoDetection_marker_id
{
public:
  Init_ArucoDetection_marker_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ArucoDetection_corners marker_id(::drone_msgs::msg::ArucoDetection::_marker_id_type arg)
  {
    msg_.marker_id = std::move(arg);
    return Init_ArucoDetection_corners(msg_);
  }

private:
  ::drone_msgs::msg::ArucoDetection msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::drone_msgs::msg::ArucoDetection>()
{
  return drone_msgs::msg::builder::Init_ArucoDetection_marker_id();
}

}  // namespace drone_msgs

#endif  // DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION__BUILDER_HPP_
