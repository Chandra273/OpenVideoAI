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

                Generated Video
