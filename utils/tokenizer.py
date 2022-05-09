
from sacremoses import MosesTokenizer
import nltk.corpus.stopwords


class Tokenizer:
    def __init__(self, use_stopwords: bool = False, language: str = "sp"):
        self.tokenizer = MosesTokenizer(lang=language)
        if use_stopwords:
            stopwords = nltk.corpus.stopwords.words("english")
            self.stopwords = stopwords
        else:
            self.stopwords = list()

    def clean_text(self, text: str) -> str:
        text_lower = text.lower()
        text_lower = " ".join([word for word in text_lower.split() if word not in self.stopwords])
        return text_lower

    def tokenize(self, text: str, process: bool = True) -> str:
        if process:
            text = self.clean_text(text)
        return self.tokenizer.tokenize(text, escape=False)
