# -*- coding: utf-8 -*-
"""
train_lora.py - Fine-tuning LoRA propre et stable
"""

import os
import sys
import json
import time
import torch
from PIL import Image
from torch.utils.data import Dataset
from transformers import (
    AutoProcessor,
    Qwen2VLForConditionalGeneration, 
    TrainingArguments, 
    Trainer, 
    TrainerCallback,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Force l'utilisation exclusive du cache local
os.environ["HF_HUB_OFFLINE"] = "1"

DATASET_PATH = "dataset_sos/dataset.jsonl"
OUTPUT_DIR = "my_sos_lora_weights"
MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"

class LoggingCallback(TrainerCallback):
    def __init__(self):
        self.step_start_time = time.time()

    def on_step_begin(self, args, state, control, **kwargs):
        self.step_start_time = time.time()
        print(f"\n[PROGRESSION] Début de l'étape {state.global_step + 1}/{state.max_steps}...", flush=True)

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            elapsed = time.time() - self.step_start_time
            loss = logs.get("loss", "N/A")
            print(f" [OK] Étape {state.global_step}/{state.max_steps} terminée | Perte (Loss): {loss} | Durée: {elapsed:.2f}s", flush=True)

class SOSDataset(Dataset):
    def __init__(self, entries, processor):
        self.entries = entries
        self.processor = processor

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, idx):
        item = self.entries[idx]
        image_paths = item.get("images", [])
        
        image = None
        if image_paths and os.path.exists(image_paths[0]):
            try:
                image = Image.open(image_paths[0]).convert("RGB")
                image.thumbnail((448, 448))
            except Exception as e:
                print(f"[ERREUR IMAGE] Impossible de charger {image_paths[0]}: {e}", flush=True)

        prompt = item.get("prompt", "Décris l'étape industrielle.")
        response = item.get("response", "")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt},
                ],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": response}],
            }
        ]

        text_prompt = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)

        if image:
            inputs = self.processor(text=[text_prompt], images=[image], return_tensors="pt", padding=True)
        else:
            inputs = self.processor(text=[text_prompt], return_tensors="pt", padding=True)

        inputs = {k: v.squeeze(0) for k, v in inputs.items()}
        inputs["labels"] = inputs["input_ids"].clone()
        return inputs

def load_local_dataset():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Jeu de données {DATASET_PATH} introuvable.")
    
    entries = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                if data.get("images"):
                    entries.append(data)
    return entries

def main():
    print("=" * 60, flush=True)
    print("[TRAINING] Début du processus de fine-tuning LoRA", flush=True)
    print("=" * 60, flush=True)

    entries = load_local_dataset()
    is_cuda = torch.cuda.is_available()

    processor = AutoProcessor.from_pretrained(MODEL_ID, local_files_only=True)

    if is_cuda:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_ID,
            quantization_config=bnb_config,
            device_map="auto",
            local_files_only=True
        )
        model = prepare_model_for_kbit_training(model)
    else:
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            device_map="cpu",
            local_files_only=True
        )

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)

    train_dataset = SOSDataset(entries, processor)

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=2,
        warmup_steps=2,
        max_steps=20,
        learning_rate=2e-4,
        fp16=is_cuda,
        logging_steps=1,
        save_strategy="no",
        report_to="none",
        remove_unused_columns=False,
        gradient_checkpointing=True,
        dataloader_pin_memory=False
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        callbacks=[LoggingCallback()]
    )

    trainer.train()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model.save_pretrained(OUTPUT_DIR)
    processor.save_pretrained(OUTPUT_DIR)
    print(f"\n[SUCCÈS] Entraînement terminé et poids sauvegardés dans {OUTPUT_DIR} !", flush=True)

if __name__ == "__main__":
    main()