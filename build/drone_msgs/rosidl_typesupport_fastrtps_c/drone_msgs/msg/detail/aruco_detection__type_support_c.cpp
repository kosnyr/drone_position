// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from drone_msgs:msg/ArucoDetection.idl
// generated code does not contain a copyright notice
#include "drone_msgs/msg/detail/aruco_detection__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "drone_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "drone_msgs/msg/detail/aruco_detection__struct.h"
#include "drone_msgs/msg/detail/aruco_detection__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif


// forward declare type support functions


using _ArucoDetection__ros_msg_type = drone_msgs__msg__ArucoDetection;

static bool _ArucoDetection__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _ArucoDetection__ros_msg_type * ros_message = static_cast<const _ArucoDetection__ros_msg_type *>(untyped_ros_message);
  // Field name: marker_id
  {
    cdr << ros_message->marker_id;
  }

  // Field name: corners
  {
    size_t size = 8;
    auto array_ptr = ros_message->corners;
    cdr.serializeArray(array_ptr, size);
  }

  return true;
}

static bool _ArucoDetection__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _ArucoDetection__ros_msg_type * ros_message = static_cast<_ArucoDetection__ros_msg_type *>(untyped_ros_message);
  // Field name: marker_id
  {
    cdr >> ros_message->marker_id;
  }

  // Field name: corners
  {
    size_t size = 8;
    auto array_ptr = ros_message->corners;
    cdr.deserializeArray(array_ptr, size);
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_drone_msgs
size_t get_serialized_size_drone_msgs__msg__ArucoDetection(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _ArucoDetection__ros_msg_type * ros_message = static_cast<const _ArucoDetection__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name marker_id
  {
    size_t item_size = sizeof(ros_message->marker_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name corners
  {
    size_t array_size = 8;
    auto array_ptr = ros_message->corners;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _ArucoDetection__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_drone_msgs__msg__ArucoDetection(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_drone_msgs
size_t max_serialized_size_drone_msgs__msg__ArucoDetection(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // member: marker_id
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: corners
  {
    size_t array_size = 8;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = drone_msgs__msg__ArucoDetection;
    is_plain =
      (
      offsetof(DataType, corners) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _ArucoDetection__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_drone_msgs__msg__ArucoDetection(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_ArucoDetection = {
  "drone_msgs::msg",
  "ArucoDetection",
  _ArucoDetection__cdr_serialize,
  _ArucoDetection__cdr_deserialize,
  _ArucoDetection__get_serialized_size,
  _ArucoDetection__max_serialized_size
};

static rosidl_message_type_support_t _ArucoDetection__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_ArucoDetection,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, drone_msgs, msg, ArucoDetection)() {
  return &_ArucoDetection__type_support;
}

#if defined(__cplusplus)
}
#endif
