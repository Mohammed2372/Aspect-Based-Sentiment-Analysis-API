import torch
import spacy
import subprocess
import sys
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class ABSAModel:
    def __init__(self, model_path: str = "bert-base-uncased"):
        print("⏳ Loading AI Models...")

        # load aspect extractor
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⬇️ Downloading SpaCy model 'en_core_web_sm'...")
            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
            )
            self.nlp = spacy.load("en_core_web_sm")

        # load BERT sentiment model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()

        # labels map
        self.labels = {0: "negative", 1: "neutral", 2: "positive"}
        print(f"✅ Models loaded on {self.device}!")

    def predict(self, text: str):
        IGNORED_ASPECTS = {
            "time",
            "minute",
            "hour",
            "day",
            "year",
            "moment",
            "lot",
            "bit",
            "bunch",
            "plenty",
            "thing",
            "something",
            "anything",
            "everything",
            "nothing",
            "way",
            "part",
            "side",
            "kind",
            "sort",
            "type",
            "one",
            "example",
            "reason",
            "issue",
            "problem",
        }
        # extract aspects
        doc = self.nlp(text)
        aspects = []

        for chunk in doc.noun_chunks:
            word = chunk.root.text.lower().strip()
            token = chunk.root

            if (
                not token.is_stop
                and token.pos_ != "PRON"
                and len(word) > 2
                and word not in IGNORED_ASPECTS
            ):
                aspects.append(chunk.root.text)

        aspects = list(set(aspects))

        # analyze each aspect
        results = []
        for aspect in aspects:
            inputs = self.tokenizer(
                text,
                aspect,
                return_tensors="pt",
                truncation=True,
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=1)

            confidence, pred_id = torch.max(probs, dim=1)
            sentiment = self.labels.get(pred_id.item(), "unknown")

            results.append(
                {
                    "aspect": aspect,
                    "sentiment": sentiment,
                    "confidence": float(confidence.item()),
                }
            )

        return results
