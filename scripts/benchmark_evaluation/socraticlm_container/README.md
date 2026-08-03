# SocraticLM vLLM container

This minimal image pins the upstream `vllm/vllm-openai:v0.9.2` runtime.
The Vertex Model resource supplies the command, checkpoint and serving
parameters. Do not add benchmark prompts, Hugging Face tokens or project
credentials to this build context.
