#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "drone_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__drone_msgs__msg__ArucoDetection() -> *const std::ffi::c_void;
}

#[link(name = "drone_msgs__rosidl_generator_c")]
extern "C" {
    fn drone_msgs__msg__ArucoDetection__init(msg: *mut ArucoDetection) -> bool;
    fn drone_msgs__msg__ArucoDetection__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ArucoDetection>, size: usize) -> bool;
    fn drone_msgs__msg__ArucoDetection__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ArucoDetection>);
    fn drone_msgs__msg__ArucoDetection__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ArucoDetection>, out_seq: *mut rosidl_runtime_rs::Sequence<ArucoDetection>) -> bool;
}

// Corresponds to drone_msgs__msg__ArucoDetection
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Single ArUco marker detection

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ArucoDetection {

    // This member is not documented.
    #[allow(missing_docs)]
    pub marker_id: i32,

    /// 4 corners, each with (x, y) coordinates: [x1, y1, x2, y2, x3, y3, x4, y4]
    pub corners: [f32; 8],

}



impl Default for ArucoDetection {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !drone_msgs__msg__ArucoDetection__init(&mut msg as *mut _) {
        panic!("Call to drone_msgs__msg__ArucoDetection__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ArucoDetection {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__ArucoDetection__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__ArucoDetection__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__ArucoDetection__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ArucoDetection {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ArucoDetection where Self: Sized {
  const TYPE_NAME: &'static str = "drone_msgs/msg/ArucoDetection";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__drone_msgs__msg__ArucoDetection() }
  }
}


#[link(name = "drone_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__drone_msgs__msg__ArucoDetectionArray() -> *const std::ffi::c_void;
}

#[link(name = "drone_msgs__rosidl_generator_c")]
extern "C" {
    fn drone_msgs__msg__ArucoDetectionArray__init(msg: *mut ArucoDetectionArray) -> bool;
    fn drone_msgs__msg__ArucoDetectionArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ArucoDetectionArray>, size: usize) -> bool;
    fn drone_msgs__msg__ArucoDetectionArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ArucoDetectionArray>);
    fn drone_msgs__msg__ArucoDetectionArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ArucoDetectionArray>, out_seq: *mut rosidl_runtime_rs::Sequence<ArucoDetectionArray>) -> bool;
}

// Corresponds to drone_msgs__msg__ArucoDetectionArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Array of ArUco marker detections

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ArucoDetectionArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub detections: rosidl_runtime_rs::Sequence<super::super::msg::rmw::ArucoDetection>,

}



impl Default for ArucoDetectionArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !drone_msgs__msg__ArucoDetectionArray__init(&mut msg as *mut _) {
        panic!("Call to drone_msgs__msg__ArucoDetectionArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ArucoDetectionArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__ArucoDetectionArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__ArucoDetectionArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__ArucoDetectionArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ArucoDetectionArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ArucoDetectionArray where Self: Sized {
  const TYPE_NAME: &'static str = "drone_msgs/msg/ArucoDetectionArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__drone_msgs__msg__ArucoDetectionArray() }
  }
}


#[link(name = "drone_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__drone_msgs__msg__MarkerPose() -> *const std::ffi::c_void;
}

#[link(name = "drone_msgs__rosidl_generator_c")]
extern "C" {
    fn drone_msgs__msg__MarkerPose__init(msg: *mut MarkerPose) -> bool;
    fn drone_msgs__msg__MarkerPose__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MarkerPose>, size: usize) -> bool;
    fn drone_msgs__msg__MarkerPose__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MarkerPose>);
    fn drone_msgs__msg__MarkerPose__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MarkerPose>, out_seq: *mut rosidl_runtime_rs::Sequence<MarkerPose>) -> bool;
}

// Corresponds to drone_msgs__msg__MarkerPose
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Marker pose with ID

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MarkerPose {

    // This member is not documented.
    #[allow(missing_docs)]
    pub marker_id: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pose: geometry_msgs::msg::rmw::Pose,

}



impl Default for MarkerPose {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !drone_msgs__msg__MarkerPose__init(&mut msg as *mut _) {
        panic!("Call to drone_msgs__msg__MarkerPose__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MarkerPose {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__MarkerPose__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__MarkerPose__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__MarkerPose__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MarkerPose {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MarkerPose where Self: Sized {
  const TYPE_NAME: &'static str = "drone_msgs/msg/MarkerPose";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__drone_msgs__msg__MarkerPose() }
  }
}


#[link(name = "drone_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__drone_msgs__msg__MarkerPoseArray() -> *const std::ffi::c_void;
}

#[link(name = "drone_msgs__rosidl_generator_c")]
extern "C" {
    fn drone_msgs__msg__MarkerPoseArray__init(msg: *mut MarkerPoseArray) -> bool;
    fn drone_msgs__msg__MarkerPoseArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MarkerPoseArray>, size: usize) -> bool;
    fn drone_msgs__msg__MarkerPoseArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MarkerPoseArray>);
    fn drone_msgs__msg__MarkerPoseArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MarkerPoseArray>, out_seq: *mut rosidl_runtime_rs::Sequence<MarkerPoseArray>) -> bool;
}

// Corresponds to drone_msgs__msg__MarkerPoseArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Array of marker poses

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MarkerPoseArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub poses: rosidl_runtime_rs::Sequence<super::super::msg::rmw::MarkerPose>,

}



impl Default for MarkerPoseArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !drone_msgs__msg__MarkerPoseArray__init(&mut msg as *mut _) {
        panic!("Call to drone_msgs__msg__MarkerPoseArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MarkerPoseArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__MarkerPoseArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__MarkerPoseArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { drone_msgs__msg__MarkerPoseArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MarkerPoseArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MarkerPoseArray where Self: Sized {
  const TYPE_NAME: &'static str = "drone_msgs/msg/MarkerPoseArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__drone_msgs__msg__MarkerPoseArray() }
  }
}


