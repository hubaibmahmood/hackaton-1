# Feature Specification: Physical AI & Humanoid Robotics Textbook Content

**Feature Branch**: `002-textbook-content`
**Created**: 2025-11-30
**Status**: Draft
**Input**: User description: "Create comprehensive textbook content for Physical AI & Humanoid Robotics course covering 6 learning outcomes across 4 modules: ROS 2 fundamentals, Gazebo/Unity simulation, NVIDIA Isaac platform, Vision-Language-Action integration, humanoid robot development, and conversational robotics with GPT models"

## Clarifications

### Session 2025-11-30

- Q: What content granularity strategy should guide chapter breakdown? → A: Fine granularity (8-10 focused chapters per Part with 20-30 minute reading sessions for better engagement)
- Q: When should exercise solutions be visible to students? → A: Progressive reveal (hidden initially, revealed after attempt or time-locked)
- Q: What executability standard should all code examples meet? → A: Hybrid approach (complete examples are fully runnable, illustrative snippets clearly marked)
- Q: How should cloud-based alternatives be integrated into the content structure? → A: Integrated with choice points (each chapter presents local and cloud options at decision points)
- Q: When should the 4 major assessments be administered in the course timeline? → A: End-of-Part milestones (aligned with Part completion for modular verification)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Foundational Concepts (Priority: P1)

As a student with AI/ML background, I need to understand Physical AI principles, embodied intelligence, and the robotics landscape so I can transition from digital AI to physical-world robotics applications.

**Why this priority**: Essential foundation - students cannot proceed to practical modules without understanding why Physical AI matters, what embodied intelligence means, and the hardware/software ecosystem. This establishes the "why" before the "how."

**Independent Test**: Can be fully tested by having a student with AI background read Part 1 content and successfully complete comprehension assessments on Physical AI vs traditional AI, sensor types and their purposes, and the humanoid robotics landscape. Deliverable: Student can explain why humanoids excel in human environments and identify appropriate sensors for given scenarios.

**Acceptance Scenarios**:

1. **Given** a student has completed traditional AI/ML coursework, **When** they read Part 1 foundational chapters, **Then** they can articulate the difference between digital AI and Physical AI in their own words
2. **Given** content on sensor systems, **When** a student encounters a robotics scenario, **Then** they can identify which sensors (LIDAR, cameras, IMUs) are appropriate and why
3. **Given** explanations of embodied intelligence, **When** students review humanoid robot examples, **Then** they understand why physical form matters for human-environment interaction
4. **Given** overview content on the robotics landscape, **When** students encounter different robot types, **Then** they can categorize them and explain trade-offs between humanoids, quadrupeds, and manipulators

---

### User Story 2 - ROS 2 Fundamentals (Priority: P2)

As a Python developer learning robotics, I need comprehensive ROS 2 tutorials with hands-on examples so I can build, test, and deploy robot control software using industry-standard middleware.

**Why this priority**: ROS 2 is the "nervous system" for all subsequent modules. Students must be able to create nodes, communicate via topics/services, and understand URDF before attempting simulation or hardware deployment. Foundational concepts (P1) provide context, but ROS 2 skills enable actual implementation.

**Independent Test**: Can be tested independently by having a student complete Part 2 content and successfully create a working ROS 2 package with nodes communicating via topics and services. No simulation or hardware required - just the middleware layer. Deliverable: Student builds a multi-node ROS 2 system demonstrating pub/sub and service patterns.

**Acceptance Scenarios**:

1. **Given** a student knows Python basics, **When** they follow ROS 2 installation and setup chapters, **Then** they can install ROS 2 Humble on Ubuntu and verify installation with demo nodes
2. **Given** tutorials on nodes and topics, **When** a student writes their first publisher/subscriber pair, **Then** messages flow correctly between nodes as verified by `ros2 topic echo`
3. **Given** service tutorials, **When** a student implements a request/response pattern, **Then** they can call services programmatically and handle responses
4. **Given** URDF tutorials and examples, **When** a student creates a robot description file, **Then** they can visualize it in RViz and understand joint relationships
5. **Given** launch file examples, **When** a student creates a multi-node system, **Then** they can start/stop the entire system with a single command

---

### User Story 3 - Simulation Environments (Priority: P3)

As a robotics student, I need detailed guidance on Gazebo and Unity simulation environments so I can test robot behaviors in physics-accurate virtual worlds before deploying to hardware.

