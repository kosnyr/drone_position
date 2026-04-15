// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from drone_msgs:msg/ArucoDetection.idl
// generated code does not contain a copyright notice

#ifndef DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION__STRUCT_H_
#define DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/ArucoDetection in the package drone_msgs.
/**
  * Single ArUco marker detection
 */
typedef struct drone_msgs__msg__ArucoDetection
{
  int32_t marker_id;
  /// 4 corners, each with (x, y) coordinates: [x1, y1, x2, y2, x3, y3, x4, y4]
  float corners[8];
} drone_msgs__msg__ArucoDetection;

// Struct for a sequence of drone_msgs__msg__ArucoDetection.
typedef struct drone_msgs__msg__ArucoDetection__Sequence
{
  drone_msgs__msg__ArucoDetection * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} drone_msgs__msg__ArucoDetection__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION__STRUCT_H_
