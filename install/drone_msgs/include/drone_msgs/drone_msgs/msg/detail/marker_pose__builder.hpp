// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from drone_msgs:msg/MarkerPose.idl
// generated code does not contain a copyright notice

#ifndef DRONE_MSGS__MSG__DETAIL__MARKER_POSE__BUILDER_HPP_
#define DRONE_MSGS__MSG__DETAIL__MARKER_POSE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "drone_msgs/msg/detail/marker_pose__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace drone_msgs
{

namespace msg
{

namespace builder
{

class Init_MarkerPose_pose
{
public:
  explicit Init_MarkerPose_pose(::drone_msgs::msg::MarkerPose & msg)
  : msg_(msg)
  {}
  ::drone_msgs::msg::MarkerPose pose(::drone_msgs::msg::MarkerPose::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::drone_msgs::msg::MarkerPose msg_;
};

class Init_MarkerPose_marker_id
{
public:
  Init_MarkerPose_marker_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MarkerPose_pose marker_id(::drone_msgs::msg::MarkerPose::_marker_id_type arg)
  {
    msg_.marker_id = std::move(arg);
    return Init_MarkerPose_pose(msg_);
  }

private:
  ::drone_msgs::msg::MarkerPose msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::drone_msgs::msg::MarkerPose>()
{
  return drone_msgs::msg::builder::Init_MarkerPose_marker_id();
}

}  // namespace drone_msgs

#endif  // DRONE_MSGS__MSG__DETAIL__MARKER_POSE__BUILDER_HPP_
