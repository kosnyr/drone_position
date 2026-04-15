// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from drone_msgs:msg/ArucoDetectionArray.idl
// generated code does not contain a copyright notice

#ifndef DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION_ARRAY__STRUCT_H_
#define DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION_ARRAY__STRUCT_H_

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
// Member 'detections'
#include "drone_msgs/msg/detail/aruco_detection__struct.h"

/// Struct defined in msg/ArucoDetectionArray in the package drone_msgs.
/**
  * Array of ArUco marker detections
 */
typedef struct drone_msgs__msg__ArucoDetectionArray
{
  std_msgs__msg__Header header;
  drone_msgs__msg__ArucoDetection__Sequence detections;
} drone_msgs__msg__ArucoDetectionArray;

// Struct for a sequence of drone_msgs__msg__ArucoDetectionArray.
typedef struct drone_msgs__msg__ArucoDetectionArray__Sequence
{
  drone_msgs__msg__ArucoDetectionArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} drone_msgs__msg__ArucoDetectionArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // DRONE_MSGS__MSG__DETAIL__ARUCO_DETECTION_ARRAY__STRUCT_H_