**Why this priority**: Simulation provides safe, cost-effective testing but requires understanding both ROS 2 (P2) and Physical AI concepts (P1). Students need "digital twin" skills to prototype before hardware investment. Less critical than ROS 2 since simple ROS 2 systems can run without simulation, but essential for complex behaviors.

**Independent Test**: Can be tested by having a student complete Part 3 content and successfully launch a simulated robot in Gazebo, spawn obstacles, and demonstrate basic physics interactions (gravity, collisions). Deliverable: Student creates a custom Gazebo world with a robot model and simulated sensors.

**Acceptance Scenarios**:

1. **Given** a student has ROS 2 knowledge, **When** they install and configure Gazebo, **Then** they can launch pre-built simulation worlds and spawn robots
2. **Given** URDF tutorials from Part 2, **When** a student imports their robot model into Gazebo, **Then** the robot displays correctly with accurate physics properties
3. **Given** sensor simulation chapters, **When** a student adds LIDAR or cameras to their model, **Then** simulated sensor data appears on ROS 2 topics in expected formats
4. **Given** physics simulation tutorials, **When** a student modifies gravity or friction parameters, **Then** they observe corresponding behavior changes in the simulation
5. **Given** Unity introduction content, **When** a student compares Gazebo vs Unity use cases, **Then** they can explain when to use each tool (physics accuracy vs visual fidelity)

---

### User Story 4 - NVIDIA Isaac Platform (Priority: P4)

As an advanced robotics student, I need comprehensive Isaac Sim and Isaac ROS tutorials so I can leverage GPU-accelerated perception, synthetic data generation, and hardware-accelerated SLAM for production-grade robot systems.

**Why this priority**: Isaac represents cutting-edge tools but requires solid ROS 2 (P2) and simulation (P3) foundation. Critical for students targeting industry roles but not essential for basic understanding. High hardware requirements (RTX GPUs) make this advanced content.

**Independent Test**: Can be tested by having a student with RTX-capable workstation complete Part 4 content and successfully run Isaac Sim with a simulated robot performing VSLAM (Visual SLAM) navigation. Deliverable: Student generates synthetic training data in Isaac Sim and deploys a perception pipeline using Isaac ROS nodes.

**Acceptance Scenarios**:

1. **Given** a student has an RTX GPU and prior ROS 2 knowledge, **When** they install Isaac Sim, **Then** they can launch photorealistic simulation environments and load USD robot assets
2. **Given** synthetic data generation tutorials, **When** a student configures Isaac Sim cameras and sensors, **Then** they can export labeled datasets for training perception models
3. **Given** Isaac ROS tutorials, **When** a student sets up hardware-accelerated VSLAM, **Then** their robot can localize and map environments in real-time with GPU acceleration
4. **Given** Nav2 integration chapters, **When** a student configures path planning for a bipedal robot, **Then** the system generates collision-free paths and executes navigation commands
5. **Given** sim-to-real transfer content, **When** a student trains a model in Isaac Sim, **Then** they understand domain randomization techniques to improve real-world performance

---

### User Story 5 - Humanoid Development (Priority: P5)

As a robotics engineer, I need detailed tutorials on humanoid kinematics, bipedal locomotion, and manipulation so I can develop control systems for human-form robots capable of natural interactions.

**Why this priority**: Specialized content building on all previous modules. Students need ROS 2 (P2), simulation (P3), and ideally Isaac (P4) before tackling complex humanoid-specific challenges like balance control and bipedal walking. High value but narrow audience.

**Independent Test**: Can be tested by having a student complete Part 5 content and successfully implement a bipedal walking controller in simulation that maintains balance and executes stable gaits. Deliverable: Student creates a humanoid manipulation demo (pick-and-place) in Gazebo or Isaac Sim.

**Acceptance Scenarios**:

1. **Given** a student understands robot kinematics, **When** they study forward/inverse kinematics for humanoids, **Then** they can calculate joint angles for desired end-effector positions
2. **Given** bipedal locomotion tutorials, **When** a student implements a walking controller, **Then** the simulated humanoid achieves stable walking without falling
3. **Given** balance control chapters, **When** external forces are applied to the robot, **Then** balance compensation algorithms keep the robot upright
4. **Given** manipulation tutorials with humanoid hands, **When** a student programs grasping behaviors, **Then** the robot successfully picks up objects of various sizes
5. **Given** human-robot interaction design content, **When** a student reviews gesture and proximity scenarios, **Then** they can design natural, safe interaction patterns

