from prompts import build_summary_prompt


class SummaryEngine:
    def __init__(self):
        self.summary = ""
        self.turn_count = 0

    # -----------------------------
    # TURN TRACKING
    # -----------------------------
    def increment_turn(self):
        self.turn_count += 1

    def should_update_summary(self):
        # update every 2–3 turns
        return self.turn_count % 3 == 0

    # -----------------------------
    # SUMMARY STORAGE
    # -----------------------------
    def get_summary(self):
        return self.summary

    def update_summary(self, new_summary):
        self.summary = new_summary.strip()

    # -----------------------------
    # CONTEXT READINESS
    # -----------------------------
    def has_enough_context(self):
        """
        Heuristic:
        - at least 8 turns
        - summary has some substance
        """
        return (
            self.turn_count >= 8
            and len(self.summary.split()) >= 25
        )

    # -----------------------------
    # SUMMARY GENERATION (YOUR LOGIC)
    # -----------------------------
    def generate_summary(self, gemini_client, recent_messages):
        """
        recent_messages: list of last 2–3 strings (user + ai)
        """
        prompt = build_summary_prompt(self.summary, recent_messages)

        try:
            new_summary = gemini_client.generate(prompt)
            return new_summary.strip()
        except Exception as e:
            print("SUMMARY ERROR:", e)
            return self.summary  # fail safe
