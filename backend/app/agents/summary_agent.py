import dspy

class SummarizerSignature(dspy.Signature):
    journal_text = dspy.InputField(desc="Full personal journal entry.")
    summary = dspy.OutputField(desc="Warm, supportive summary highlighting the key feelings and themes in the entry.")

class Summarizer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.teleprompt = dspy.Predict(SummarizerSignature)
    
    def forward(self, transcript:str):
        return self.teleprompt(journal_text=transcript)