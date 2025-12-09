import torch
import re
import html
import emoji
import torch.nn.functional as F


from django.apps import apps


class ABSAService:
    @staticmethod
    def clean_text(text) -> str:
        text = html.unescape(str(text))
        text = re.sub(r"http\S+|www\S+|https\S+", "[URL]", text)
        text = emoji.demojize(text, delimiters=(" ", " "))
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def get_models():
        app_config = apps.get_app_config("analyzer")
        return (
            app_config.nlp,
            app_config.tokenizer,
            app_config.bert_model,
            app_config.device,
        )

    @staticmethod
    def extract_aspects(text) -> list:
        nlp, _, _, _ = ABSAService.get_models()
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
        nlp, tokenizer, model, device = ABSAService.get_models()

        cleaned_text = ABSAService.clean_text(text)
        detected_aspects = ABSAService.extract_aspects(cleaned_text)

        results = []
        id2label = {0: "negative", 1: "neutral", 2: "positive"}

        # fallback if not aspects found
        if not detected_aspects:
            print("No clear aspects found. Analyze whole sentence as general")
            detected_aspects = ["general"]

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
