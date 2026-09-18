# Business rules

## Scope

These are intended business rules, not a claim that every rule is enforced by the current schema. Notebook 03 records enforcement gaps. Matching, live locations, and payment-provider operations are simulated or conceptual; there is no deployed ride-hailing application.

Mansoura Mobility Analytics models a fictional ride marketplace around Mansoura, Talkha, and nearby areas in Dakahlia.

- An offer records one passenger contacting one driver about a route, vehicle, and initial fare.
- A ride is created only after an offer is accepted.
- A passenger may have one open offer and one active ride at a time.
- Driver offers are sequential in version one.
- Currency is Egyptian pound (`EGP`) with two decimal places.
- The intended convention is `TIMESTAMPTZ` with `Africa/Cairo` business time. The current `rides.started_at` and `rides.completed_at` columns use timezone-naive `TIMESTAMP`; timezone consistency remains a schema limitation.
- Names, contact details, and vehicle plates are synthetic.
- Version one excludes cash, simultaneous offers, street-level GIS, per-second GPS storage, promotions, surge pricing, and multiple currencies.

## Accounts and roles

- Identity is stored once in `accounts`.
- The same account may have a passenger role, a driver role, or both.
- Driver availability depends on account state, recent activity, willingness to accept offers, a usable vehicle, a known live location, and the absence of another active ride.
- Live driver positions remain in application memory during matching rather than being written to PostgreSQL every second.

## Offers

- Every offer identifies one passenger, driver, vehicle, pickup zone, drop-off zone, and initial fare.
- The displayed vehicle must belong to the selected driver.
- Offer statuses are `PENDING`, `NEGOTIATING`, `ACCEPTED`, `DECLINED`, `WITHDRAWN`, and `AUTO_CANCELLED`.
- Closed offers record a decision time.
- Declined, withdrawn, and automatically cancelled offers record the actor and reason.
- An unsuccessful offer creates no ride.
- Counteroffer history is not stored; only the initial offer and the final ride fare remain.
- Offline users and drivers who become busy can cause automatic cancellation.

## Rides

- One accepted offer creates at most one ride.
- Ride statuses are `AWAITING_PAYMENT`, `DRIVER_EN_ROUTE`, `READY_TO_START`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED_BEFORE_START`, and `TERMINATED_EARLY`.
- Terminal outcomes are `COMPLETED`, `CANCELLED_BEFORE_START`, and `TERMINATED_EARLY`.
- `FAILED` is a payment-attempt status, not a ride status.
- The trip starts only after payment authorization, passenger confirmation, and a simulated passenger-driver distance of at most 100 metres.
- Estimated distance, duration, and fare are not stored in version one.
- Actual trip distance and duration are not stored in the current schema; `start_distance_metres` measures passenger-driver proximity, not distance travelled.
- The normal minimum charge after a trip starts is `25.00 EGP` before later refunds.
- Reports remain separate from ride status.
- A separate ride-event history is not stored in version one.

## Cancellations

- Passenger or driver may cancel before the trip begins.
- A driver cancellation after acceptance but before start leaves a `CANCELLED_BEFORE_START` ride record.
- The driver receives nothing after a pre-start driver cancellation.
- Passenger funds are fully released when still held or fully refunded when already captured.
- Cancellation after `IN_PROGRESS` produces `TERMINATED_EARLY`, fare settlement, and possibly a report.
- Cancellation data includes the actor, stage, reason, and ending time where applicable.

Passenger reason codes include `CHANGE_OF_PLANS`, `DRIVER_TOO_FAR`, `WAIT_TOO_LONG`, `PRICE_DISAGREEMENT`, `VEHICLE_MISMATCH`, `SAFETY_CONCERN`, `DRIVER_BEHAVIOR`, and `WRONG_PICKUP`.

Driver reason codes include `PASSENGER_NO_SHOW`, `PASSENGER_BEHAVIOR`, `UNSAFE_PICKUP`, `VEHICLE_PROBLEM`, `EMERGENCY`, `PRICE_DISAGREEMENT`, and `UNABLE_TO_REACH_PICKUP`.

## Payments and refunds

- Version one supports card and wallet payments.
- Payment must be authorized before a trip begins.
- A ride may have multiple payment attempts.
- A completed ride cannot remain unpaid.
- A refund is stored separately from the original payment attempt.
- Completed refunds cannot exceed captured funds.
- Driver payout tracking is postponed from the first implemented schema.

## Ratings and reports

- Passenger and driver may rate each other after a trip reaches `IN_PROGRESS`.
- Each direction may submit at most one rating row per ride.
- Rating dimensions use integers from 1 through 5.
- Ratings are not edited in version one.
- A missing rating is represented by the absence of a rating row.
- A ride may have several reports.
- Reports support passenger, driver, and system initiation.

## Zones and routes

- Pickup and drop-off zones differ for an offer in the implemented schema.
- Route baselines are directional; A-to-B and B-to-A may differ.
- Each ordered zone pair has at most one stored baseline distance and duration.
- Missing route baselines cause data generation to fail instead of inventing unrelated values.

## Core invariants

1. Every role references an existing account.
2. Every vehicle references an existing driver.
3. Every offer references one valid passenger and one driver-owned vehicle.
4. An offer may exist without a ride; a ride cannot exist without an offer.
5. One offer creates at most one ride.
6. A trip cannot start without an accepted offer and authorized payment.
7. Monetary amounts, distances, and durations cannot be negative.
8. Rating scores remain between 1 and 5.
9. Payment attempt numbers do not repeat within a ride.
10. Provider payment references are unique.
11. Refunds reference payment attempts.
12. Each ordered zone pair has at most one route baseline.

Rules that depend on other rows or lifecycle transitions require transactions, partial indexes, controlled functions, or triggers rather than ordinary row-level checks.
