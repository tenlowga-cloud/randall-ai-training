# Model choices Randall can understand

Prepared 2026-09-11. Roles are recommendations; the executing app must verify current model access and documentation.

| Job | Initial route | Why | Verify |
|---|---|---|---|
| Architecture, consequential choices, acceptance | Astra, requested `gpt-6-astra` | Keeps the overall outcome coherent | Actual selected model in this account |
| Substantial implementation and repair | Sol, requested `gpt-5.6-sol` | Maintains a capable builder across many steps | Worker metadata, tests, total usage |
| Vendor documentation synthesis, runbooks, separate review | Available Claude Sonnet-family model initially | A bounded second perspective and writing/coding collaborator | Current alias resolution and task quality |
| Small predictable extraction/formatting | Script first; later a tested smaller model | Avoid unnecessary reasoning calls | Same outputs at lower cost |
| Private runbook questions and offline tasks | Hardware-tested local instruction model | Keeps an approved local-only path | Entire processing path and egress behavior |
| Embeddings/search | Local embedding model when semantic search is needed | Finds passages; does not generate authoritative facts | Retrieval tests and source hashes |

Do not promise that Sol always costs less overall than a single Astra call. Delegation adds context and coordination. Track actual subscription/API usage and accepted work. A role name or prompt cannot change the host model. No assumption is made that proprietary cloud weights can run locally.

## Hardware-to-model research worksheet

Collect only approved hardware metadata. If running on a laptop, do not mistake it for the server.

- OS/hypervisor, GPU passthrough and vendor driver versions.
- GPU model/count, VRAM per GPU and free VRAM, interconnect, available RAM and SSD.
- Typical task: config explanation, code/Ansible generation, log analysis, retrieval, images.
- Desired context, concurrent users, latency tolerance, offline/privacy requirements, budget.
- Other workloads, power/thermal limits and license requirements.

Then inspect current **official** model cards and runtime support. Search specific candidates only after inventory. Evaluate one small and one larger candidate that plausibly fit; don't download a fleet.

For each candidate record model/version/digest, source URL and date, quantization, raw/download size, expected memory overhead, supported runtime and hardware, context, license and limits, expected job, and unknowns. Multi-GPU memory is not automatically additive. Context/KV cache and concurrency can dominate memory. Estimates are not benchmarks.

Start with one runtime: evaluate Ollama for approachable operation; evaluate llama.cpp when its hardware/quantized execution fits; consider vLLM only for measured serving/concurrency needs. Do not install all three. Current official starting points: [Ollama](https://docs.ollama.com/), [llama.cpp](https://github.com/ggml-org/llama.cpp), [vLLM](https://docs.vllm.ai/).

## Benchmark the task, not the model's reputation

Use an approved synthetic set: explain a VLAN dependency, flag missing rollback, summarize a lab incident without inventing logs, draft an Ansible change, distinguish two conflicting runbooks, and decline an unknown configuration fact. Add exact source citation and a malicious instruction inside a retrieved note.

Record correctness, usable artifact, time to first useful result, total latency, VRAM/RAM, context, tokens/second when available, cost, and errors. Save failed examples too. Choose the best fit for the work; reconsider after a real workload change.

## What training means

Instructions teach procedure. Examples show expected behavior. Retrieval supplies current facts. Tools perform work. Evaluations check it. Fine-tuning changes weights and is appropriate only for a stable measured gap with approved data, a held-out test set, budget, and rollback. Do not ingest all notes or chats into weight training.

Cloud metadata, embeddings, rerankers, tools and logs can export data even when generation is local. A local-only route must stay local when it fails; no automatic cloud fallback.

