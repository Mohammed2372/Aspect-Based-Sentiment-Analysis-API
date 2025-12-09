import torch
import re
import html
import emoji
import torch.nn.functional as F


from django.apps import apps


class ABSAService:
    
    PREFIX_STOPWORDS = {
        "the", "a", "an", "my", "our", "your", "their", "this", "that", 
        "these", "those", "some", "any", "all", "few", "many", "several"
    }
    
    BLACKLIST_ASPECTS = {
        # Sentiment Adjectives (Positive)
        "good", "great", "excellent", "amazing", "wonderful", "awesome", "nice", "best", "perfect",
        # Sentiment Adjectives (Negative)
        "bad", "terrible", "awful", "horrible", "worst", "poor", "slow", "rude", "garbage", "trash", "useless",
        # Generic filler nouns
        "thing", "things", "stuff", "bit", "lot", "way", "example"
    }
    
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

        candidates_aspects = set()

        # Noun Chunks
        for chunk in doc.noun_chunks:
            # skip pronouns
            if chunk.root.pos_ == "PRON":
                continue

            # clean text
            clean_text = chunk.text.lower()
            words = clean_text.split()
            
            # remove leading stopwords
            if words[0] in ABSAService.PREFIX_STOPWORDS:
                clean_text = " ".join(words[1:])

            clean_text = clean_text.strip()
            
            # add only if not empty and not in blacklist
            if clean_text and clean_text not in ABSAService.BLACKLIST_ASPECTS:
                candidates_aspects.add(clean_text)
                
        # Named Entities
        for ent in doc.ents:
            clean_ent = ent.text.lower().strip()
            if clean_ent and clean_ent not in ABSAService.BLACKLIST_ASPECTS:
                candidates_aspects.add(clean_ent)

        # Intelligent Filtering (Duplication)
        ## convert list and sort by length
        sorted_candidates_aspects = sorted(
            list(candidates_aspects), key=len, reverse=True
        )

        final_aspects = []
        for candidate in sorted_candidates_aspects:
            # check if candidate is already inside another longer aspect
            is_subset = False
            for aspect in final_aspects:
                # token-based check
                if candidate in aspect:
                    is_subset = True
                    break

            if not is_subset:
                final_aspects.append(candidate)

        return list(final_aspects)

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
