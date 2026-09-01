"""
Services Package
=================
Contains the core intelligence of SmartRail:
- GraphBuilder: Builds the railway network as a time-dependent graph
- DijkstraRouter: Finds multi-train paths through the graph
- JourneyScorer: Ranks journeys using multi-criteria scoring
- JourneySearchService: Orchestrates the entire search pipeline
"""

from app.services.journey_service import JourneySearchService

__all__ = ["JourneySearchService"]
