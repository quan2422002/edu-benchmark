ARG BASE_IMAGE=vllm/vllm-openai:v0.9.2
FROM ${BASE_IMAGE}

# The upstream image already exposes the OpenAI-compatible vLLM server.
# Runtime command and pinned SocraticLM checkpoint are supplied by Vertex
# Model Registry so this image remains provider-facing and reusable.
