# ai-bus-train-reservation-system
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
