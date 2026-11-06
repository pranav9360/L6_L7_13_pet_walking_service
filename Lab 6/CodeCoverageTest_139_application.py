"""Lab 6 line coverage tests. D Pranav Sai, PES1UG24CS139."""

import pytest

from pet_walking_service import inspect_gps_collars, process_walking_routes


def route(walks, **options):
    return {"route_confirmed": True, "walks": walks, **options}


@pytest.mark.parametrize("routes,fee", [(None, 0), ({}, 0), ((), 0), ("routes", 0), ([], -0.01)])
def test_invalid_top_level_inputs(routes, fee):
    with pytest.raises(ValueError, match="^Invalid routes list or transport fee$"):
        process_walking_routes(routes, fee)


@pytest.mark.parametrize("session,fee", [("standard_60", 40.0), ("standard_30", 27.0), ("express_15", 19.0)])
def test_each_session_base_fee(session, fee):
    assert process_walking_routes([route([{"num_pets": 1}], session_type=session)], 5) == {
        "total_revenue": fee, "status": "COMPLETED"
    }


@pytest.mark.parametrize("pets,expected", [(1, 27.0), (3, 37.0), (4, 48.6), (5, 55.8)])
def test_pet_count_boundary(pets, expected):
    assert process_walking_routes([route([{"num_pets": pets}])], 0) == {
        "total_revenue": expected, "status": "COMPLETED"
    }


def test_multiple_routes_walks_medication_weekend_and_rounding():
    routes = [route([{"num_pets": 1, "needs_meds": True}, {"num_pets": 4}], is_weekend=True),
              route([{"num_pets": 1}], session_type="express_15")]
    assert process_walking_routes(routes, 5.125) == {"total_revenue": 105.72, "status": "COMPLETED"}


def test_skips_unconfirmed_and_invalid_sessions():
    routes = [{}, {"route_confirmed": False, "walks": None},
              route(None, session_type="unknown", is_weekend=True), route([{"num_pets": 1}])]
    assert process_walking_routes(routes, 10) == {"total_revenue": 27.0, "status": "COMPLETED"}


def test_nonpositive_and_missing_pet_counts_skip_medication():
    assert process_walking_routes([route([{}, {"num_pets": 0, "needs_meds": True},
                                               {"num_pets": -1}, {"num_pets": 1}])], 0) == {
        "total_revenue": 27.0, "status": "COMPLETED"
    }


@pytest.mark.parametrize("session", ["standard_30", "express_15"])
def test_short_aggressive_walk_can_still_charge_medication(session):
    assert process_walking_routes([route([{"num_pets": 4, "aggression_alert": True, "needs_meds": True}],
                                        session_type=session)], 0) == {
        "total_revenue": 6.0, "status": "COMPLETED"
    }


def test_long_aggressive_walk_cancels_previous_earnings_and_breaks():
    walks = [{"num_pets": 1}, {"num_pets": 1, "aggression_alert": True, "needs_meds": True}, None]
    assert process_walking_routes([route(walks, session_type="standard_60", is_weekend=True)], 5) == {
        "total_revenue": 5.0, "status": "COMPLETED"
    }


@pytest.mark.parametrize("count,status", [(4, "ZERO_EARNINGS"), (5, "INCIDENT_AUDIT")])
def test_incident_threshold_and_status_precedence(count, status):
    assert process_walking_routes([route([{"num_pets": 0}] * count)], 0) == {
        "total_revenue": 0.0, "status": status
    }


def test_audit_keeps_positive_revenue():
    assert process_walking_routes([route([{}] * 5 + [{"num_pets": 1}])], 0) == {
        "total_revenue": 27.0, "status": "INCIDENT_AUDIT"
    }


@pytest.mark.parametrize("routes", [[], [{}], [{"route_confirmed": True}], [route([])]])
def test_empty_or_skipped_work(routes):
    assert process_walking_routes(routes, 0) == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


@pytest.mark.parametrize("routes,fee,error", [
    ([None], 0, AttributeError), ([route([None])], 0, AttributeError),
    ([route(None)], 0, TypeError), ([route([{"num_pets": "1"}])], 0, TypeError), ([], None, TypeError),
])
def test_malformed_nested_inputs_propagate_native_errors(routes, fee, error):
    with pytest.raises(error):
        process_walking_routes(routes, fee)


@pytest.mark.parametrize("matrix,expected", [
    ([], "NO_DATA"), (None, "NO_DATA"), ([[]], "ONLINE"),
    ([[20]], "ONLINE"), ([[19]], "ONLINE"), ([[19, 19]], "LOST_SIGNAL_ALERT"),
    ([[0, 20, 0]], "ONLINE"), ([[19], [19]], "ONLINE"),
    ([[], [100, 19, 20], [19, 19]], "LOST_SIGNAL_ALERT"),
])
def test_gps_signals(matrix, expected):
    assert inspect_gps_collars(matrix) == expected


@pytest.mark.parametrize("matrix", [[None], [[None]], [["19"]]])
def test_malformed_gps_data_raises_type_error(matrix):
    with pytest.raises(TypeError):
        inspect_gps_collars(matrix)
