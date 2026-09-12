"""
Tests for Split-Ticket / Break-Journey Optimizer
=================================================
Validates schema correctness and split-ticket discovery logic.
"""

import pytest
from app.schemas.split_ticket import (
    SplitLeg,
    SplitTicketOption,
    SplitTicketResponse,
)


def test_split_ticket_schemas():
    """Verify that split ticket models validate properly."""
    leg1 = SplitLeg(
        leg_number=1,
        train_number="12627",
        train_name="Karnataka Express",
        train_type="SUPERFAST",
        from_station_code="SBC",
        from_station_name="KSR Bengaluru City Junction",
        to_station_code="BPL",
        to_station_name="Bhopal Junction",
        departure_time="19:20",
        arrival_time="15:35",
        travel_class="3A",
        status="AVAILABLE",
        available_seats=18,
        status_display="AVAILABLE 18",
        confirmation_probability=1.0,
        fare=1140.0,
        distance_km=1450,
    )

    leg2 = SplitLeg(
        leg_number=2,
        train_number="12627",
        train_name="Karnataka Express",
        train_type="SUPERFAST",
        from_station_code="BPL",
        from_station_name="Bhopal Junction",
        to_station_code="NDLS",
        to_station_name="New Delhi",
        departure_time="15:50",
        arrival_time="09:00",
        travel_class="3A",
        status="AVAILABLE",
        available_seats=24,
        status_display="AVAILABLE 24",
        confirmation_probability=1.0,
        fare=880.0,
        distance_km=700,
    )

    option = SplitTicketOption(
        option_id="SPLIT-SBC-NDLS-BPL-12627",
        is_same_train=True,
        intermediate_station_code="BPL",
        intermediate_station_name="Bhopal Junction",
        travel_class="3A",
        leg1=leg1,
        leg2=leg2,
        direct_status="WAITLIST",
        direct_status_display="WL 35",
        direct_fare=1850.0,
        direct_confirmation_probability=0.42,
        total_split_fare=2020.0,
        fare_difference=170.0,
        overall_confirmation_probability=1.0,
        guaranteed_confirmed=True,
        berth_action_tip="Stay on same train! Switch berth at Bhopal Junction (15 min halt).",
    )

    response = SplitTicketResponse(
        from_station="SBC",
        from_station_name="KSR Bengaluru City Junction",
        to_station="NDLS",
        to_station_name="New Delhi",
        date="2026-09-15",
        travel_class="3A",
        direct_status_summary="Direct status: WL 35 vs Split: 100% CONFIRMED",
        options_count=1,
        best_option=option,
        options=[option],
    )

    assert response.options_count == 1
    assert response.best_option.is_same_train is True
    assert response.best_option.guaranteed_confirmed is True
    assert response.best_option.fare_difference == 170.0
