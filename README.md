# OpenVideoAI (Backend-first)

This repository contains a FastAPI backend for a Text-to-Video SaaS project. We're building iteratively — no frontend for now. The service will accept text prompts and generate simple videos saved to the user's Downloads folder.

Run locally:

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the app:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/health`.
# OpenVideoAI

OpenVideoAI is a local, open-source Text-to-Video AI platform designed to generate high-quality videos directly from text prompts without relying on expensive commercial services such as Veo, Kling, Runway, Pika, or Sora.

The project follows a **research-first approach**, where every component is understood, documented, and learned before implementation.

---

# Vision

Build a fully local Text-to-Video AI system that enables users to generate videos from natural language prompts while learning the underlying AI technologies, model architectures, and engineering practices.

Rather than using AI as a black box, OpenVideoAI aims to become a platform for both creation and education.

---

# Objectives

## Primary Goals

- Generate videos from text prompts
- Run locally on consumer hardware
- Use open-source AI models
- Avoid recurring API costs
- Learn AI engineering while building
- Build production-quality architecture
- Support future model fine-tuning
- Create a reusable generative AI platform

---
# Contributing to OpenVideoAI

Thank you for your interest in contributing.

## Ways to Contribute

- Bug fixes
- Performance optimization
- New diffusion model support
- UI improvements
- Documentation
- Tutorials
- Fine-tuning experiments

## Development Setup

1. Fork repository
2. Clone locally
3. Create virtual environment
4. Install requirements

## bash
git clone https://github.com/yourusername/OpenVideoAI.git

cd OpenVideoAI

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

# System Design

## High Level Design

User Prompt
→ Prompt Processor
→ Text Encoder
→ Video Generator
→ Video Renderer
→ Storage Layer
→ User Download

## Modules

### Prompt Module

Responsibilities:

- prompt validation
- prompt enhancements
- negative prompts

### Inference Module

Responsibilities:

- model loading
- memory management
- generation

### Render Module

Responsibilities:

- frame extraction
- video encoding
- mp4 export

### Model Registry

Responsibilities:

- checkpoint storage
- version control
- model metadata

# Supported Models

## Image Models

- SDXL
- SDXL Turbo
- Flux

## Video Models

- CogVideoX
- Wan 2.1
- Stable Video Diffusion
- AnimateDiff

## Future Models

- Open Sora
- Hunyuan Video
- Mochi
- LTX Video

## Fine Tuning

- LoRA
- DreamBooth
- QLoRA

# Research Roadmap

## Stage 1

Text → Image

Goal:

Understand diffusion basics

Deliverable:

Generate realistic images

---

## Stage 2

Image → Video

Goal:

Learn motion generation

Deliverable:

Animate static images

---

## Stage 3

Text → Video

Goal:

Generate complete videos

Deliverable:

Create videos from prompts

---

## Stage 4

Character Consistency

Goal:

Preserve characters across scenes

---

## Stage 5

Movie Generation

Goal:

Story → Scenes → Video

# Deployment Guide

## Local Deployment

Run:

python app.py

# High-Level Architecture

```text
                ┌─────────────────────┐
                │     Gradio UI       │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │     FastAPI API     │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │ Video Generation    │
                │ Service             │
                └─────────┬───────────┘
                          │
     ┌────────────────────┼─────────────────────┐
     ▼                    ▼                     ▼

 Text Encoder       Diffusion Model      Motion Module

     ▼                    ▼                     ▼

            Video Latent Generation

                          ▼

              Frame Decoder (VAE)

                          ▼

                 MP4 Renderer

                          ▼

