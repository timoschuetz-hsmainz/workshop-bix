from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MultivariateScores:
    scores: list[float]  # lower => more anomalous (IsolationForest decision_function)
    flags: list[bool]


def _fit_isolation_forest(train_vectors: list[list[float]], *, contamination: float = 0.05) -> Any:
    from sklearn.ensemble import IsolationForest  # type: ignore

    model = IsolationForest(
        n_estimators=200,
        contamination=float(contamination),
        random_state=42,
    )
    model.fit(train_vectors)
    return model


def score_isolation_forest(
    *,
    train_vectors: list[list[float]],
    test_vectors: list[list[float]],
    contamination: float = 0.05,
    score_threshold: float = 0.0,
) -> MultivariateScores:
    """
    Fits an IsolationForest on train_vectors and scores test_vectors.
    - score: decision_function (higher => more normal)
    - flag: score < score_threshold
    """
    if not train_vectors or not test_vectors:
        return MultivariateScores(scores=[], flags=[])

    model = _fit_isolation_forest(train_vectors, contamination=contamination)
    scores = [float(s) for s in model.decision_function(test_vectors)]
    flags = [s < float(score_threshold) for s in scores]
    return MultivariateScores(scores=scores, flags=flags)

