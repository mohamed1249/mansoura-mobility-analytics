# Operational logical model

This document describes the seven operational tables after the six foundation tables. Many non-key fields are nullable. Status checks validate supplied values but do not establish a complete lifecycle, rating eligibility, payment settlement, or timestamp ordering.

## `offers`

An offer records one passenger contacting one driver before a ride exists.

| Column | Rule |
|---|---|
| `offer_id` | Generated primary key. |
| `passenger_id` | Foreign key to `passengers`. |
| `driver_id`, `vehicle_id` | Composite foreign key to a driver-owned vehicle. |
| `pickup_zone_id` | Foreign key to `zones`. |
| `dropoff_zone_id` | Foreign key to `zones` and different from pickup. |
| `initial_fare_egp` | Greater than 25 EGP when supplied; nullable. |
| `offer_status` | `PENDING`, `NEGOTIATING`, `ACCEPTED`, `DECLINED`, `WITHDRAWN`, or `AUTO_CANCELLED`. |
| `initiated_at` | Offer creation timestamp. |
| `declined_by` | `PASSENGER`, `DRIVER`, or `SYSTEM` when applicable. |
| `decided_at` | Decision timestamp for closed offers. |
| `decline_reason` | Reason for an unsuccessful offer. |

Accepted offers keep decline fields empty. Declined, withdrawn, and automatically cancelled offers require an actor and reason. Only `rides` references `offer_id`.

## `rides`

A ride represents an accepted offer.

| Column | Rule |
|---|---|
| `ride_id` | Generated primary key. |
| `offer_id` | Required unique foreign key to `offers`. |
| `final_fare_egp` | Non-negative settled fare when present. |
| `ride_status` | `AWAITING_PAYMENT`, `DRIVER_EN_ROUTE`, `READY_TO_START`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED_BEFORE_START`, or `TERMINATED_EARLY`. |
| `started_at` | Timezone-naive `TIMESTAMP` with a current-time default; not proof that a trip started. |
| `start_distance_metres` | Non-negative proximity measurement. |
| `completed_at` | Timezone-naive `TIMESTAMP` for completion or ending when present. |
| `cancelled_by` | `PASSENGER`, `DRIVER`, or `SYSTEM`. |
| `cancellation_reason` | Cancellation explanation. |
| `cancellation_stage` | `BEFORE_DRIVER_ARRIVAL`, `AFTER_DRIVER_ARRIVAL`, or `DURING_RIDE`. |

Ride milestone expansion and stricter lifecycle checks remain deferred. Acceptance of the referenced offer is an intended rule, not enforced by the current foreign key. The generator creates consistent records, but arbitrary database writes can violate it; notebook 03 demonstrates this gap.

## `payment_attempts`

| Column | Rule |
|---|---|
| `payment_attempt_id` | Generated primary key. |
| `ride_id` | Foreign key to `rides`. |
| `attempt_number` | Positive number unique within a ride. |
| `payment_method` | `CARD` or `WALLET`. |
| `payment_status` | `INITIATED`, `AUTHORIZED`, `FAILED`, `CAPTURED`, or `RELEASED`. |
| `requested_amount_egp` | Greater than 25 EGP when supplied; nullable. |
| `authorized_amount_egp` | Greater than 25 EGP when present. |
| `captured_amount_egp` | Greater than 25 EGP when present. |
| `provider_reference` | Unique payment-provider reference. |
| `failure_reason` | Required by the status check after failure. |
| `initiated_at` | Attempt creation timestamp. |
| `authorized_at` | Authorization timestamp. |
| `captured_at` | Capture timestamp. |
| `released_at` | Hold-release timestamp. |

## `refunds`

| Column | Rule |
|---|---|
| `refund_id` | Generated primary key. |
| `payment_attempt_id` | Foreign key to `payment_attempts`. |
| `refund_amount_egp` | Positive refund amount. |
| `refund_reason` | Refund explanation. |
| `refund_status` | `REQUESTED`, `PROCESSING`, `COMPLETED`, or `FAILED`. |
| `requested_at` | Request timestamp. |
| `completed_at` | Required by the status check after completion. |
| `failure_reason` | Required by the status check after failure. |

The total completed-refund amount cannot be enforced with a single row-level check because it depends on other rows and captured payment totals.

## `passenger_driver_ratings`

| Column | Rule |
|---|---|
| `ride_id` | Primary key and foreign key to `rides`. |
| `attitude_score` | Integer from 1 through 5 when supplied. |
| `driving_safety_score` | Integer from 1 through 5 when supplied. |
| `vehicle_cleanliness_score` | Integer from 1 through 5 when supplied. |
| `comfort_score` | Integer from 1 through 5 when supplied. |
| `route_quality_score` | Integer from 1 through 5 when supplied. |
| `submitted_at` | Submission timestamp. |
| `comment` | Optional text. |

The table direction identifies the passenger as author and the driver as subject; those identifiers are reached through the ride's offer rather than duplicated.

## `driver_passenger_ratings`

| Column | Rule |
|---|---|
| `ride_id` | Primary key and foreign key to `rides`. |
| `attitude_score` | Integer from 1 through 5 when supplied. |
| `punctuality_score` | Integer from 1 through 5 when supplied. |
| `pickup_cooperation_score` | Integer from 1 through 5 when supplied. |
| `respect_safety_score` | Integer from 1 through 5 when supplied. |
| `submitted_at` | Submission timestamp. |
| `comment` | Optional text. |

The table direction identifies the driver as author and the passenger as subject.

## `reports`

| Column | Rule |
|---|---|
| `report_id` | Generated primary key. |
| `ride_id` | Foreign key to `rides`. |
| `opened_by` | `PASSENGER`, `DRIVER`, or `SYSTEM`. |
| `report_category` | `PASSENGER_BEHAVIOR`, `DRIVER_BEHAVIOR`, `VEHICLE_ISSUE`, `PAYMENT_ISSUE`, or `OTHER`. |
| `other_report_category` | Custom category text when applicable. |
| `description` | Report description. |
| `report_status` | `OPEN`, `IN_PROGRESS`, `RESOLVED`, or `REJECTED`. |
| `opened_at` | Creation timestamp. |
| `resolved_at` | Resolution timestamp. |
| `resolution_notes` | Resolution details. |

A ride may have several reports. Reports do not change ride status and do not store refund amounts.
