// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from drone_msgs:msg/ArucoDetectionArray.idl
// generated code does not contain a copyright notice

#ifndef DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION_ARRAY__STRUCT_HPP_
#define DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION_ARRAY__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'detections'
#include "drone_msgs/msg/detail/aruco_detection__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__drone_msgs__msg__ArucoDetectionArray __attribute__((deprecated))
#else
# define DEPRECATED__drone_msgs__msg__ArucoDetectionArray __declspec(deprecated)
#endif

namespace drone_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ArucoDetectionArray_
{
  using Type = ArucoDetectionArray_<ContainerAllocator>;

  explicit ArucoDetectionArray_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    (void)_init;
  }

  explicit ArucoDetectionArray_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _detections_type =
    std::vector<drone_msgs::msg::ArucoDetection_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<drone_msgs::msg::ArucoDetection_<ContainerAllocator>>>;
  _detections_type detections;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__detections(
    const std::vector<drone_msgs::msg::ArucoDetection_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<drone_msgs::msg::ArucoDetection_<ContainerAllocator>>> & _arg)
  {
    this->detections = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator> *;
  using ConstRawPtr =
    const drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__drone_msgs__msg__ArucoDetectionArray
    std::shared_ptr<drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__drone_msgs__msg__ArucoDetectionArray
    std::shared_ptr<drone_msgs::msg::ArucoDetectionArray_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ArucoDetectionArray_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->detections != other.detections) {
      return false;
    }
    return true;
  }
  bool operator!=(const ArucoDetectionArray_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ArucoDetectionArray_

// alias to use template instance with default allocator
using ArucoDetectionArray =
  drone_msgs::msg::ArucoDetectionArray_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace drone_msgs

#endif  // DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION_ARRAY__STRUCT_HPP_
