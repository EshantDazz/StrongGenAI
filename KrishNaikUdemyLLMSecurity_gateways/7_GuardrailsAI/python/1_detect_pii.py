import logging
import warnings

from dotenv import load_dotenv
from guardrails import Guard, OnFailAction, ValidationOutcome
from guardrails.hub import CompetitorCheck, DetectPII

warnings.filterwarnings("ignore")
logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)

_ = load_dotenv()

pii_guard = Guard().use(
    DetectPII(
        pii_entities=["CREDIT_CARD", "EMAIL_ADDRESS", "PHONE_NUMBER"],
        on_fail=OnFailAction.FIX,
        use_local=True,  # light: Presidio + spaCy small, no torch
    )
)

raw = "We'll refund card 4111 1111 1111 1111 and email the receipt to jane@example.com."
out = pii_guard.validate(raw)
print(out)

# ValidationOutcome[TypeVar](
#     call_id='4841896160',
#     raw_llm_output="We'll refund card 4111 1111 1111 1111 and email the receipt to jane@example.com.",
#     validation_summaries=[
#         ValidationSummary(
#             validator_name='DetectPII',
#             validator_status='fail',
#             property_path='$',
#             failure_reason="The following text in your response contains PII:\nWe'll refund card 4111 1111 1111 1111 and email the receipt to jane@example.com.",
#             error_spans=[
#                 ErrorSpan(
#                     start=18,
#                     end=37,
#                     reason='PII detected in 4111 1111 1111 1111'
#                 ),
#                 ErrorSpan(
#                     start=63,
#                     end=75,
#                     reason='PII detected in jane@example'
#                 )
#             ]
#         )
#     ],
#     validated_output="We'll refund card <CREDIT_CARD> and email the receipt to <EMAIL_ADDRESS>.",
#     reask=None,
#     validation_passed=True,
#     error=None
# )


COMPETITORS = ["Stripe", "PayPal", "Square"]
BAD_TEXT = (
    "Thanks for reaching out! Honestly, Stripe has lower fees than us, "
    "and PayPal is easier to set up. But we're happy to help with your refund."
)
GOOD_TEXT = "Thanks for reaching out! We're happy to help with your refund."


comp_guard = Guard().use(
    CompetitorCheck(
        competitors=COMPETITORS, on_fail=OnFailAction.FILTER, use_local=True
    )
)
out = comp_guard.validate(GOOD_TEXT)
print("OUT:", repr(out.validated_output))
