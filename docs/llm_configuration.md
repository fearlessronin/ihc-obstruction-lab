# LLM Configuration

Phase 6C adds a configurable extraction interface for local literature packets. It does not make provider calls unless explicitly requested.

Supported providers:

- `mock`: deterministic offline provider used by tests and CI.
- `manual`: import JSON produced by a human workflow, ChatGPT Pro, Claude UI, or another tool.
- `openai-compatible`: optional provider adapter using `OPENAI_API_KEY`.
- `anthropic`: optional provider adapter using `ANTHROPIC_API_KEY`.

Users must supply their own `ANTHROPIC_API_KEY`; no shared or repository key is provided.

## Configuration

Copy the example file and keep local secrets untracked:

```powershell
Copy-Item config/llm.example.toml config/llm.local.toml
```

Set API keys in your shell when using external providers:

```bash
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."
```

Do not commit API keys, `.env` files, or `config/llm.local.toml`.

## Commands

Offline mock extraction:

```powershell
python -m ihc_lab.cli run-llm-extraction --provider mock
```

Manual import:

```powershell
python -m ihc_lab.cli import-manual-extraction --input data/literature_queue/manual_extraction.sample.json
```

Provider calls are disabled by default. To use an external provider, pass `--allow-provider-call` and a local config:

```powershell
python -m ihc_lab.cli run-llm-extraction --provider anthropic --config config/llm.local.toml --allow-provider-call
```

API usage may incur provider charges.

## Safety

All LLM and manual outputs are reset to `llm_extracted_unverified` and `needs_human_review`. LLM extraction is not theorem verification, and extracted rows are not primary claims until human review and explicit promotion.
