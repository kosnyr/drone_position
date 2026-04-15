// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from drone_msgs:msg/MarkerPose.idl
// generated code does not contain a copyright notice
#include "drone_msgs/msg/detail/marker_pose__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `pose`
#include "geometry_msgs/msg/detail/pose__functions.h"

bool
drone_msgs__msg__MarkerPose__init(drone_msgs__msg__MarkerPose * msg)
{
  if (!msg) {
    return false;
  }
  // marker_id
  // pose
  if (!geometry_msgs__msg__Pose__init(&msg->pose)) {
    drone_msgs__msg__MarkerPose__fini(msg);
    return false;
  }
  return true;
}

void
drone_msgs__msg__MarkerPose__fini(drone_msgs__msg__MarkerPose * msg)
{
  if (!msg) {
    return;
  }
  // marker_id
  // pose
  geometry_msgs__msg__Pose__fini(&msg->pose);
}

bool
drone_msgs__msg__MarkerPose__are_equal(const drone_msgs__msg__MarkerPose * lhs, const drone_msgs__msg__MarkerPose * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // marker_id
  if (lhs->marker_id != rhs->marker_id) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__Pose__are_equal(
      &(lhs->pose), &(rhs->pose)))
  {
    return false;
  }
  return true;
}

bool
drone_msgs__msg__MarkerPose__copy(
  const drone_msgs__msg__MarkerPose * input,
  drone_msgs__msg__MarkerPose * output)
{
  if (!input || !output) {
    return false;
  }
  // marker_id
  output->marker_id = input->marker_id;
  // pose
  if (!geometry_msgs__msg__Pose__copy(
      &(input->pose), &(output->pose)))
  {
    return false;
  }
  return true;
}

drone_msgs__msg__MarkerPose *
drone_msgs__msg__MarkerPose__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  drone_msgs__msg__MarkerPose * msg = (drone_msgs__msg__MarkerPose *)allocator.allocate(sizeof(drone_msgs__msg__MarkerPose), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(drone_msgs__msg__MarkerPose));
  bool success = drone_msgs__msg__MarkerPose__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
drone_msgs__msg__MarkerPose__destroy(drone_msgs__msg__MarkerPose * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    drone_msgs__msg__MarkerPose__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
drone_msgs__msg__MarkerPose__Sequence__init(drone_msgs__msg__MarkerPose__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  drone_msgs__msg__MarkerPose * data = NULL;

  if (size) {
    data = (drone_msgs__msg__MarkerPose *)allocator.zero_allocate(size, sizeof(drone_msgs__msg__MarkerPose), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = drone_msgs__msg__MarkerPose__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        drone_msgs__msg__MarkerPose__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
drone_msgs__msg__MarkerPose__Sequence__fini(drone_msgs__msg__MarkerPose__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      drone_msgs__msg__MarkerPose__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

drone_msgs__msg__MarkerPose__Sequence *
drone_msgs__msg__MarkerPose__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  drone_msgs__msg__MarkerPose__Sequence * array = (drone_msgs__msg__MarkerPose__Sequence *)allocator.allocate(sizeof(drone_msgs__msg__MarkerPose__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = drone_msgs__msg__MarkerPose__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
drone_msgs__msg__MarkerPose__Sequence__destroy(drone_msgs__msg__MarkerPose__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    drone_msgs__msg__MarkerPose__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
drone_msgs__msg__MarkerPose__Sequence__are_equal(const drone_msgs__msg__MarkerPose__Sequence * lhs, const drone_msgs__msg__MarkerPose__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!drone_msgs__msg__MarkerPose__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
drone_msgs__msg__MarkerPose__Sequence__copy(
  const drone_msgs__msg__MarkerPose__Sequence * input,
  drone_msgs__msg__MarkerPose__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(drone_msgs__msg__MarkerPose);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    drone_msgs__msg__MarkerPose * data =
      (drone_msgs__msg__MarkerPose *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!drone_msgs__msg__MarkerPose__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          drone_msgs__msg__MarkerPose__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!drone_msgs__msg__MarkerPose__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
