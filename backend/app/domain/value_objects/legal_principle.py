from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LegalPrinciple:
    title: str
    article_number: str
    description: str
    severity: int
