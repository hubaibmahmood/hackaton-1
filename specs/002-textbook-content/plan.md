# Implementation Plan: Textbook Content

**Branch**: `002-textbook-content` | **Date**: 2025-11-30 | **Spec**: [Link](spec.md)
**Input**: Feature specification from `/specs/002-textbook-content/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan details the structure and workflow for generating the content of the "Physical AI & Humanoid Robotics" textbook. It involves creating a 6-Part modular structure in Docusaurus, covering topics from Physical AI foundations to ROS 2, Simulation, NVIDIA Isaac, and a Conversational Robotics capstone. Content will be authored in MDX, incorporating code examples, exercises, and assessments.

## Technical Context

**Language/Version**: Markdown (MDX), Python 3.10+, C++ (limited), Bash.
**Primary Dependencies**: Docusaurus (v3+), ROS 2 Humble, Gazebo Fortress, NVIDIA Isaac Sim 2023.1+, OpenAI API.
**Storage**: Git (File-based content).
**Testing**: `markdownlint`, Code Example Verification (manual/CI), Assessment Rubrics.
**Target Platform**: Web (Static Site), Ubuntu 22.04 (Student Environment).
**Project Type**: Content / Documentation.
**Performance Goals**: 20-30 min read time per chapter, <2s page load.
**Constraints**: Hardware requirements for advanced modules (RTX GPU), Cloud alternative requirement.
**Scale/Scope**: 6 Parts, ~60 Chapters, 4 Major Assessments.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Embodied Intelligence Focus**: ✅ Content structure prioritizes physical constraints and interaction.
- **II. ROS 2 as Nervous System**: ✅ Part 2 and subsequent modules enforce ROS 2 Humble.
- **III. Digital Twin**: ✅ Part 3 covers Gazebo; Part 4 covers Isaac Sim.
- **IV. NVIDIA Isaac**: ✅ Dedicated Part 4.
- **V. VLA Integration**: ✅ Dedicated Part 6.
- **VI. Learning Outcomes**: ✅ Content maps 1:1 to defined learning outcomes.
- **VII. Capstone**: ✅ Defined as Assessment 4.
- **VIII. SDD**: ✅ Following Spec-Kit Plus workflow.
- **IX. RAG Chatbot**: ⏳ Deferred to separate feature (infrastructure), but content structure supports it.
- **X. Quality/Integrity**: ✅ Citation and anti-plagiarism rules in place.

## Project Structure

### Documentation (this feature)

```text
specs/002-textbook-content/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chapter-frontmatter.schema.json
└── tasks.md             # Phase 2 output (pending)
```

### Source Code (repository root)

```text
book/
├── docs/
│   ├── part-01-physical-ai/
│   │   ├── _category_.json
│   │   ├── chapter-01-intro/
│   │   │   ├── index.md
│   │   │   └── img/
│   │   └── assessment.md
│   ├── part-02-ros2/
│   ├── part-03-simulation/
│   ├── part-04-isaac/
│   ├── part-05-humanoid/
│   └── part-06-conversational/
└── static/
    └── code/              # Downloadable source archives
```

**Structure Decision**: Nested directory structure (`docs/part/chapter/index.md`) chosen for scalability and asset localization.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | | |

