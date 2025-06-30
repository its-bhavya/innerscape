import dspy

class ResourceRecommenderSignature(dspy.Signature):
    journal_text = dspy.InputField(desc="A personal journal entry.")
    strategies = dspy.OutputField(desc="""
Return 4–6 coping strategies in this format:

[
  {
    "title": "Short strategy name",
    "summary": "1-line description.",
    "steps": ["Step 1", "Step 2", ...]
  },
  ...
]

No links. Keep everything concise and tailored to the journal.
""")

class ResourceRecommender(dspy.Module):
    def __init__(self):
        super().__init__()
        self.agent = dspy.ChainOfThought(ResourceRecommenderSignature)

    def forward(self, transcript: str):
        return self.agent(journal_text=transcript)
