# GreenIntel

This is a precision agriculture project that integrates machine learning, robotics and FPGA-based path planning to autonomously detect weeds and navigate a field. It leverages a MobileNetV2-based weed classifier, FPGA Verilog logic for movement planning, and an Arduino-controlled walking robot.

## Project Overview

### GreenIntel unifies three core components to enable an autonomous field robot that detects weeds and plans navigation:
1. Machine Learning: A MobileNetV2 model implemented with Tensorflow/Keras that classifies images of plants into weed or non-weed.
2. Walking Robot (Arduino C): Servo-driven quadruped robot controlled via serial commands to execute sit, stand, wave, and movement routines.
3. FPGA Path Planning: A custom Verilog module (weedIntel.v) that generates movement signals for the robot (front, right, stop) based on detection input.

## Features
- Real-time image-based weed detection
- Arduino firmware supporting multiple gaits and actions
- Modular Verilog FSM for movement and decision logic

## Requirements
- Python 3.8+ with OpenCV, TensorFlow/Keras, scikit-learn
- Vivado / Quartus for Verilog synthesis
- Arduino IDE or PlatformIO
- USB camera

## Folder Structure
- `ML_Model/` → Machine Learning scripts for weed detection with MobileNetV2 model.
- `FPGA_PathPlanning/` → Verilog code for robot path planning.
- `WalkingRobot/` → Arduino C code for robot movement.
- `Integration_Plan/` → Notes on integrating all components.
- `docs/` → Architecture diagrams & extra documentation.

## Future Enhancements
- End-to-end integration of the ML model with latest FPGA development boards for streamlined usage.
- Real-time execution improvements with upgraded processing modules.
- GPS-based autonomous movement tracking and mapping.
- Expanded dataset to detect and classify additional weed species.
- Cloud-based dashboard for remote monitoring and data storage.

---
Made for a hackathon project!

For any issues or contributions, feel free to open an issue or submit a pull request.

