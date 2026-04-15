// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from drone_msgs:msg/MarkerPose.idl
// generated code does not contain a copyright notice

#ifndef DRONE_MSGS__MSG__DETAIL__MARKER_POSE__STRUCT_H_
#define DRONE_MSGS__MSG__DETAIL__MARKER_POSE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__struct.h"

/// Struct defined in msg/MarkerPose in the package drone_msgs.
/**
  * Marker pose with ID
 */
typedef struct drone_msgs__msg__MarkerPose
{
  int32_t marker_id;
  geometry_msgs__msg__Pose pose;
} drone_msgs__msg__MarkerPose;

// Struct for a sequence of drone_msgs__msg__MarkerPose.
typedef struct drone_msgs__msg__MarkerPose__Sequence
{
  drone_msgs__msg__MarkerPose * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} drone_msgs__msg__MarkerPose__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DRONE_MSGS__MSG__DETAIL__MARKER_POSE__STRUCT_H_
