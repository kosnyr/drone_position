// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from drone_msgs:msg/MarkerPoseArray.idl
// generated code does not contain a copyright notice

#ifndef DRONE_MSGS__MSG__DETAIL__MARKER_POSE_ARRAY__BUILDER_HPP_
#define DRONE_MSGS__MSG__DETAIL__MARKER_POSE_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "drone_msgs/msg/detail/marker_pose_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace drone_msgs
{

namespace msg
{

namespace builder
{

class Init_MarkerPoseArray_poses
{
public:
  explicit Init_MarkerPoseArray_poses(::drone_msgs::msg::MarkerPoseArray & msg)
  : msg_(msg)
  {}
  ::drone_msgs::msg::MarkerPoseArray poses(::drone_msgs::msg::MarkerPoseArray::_poses_type arg)
  {
    msg_.poses = std::move(arg);
    return std::move(msg_);
  }

private:
  ::drone_msgs::msg::MarkerPoseArray msg_;
};

class Init_MarkerPoseArray_header
{
public:
  Init_MarkerPoseArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MarkerPoseArray_poses header(::drone_msgs::msg::MarkerPoseArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_MarkerPoseArray_poses(msg_);
  }

private:
  ::drone_msgs::msg::MarkerPoseArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::drone_msgs::msg::MarkerPoseArray>()
{
  return drone_msgs::msg::builder::Init_MarkerPoseArray_header();
}

}  // namespace drone_msgs

#endif  // DRONE_MSGS__MSG__DETAIL__MARKER_POSE_ARRAY__BUILDER_HPP_
