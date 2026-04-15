#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kalman Filter for 3D Position Tracking
Shared module for drone position estimation
"""

import numpy as np


class KalmanFilter3D:
    """Simple Kalman filter for 3D position tracking"""
    
    def __init__(self, process_noise: float = 0.01, measurement_noise: float = 0.1):
        # State: [x, y, z, vx, vy, vz]
        self.state = np.zeros(6)
        self.P = np.eye(6) * 1.0  # Covariance matrix
        
        # Process noise
        self.Q = np.eye(6) * process_noise
        
        # Measurement noise
        self.R = np.eye(3) * measurement_noise
        
        # State transition matrix (constant velocity model)
        self.F = np.eye(6)
        
        # Measurement matrix (we only measure position)
        self.H = np.zeros((3, 6))
        self.H[0, 0] = 1.0
        self.H[1, 1] = 1.0
        self.H[2, 2] = 1.0
        
        self.initialized = False
        self.last_time = None
    
    def predict(self, dt: float):
        """Predict step with time delta"""
        # Update state transition matrix with dt
        self.F[0, 3] = dt
        self.F[1, 4] = dt
        self.F[2, 5] = dt
        
        # Predict state
        self.state = self.F @ self.state
        
        # Predict covariance
        self.P = self.F @ self.P @ self.F.T + self.Q
    
    def update(self, measurement: np.ndarray):
        """Update step with new measurement [x, y, z]"""
        if not self.initialized:
            # Initialize state with first measurement
            self.state[0:3] = measurement
            self.initialized = True
            return self.state[0:3]
        
        # Innovation
        y = measurement - self.H @ self.state
        
        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R
        
        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Update state
        self.state = self.state + K @ y
        
        # Update covariance
        self.P = (np.eye(6) - K @ self.H) @ self.P
        
        return self.state[0:3]
    
    def process(self, measurement: np.ndarray, timestamp: float) -> np.ndarray:
        """Process measurement with timestamp"""
        if self.last_time is not None:
            dt = timestamp - self.last_time
            if dt > 0 and dt < 1.0:  # Sanity check
                self.predict(dt)
        
        self.last_time = timestamp
        return self.update(measurement)
