from django.apps import AppConfig
from transformers import AutoTokenizer, AutoModelForSequenceClassification

import torch
import spacy
import os
import sys


class AnalyzerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "analyzer"

    bert_model = None
    tokenizer = None
    nlp = None
    device = None

    def ready(self) -> None:
        # Prevent double loading if Django reloads
        if AnalyzerConfig.bert_model is not None:
            return

        # List of commands where we definitely DO NOT want to load models
        ignore_commands = [
            "makemigrations",
            "migrate",
            "createsuperuser",
            "test",
            "shell",
            "collectstatic",
            "showmigrations",
        ]

        # Check if any argument in the command line matches the ignore list
        is_management_command = any(cmd in sys.argv for cmd in ignore_commands)

        # Also, ensure we are actually running a server process.
        is_runserver = "runserver" in sys.argv
        is_production_server = (
            "manage.py" not in sys.argv[0]
        )

        if is_management_command:
            print("🛑 Skipping AI Model load for management command.")
            return

        if not (is_runserver or is_production_server):
            return

        print("🤖 Loading AI Models...")

        try:
            # path to the model folder
            app_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(app_dir)
            model_path = os.path.join(project_root, "model", "absa_bert_model")
            print(f"   📂 Looking for model at: {model_path}")

            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model folder not found at {model_path}")

            # load bert model
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(
                model_path
            )

            # setup GPU/CPU
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.bert_model = self.bert_model.to(self.device)
            self.bert_model.eval()

            # load spacy (for aspect extraction)
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("   ⚠️  SpaCy model not found. Downloading...")
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")

            print("✅ AI Models Loaded Successfully!")

        except Exception as e:
            print(f"❌ Error loading models: {e}")
