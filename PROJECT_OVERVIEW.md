Project Overview — PVL Operator Analyzer (ChatBot V3.0)

This file summarizes the project's structure, the purpose of each Python file, how modules interact, data/output locations, and important notes. Use it as a shareable summary when discussing the project.

---

1) Top-level project tree (important Python files and packages)

- Root files
  - app.py — Entry point. Launches the GUI (DescriptionApp).
  - data_collector.py — Saves training samples (images + JSON) into dataset_sos/ for LoRA training.
  - excel_generator.py — Builds the FOR-054 SOS Excel report from a JSON analysis report.
  - custom_model_client.py — Loads a locally fine-tuned LoRA model and runs inference (Qwen2-VL based).
  - train_lora.py — Fine-tuning pipeline using HuggingFace + PEFT; trains on dataset_sos and writes my_sos_lora_weights/.

- app_ui/ (GUI package)
  - __init__.py — Re-exports GUI entrypoints (DescriptionApp and analyze_video).
  - widgets.py — Custom Tkinter widgets (RoundedButton, Section/RoundedCard, OptionRow, StatusPill, ScrollableArea, StyledEntry, etc.).
  - theme.py — Theme tokens (colors, fonts, spacing) used by widgets.
  - step_builder.py — Palette of common actions and utilities to compose custom step lists.
  - main_window.py — DescriptionApp (main window). Orchestrates user flows, threads tasks, and calls pipeline and other components.
  - dialog.py — ModernDialog: workflow configuration dialog (select workflow, capture params, custom steps).
  - analysis.py — Thin wrapper that calls the pipeline (test.run_pipeline) and archives samples with data_collector.

- config/ (static configuration)
  - __init__.py — Re-exports values from submodules for convenient import config.X.
  - paths.py — Output and Excel template path helpers; make_session_dir(session folder creation).
  - defaults.py — Default extraction and sampling parameters.
  - workflows.py — WORKFLOW_TYPES definitions and parse_custom_steps helper.
  - prompts.py — SOS_ANALYSIS_PROMPT used to format prompts for the model.
  - risk_mapping.py — RISK_MAPPINGS to suggest "raison du point clé" values.
  - theme.py — GUI theme tokens used by config consumers.

- dataset_sos/
  - dataset_viewer.py — Small Tkinter app to inspect/edit dataset_sos/dataset.jsonl and images.

- test/ (pipeline and helpers)
  - pipeline.py — run_pipeline(): orchestrates the full video->frames->AI->report flow, saves rapport_analyse.json.
  - video_extraction.py — extract_frames_smart(): extracts frames, saves to outputs/<session>/frames and returns base64 strings and paths.
  - ollama_client.py — Calls Ollama REST API (or delegates to custom_model_client). Prepares prompts, optimizes images, parses JSON responses.
  - text_processing.py — Post-processing utilities for model output (normalize verb forms, clean points_cles, etc.).
  - verb_utils.py — Verb normalization and extraction helpers (used to de-duplicate verbs across steps).

---

2) What each file is responsible for (short descriptions)

Root files
- app.py
  - Launches the GUI by creating DescriptionApp and starting mainloop.

- data_collector.py
  - init_dataset_structure() and save_training_sample(base64_images, final_json, workflow_type, step_label).
  - Writes images to dataset_sos/images/ and appends JSONL entries to dataset_sos/dataset.jsonl.

- excel_generator.py
  - generate_sos_excel(json_path, output_path=None, project_name=None) creates an Excel report from the analysis report JSON.
  - Handles layout, image insertion, keyword-rich formatting and adding pages when needed. Uses an Excel template (FOR-054-Multi-J-SOS Analysis.xlsx).

- custom_model_client.py
  - load_custom_model() loads the base Qwen2-VL model + LoRA weights from my_sos_lora_weights/.
  - analyze_sequence_with_custom_model(images_base64, previous_action, **kwargs) runs the model locally and returns structured JSON analysis.

- train_lora.py
  - main() builds a Trainer + SOSDataset() from dataset_sos/dataset.jsonl and fine-tunes with PEFT/LoRA.
  - Saves model + processor to my_sos_lora_weights/.

app_ui/
- widgets.py
  - Custom UI components (rounded buttons, cards, status pills, scrollable area, styled inputs).

- theme.py
  - Theme tokens for the app (colors, fonts, spacing).

- step_builder.py
  - UI component to quickly add common action lines to the custom-step textbox.
  - Methods: add_step, renumber_steps, clear_all.

