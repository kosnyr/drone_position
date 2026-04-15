// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from drone_msgs:msg/MarkerPoseArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "drone_msgs/msg/detail/marker_pose_array__rosidl_typesupport_introspection_c.h"
#include "drone_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "drone_msgs/msg/detail/marker_pose_array__functions.h"
#include "drone_msgs/msg/detail/marker_pose_array__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `poses`
#include "drone_msgs/msg/marker_pose.h"
// Member `poses`
#include "drone_msgs/msg/detail/marker_pose__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  drone_msgs__msg__MarkerPoseArray__init(message_memory);
}

void drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_fini_function(void * message_memory)
{
  drone_msgs__msg__MarkerPoseArray__fini(message_memory);
}

size_t drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__size_function__MarkerPoseArray__poses(
  const void * untyped_member)
{
  const drone_msgs__msg__MarkerPose__Sequence * member =
    (const drone_msgs__msg__MarkerPose__Sequence *)(untyped_member);
  return member->size;
}

const void * drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__get_const_function__MarkerPoseArray__poses(
  const void * untyped_member, size_t index)
{
  const drone_msgs__msg__MarkerPose__Sequence * member =
    (const drone_msgs__msg__MarkerPose__Sequence *)(untyped_member);
  return &member->data[index];
}

void * drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__get_function__MarkerPoseArray__poses(
  void * untyped_member, size_t index)
{
  drone_msgs__msg__MarkerPose__Sequence * member =
    (drone_msgs__msg__MarkerPose__Sequence *)(untyped_member);
  return &member->data[index];
}

void drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__fetch_function__MarkerPoseArray__poses(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const drone_msgs__msg__MarkerPose * item =
    ((const drone_msgs__msg__MarkerPose *)
    drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__get_const_function__MarkerPoseArray__poses(untyped_member, index));
  drone_msgs__msg__MarkerPose * value =
    (drone_msgs__msg__MarkerPose *)(untyped_value);
  *value = *item;
}

void drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__assign_function__MarkerPoseArray__poses(
  void * untyped_member, size_t index, const void * untyped_value)
{
  drone_msgs__msg__MarkerPose * item =
    ((drone_msgs__msg__MarkerPose *)
    drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__get_function__MarkerPoseArray__poses(untyped_member, index));
  const drone_msgs__msg__MarkerPose * value =
    (const drone_msgs__msg__MarkerPose *)(untyped_value);
  *item = *value;
}

bool drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__resize_function__MarkerPoseArray__poses(
  void * untyped_member, size_t size)
{
  drone_msgs__msg__MarkerPose__Sequence * member =
    (drone_msgs__msg__MarkerPose__Sequence *)(untyped_member);
  drone_msgs__msg__MarkerPose__Sequence__fini(member);
  return drone_msgs__msg__MarkerPose__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_message_member_array[2] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(drone_msgs__msg__MarkerPoseArray, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "poses",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(drone_msgs__msg__MarkerPoseArray, poses),  // bytes offset in struct
    NULL,  // default value
    drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__size_function__MarkerPoseArray__poses,  // size() function pointer
    drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__get_const_function__MarkerPoseArray__poses,  // get_const(index) function pointer
    drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__get_function__MarkerPoseArray__poses,  // get(index) function pointer
    drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__fetch_function__MarkerPoseArray__poses,  // fetch(index, &value) function pointer
    drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__assign_function__MarkerPoseArray__poses,  // assign(index, value) function pointer
    drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__resize_function__MarkerPoseArray__poses  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_message_members = {
  "drone_msgs__msg",  // message namespace
  "MarkerPoseArray",  // message name
  2,  // number of fields
  sizeof(drone_msgs__msg__MarkerPoseArray),
  drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_message_member_array,  // message members
  drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_init_function,  // function to initialize message memory (memory has to be allocated)
  drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_message_type_support_handle = {
  0,
  &drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_drone_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, drone_msgs, msg, MarkerPoseArray)() {
  drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, drone_msgs, msg, MarkerPose)();
  if (!drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_message_type_support_handle.typesupport_identifier) {
    drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &drone_msgs__msg__MarkerPoseArray__rosidl_typesupport_introspection_c__MarkerPoseArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