---

### User Story 6 - Conversational Robotics (Priority: P6)

As a student interested in human-robot interaction, I need comprehensive tutorials on integrating GPT models, speech recognition, and natural language understanding so I can create robots that communicate naturally with humans.

**Why this priority**: Represents the convergence of AI and robotics - the capstone experience. Requires all previous foundations (P1-P5) plus additional LLM/NLP knowledge. Highest complexity but delivers the "wow factor" of voice-controlled autonomous robots.

**Independent Test**: Can be tested by having a student complete Part 6 content and successfully implement a voice-to-action pipeline where a robot receives a natural language command (e.g., "bring me the red cup"), translates it to ROS 2 actions, and executes the task. Deliverable: Student creates a chatbot-controlled robot that demonstrates multi-turn conversation and action execution.

**Acceptance Scenarios**:

1. **Given** OpenAI Whisper integration tutorials, **When** a student sets up voice recognition, **Then** spoken commands are accurately transcribed to text
2. **Given** GPT integration chapters, **When** a student sends natural language text to the LLM, **Then** the model generates structured action sequences in JSON or ROS 2 message format
3. **Given** vision-language-action (VLA) tutorials, **When** a student combines voice input with camera data, **Then** the robot can identify objects and execute commands like "pick up the blue block"
4. **Given** multi-modal interaction content, **When** a student implements gesture recognition alongside speech, **Then** the robot responds to both verbal and non-verbal cues
5. **Given** the capstone project guidelines, **When** a student integrates all components (voice → planning → navigation → manipulation), **Then** the autonomous humanoid successfully completes end-to-end tasks in simulation

---

### Edge Cases

- What happens when content references hardware (Jetson, RealSense) that students don't have access to? Include cloud-based alternatives and detailed workarounds.
- How does the textbook handle multiple ROS 2 distributions (Humble vs Iron vs newer)? Version-specific notes and migration guides in appendices.
- What if students have non-Linux systems (macOS, Windows)? Provide Docker-based development environments and cross-platform setup guides.
- How do we address the RTX GPU requirement for Isaac Sim? Offer cloud instance tutorials (AWS g5.2xlarge) with cost estimates and setup instructions.
- What happens when external APIs change (OpenAI, NVIDIA)? Maintain an errata/updates section with migration notes and alternative API examples.
- How do students without robotics hardware complete hands-on exercises? Ensure 100% of exercises have simulation-based alternatives with equivalent learning outcomes.

## Requirements *(mandatory)*

### Functional Requirements

#### Part 1: Physical AI Foundations (Weeks 1-2)

- **FR-001**: Content MUST explain Physical AI definition and contrast it with traditional digital AI systems
- **FR-002**: Content MUST describe embodied intelligence with concrete examples of how physical form affects learning
- **FR-003**: Content MUST provide overview of humanoid robotics landscape including current commercial systems (Unitree, Tesla, Figure, etc.)
- **FR-004**: Content MUST cover sensor systems (LIDAR, RGB cameras, depth cameras, IMUs, force/torque sensors) with use cases
- **FR-005**: Content MUST include visual diagrams of sensor placement on humanoid robots
- **FR-006**: Content MUST explain why humanoids are particularly suited for human-centric environments

#### Part 2: ROS 2 Fundamentals (Weeks 3-5)

- **FR-007**: Content MUST provide step-by-step ROS 2 Humble installation guide for Ubuntu 22.04
- **FR-008**: Content MUST explain ROS 2 architecture including DDS middleware, nodes, topics, services, and actions
- **FR-009**: Content MUST include hands-on tutorials for creating Python-based ROS 2 packages using rclpy
- **FR-010**: Content MUST demonstrate publisher/subscriber pattern with working code examples
- **FR-011**: Content MUST demonstrate service/client pattern with request/response examples
- **FR-012**: Content MUST explain URDF format with a complete humanoid robot description example
- **FR-013**: Content MUST cover launch files for multi-node system orchestration
- **FR-014**: Content MUST explain parameter management and dynamic reconfiguration
- **FR-015**: Content MUST include troubleshooting section for common ROS 2 issues

#### Part 3: Simulation Environments (Weeks 6-7)

