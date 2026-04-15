// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from drone_msgs:msg/MarkerPoseArray.idl
// generated code does not contain a copyright notice

#ifndef DRONE_MSGS__MSG__DETAIL__MARKER_POSE_ARRAY__STRUCT_H_
#define DRONE_MSGS__MSG__DETAIL__MARKER_POSE_ARRAY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'poses'
#include "drone_msgs/msg/detail/marker_pose__struct.h"

/// Struct defined in msg/MarkerPoseArray in the package drone_msgs.
/**
  * Array of marker poses
 */
typedef struct drone_msgs__msg__MarkerPoseArray
{
  std_msgs__msg__Header header;
  drone_msgs__msg__MarkerPose__Sequence poses;
} drone_msgs__msg__MarkerPoseArray;

// Struct for a sequence of drone_msgs__msg__MarkerPoseArray.
typedef struct drone_msgs__msg__MarkerPoseArray__Sequence
{
  drone_msgs__msg__MarkerPoseArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} drone_msgs__msg__MarkerPoseArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DRONE_MSGS__MSG__DETAIL__MARKER_POSE_ARRAY__STRUCT_H_
