// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from drone_msgs:msg/MarkerPoseArray.idl
// generated code does not contain a copyright notice
#include "drone_msgs/msg/detail/marker_pose_array__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `poses`
#include "drone_msgs/msg/detail/marker_pose__functions.h"

bool
drone_msgs__msg__MarkerPoseArray__init(drone_msgs__msg__MarkerPoseArray * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    drone_msgs__msg__MarkerPoseArray__fini(msg);
    return false;
  }
  // poses
  if (!drone_msgs__msg__MarkerPose__Sequence__init(&msg->poses, 0)) {
    drone_msgs__msg__MarkerPoseArray__fini(msg);
    return false;
  }
  return true;
}

void
drone_msgs__msg__MarkerPoseArray__fini(drone_msgs__msg__MarkerPoseArray * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // poses
  drone_msgs__msg__MarkerPose__Sequence__fini(&msg->poses);
}

bool
drone_msgs__msg__MarkerPoseArray__are_equal(const drone_msgs__msg__MarkerPoseArray * lhs, const drone_msgs__msg__MarkerPoseArray * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // poses
  if (!drone_msgs__msg__MarkerPose__Sequence__are_equal(
      &(lhs->poses), &(rhs->poses)))
  {
    return false;
  }
  return true;
}

bool
drone_msgs__msg__MarkerPoseArray__copy(
  const drone_msgs__msg__MarkerPoseArray * input,
  drone_msgs__msg__MarkerPoseArray * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // poses
  if (!drone_msgs__msg__MarkerPose__Sequence__copy(
      &(input->poses), &(output->poses)))
  {
    return false;
  }
  return true;
}

drone_msgs__msg__MarkerPoseArray *
drone_msgs__msg__MarkerPoseArray__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  drone_msgs__msg__MarkerPoseArray * msg = (drone_msgs__msg__MarkerPoseArray *)allocator.allocate(sizeof(drone_msgs__msg__MarkerPoseArray), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(drone_msgs__msg__MarkerPoseArray));
  bool success = drone_msgs__msg__MarkerPoseArray__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
drone_msgs__msg__MarkerPoseArray__destroy(drone_msgs__msg__MarkerPoseArray * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    drone_msgs__msg__MarkerPoseArray__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
drone_msgs__msg__MarkerPoseArray__Sequence__init(drone_msgs__msg__MarkerPoseArray__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  drone_msgs__msg__MarkerPoseArray * data = NULL;

  if (size) {
    data = (drone_msgs__msg__MarkerPoseArray *)allocator.zero_allocate(size, sizeof(drone_msgs__msg__MarkerPoseArray), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = drone_msgs__msg__MarkerPoseArray__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        drone_msgs__msg__MarkerPoseArray__fini(&data[i - 1]);
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
drone_msgs__msg__MarkerPoseArray__Sequence__fini(drone_msgs__msg__MarkerPoseArray__Sequence * array)
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
      drone_msgs__msg__MarkerPoseArray__fini(&array->data[i]);
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

drone_msgs__msg__MarkerPoseArray__Sequence *
drone_msgs__msg__MarkerPoseArray__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  drone_msgs__msg__MarkerPoseArray__Sequence * array = (drone_msgs__msg__MarkerPoseArray__Sequence *)allocator.allocate(sizeof(drone_msgs__msg__MarkerPoseArray__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = drone_msgs__msg__MarkerPoseArray__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
drone_msgs__msg__MarkerPoseArray__Sequence__destroy(drone_msgs__msg__MarkerPoseArray__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    drone_msgs__msg__MarkerPoseArray__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
drone_msgs__msg__MarkerPoseArray__Sequence__are_equal(const drone_msgs__msg__MarkerPoseArray__Sequence * lhs, const drone_msgs__msg__MarkerPoseArray__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!drone_msgs__msg__MarkerPoseArray__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
drone_msgs__msg__MarkerPoseArray__Sequence__copy(
  const drone_msgs__msg__MarkerPoseArray__Sequence * input,
  drone_msgs__msg__MarkerPoseArray__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(drone_msgs__msg__MarkerPoseArray);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    drone_msgs__msg__MarkerPoseArray * data =
      (drone_msgs__msg__MarkerPoseArray *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!drone_msgs__msg__MarkerPoseArray__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          drone_msgs__msg__MarkerPoseArray__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!drone_msgs__msg__MarkerPoseArray__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