- **FR-016**: Content MUST provide Gazebo installation and configuration tutorial
- **FR-017**: Content MUST explain SDF (Simulation Description Format) and its relationship to URDF
- **FR-018**: Content MUST demonstrate creating custom Gazebo worlds with physics properties (gravity, friction, damping)
- **FR-019**: Content MUST cover sensor simulation for LIDAR, cameras, and IMUs with ROS 2 integration
- **FR-020**: Content MUST include collision detection and physics debugging techniques
- **FR-021**: Content MUST introduce Unity as a complementary tool for high-fidelity rendering
- **FR-022**: Content MUST explain when to use Gazebo vs Unity (physics accuracy vs visual quality)

#### Part 4: NVIDIA Isaac Platform (Weeks 8-10)

- **FR-023**: Content MUST provide Isaac Sim installation guide with hardware requirements (RTX GPU, Ubuntu)
- **FR-024**: Content MUST explain USD (Universal Scene Description) format for Isaac Sim assets
- **FR-025**: Content MUST demonstrate synthetic data generation for training perception models
- **FR-026**: Content MUST cover Isaac ROS nodes for hardware-accelerated VSLAM (Visual SLAM)
- **FR-027**: Content MUST explain Nav2 integration for path planning and navigation
- **FR-028**: Content MUST demonstrate reinforcement learning workflows in Isaac Sim
- **FR-029**: Content MUST cover sim-to-real transfer techniques including domain randomization
- **FR-030**: Content MUST integrate cloud-based alternatives (Omniverse Cloud, AWS g5.2xlarge) at decision points within chapters using clear "Local Setup" and "Cloud Setup" markers, rather than separate parallel chapters

#### Part 5: Humanoid Robot Development (Weeks 11-12)

- **FR-031**: Content MUST explain forward and inverse kinematics for humanoid manipulators
- **FR-032**: Content MUST cover bipedal locomotion fundamentals including gait cycles and stability
- **FR-033**: Content MUST demonstrate balance control algorithms (ZMP, CoM tracking)
- **FR-034**: Content MUST explain manipulation with humanoid hands including grasp planning
- **FR-035**: Content MUST cover natural human-robot interaction design (proxemics, gesture recognition)
- **FR-036**: Content MUST include working examples of humanoid controllers in Gazebo or Isaac Sim

#### Part 6: Conversational Robotics (Week 13)

- **FR-037**: Content MUST demonstrate OpenAI Whisper integration for voice recognition
- **FR-038**: Content MUST explain GPT model integration for natural language understanding and action planning
- **FR-039**: Content MUST cover vision-language-action (VLA) pipelines combining perception and language
- **FR-040**: Content MUST demonstrate multi-modal interaction (speech + gesture + vision)
- **FR-041**: Content MUST include complete capstone project specification: voice-controlled autonomous humanoid
- **FR-042**: Content MUST provide step-by-step capstone implementation guide with checkpoints

#### Cross-Cutting Requirements

- **FR-043**: Complete code examples MUST be fully runnable and tested on Ubuntu 22.04 with ROS 2 Humble; illustrative code snippets MUST be clearly marked with "Excerpt:" label and provide context for where they fit in complete programs
- **FR-044**: Content MUST include Python code snippets with inline comments explaining key concepts
- **FR-045**: Each chapter MUST include learning objectives at the beginning and summary at the end
- **FR-046**: Content MUST provide troubleshooting sections for common errors
- **FR-047**: Content MUST include "Further Reading" sections with links to official documentation and research papers
- **FR-048**: Diagrams and illustrations MUST be included for complex concepts (architecture diagrams, sensor layouts, data flow)
- **FR-049**: Content MUST be structured to support both self-paced learning and instructor-led courses
- **FR-050**: All external dependencies (APIs, libraries) MUST be documented with version numbers and installation commands
- **FR-051**: Each Part MUST contain 8-10 focused chapters (fine granularity) to support 20-30 minute reading sessions per chapter for better student engagement
- **FR-052**: Exercise solutions MUST use progressive reveal strategy (hidden initially, revealed after student attempts or time-locked after 24 hours) to encourage independent problem-solving
- **FR-053**: Cloud-based alternatives MUST be integrated within chapters at decision points using consistent markers ("💻 Local Setup" / "☁️ Cloud Setup") rather than creating duplicate parallel chapters
- **FR-054**: The 4 major assessments MUST be administered as end-of-Part milestones (Assessment 1 after Part 2, Assessment 2 after Part 3, Assessment 3 after Part 4, Assessment 4 as Part 6 capstone) to validate mastery before progression

