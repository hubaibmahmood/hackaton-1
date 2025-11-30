<!--
Sync Impact Report:
Version change: None → v0.1.0
Modified principles:
- PROJECT_NAME: Physical AI & Humanoid Robotics Textbook
- Principle 1: I. Embodied Intelligence Focus
- Principle 2: II. ROS 2 as the Robotic Nervous System
- Principle 3: III. Digital Twin for Simulation and Interaction
- Principle 4: IV. NVIDIA Isaac for Advanced AI-Robot Brain
- Principle 5: V. Vision-Language-Action (VLA) Integration
- Principle 6: VI. Learning Outcomes Driven Content
- Principle 7: VII. Practical Capstone Project
- Principle 8: VIII. AI/Spec-Driven Book Creation with Spec-Kit Plus
- Principle 9: IX. Embedded RAG Chatbot for Interactive Learning
Added sections: None
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ✅ updated
- .specify/templates/spec-template.md: ✅ updated
- .specify/templates/tasks-template.md: ✅ updated
- .specify/templates/commands/*.md: ✅ updated
Follow-up TODOs: None
-->
# Physical AI & Humanoid Robotics Textbook Constitution

## Core Principles

### I. Embodied Intelligence Focus
AI systems must operate within physical constraints, bridging digital intelligence with robotic embodiments for real-world interaction. All components and content must demonstrate direct and practical application in humanoid robotics, evidenced by functional simulations, proof-of-concept code, or direct integration with specified hardware/software platforms (e.g., ROS 2, Gazebo, NVIDIA Isaac).

### II. ROS 2 as the Robotic Nervous System
ROS 2 must be the foundational middleware for all robotic control and communication. This includes strict adherence to ROS 2 nodes, topics, services, and the seamless integration of Python agents via `rclpy`. URDF will be the standard for humanoid robot descriptions.

### III. Digital Twin for Simulation and Interaction
Gazebo and Unity will be used for high-fidelity physics simulation, environment building, and human-robot interaction. Simulation accuracy, including gravity, collisions, and sensor data (LiDAR, Depth Cameras, and IMUs), is paramount.

### IV. NVIDIA Isaac for Advanced AI-Robot Brain
NVIDIA Isaac Sim will be utilized for photorealistic simulation and synthetic data generation, and Isaac ROS for hardware-accelerated VSLAM and navigation. Nav2 will be the framework for bipedal humanoid path planning.

### V. Vision-Language-Action (VLA) Integration
The convergence of LLMs and robotics is central. OpenAI Whisper will enable voice-to-action commands, and LLMs will be used for cognitive planning, translating natural language ("Clean the room") into sequences of ROS 2 actions for autonomous robot tasks.

### VI. Learning Outcomes Driven Content
All textbook content, examples, and projects must directly align with and facilitate the six defined learning outcomes. This alignment will be explicitly mapped in content specifications (refer to Spec-Kit Plus workflow), and regular content audits will verify that each section contributes measurably to specific learning outcomes: understanding Physical AI principles, mastering ROS 2, simulating robots with Gazebo and Unity, developing with NVIDIA Isaac, designing humanoid robots for natural interactions, and integrating GPT models for conversational robotics.

### VII. Practical Capstone Project
The "Autonomous Humanoid" capstone project must be the ultimate demonstration of integrated learning, where a simulated robot receives a voice command, plans a path, navigates obstacles, identifies an object using computer vision, and manipulates it.

### VIII. AI/Spec-Driven Book Creation with Spec-Kit Plus
The book development process will strictly adhere to Specification-Driven Development (SDD) principles using Spec-Kit Plus. This includes generating precise specifications for content, detailed implementation plans, and testable tasks for all chapters and modules.

### IX. Embedded RAG Chatbot for Interactive Learning
An integrated RAG chatbot, built with OpenAI Agents/ChatKit SDKs, FastAPI, Neon Serverless Postgres, and Qdrant Cloud Free Tier, must be embedded within the published book. It must be capable of answering questions about book content, including user-selected text, to enhance interactive learning.

### X. Content Quality and Academic Integrity
All textbook content must adhere to academic standards for clarity, accuracy, and originality. Factual claims must be verifiable and properly cited using a consistent, project-defined citation style (e.g., IEEE). Plagiarism checks will be mandatory for all generated and human-contributed content to ensure intellectual honesty.

## Governance
This Constitution supersedes all other project practices and documentation. Amendments require a formal proposal, review, and explicit approval by project leadership, followed by documentation of the rationale and a plan for migrating any affected components. All pull requests and code reviews must explicitly verify compliance with these principles. Complexity must always be justified against these core tenets.

**Version**: v0.1.0 | **Ratified**: 2025-11-30 | **Last Amended**: 2025-11-30