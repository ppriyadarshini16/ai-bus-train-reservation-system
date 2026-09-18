"""
Intelligent Seat Allocation Module
------------------------------------
Part of the AI-Enabled Bus and Train Reservation System.

Allocates seats to passenger booking requests (individuals or groups)
across a bus/train coach, trying to:
  1. Keep groups seated together where possible.
  2. Honor seat-type preferences (window / aisle / any).
  3. Minimize wasted/fragmented seating (leftover single gaps).

Approach:
Greedy best-fit allocation.
- Seats are modeled as a flat list of seat objects, each with an id,
  a type ('window' or 'aisle'), and availability.
- Booking requests are sorted largest-group-first. This is the
  classic "best-fit decreasing" heuristic used in bin-packing style
  problems: placing the hardest-to-fit (largest) requests first
  leaves smaller, more flexible gaps for the smaller requests that
  follow, reducing fragmentation.
- For each request, we scan available seats and pick the smallest
  contiguous block of seats (by seat id/row) that fits the group
  and, if possible, matches the preferred seat type. "Smallest
  contiguous block that still fits" is the best-fit rule — it avoids
  breaking up large open blocks unnecessarily.
- If no contiguous block is available, falls back to allocating the
  best individually-matching seats one by one.

This greedy approach doesn't guarantee a globally optimal seating
plan (that would require solving a variant of bin packing, which is
NP-hard), but it runs fast and produces good, explainable results
for real-time booking — appropriate for a reservation system.
"""

from typing import List, Dict, Optional


class Seat:
    def __init__(self, seat_id: int, seat_type: str):
        self.seat_id = seat_id          # position/order in the coach
        self.seat_type = seat_type      # 'window' or 'aisle'
        self.is_booked = False


def allocate_seats(
    seats: List[Seat],
    requests: List[Dict],
) -> Dict[str, List[int]]:
    """
    Allocate seats to a list of booking requests.

    Args:
        seats: All seats in the coach, in physical row order.
        requests: List of dicts, each like:
                  {"passenger_id": "P1", "group_size": 3, "preference": "window"}
                  preference is optional ("window", "aisle", or None/"any").

    Returns:
        A dict mapping passenger_id -> list of allocated seat_ids.
        Passengers who couldn't be fully seated map to an empty list.
    """
    # Best-fit decreasing: handle largest groups first to reduce fragmentation.
    sorted_requests = sorted(requests, key=lambda r: r["group_size"], reverse=True)

    allocation: Dict[str, List[int]] = {}

    for req in sorted_requests:
        group_size = req["group_size"]
        preference = req.get("preference")
        best_block = _find_best_contiguous_block(seats, group_size, preference)

        if best_block:
            for seat in best_block:
                seat.is_booked = True
            allocation[req["passenger_id"]] = [s.seat_id for s in best_block]
        else:
            # Fallback: grab any individually available seats (may split the group).
            fallback = [s for s in seats if not s.is_booked][:group_size]
            for seat in fallback:
                seat.is_booked = True
            allocation[req["passenger_id"]] = [s.seat_id for s in fallback] if len(fallback) == group_size else []

    return allocation


def _find_best_contiguous_block(
    seats: List[Seat],
    group_size: int,
    preference: Optional[str],
) -> Optional[List[Seat]]:
    """
    Scan for the smallest contiguous run of free seats of at least
    `group_size`, preferring one that matches `preference` throughout.
    Returns the exact `group_size`-length slice to allocate, or None.
    """
    n = len(seats)
    best_start = None
    best_len = None
    best_matches_pref = False

    i = 0
    while i < n:
        if seats[i].is_booked:
            i += 1
            continue

        # Measure the run of free seats starting at i.
        j = i
        while j < n and not seats[j].is_booked:
            j += 1
        run_length = j - i

        if run_length >= group_size:
            matches_pref = preference in (None, "any") or all(
                seats[k].seat_type == preference for k in range(i, i + group_size)
            )
            # Prefer: (a) preference match, (b) smallest sufficient run (best-fit).
            is_better = best_start is None or (
                (matches_pref and not best_matches_pref)
                or (matches_pref == best_matches_pref and run_length < best_len)
            )
            if is_better:
                best_start, best_len, best_matches_pref = i, run_length, matches_pref

        i = j  # jump past this run (booked seat or end of run)

    if best_start is None:
        return None
    return seats[best_start:best_start + group_size]


if __name__ == "__main__":
    coach = [Seat(i, "window" if i % 2 == 0 else "aisle") for i in range(1, 21)]

    booking_requests = [
        {"passenger_id": "P1", "group_size": 2, "preference": "window"},
        {"passenger_id": "P2", "group_size": 4, "preference": "any"},
        {"passenger_id": "P3", "group_size": 1, "preference": "aisle"},
    ]

    result = allocate_seats(coach, booking_requests)
    print("Seat allocation:", result)