### Key Entities

- **Chapter**: Represents a focused topic within a Part (e.g., "ROS 2 Nodes and Topics"). Each Part contains 8-10 chapters designed for 20-30 minute reading sessions. Contains learning objectives, content sections, code examples, exercises, and summary.
- **Section**: A subdivision of a Chapter focusing on one specific concept (e.g., "Creating Your First Publisher"). Contains narrative text, code snippets, and diagrams.
- **Code Example**: Code demonstrating a concept. Two types: (1) Complete examples - fully runnable scripts with filename, language, inline comments, and expected output; (2) Illustrative snippets - marked with "Excerpt:" label, showing focused code segments with context about their placement in complete programs.
- **Exercise**: Hands-on activity for students to practice concepts. Includes problem statement, hints, and solution (hidden initially using progressive reveal - unlocked after student attempts or 24-hour time-lock).
- **Diagram**: Visual representation of concepts, architectures, or data flows. Includes alt text for accessibility.
- **Assessment**: Quiz, project, or practical exam tied to specific learning outcomes. Four major assessments administered as end-of-Part milestones: (1) ROS 2 Package after Part 2, (2) Gazebo Simulation after Part 3, (3) Isaac Pipeline after Part 4, (4) Voice-Controlled Capstone after Part 6. Includes questions, rubrics, and expected deliverables.
- **Glossary Term**: Technical term with definition and context. Cross-referenced throughout content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students with AI/ML background can articulate Physical AI principles and explain embodied intelligence in under 5 minutes after completing Part 1
- **SC-002**: 90% of students can successfully install ROS 2 and run demo nodes within 30 minutes using Part 2 tutorials
- **SC-003**: Students can create a working ROS 2 publisher/subscriber system within 2 hours using Part 2 code examples
- **SC-004**: 85% of students can launch a simulated robot in Gazebo with functional sensors using Part 3 content
- **SC-005**: Students with RTX GPUs can run Isaac Sim and generate synthetic data within 1 hour using Part 4 tutorials
- **SC-006**: Students can implement a basic bipedal walking controller in simulation within 4 hours using Part 5 content
- **SC-007**: 80% of students successfully complete the voice-controlled robot capstone project demonstrating end-to-end integration
- **SC-008**: Content supports both cloud-based (AWS) and local (RTX workstation) development with choice points integrated within chapters using consistent "Local Setup" / "Cloud Setup" markers
- **SC-009**: Students report 90% confidence in transitioning from textbook examples to independent robotics projects
- **SC-010**: Content enables students to complete all 4 course assessments (ROS 2 package, Gazebo simulation, Isaac pipeline, capstone) with textbook as primary reference
- **SC-011**: Each Part can be completed independently by students with appropriate prerequisites (e.g., Part 2 requires only Python knowledge)
- **SC-012**: Average chapter reading time is 20-30 minutes with code examples taking additional 60-90 minutes to complete (total 80-120 minutes per chapter session)

## Assumptions *(optional)*

1. **Student Prerequisites**: Students have completed AI/ML coursework covering neural networks, reinforcement learning, and Python programming
2. **Hardware Access**: Students have either RTX-capable workstations OR access to cloud GPU instances (AWS g5.2xlarge or equivalent)
3. **Operating System**: Primary development environment is Ubuntu 22.04 LTS (dual-boot, VM, or cloud instance)
4. **Internet Access**: Students have reliable internet for downloading ROS 2 packages, Isaac Sim assets, and accessing LLM APIs
5. **Time Commitment**: Students allocate 10-12 hours per week for reading, coding, and hands-on exercises
6. **English Proficiency**: Content is written in English with technical terminology explained but not translated
7. **Existing Book Infrastructure**: The Docusaurus-based infrastructure (001-book-infrastructure) is fully deployed and functional
8. **Content Format**: All content is in Markdown format compatible with Docusaurus MDX
9. **API Availability**: OpenAI APIs (Whisper, GPT) and NVIDIA Isaac resources remain accessible during course duration
10. **Version Stability**: ROS 2 Humble remains the recommended distribution throughout course timeframe (2025-2026)

## Out of Scope *(optional)*

