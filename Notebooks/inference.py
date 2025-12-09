import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import re
import html
import emoji
import torch.nn.functional as F


MODEL_PATH = "model/absa_bert_model"
print(f"Loading model from {MODEL_PATH}...")

try:
    # Load Model & Tokenizer
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

    # Move to GPU if available (optional for inference, but faster)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()  # Set to evaluation mode (turns off Dropout, etc.)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()


def clean_text(text) -> str:
    text = html.unescape(str(text))
    text = re.sub(r"http\S+|www\S+|https\S+", "[URL]", text)
    text = re.sub(r"@\w+", "[USER]", text)
    text = emoji.demojize(text, delimiters=(" ", " "))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def predict_sentiment(sentence, aspect) -> tuple[str, int | float | bool]:
    cleaned_text = clean_text(sentence)

    inputs = tokenizer(
        cleaned_text,
        aspect,
        return_tensors="pt",  # Return PyTorch tensors
        truncation=True,
        padding="max_length",
        max_length=128,
    )

    # Move inputs to the same device as model
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Inference
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

        # Convert logits to probabilities (0.0 to 1.0)
        probs = F.softmax(logits, dim=1)

        # Get the highest probability class
        prediction = torch.argmax(logits, dim=1).item()
        confidence = probs[0][prediction].item()

    id2label = {0: "Negative 😡", 1: "Neutral 😐", 2: "Positive 😃"}
    return id2label[prediction], confidence


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🤖 AI Multi-Aspect Tester")
    print("=" * 50)

    while True:
        print("\n" + "-" * 30)
        text = input("1. Enter Review Sentence (or 'q'): ")
        if text.lower() == "q":
            break

        # input: "food, service, price"
        aspects_input = input("2. Enter Aspects (comma separated): ")
        if aspects_input.lower() == "q":
            break

        # Split string into list: ['food', 'service', 'price']
        aspect_list = [a.strip() for a in aspects_input.split(",")]

        print(f'\nAnalyzing: "{text}"')
        for aspect in aspect_list:
            if not aspect:
                continue  # skip empty strings

            sentiment, score = predict_sentiment(text, aspect)

            # Print a nice table row
            print(
                f"   👉 Aspect: {aspect.ljust(15)} | Sentiment: {sentiment} ({score:.1%})"
            )
