import torch
import re
import html
import emoji
import torch.nn.functional as F


from .apps import AnalyzerConfig


class ABSAService:
    @staticmethod
    def clean_text(text) -> str:
        text = html.unescape(str(text))
        text = re.sub(r"http\S+|www\S+|https\S+", "[URL]", text)
        text = emoji.demojize(text, delimiters=(" ", " "))
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def extract_aspects(text) -> list:
        nlp = AnalyzerConfig.nlp
        doc = nlp(text)

        aspects = set()

        # Noun Chunks
        for chunk in doc.noun_chunks:
            if chunk.root.pos_ == "PRON":
                continue
            aspects.add(chunk.text.lower())

        # Standalone Nouns
        for token in doc:
            if token.pos_ == "NOUN" and len(token.text) > 2:
                aspects.add(token.text.lower())

        return list(aspects)

    @staticmethod
    def analyze_sentiment(text):
        tokenizer = AnalyzerConfig.tokenizer
        model = AnalyzerConfig.bert_model
        device = AnalyzerConfig.device

        cleaned_text = ABSAService.clean_text(text)
        detected_aspects = ABSAService.extract_aspects(cleaned_text)

        results = []
        id2label = {0: "negative", 1: "neutral", 2: "positive"}

        if not detected_aspects:
            return {"error": "No clear aspects found. Try being more specific"}

        for aspect in detected_aspects:
            # Tokenize Pair
            inputs = tokenizer(
                cleaned_text,
                aspect,
                return_tensors="pt",
                truncation=True,
                max_length=128,
            ).to(device)

            with torch.no_grad():
                outputs = model(**inputs)
                probs = F.softmax(outputs.logits, dim=1)
                pred_id = torch.argmax(probs, dim=1).item()
                confidence = probs[0][pred_id].item()

            results.append(
                {
                    "aspect": aspect,
                    "sentiment": id2label[pred_id],
                    "confidence": round(confidence, 4),
                }
            )
        return {
            "original_text": text,
            "analysis": results,
        }
