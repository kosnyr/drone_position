// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from drone_msgs:msg/ArucoDetection.idl
// generated code does not contain a copyright notice

#ifndef DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION__STRUCT_HPP_
#define DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__drone_msgs__msg__ArucoDetection __attribute__((deprecated))
#else
# define DEPRECATED__drone_msgs__msg__ArucoDetection __declspec(deprecated)
#endif

namespace drone_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ArucoDetection_
{
  using Type = ArucoDetection_<ContainerAllocator>;

  explicit ArucoDetection_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->marker_id = 0l;
      std::fill<typename std::array<float, 8>::iterator, float>(this->corners.begin(), this->corners.end(), 0.0f);
    }
  }

  explicit ArucoDetection_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : corners(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->marker_id = 0l;
      std::fill<typename std::array<float, 8>::iterator, float>(this->corners.begin(), this->corners.end(), 0.0f);
    }
  }

  // field types and members
  using _marker_id_type =
    int32_t;
  _marker_id_type marker_id;
  using _corners_type =
    std::array<float, 8>;
  _corners_type corners;

  // setters for named parameter idiom
  Type & set__marker_id(
    const int32_t & _arg)
  {
    this->marker_id = _arg;
    return *this;
  }
  Type & set__corners(
    const std::array<float, 8> & _arg)
  {
    this->corners = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    drone_msgs::msg::ArucoDetection_<ContainerAllocator> *;
  using ConstRawPtr =
    const drone_msgs::msg::ArucoDetection_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<drone_msgs::msg::ArucoDetection_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<drone_msgs::msg::ArucoDetection_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      drone_msgs::msg::ArucoDetection_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<drone_msgs::msg::ArucoDetection_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      drone_msgs::msg::ArucoDetection_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<drone_msgs::msg::ArucoDetection_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<drone_msgs::msg::ArucoDetection_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<drone_msgs::msg::ArucoDetection_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__drone_msgs__msg__ArucoDetection
    std::shared_ptr<drone_msgs::msg::ArucoDetection_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__drone_msgs__msg__ArucoDetection
    std::shared_ptr<drone_msgs::msg::ArucoDetection_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ArucoDetection_ & other) const
  {
    if (this->marker_id != other.marker_id) {
      return false;
    }
    if (this->corners != other.corners) {
      return false;
    }
    return true;
  }
  bool operator!=(const ArucoDetection_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ArucoDetection_

// alias to use template instance with default allocator
using ArucoDetection =
  drone_msgs::msg::ArucoDetection_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace drone_msgs

#endif  // DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION__STRUCT_HPP_
