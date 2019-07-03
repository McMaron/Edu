import nltk

class Analyzer():
    """Implements sentiment analysis."""

    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        
        self.positives = []
        positive_words = open(positives, "r")
        if positive_words == None:
            raise ValueError("Could not open the dictionary file!")
        for line in positive_words:
            if not line.startswith(";") and not line.startswith("\n"):
                 self.positives.append(line.strip())
        positive_words.close()
        
        self.negatives = []
        negative_words = open(negatives, "r")
        if negative_words == None:
            raise ValueError("Could not open the dictionary file!")
        for line in negative_words:
            if not line.startswith(";") and not line.startswith("\n"):
                 self.negatives.append(line.strip())
        negative_words.close()        
        

    def analyze(self, text):
        """Analyze text for sentiment, returning its score."""
        score = 0
        
        tokenizer = nltk.tokenize.TweetTokenizer()
        tokens = tokenizer.tokenize(text)
        for token in tokens:
            if token.lower() in self.positives:
                score += 1
            if token.lower() in self.negatives:
                score -= 1
        return score
