// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from drone_msgs:msg/ArucoDetection.idl
// generated code does not contain a copyright notice
#include "drone_msgs/msg/detail/aruco_detection__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
drone_msgs__msg__ArucoDetection__init(drone_msgs__msg__ArucoDetection * msg)
{
  if (!msg) {
    return false;
  }
  // marker_id
  // corners
  return true;
}

void
drone_msgs__msg__ArucoDetection__fini(drone_msgs__msg__ArucoDetection * msg)
{
  if (!msg) {
    return;
  }
  // marker_id
  // corners
}

bool
drone_msgs__msg__ArucoDetection__are_equal(const drone_msgs__msg__ArucoDetection * lhs, const drone_msgs__msg__ArucoDetection * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // marker_id
  if (lhs->marker_id != rhs->marker_id) {
    return false;
  }
  // corners
  for (size_t i = 0; i < 8; ++i) {
    if (lhs->corners[i] != rhs->corners[i]) {
      return false;
    }
  }
  return true;
}

bool
drone_msgs__msg__ArucoDetection__copy(
  const drone_msgs__msg__ArucoDetection * input,
  drone_msgs__msg__ArucoDetection * output)
{
  if (!input || !output) {
    return false;
  }
  // marker_id
  output->marker_id = input->marker_id;
  // corners
  for (size_t i = 0; i < 8; ++i) {
    output->corners[i] = input->corners[i];
  }
  return true;
}

drone_msgs__msg__ArucoDetection *
drone_msgs__msg__ArucoDetection__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  drone_msgs__msg__ArucoDetection * msg = (drone_msgs__msg__ArucoDetection *)allocator.allocate(sizeof(drone_msgs__msg__ArucoDetection), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(drone_msgs__msg__ArucoDetection));
  bool success = drone_msgs__msg__ArucoDetection__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
drone_msgs__msg__ArucoDetection__destroy(drone_msgs__msg__ArucoDetection * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    drone_msgs__msg__ArucoDetection__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
drone_msgs__msg__ArucoDetection__Sequence__init(drone_msgs__msg__ArucoDetection__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  drone_msgs__msg__ArucoDetection * data = NULL;

  if (size) {
    data = (drone_msgs__msg__ArucoDetection *)allocator.zero_allocate(size, sizeof(drone_msgs__msg__ArucoDetection), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = drone_msgs__msg__ArucoDetection__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        drone_msgs__msg__ArucoDetection__fini(&data[i - 1]);
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
drone_msgs__msg__ArucoDetection__Sequence__fini(drone_msgs__msg__ArucoDetection__Sequence * array)
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
      drone_msgs__msg__ArucoDetection__fini(&array->data[i]);
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

drone_msgs__msg__ArucoDetection__Sequence *
drone_msgs__msg__ArucoDetection__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  drone_msgs__msg__ArucoDetection__Sequence * array = (drone_msgs__msg__ArucoDetection__Sequence *)allocator.allocate(sizeof(drone_msgs__msg__ArucoDetection__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = drone_msgs__msg__ArucoDetection__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
drone_msgs__msg__ArucoDetection__Sequence__destroy(drone_msgs__msg__ArucoDetection__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    drone_msgs__msg__ArucoDetection__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
drone_msgs__msg__ArucoDetection__Sequence__are_equal(const drone_msgs__msg__ArucoDetection__Sequence * lhs, const drone_msgs__msg__ArucoDetection__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!drone_msgs__msg__ArucoDetection__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
drone_msgs__msg__ArucoDetection__Sequence__copy(
  const drone_msgs__msg__ArucoDetection__Sequence * input,
  drone_msgs__msg__ArucoDetection__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(drone_msgs__msg__ArucoDetection);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    drone_msgs__msg__ArucoDetection * data =
      (drone_msgs__msg__ArucoDetection *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!drone_msgs__msg__ArucoDetection__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          drone_msgs__msg__ArucoDetection__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!drone_msgs__msg__ArucoDetection__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
