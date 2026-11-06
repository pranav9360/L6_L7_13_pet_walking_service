"""Independent decision and loop tests. D Pranav Sai, PES1UG24CS139."""

import pytest

from pet_walking_service import inspect_gps_collars, process_walking_routes


def confirmed(walks, **options):
    return {"route_confirmed": True, "walks": walks, **options}


@pytest.mark.parametrize("routes,fee", [(None, -1), ({}, 0), ((), 0), ([], -0.01)])
def test_validation_rejects_bad_routes_or_negative_fee(routes, fee):
    with pytest.raises(ValueError, match="^Invalid routes list or transport fee$"):
        process_walking_routes(routes, fee)


@pytest.mark.parametrize("routes,expected", [
    ([], 0.0), ([{}], 0.0), ([{"route_confirmed": False}], 0.0),
    ([{"route_confirmed": True}], 0.0),
    ([confirmed([{"num_pets": 1}])], 27.0),
    ([{}, confirmed([{"num_pets": 1}, {"num_pets": 2}]), confirmed([{"num_pets": 3}])], 96.0),
])
def test_route_and_walk_loops_zero_one_multiple(routes, expected):
    assert process_walking_routes(routes, 0) == {
        "total_revenue": expected, "status": "COMPLETED" if expected else "ZERO_EARNINGS"
    }


@pytest.mark.parametrize("session,pets,expected", [
    ("standard_60", 3, 50.0), ("standard_60", 4, 60.3),
    ("standard_30", 3, 37.0), ("standard_30", 4, 48.6),
    ("express_15", 3, 29.0), ("express_15", 4, 41.4),
])
@pytest.mark.parametrize("meds", [False, True])
def test_session_chain_pet_boundary_and_medication(session, pets, expected, meds):
    assert process_walking_routes([confirmed([{"num_pets": pets, "needs_meds": meds}],
                                            session_type=session)], 0) == {
        "total_revenue": round(expected + (6 if meds else 0), 2), "status": "COMPLETED"
    }


@pytest.mark.parametrize("session", ["unknown", "", None])
def test_invalid_session_skips_walks_and_weekend_fee(session):
    assert process_walking_routes([confirmed(None, session_type=session, is_weekend=True)], 99) == {
        "total_revenue": 0.0, "status": "ZERO_EARNINGS"
    }


@pytest.mark.parametrize("pets", [-1, 0])
def test_invalid_pet_count_continues_to_next_walk(pets):
    walks = [{"num_pets": pets, "aggression_alert": True, "needs_meds": True}, {}, {"num_pets": 1}]
    assert process_walking_routes([confirmed(walks)], 0) == {"total_revenue": 27.0, "status": "COMPLETED"}


@pytest.mark.parametrize("session", ["standard_30", "express_15"])
@pytest.mark.parametrize("meds,expected", [(False, 0.0), (True, 6.0)])
def test_short_session_aggression_does_not_break(session, meds, expected):
    walks = [{"num_pets": 4, "aggression_alert": True, "needs_meds": meds}]
    assert process_walking_routes([confirmed(walks, session_type=session)], 0) == {
        "total_revenue": expected, "status": "COMPLETED" if expected else "ZERO_EARNINGS"
    }


@pytest.mark.parametrize("weekend,fee,expected", [(False, 5, 0.0), (True, 0, 0.0), (True, 5, 5.0)])
def test_long_session_break_resets_earnings_but_weekend_still_applies(weekend, fee, expected):
    walks = [{"num_pets": 2}, {"num_pets": 1, "aggression_alert": True, "needs_meds": True}, None]
    routes = [confirmed(walks, session_type="standard_60", is_weekend=weekend)]
    assert process_walking_routes(routes, fee) == {
        "total_revenue": expected, "status": "COMPLETED" if expected else "ZERO_EARNINGS"
    }


def test_short_aggression_continues_and_route_incidents_accumulate():
    routes = [confirmed([{"num_pets": 1, "aggression_alert": True}, {"num_pets": 1}]),
              confirmed([{}] * 3), confirmed([], session_type="invalid")]
    assert process_walking_routes(routes, 0) == {"total_revenue": 27.0, "status": "INCIDENT_AUDIT"}


@pytest.mark.parametrize("incidents", [0, 4, 5])
@pytest.mark.parametrize("earning", [False, True])
def test_audit_and_zero_revenue_decisions(incidents, earning):
    walks = [{}] * incidents + ([{"num_pets": 1}] if earning else [])
    status = "INCIDENT_AUDIT" if incidents > 4 else ("COMPLETED" if earning else "ZERO_EARNINGS")
    assert process_walking_routes([confirmed(walks)], 0) == {
        "total_revenue": 27.0 if earning else 0.0, "status": status
    }


def test_empty_weekend_route_charges_transport_and_rounds():
    assert process_walking_routes([confirmed([], is_weekend=True)], 1.234) == {
        "total_revenue": 1.23, "status": "COMPLETED"
    }


@pytest.mark.parametrize("routes,fee,error", [
    ([None], 0, AttributeError), ([confirmed([None])], 0, AttributeError),
    ([confirmed(None)], 0, TypeError), ([confirmed([{"num_pets": None}])], 0, TypeError),
    ([], "0", TypeError),
])
def test_native_exception_paths(routes, fee, error):
    with pytest.raises(error):
        process_walking_routes(routes, fee)


@pytest.mark.parametrize("matrix,expected", [
    ([], "NO_DATA"), (None, "NO_DATA"), ([[]], "ONLINE"), ([[], []], "ONLINE"),
    ([[20]], "ONLINE"), ([[19]], "ONLINE"), ([[19, 20, 19]], "ONLINE"),
    ([[20, 21, 100]], "ONLINE"), ([[19, 19]], "LOST_SIGNAL_ALERT"),
    ([[19, 19, None]], "LOST_SIGNAL_ALERT"), ([[19], [19]], "ONLINE"),
    ([[], [19], [20, 19, 18]], "LOST_SIGNAL_ALERT"),
    ([[19, 20, 19, 19]], "LOST_SIGNAL_ALERT"),
])
def test_gps_threshold_streak_reset_and_nested_loop_outcomes(matrix, expected):
    assert inspect_gps_collars(matrix) == expected


@pytest.mark.parametrize("matrix", [[None], [[None]], [["20"]]])
def test_invalid_gps_elements(matrix):
    with pytest.raises(TypeError):
        inspect_gps_collars(matrix)
