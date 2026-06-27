import logging

from google.adk import Context
from google.adk.workflow import node

from src.schemas import RetrievedContext, SearchPlan
from src.settings import settings

logger = logging.getLogger(__name__)

MOCK_DOCS_COMPLETE: list[RetrievedContext] = [
    RetrievedContext(
        corpus_id="medication_corpus",
        source_id="dc_001",
        title="Discharge Summary - Patient #4821",
        content=(
            "Patient was discharged on 2024-11-14. Discharge medications: "
            "Metformin 500mg twice daily with meals, Lisinopril 10mg once daily in the morning, "
            "Atorvastatin 20mg once daily at bedtime. Follow-up appointment scheduled with "
            "Dr. Patel in 2 weeks. Patient instructed to follow a low-sodium, low-fat diet. "
            "No strenuous activity for 4 weeks. Return to ER if chest pain or shortness of breath."
        ),
        score=0.94,
    ),
    RetrievedContext(
        corpus_id="clinical_notes_corpus",
        source_id="dc_002",
        title="Nursing Discharge Notes - Patient #4821",
        content=(
            "Patient educated on medication schedule and dietary restrictions. "
            "Patient verbalized understanding of low-sodium diet (less than 1500mg/day). "
            "Wound care instructions provided for surgical site on left knee. "
            "Patient and family demonstrated correct dressing change technique."
        ),
        score=0.88,
    ),
    RetrievedContext(
        corpus_id="clinical_notes_corpus",
        source_id="dc_003",
        title="Adverse Events & Allergy Log - Patient #4821",
        content=(
            "No allergic reactions were observed during the hospital stay. "
            "No adverse drug events recorded. Patient tolerated all administered medications "
            "without incident. No rashes, urticaria, or anaphylactic episodes noted."
        ),
        score=0.85,
    ),
]

MOCK_DOCS_PARTIAL: list[RetrievedContext] = [
    RetrievedContext(
        corpus_id="medication_corpus",
        source_id="dc_001",
        title="Discharge Summary - Patient #4821",
        content=(
            "Patient was discharged on 2024-11-14. Discharge medications: "
            "Metformin 500mg twice daily with meals, Lisinopril 10mg once daily in the morning, "
            "Atorvastatin 20mg once daily at bedtime. Follow-up appointment scheduled with "
            "Dr. Patel in 2 weeks. Patient instructed to follow a low-sodium, low-fat diet."
        ),
        score=0.91,
    ),
    RetrievedContext(
        corpus_id="clinical_notes_corpus",
        source_id="dc_002",
        title="Nursing Discharge Notes - Patient #4821",
        content=(
            "Patient educated on medication schedule and dietary restrictions. "
            "Patient verbalized understanding of low-sodium diet."
        ),
        score=0.82,
    ),
]


@node(name="mock_retrieval_node")
async def mock_retrieval_node(ctx: Context, node_input: SearchPlan) -> list[RetrievedContext]:
    """Mock retrieval node for demo purposes.

    Scenario 1 (settings.demo_scenario == 1): always returns complete documents.
    Scenario 2 (settings.demo_scenario == 2): returns partial documents on the first
    retrieval round and complete documents on the second.
    """
    search_plan = node_input
    round_key = "_retrieval_round"
    current_round = ctx.session.state.get(round_key, 0)
    ctx.session.state[round_key] = current_round + 1

    logger.info(
        "Mock retrieval — scenario=%d  round=%d  plan_corpora=%s",
        settings.demo_scenario,
        current_round,
        [t.corpus_id for t in search_plan.tasks],
    )

    if settings.demo_scenario == 2 and current_round == 0:
        logger.info("Returning partial documents (round 1 of scenario 2)")
        return MOCK_DOCS_PARTIAL

    logger.info("Returning complete documents")
    return MOCK_DOCS_COMPLETE
