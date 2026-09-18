# Foundation logical model

Identity is stored in `accounts`. Passenger and driver tables represent optional roles by reusing the account identifier as their primary key.

## `accounts`

| Column | Rule |
|---|---|
| `account_id` | Generated primary key. |
| `full_name` | Required synthetic name. |
| `phone_number` | Unique when present. |
| `email` | Unique when present. |
| `signup_at` | Account creation timestamp. |
| `account_status` | `ACTIVE`, `INACTIVE`, or `SUSPENDED`. |
| `last_seen_at` | Latest durable activity timestamp. |

At least one of `phone_number` or `email` must be present.

## `passengers`

| Column | Rule |
|---|---|
| `passenger_id` | Primary key and foreign key to `accounts.account_id`. |

The one-column role table prevents unrelated accounts from being referenced as passengers.

## `drivers`

| Column | Rule |
|---|---|
| `driver_id` | Primary key and foreign key to `accounts.account_id`. |
| `license_number` | Unique driver licence identifier. |
| `is_accepting_offers` | Driver-controlled availability flag. |

Current matching also depends on recent account activity, a usable vehicle, an application-held live location, and the absence of another active ride.

## `vehicles`

| Column | Rule |
|---|---|
| `vehicle_id` | Generated primary key. |
| `driver_id` | Foreign key to `drivers`. |
| `brand` | Manufacturer. |
| `model` | Vehicle model. |
| `model_year` | Year from 1886 through the current year. |
| `vehicle_category` | `ECONOMY`, `COMFORT`, or `PREMIUM`. |
| `plate_number` | Unique synthetic plate. |
| `service_status` | `ACTIVE`, `INACTIVE`, or `OUT_OF_SERVICE`. |
| `registered_at` | Service registration timestamp. |
| `retired_at` | Optional retirement timestamp after registration. |

`(driver_id, vehicle_id)` is unique so offers can use a composite foreign key that proves the selected vehicle belongs to the selected driver.

## `zones`

| Column | Rule |
|---|---|
| `zone_id` | Generated primary key. |
| `zone_name` | Unique together with `city_name`. |
| `city_name` | Supported city name. |
| `zone_type` | `RESIDENTIAL`, `COMMERCIAL`, `INDUSTRIAL`, `MIXED`, or `TRANSPORT_HUB`. |
| `center_latitude` | Decimal latitude between -90 and 90. |
| `center_longitude` | Decimal longitude between -180 and 180. |

## `zone_routes`

| Column | Rule |
|---|---|
| `origin_zone_id` | Foreign key and first part of the primary key. |
| `destination_zone_id` | Foreign key and second part of the primary key. |
| `baseline_distance_km` | Positive baseline distance. |
| `baseline_duration_minutes` | Positive baseline duration. |

Routes are directional: A-to-B and B-to-A are separate rows.

## Identity relationships

```text
accounts 1 ── 0..1 passengers
accounts 1 ── 0..1 drivers
drivers  1 ── many vehicles
```
