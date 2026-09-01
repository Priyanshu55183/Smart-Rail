"""
Journey Scoring Engine
======================
Ranks journeys using multi-criteria scoring, then tags the best ones.

Scoring Dimensions (0-100 each):
  1. Travel Time    (35%): Faster journey = higher score
  2. Layover Quality(25%): Comfortable layovers = higher score
  3. Reliability    (20%): Lower delay risk = higher score (ML fills this later)
  4. Price          (15%): Cheaper = higher score
  5. Convenience    (5%):  Fewer connections = higher score

The composite score is a weighted average:
  composite = 0.35×time + 0.25×layover + 0.20×reliability + 0.15×price + 0.05×convenience

Smart Tags:
  After scoring, the best journey in each category gets a tag:
  - BEST_OVERALL:   Highest composite score
  - FASTEST:        Lowest total travel time
  - CHEAPEST:       Lowest total fare
  - SAFEST:         Highest reliability + lowest connection risk
  - FEWEST_CHANGES: Fewest train changes

These tags become the "Recommended" cards in the frontend.
"""

from typing import Optional
from app.config import get_settings

settings = get_settings()


class JourneyScorer:
    """
    Scores and ranks a list of journey dicts.

    Usage:
        scorer = JourneyScorer()
        scored = scorer.score_journeys(journey_list)
        tagged  = scorer.tag_recommendations(scored)
    """

    def score_journeys(self, journeys: list[dict]) -> list[dict]:
        """
        Score all journeys relative to each other.

        Why relative? Because "2 hours" is fast for Delhi→Chennai
        but slow for Delhi→Agra. Normalizing against the group
        gives meaningful 0-100 scores regardless of distance.
        """
        if not journeys:
            return []

        # Collect metrics for normalization
        times = [j.get("total_duration_minutes", 0) for j in journeys]
        fares = [j.get("total_fare", 0) or 0 for j in journeys]
        connections = [j.get("num_connections", 0) for j in journeys]

        min_time = min(times) if times else 1
        max_time = max(times) if times else 1
        min_fare = min(f for f in fares if f > 0) if any(f > 0 for f in fares) else 1
        max_fare = max(fares) if fares else 1
        max_conn = max(connections) if connections else 1

        for j in journeys:
            j["score"] = self._compute_score(
                j, min_time, max_time, min_fare, max_fare, max_conn
            )

        # Sort by composite score (highest first)
        journeys.sort(key=lambda j: j["score"]["composite"], reverse=True)

        return journeys

    def _compute_score(
        self,
        journey: dict,
        min_time: int,
        max_time: int,
        min_fare: float,
        max_fare: float,
        max_conn: int,
    ) -> dict:
        """Compute the multi-criteria score for a single journey."""

        # ── 1. Travel Time Score ──────────────────────────────
        # Lower time = higher score. Normalized to 0-100.
        travel_time = journey.get("total_duration_minutes", 0)
        if max_time > min_time:
            time_score = 100 * (1 - (travel_time - min_time) / (max_time - min_time))
        else:
            time_score = 100.0
        time_score = max(0, min(100, time_score))

        # ── 2. Layover Quality Score ─────────────────────────
        # Based on risk levels of layovers.
        layover_score = self._score_layovers(journey.get("layovers", []))

        # ── 3. Reliability Score ─────────────────────────────
        # Placeholder — returns a sensible default based on train type.
        # Phase 3 (ML) will replace this with XGBoost predictions.
        reliability_score = self._score_reliability(journey)

        # ── 4. Price Score ───────────────────────────────────
        total_fare = journey.get("total_fare", 0) or 0
        if max_fare > min_fare and total_fare > 0:
            price_score = 100 * (1 - (total_fare - min_fare) / (max_fare - min_fare))
        else:
            price_score = 80.0  # Default if fares unavailable
        price_score = max(0, min(100, price_score))

        # ── 5. Convenience Score ─────────────────────────────
        # Direct (0 connections) = 100, 1 connection = 70, 2 = 40, 3 = 10
        num_conn = journey.get("num_connections", 0)
        convenience_score = max(0, 100 - (num_conn * 30))

        # ── Composite ────────────────────────────────────────
        composite = (
            settings.SCORE_WEIGHT_TRAVEL_TIME * time_score
            + settings.SCORE_WEIGHT_LAYOVER_QUALITY * layover_score
            + settings.SCORE_WEIGHT_RELIABILITY * reliability_score
            + settings.SCORE_WEIGHT_PRICE * price_score
            + settings.SCORE_WEIGHT_CONVENIENCE * convenience_score
        )

        return {
            "composite": round(composite, 1),
            "travel_time_score": round(time_score, 1),
            "layover_score": round(layover_score, 1),
            "reliability_score": round(reliability_score, 1),
            "price_score": round(price_score, 1),
            "convenience_score": round(convenience_score, 1),
        }

    def _score_layovers(self, layovers: list[dict]) -> float:
        """
        Score layover quality. No layovers (direct) = 100.
        Average the scores for each individual layover.
        """
        if not layovers:
            return 100.0  # Direct train — best possible

        scores = []
        for layover in layovers:
            risk = layover.get("risk_level", "LOW_RISK")
            if risk == "HIGH_RISK":
                scores.append(20.0)
            elif risk == "MODERATE_RISK":
                scores.append(55.0)
            elif risk == "LOW_RISK":
                scores.append(90.0)
            elif risk == "LONG_LAYOVER":
                scores.append(60.0)
            else:
                scores.append(70.0)

        return sum(scores) / len(scores) if scores else 100.0

    def _score_reliability(self, journey: dict) -> float:
        """
        Placeholder reliability score based on train types.

        Train type reliability heuristic (real ML replaces this in Phase 3):
          RAJDHANI:     92 (premium, priority)
          VANDE_BHARAT: 90 (modern, well-maintained)
          SHATABDI:     88 (day train, fewer delays)
          DURONTO:      86 (non-stop, fewer delays)
          SUPERFAST:    80 (standard)
          EXPRESS:      72 (regular)
          MAIL:         65 (older, more delays)
          PASSENGER:    55 (stops everywhere, low priority)
        """
        type_scores = {
            "RAJDHANI": 92,
            "VANDE_BHARAT": 90,
            "SHATABDI": 88,
            "DURONTO": 86,
            "SUPERFAST": 80,
            "EXPRESS": 72,
            "MAIL": 65,
            "PASSENGER": 55,
        }

        segments = journey.get("train_segments", [])
        if not segments:
            return 75.0

        # Average reliability across all train segments
        seg_scores = []
        for seg in segments:
            train_type = seg.get("train_type", "EXPRESS")
            seg_scores.append(type_scores.get(train_type, 72))

        # Penalty for connections (each connection adds failure risk)
        num_conn = journey.get("num_connections", 0)
        connection_penalty = num_conn * 5  # -5 per connection

        score = (sum(seg_scores) / len(seg_scores)) - connection_penalty
        return max(0, min(100, score))

    def tag_recommendations(self, journeys: list[dict]) -> list[dict]:
        """
        Tag the best journey in each category.

        Tags: BEST_OVERALL, FASTEST, CHEAPEST, SAFEST, FEWEST_CHANGES

        A journey can have multiple tags (e.g., the direct Rajdhani
        might be both FASTEST and SAFEST).
        """
        if not journeys:
            return []

        # Initialize tags
        for j in journeys:
            j["tags"] = []

        # BEST_OVERALL: Already sorted by composite score (first one)
        journeys[0]["tags"].append("BEST_OVERALL")

        # FASTEST: Lowest total_duration_minutes
        fastest = min(journeys, key=lambda j: j.get("total_duration_minutes", float("inf")))
        if "FASTEST" not in fastest["tags"]:
            fastest["tags"].append("FASTEST")

        # CHEAPEST: Lowest total_fare (excluding zero/None)
        priced = [j for j in journeys if (j.get("total_fare") or 0) > 0]
        if priced:
            cheapest = min(priced, key=lambda j: j["total_fare"])
            if "CHEAPEST" not in cheapest["tags"]:
                cheapest["tags"].append("CHEAPEST")

        # SAFEST: Highest reliability_score
        safest = max(
            journeys,
            key=lambda j: j.get("score", {}).get("reliability_score", 0)
        )
        if "SAFEST" not in safest["tags"]:
            safest["tags"].append("SAFEST")

        # FEWEST_CHANGES: Lowest num_connections
        fewest = min(journeys, key=lambda j: j.get("num_connections", float("inf")))
        if "FEWEST_CHANGES" not in fewest["tags"]:
            fewest["tags"].append("FEWEST_CHANGES")

        return journeys