- main_window.py
  - DescriptionApp: full GUI flow (choose video, configure workflow, start/stop analysis, train model, generate Excel, open/save outputs).
  - Uses threads for long-running tasks and shows status via widgets.

- dialog.py
  - ModernDialog: workflow configuration (select workflow type, defects, capture parameters, custom steps editor + StepBuilderFrame).

- analysis.py
  - analyze_video wrapper: calls test.run_pipeline, then formats a textual report and archives each step to dataset via data_collector.save_training_sample.

config/
- paths.py: make_session_dir creates outputs/<session>/frames and returns session Directory.
- defaults.py: sampling and extraction defaults (DEFAULT_INTERVAL_S, DEFAULT_WINDOW_SIZE, DEFAULT_RESIZE_FACTOR, etc.).
- workflows.py: definitions of industrial workflow types and parse_custom_steps helper.
- prompts.py: long prompt template (SOS_ANALYSIS_PROMPT) used for Ollama model calls.
- risk_mapping.py: mapping to populate "raison_point_cle" suggestions.

dataset_sos/
- dataset_viewer.py: UI to inspect and edit dataset.jsonl records and their images.

test/
- pipeline.py: main orchestration. Key responsibilities:
  - Create outputs session dir, extract frames, partition frames into windows for steps, call analyze_sequence_with_ollama or custom_model_client, ensure/clean JSON, save rapport_analyse.json and return chronological_logs.
  - Supports fixed workflows (custom steps) and auto detection.

- video_extraction.py: extract_frames_smart() returns (extracted_base64_frames, frame_paths, calculated_interval_s).
- ollama_client.py: prepares the full prompt using config.SOS_ANALYSIS_PROMPT, optimizes images, posts to the Ollama API, parses JSON results with robust fallbacks.
- text_processing.py & verb_utils.py: support parsing and normalization of the model's textual output.

---

3) Data and outputs

- Dataset (for LoRA training): dataset_sos/dataset.jsonl (JSONL) and dataset_sos/images/ (images saved as JPEG).
  - data_collector.save_training_sample appends entries and writes images.

- Analysis session outputs: outputs/<session_name>/
  - frames/ (extracted frames saved by video_extraction)
  - rapport_analyse.json (final chronological_logs saved by pipeline)

- LoRA weights: my_sos_lora_weights/ (written by train_lora.py and consumed by custom_model_client.py when enabled).

---

4) Typical runtime flow (high level)

1. User selects a video in the GUI (app_ui/main_window.py) and confirms workflow config via ModernDialog.
2. DescriptionApp.start_analysis -> app_ui.analysis.analyze_video -> test.run_pipeline:
   - make_session_dir -> extract_frames_smart -> windows creation -> analyze_sequence_with_ollama/custom_model_client.
   - Parsed/cleaned step dicts are collected into chronological_logs.
   - Final report saved to outputs/<session>/rapport_analyse.json.
3. app_ui.analysis receives chronological_logs and calls data_collector.save_training_sample for each step to append training samples.
4. User may train a local LoRA model via the GUI (train_lora -> my_sos_lora_weights/).
5. When USE_CUSTOM_LORA_MODEL is enabled, ollama_client delegates inference to custom_model_client.
6. User can export an Excel SOS report using generate_sos_excel which uses the template file FOR-054-Multi-J-SOS Analysis.xlsx.

---

5) Notes & gotchas

- Ollama endpoint: test/ollama_client.py expects an Ollama server at http://localhost:11434. If unavailable, the GUI can optionally use a local LoRA model (if trained + enabled).
- Excel template: excel_generator requires the template file (FOR-054-Multi-J-SOS Analysis.xlsx) somewhere in the project or parent directories. If missing, generation will raise FileNotFoundError.
- Cancellation: the pipeline and the Ollama client accept a cancellation_event to allow user interruptions.
- Defensive parsing: model outputs are parsed with robust fallbacks (strip markdown fences, search for JSON braces, fallback defaults) — this keeps the system stable even if the model returns unexpected text.

---

6) Quick next actions you might want me to do

- Create a short developer README with run instructions (how to run the app, how to train LoRA, how to configure Ollama).
- Produce a one-page slide (text) summarizing the architecture for a meeting.
- Extract the exact JSON schema expected from the model and provide a small validator script.

Tell me which of those (if any) you'd like next and I can produce it.

---

Generated by: AI assistant using Copilot CLI runtime in VS Code
Date: 2026-08-05

