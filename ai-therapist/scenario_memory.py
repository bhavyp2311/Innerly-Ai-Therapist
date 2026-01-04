# class ScenarioMemory:
#     def __init__(self, max_items=5):
#         self.items = []
#         self.max_items = max_items

#     def add_once(self, scenario: str):
#         if scenario not in self.items:
#             self.items.append(scenario)
#         if len(self.items) > self.max_items:
#             self.items.pop(0)

#     def get(self):
#         return self.items



# from collections import deque

# class ScenarioMemory:
#     def __init__(self, window_size=5):
#         self.window_size = window_size
#         self.recent_inputs = deque(maxlen=window_size)
#         self.summary = ""

#     def add_input(self, user_text: str):
#         clean = user_text.strip().replace("\n", " ")
#         if clean:
#             self.recent_inputs.append(clean)

#     def update_summary(self, summarizer_fn):
#         """
#         summarizer_fn: function that takes a string and returns a short summary
#         """
#         if len(self.recent_inputs) < 2:
#             return  # too early to summarize

#         text = " ".join(self.recent_inputs)

#         self.summary = summarizer_fn(text)

#     def get(self):
#         if not self.summary:
#             return []
#         return [self.summary]


from collections import deque

class ScenarioMemory:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.recent_inputs = deque(maxlen=window_size)

        # Accumulated scenario summaries (USED BY AI)
        self.scenario_history = []

    def add_input(self, user_text: str):
        clean = user_text.strip().replace("\n", " ")
        if clean:
            self.recent_inputs.append(clean)

    def update_summary(self, summarizer_fn):
        """
        summarizer_fn: function that takes a string and returns a short summary
        """
        if len(self.recent_inputs) < 2:
            return

        text = " ".join(self.recent_inputs)
        new_summary = summarizer_fn(text)

        # Append only if meaningfully new
        if new_summary:
            if not self.scenario_history:
                self.scenario_history.append(new_summary)
            elif new_summary != self.scenario_history[-1]:
                self.scenario_history.append(new_summary)

    def get(self):
        """
        This is what the AI sees.
        Returns ALL scenario summaries, oldest → newest.
        """
        return self.scenario_history
