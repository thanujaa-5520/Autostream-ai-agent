from __future__ import annotations

import json
from pathlib import Path
from typing import List


class LocalKnowledgeBase:
    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Knowledge file not found: {self.file_path}")
        self.data = json.loads(self.file_path.read_text(encoding="utf-8"))
        self.documents = self._build_documents()

    def _build_documents(self) -> List[str]:
        docs: List[str] = []
        docs.append(
            f"{self.data['company']} is a SaaS product that provides {self.data['product']}."
        )

        for plan in self.data.get("plans", []):
            docs.append(
                f"{plan['name']}: price is {plan['price']}. Features: {', '.join(plan['features'])}."
            )

        for policy in self.data.get("policies", []):
            docs.append(f"Policy: {policy}.")

        for faq in self.data.get("faq", []):
            docs.append(f"FAQ - {faq['question']} Answer: {faq['answer']}")

        return docs

    def retrieve(self, query: str, top_k: int = 3) -> str:
        """Tiny local retrieval mechanism using simple keyword overlap.

        This keeps the project fully runnable without external vector DB setup,
        while still satisfying the requirement to answer from a local knowledge base.
        """
        query_terms = set(query.lower().split())
        scored = []
        for doc in self.documents:
            doc_terms = set(doc.lower().split())
            overlap = len(query_terms.intersection(doc_terms))
            scored.append((overlap, doc))

        scored.sort(key=lambda item: item[0], reverse=True)
        selected = [doc for score, doc in scored[:top_k] if score > 0]

        if not selected:
            selected = self.documents[:top_k]

        return "\n".join(selected)
