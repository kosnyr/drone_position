// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from drone_msgs:msg/MarkerPose.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "drone_msgs/msg/detail/marker_pose__rosidl_typesupport_introspection_c.h"
#include "drone_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "drone_msgs/msg/detail/marker_pose__functions.h"
#include "drone_msgs/msg/detail/marker_pose__struct.h"


// Include directives for member types
// Member `pose`
#include "geometry_msgs/msg/pose.h"
// Member `pose`
#include "geometry_msgs/msg/detail/pose__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  drone_msgs__msg__MarkerPose__init(message_memory);
}

void drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_fini_function(void * message_memory)
{
  drone_msgs__msg__MarkerPose__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_message_member_array[2] = {
  {
    "marker_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(drone_msgs__msg__MarkerPose, marker_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pose",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(drone_msgs__msg__MarkerPose, pose),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_message_members = {
  "drone_msgs__msg",  // message namespace
  "MarkerPose",  // message name
  2,  // number of fields
  sizeof(drone_msgs__msg__MarkerPose),
  drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_message_member_array,  // message members
  drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_init_function,  // function to initialize message memory (memory has to be allocated)
  drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_message_type_support_handle = {
  0,
  &drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_drone_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, drone_msgs, msg, MarkerPose)() {
  drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Pose)();
  if (!drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_message_type_support_handle.typesupport_identifier) {
    drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &drone_msgs__msg__MarkerPose__rosidl_typesupport_introspection_c__MarkerPose_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