1. **Physical Robot Hardware**: Content does not require students to purchase physical robots (Unitree, humanoids, etc.). All exercises have simulation-based alternatives.
2. **Real-World Deployment**: Focus is on simulation and development workflows, not production deployment to actual hardware.
3. **Custom Robot Design**: Students use pre-existing robot models (humanoid templates). Custom mechanical/electrical design is not covered.
4. **Advanced Mathematics**: Deep mathematical proofs for kinematics, control theory, or RL algorithms are minimized in favor of practical implementation.
5. **Non-ROS 2 Frameworks**: Alternative middleware (ROS 1, YARP, LCM) is not covered. Content is exclusively ROS 2.
6. **Multi-Robot Systems**: Swarm robotics, multi-agent coordination, and distributed systems are out of scope.
7. **Safety Certifications**: Industrial safety standards (ISO 10218, ISO 13482) for collaborative robots are not covered.
8. **Embedded Systems Programming**: Low-level C++ development for real-time controllers is excluded. Focus is Python-based ROS 2.
9. **Computer Vision Deep Dive**: Advanced CV topics (SLAM algorithms, object detection model training) are introduced but not exhaustively covered.
10. **Hardware Troubleshooting**: Content assumes functional hardware/software. Debugging driver issues, firmware flashing, etc., is out of scope.

## Dependencies *(optional)*

### Internal Dependencies

- **Docusaurus Infrastructure** (001-book-infrastructure): Must be fully deployed with navigation, search, and accessibility features functional
- **Six-Part Structure**: Content must map to the 6 learning outcomes defined in the project constitution
- **Markdown Standards**: Content must follow markdownlint rules and WCAG 2.1 AA accessibility guidelines

### External Dependencies

- **ROS 2 Humble**: Long-term support release (Ubuntu 22.04). Content version-locked to Humble to ensure stability.
- **Gazebo 11 or Gazebo Fortress**: Simulation environment compatibility with ROS 2 Humble.
- **NVIDIA Isaac Sim 2023.1+**: Requires Omniverse and RTX GPU. Cloud alternatives (Omniverse Cloud) must be documented.
- **NVIDIA Isaac ROS**: GEM packages for hardware-accelerated perception. Requires Jetson or RTX GPU.
- **OpenAI API**: Whisper and GPT models for conversational robotics. Requires API keys and budget for API calls.
- **Python 3.10+**: Language for all code examples and ROS 2 packages.
- **Node.js 18+**: Required for Docusaurus build (inherited from 001-book-infrastructure).

### Third-Party Resources

- **Official ROS 2 Documentation**: Referenced extensively for installation and API details.
- **NVIDIA Isaac Documentation**: Referenced for Isaac Sim and Isaac ROS tutorials.
- **OpenAI Documentation**: Referenced for Whisper and GPT API integration.
- **Unitree Robot Documentation**: Referenced for robot model examples (Go2, G1, H1).
- **Research Papers**: Referenced for advanced topics (VLA models, sim-to-real transfer, bipedal locomotion).

## Risks *(optional)*

1. **Hardware Cost Barrier**: RTX GPUs are expensive. **Mitigation**: Provide comprehensive cloud-based alternatives (AWS, Azure) with cost calculators.
2. **API Cost Creep**: OpenAI API calls can accumulate costs. **Mitigation**: Provide local alternatives (Whisper.cpp, open-source LLMs like Llama) with setup guides.
3. **Rapid Technology Evolution**: Isaac Sim, ROS 2, and LLMs evolve quickly. **Mitigation**: Version-lock content to stable releases and maintain an errata page.
4. **Complexity Overwhelm**: Six modules with dense technical content may overwhelm students. **Mitigation**: Ensure each Part stands alone and provide clear prerequisites.
5. **Simulation-Reality Gap**: Students may struggle transitioning to real hardware. **Mitigation**: Include dedicated section on sim-to-real transfer and hardware limitations.
6. **Software Installation Issues**: Multi-step installations (ROS 2, Isaac Sim) often fail. **Mitigation**: Provide Docker images and troubleshooting sections for common errors.
7. **Cross-Platform Support**: Students on macOS/Windows face friction. **Mitigation**: Recommend Ubuntu but provide Docker-based workflows for other OSes.

## Open Questions *(optional)*

*None at this time. All critical aspects have reasonable defaults or are clarified in requirements.*
