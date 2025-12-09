from django.apps import AppConfig
from transformers import AutoTokenizer, AutoModelForSequenceClassification

import torch
import spacy


class AnalyzerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "analyzer"

    bert_model = None
    tokenizer = None
    nlp = None
    device = None

    def ready(self) -> None:
        print("🤖 Loading AI Models... (This may take 10-20 seconds)")

        try:
            # path to the model folder
            model_path = "../model/absa_bert_model"

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
            if not spacy.util.is_package("en_core_web_sm"):
                spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

            print("✅ AI Models Loaded Successfully!")

        except Exception as e:
            print(f"❌ Error loading models: {e}")
