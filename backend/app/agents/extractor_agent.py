import dspy, os

class StructureExtractionSignature(dspy.Signature):
    transcript = dspy.InputField(desc="The full personal journal entry written or spoken by the user.")

    central_topic = dspy.OutputField(
        desc="The main emotional theme or dominant feeling reflected in the journal (e.g., overwhelmed, grateful, hopeful, disconnected)."
    )

    subtopics = dspy.OutputField(
        desc="""A raw JSON list where each subtopic captures a key related thought, emotion, or experience. Each subtopic includes:
        - 'title': a short, empathetic label for the emotion or idea
        - 'description': a brief phrase summarizing the thought or why it matters
        - optional 'children': deeper subtopics if the thought/emotion has nuances

        Nest subtopics only when it helps express emotional depth.
        Use compassionate, human language. Avoid analytical or robotic tone.
        Example:
        [
          {
            "title": "Anxiety About Exams",
            "description": "Feeling overwhelmed by expectations and fear of underperforming",
            "children": [
              {
                "title": "Time Pressure",
                "description": "Worrying there's not enough time to revise properly"
              }
            ]
          }
        ]
        """
    )


class MindmapExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.teleprompt = dspy.ChainOfThought(StructureExtractionSignature)

    def forward(self, transcript: str):
        return self.teleprompt(transcript=transcript)
