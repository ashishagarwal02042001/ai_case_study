from backend.agents import DataExtractionAgent, ValidationAgent, EligibilityAgent, ExplanationAgent

class Orchestrator:
    def __init__(self):
        self.extractor = DataExtractionAgent()
        self.validator = ValidationAgent()
        self.eligibility = EligibilityAgent()
        self.explainer = ExplanationAgent()

    def process_application(self, application: dict):
        app_id = application.get("app_id")
        parsed_docs = self.extractor.extract(application)
        validation_report = self.validator.validate(application, parsed_docs)
        decision, score, reasons, recommendations, = self.eligibility.assess(application, parsed_docs, validation_report)
        explanation = self.explainer.explain (application, parsed_docs, validation_report, decision, score, recommendations)
        result = {
            "app_id": app_id,
            "decision": decision,
            "score": score,
            "reasons": reasons,
            "recommendations": recommendations,
            "explanation": explanation,
            }
        print(result)
        return result

    def explain_query(self, query: str, app_id: None) -> str:
        return self.explainer.answer_query(query, app_id)