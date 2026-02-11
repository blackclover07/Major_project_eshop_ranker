# =====================================
    # Sentiment Function
# =====================================

from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from scipy.special import softmax
import numpy as np
import torch
import re

MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# GLOBAL LOAD
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)


def preprocess(text):
    text = text.lower()
    text = re.sub(r'http\S+', 'http', text)
    text = re.sub(r'@\w+', '@user', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def predict_sentiment(text):
    text = preprocess(text)

    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    scores = softmax(outputs.logits[0].numpy())
    best_index = np.argmax(scores)

    return config.id2label[best_index].upper(), float(scores[best_index])