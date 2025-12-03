"""
Background information models for multi-select fields.
Defines available options and validation for JSONB array fields.
"""
from typing import List
from pydantic import BaseModel, field_validator


class BackgroundInfo(BaseModel):
    """
    Background information model for user profile.
    Handles multi-select array fields stored as JSONB in PostgreSQL.
    """

    programming_languages: List[str] = []
    frameworks: List[str] = []
    robotics_platforms: List[str] = []
    sensors_actuators: List[str] = []

    @field_validator('programming_languages', 'frameworks', 'robotics_platforms', 'sensors_actuators')
    @classmethod
    def validate_non_empty_strings(cls, v: List[str]) -> List[str]:
        """Ensure all array items are non-empty strings."""
        if v is None:
            return []

        # Filter out empty strings and strip whitespace
        cleaned = [item.strip() for item in v if item and item.strip()]
        return cleaned

    @field_validator('programming_languages', 'frameworks', 'robotics_platforms', 'sensors_actuators')
    @classmethod
    def validate_max_items(cls, v: List[str]) -> List[str]:
        """Limit arrays to reasonable maximum (20 items)."""
        if len(v) > 20:
            raise ValueError('Cannot select more than 20 items')
        return v


class PredefinedOptions(BaseModel):
    """
    Predefined options for background fields.
    These are the common choices presented to users.
    """

    programming_languages: List[str] = [
        "Python",
        "C++",
        "Java",
        "JavaScript",
        "C",
        "MATLAB",
        "R",
        "Go",
        "Rust",
        "Swift",
    ]

    frameworks: List[str] = [
        "ROS 2",
        "ROS 1",
        "TensorFlow",
        "PyTorch",
        "OpenCV",
        "Gazebo",
        "Isaac Sim",
        "Unity",
        "Unreal Engine",
        "WebRTC",
    ]

    robotics_platforms: List[str] = [
        "Arduino",
        "Raspberry Pi",
        "NVIDIA Jetson",
        "Intel NUC",
        "Custom PCB",
        "TurtleBot",
        "UR Robot",
        "Franka Emika",
        "ABB Robot",
        "Mobile Robot",
    ]

    sensors_actuators: List[str] = [
        "LiDAR",
        "Camera (RGB)",
        "Depth Camera",
        "IMU",
        "GPS",
        "Ultrasonic",
        "Servo Motors",
        "Stepper Motors",
        "DC Motors",
        "Gripper",
    ]


# Singleton instance for easy access
predefined_options = PredefinedOptions()
