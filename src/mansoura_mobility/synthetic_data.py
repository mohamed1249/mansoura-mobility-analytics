"""Deterministic synthetic data for the Mansoura mobility database."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import asin, cos, radians, sin, sqrt
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd


CAIRO = ZoneInfo("Africa/Cairo")

TABLE_ORDER = (
    "accounts",
    "passengers",
    "drivers",
    "zones",
    "vehicles",
    "zone_routes",
    "offers",
    "rides",
    "payment_attempts",
    "refunds",
    "passenger_driver_ratings",
    "driver_passenger_ratings",
    "reports",
)

SERIAL_COLUMNS = {
    "accounts": "account_id",
    "zones": "zone_id",
    "vehicles": "vehicle_id",
    "offers": "offer_id",
    "rides": "ride_id",
    "payment_attempts": "payment_attempt_id",
    "refunds": "refund_id",
    "reports": "report_id",
}


@dataclass(frozen=True)
class SimulationConfig:
    seed: int = 20260830
    passenger_count: int = 1_000
    driver_count: int = 100
    dual_role_count: int = 20
    offer_count: int = 14_000
    simulation_days: int = 180
    simulation_end: str = "2026-08-30T23:59:00+03:00"

    def __post_init__(self) -> None:
        if self.passenger_count < 1:
            raise ValueError("passenger_count must be positive")
        if self.driver_count < 1:
            raise ValueError("driver_count must be positive")
        if not 0 <= self.dual_role_count <= min(
            self.passenger_count, self.driver_count
        ):
            raise ValueError("dual_role_count exceeds the available roles")
        if self.offer_count < 1:
            raise ValueError("offer_count must be positive")
        if self.simulation_days < 1:
            raise ValueError("simulation_days must be positive")


@dataclass
class SyntheticDataset:
    tables: dict[str, pd.DataFrame]
    config: SimulationConfig
    metadata: dict[str, Any]

    def counts(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"table_name": table, "rows": len(self.tables[table])}
                for table in TABLE_ORDER
            ]
        )


FIRST_NAMES = (
    "Ahmed",
    "Mohamed",
    "Mahmoud",
    "Mostafa",
    "Omar",
    "Youssef",
    "Karim",
    "Hassan",
    "Ibrahim",
    "Khaled",
    "Tarek",
    "Amr",
    "Mina",
    "Aya",
    "Mariam",
    "Nour",
    "Salma",
    "Hana",
    "Farah",
    "Dina",
    "Esraa",
    "Menna",
    "Reem",
    "Nada",
)

LAST_NAMES = (
    "El Sayed",
    "Hassan",
    "Mahmoud",
    "Ibrahim",
    "Abdelrahman",
    "Fathy",
    "Gaber",
    "Soliman",
    "Kamel",
    "Rashad",
    "Amin",
    "Saad",
    "Hamdy",
    "Nassar",
    "Shalaby",
    "Badawy",
    "El Masry",
    "Ashour",
)

ZONE_ROWS = (
    (1, "Mansoura University", "Mansoura", "MIXED", 31.043100, 31.356700, 1.55),
    (2, "El Gomhoria", "Mansoura", "COMMERCIAL", 31.041800, 31.367300, 1.45),
    (3, "El Mashaya", "Mansoura", "MIXED", 31.047000, 31.365000, 1.35),
    (4, "Toriel", "Mansoura", "RESIDENTIAL", 31.036000, 31.383000, 1.05),
    (5, "Gedila", "Mansoura", "RESIDENTIAL", 31.027500, 31.403000, 0.90),
    (6, "Sandoub", "Mansoura", "INDUSTRIAL", 31.021000, 31.392000, 0.80),
    (7, "El Mokhtalat", "Mansoura", "MIXED", 31.036500, 31.375000, 1.25),
    (8, "El Hosayneya", "Mansoura", "RESIDENTIAL", 31.048500, 31.390000, 1.00),
    (9, "Mansoura Railway Station", "Mansoura", "TRANSPORT_HUB", 31.041000, 31.391000, 1.35),
    (10, "Mit Khamis", "Mansoura", "RESIDENTIAL", 31.011500, 31.360000, 0.75),
    (11, "Talkha Center", "Talkha", "MIXED", 31.053900, 31.377900, 1.05),
    (12, "Talkha Old Market", "Talkha", "COMMERCIAL", 31.054800, 31.383500, 0.90),
    (13, "El Mohandessin", "Talkha", "RESIDENTIAL", 31.061000, 31.373000, 0.80),
    (14, "Talkha Railway Station", "Talkha", "TRANSPORT_HUB", 31.057000, 31.380000, 0.85),
    (15, "El Rowda", "Talkha", "RESIDENTIAL", 31.050000, 31.368000, 0.75),
)

VEHICLE_PROFILES = (
    ("Chevrolet", "Aveo", "ECONOMY", 0.13),
    ("Chevrolet", "Optra", "ECONOMY", 0.12),
    ("Nissan", "Sunny", "ECONOMY", 0.18),
    ("Hyundai", "Verna", "ECONOMY", 0.10),
    ("Hyundai", "Accent", "COMFORT", 0.10),
    ("Kia", "Cerato", "COMFORT", 0.10),
    ("Toyota", "Corolla", "COMFORT", 0.12),
    ("Renault", "Logan", "ECONOMY", 0.08),
    ("Skoda", "Octavia", "PREMIUM", 0.04),
    ("Mercedes", "C180", "PREMIUM", 0.03),
)


def _simulation_bounds(config: SimulationConfig) -> tuple[datetime, datetime]:
    end = datetime.fromisoformat(config.simulation_end).astimezone(CAIRO)
    start = (end - timedelta(days=config.simulation_days - 1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return start, end


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    return radius * 2 * asin(sqrt(a))


def _clip_score(value: float) -> int:
    return int(np.clip(np.rint(value), 1, 5))


def _local_naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.astimezone(CAIRO).replace(tzinfo=None)


def _generate_accounts(
    config: SimulationConfig, rng: np.random.Generator
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    start, end = _simulation_bounds(config)
    total_accounts = (
        config.passenger_count + config.driver_count - config.dual_role_count
    )
    passenger_ids = np.arange(1, config.passenger_count + 1, dtype=int)
    driver_start = config.passenger_count - config.dual_role_count + 1
    driver_ids = np.arange(
        driver_start, driver_start + config.driver_count, dtype=int
    )

    account_rows: list[dict[str, Any]] = []
    passenger_activity: dict[int, float] = {}
    passenger_reliability: dict[int, float] = {}
    passenger_courtesy: dict[int, float] = {}
    passenger_home_zone: dict[int, int] = {}

    first_names = rng.choice(FIRST_NAMES, size=total_accounts)
    last_names = rng.choice(LAST_NAMES, size=total_accounts)
    signup_days = rng.integers(30, 900, size=total_accounts)
    signup_seconds = rng.integers(0, 86_400, size=total_accounts)

    for index, account_id in enumerate(range(1, total_accounts + 1)):
        full_name = f"{first_names[index]} {last_names[index]}"
        status = str(
            rng.choice(
                ["ACTIVE", "INACTIVE", "SUSPENDED"], p=[0.91, 0.075, 0.015]
            )
        )
        signup_at = start - timedelta(
            days=int(signup_days[index]), seconds=int(signup_seconds[index])
        )
        if status == "ACTIVE":
            inactive_days = float(rng.exponential(5.5))
        elif status == "INACTIVE":
            inactive_days = float(rng.uniform(30, 180))
        else:
            inactive_days = float(rng.uniform(10, 120))
        last_seen_at = end - timedelta(days=inactive_days)
        prefix = str(rng.choice(["010", "011", "012", "015"]))
        phone = f"{prefix}{account_id:08d}"
        email_stem = f"{str(first_names[index]).lower()}.{str(last_names[index]).lower().replace(' ', '')}"
        email = f"{email_stem}.{account_id}@example.test"
        account_rows.append(
            {
                "account_id": account_id,
                "full_name": full_name,
                "phone_number": phone,
                "email": email,
                "signup_at": signup_at,
                "account_status": status,
                "last_seen_at": last_seen_at,
            }
        )

    zone_ids = np.array([row[0] for row in ZONE_ROWS], dtype=int)
    zone_weights = np.array([row[6] for row in ZONE_ROWS], dtype=float)
    zone_weights /= zone_weights.sum()
    for passenger_id in passenger_ids:
        passenger_activity[int(passenger_id)] = float(rng.lognormal(-0.1, 0.75))
        passenger_reliability[int(passenger_id)] = float(rng.beta(9.0, 1.7))
        passenger_courtesy[int(passenger_id)] = float(
            1 + 4 * rng.beta(8.0, 1.8)
        )
        passenger_home_zone[int(passenger_id)] = int(
            rng.choice(zone_ids, p=zone_weights)
        )

    driver_quality: dict[int, float] = {}
    driver_acceptance: dict[int, float] = {}
    driver_home_zone: dict[int, int] = {}
    driver_rows: list[dict[str, Any]] = []
    account_status_by_id = {
        row["account_id"]: row["account_status"] for row in account_rows
    }
    for driver_id in driver_ids:
        driver_id = int(driver_id)
        driver_quality[driver_id] = float(1 + 4 * rng.beta(8.5, 1.6))
        driver_acceptance[driver_id] = float(rng.beta(7.0, 2.2))
        driver_home_zone[driver_id] = int(rng.choice(zone_ids, p=zone_weights))
        accepts_now = (
            account_status_by_id[driver_id] == "ACTIVE" and rng.random() < 0.72
        )
        driver_rows.append(
            {
                "driver_id": driver_id,
                "license_number": f"DKH-L-{driver_id:06d}",
                "is_accepting_offers": bool(accepts_now),
            }
        )

    metadata = {
        "passenger_ids": passenger_ids.tolist(),
        "driver_ids": driver_ids.tolist(),
        "passenger_activity": passenger_activity,
        "passenger_reliability": passenger_reliability,
        "passenger_courtesy": passenger_courtesy,
        "passenger_home_zone": passenger_home_zone,
        "driver_quality": driver_quality,
        "driver_acceptance": driver_acceptance,
        "driver_home_zone": driver_home_zone,
    }
    return (
        pd.DataFrame(account_rows),
        pd.DataFrame({"passenger_id": passenger_ids}),
        pd.DataFrame(driver_rows),
        metadata,
    )


def _generate_zones_and_routes(
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    zones = pd.DataFrame(
        [
            {
                "zone_id": row[0],
                "zone_name": row[1],
                "city_name": row[2],
                "zone_type": row[3],
                "center_latitude": row[4],
                "center_longitude": row[5],
            }
            for row in ZONE_ROWS
        ]
    )
    route_rows: list[dict[str, Any]] = []
    route_lookup: dict[tuple[int, int], tuple[float, float]] = {}
    zone_lookup = {row[0]: row for row in ZONE_ROWS}
    for origin in zone_lookup:
        for destination in zone_lookup:
            if origin == destination:
                continue
            origin_row = zone_lookup[origin]
            destination_row = zone_lookup[destination]
            direct_distance = _haversine_km(
                origin_row[4], origin_row[5], destination_row[4], destination_row[5]
            )
            road_factor = float(rng.uniform(1.28, 1.58))
            directional_factor = 1 + 0.04 * sin(origin * 1.7 + destination)
            distance = max(0.55, direct_distance * road_factor * directional_factor)
            avg_speed = float(rng.uniform(18, 29))
            duration = 3.2 + (distance / avg_speed) * 60
            if origin_row[3] in {"COMMERCIAL", "TRANSPORT_HUB"}:
                duration *= 1.08
            distance = round(distance, 2)
            duration = round(max(4.0, duration), 2)
            route_rows.append(
                {
                    "origin_zone_id": origin,
                    "destination_zone_id": destination,
                    "baseline_distance_km": distance,
                    "baseline_duration_minutes": duration,
                }
            )
            route_lookup[(origin, destination)] = (distance, duration)

    zone_metadata = {
        "zone_types": {row[0]: row[3] for row in ZONE_ROWS},
        "zone_weights": {row[0]: row[6] for row in ZONE_ROWS},
        "route_lookup": route_lookup,
    }
    return zones, pd.DataFrame(route_rows), zone_metadata


def _generate_vehicles(
    drivers: pd.DataFrame,
    accounts: pd.DataFrame,
    config: SimulationConfig,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    simulation_start, simulation_end = _simulation_bounds(config)
    profiles = list(VEHICLE_PROFILES)
    profile_weights = np.array([profile[3] for profile in profiles], dtype=float)
    profile_weights /= profile_weights.sum()
    signup_lookup = accounts.set_index("account_id")["signup_at"].to_dict()
    vehicle_rows: list[dict[str, Any]] = []
    primary_vehicle: dict[int, int] = {}
    vehicle_quality: dict[int, float] = {}
    vehicle_category: dict[int, str] = {}
    vehicle_id = 1

    for driver_id in drivers["driver_id"].astype(int):
        vehicle_total = 2 if rng.random() < 0.24 else 1
        for vehicle_number in range(vehicle_total):
            profile_index = int(rng.choice(len(profiles), p=profile_weights))
            brand, model, category, _ = profiles[profile_index]
            if category == "PREMIUM":
                model_year = int(rng.integers(2014, 2026))
            elif category == "COMFORT":
                model_year = int(rng.integers(2011, 2026))
            else:
                model_year = int(rng.integers(2007, 2025))
            registered_at = min(
                signup_lookup[driver_id] + timedelta(days=int(rng.integers(1, 60))),
                simulation_start - timedelta(days=1),
            )
            service_status = "ACTIVE"
            retired_at = None
            if vehicle_number > 0 and rng.random() < 0.28:
                service_status = str(
                    rng.choice(["INACTIVE", "OUT_OF_SERVICE"], p=[0.7, 0.3])
                )
                if service_status == "INACTIVE" and rng.random() < 0.45:
                    retired_at = min(
                        registered_at + timedelta(days=int(rng.integers(300, 1_500))),
                        simulation_end - timedelta(days=1),
                    )
            vehicle_rows.append(
                {
                    "vehicle_id": vehicle_id,
                    "driver_id": driver_id,
                    "brand": brand,
                    "model": model,
                    "model_year": model_year,
                    "vehicle_category": category,
                    "plate_number": f"DKH-{vehicle_id:05d}",
                    "service_status": service_status,
                    "registered_at": registered_at,
                    "retired_at": retired_at,
                }
            )
            age_penalty = max(0, 2026 - model_year) * 0.035
            category_bonus = {"ECONOMY": 0.0, "COMFORT": 0.2, "PREMIUM": 0.35}[
                category
            ]
            vehicle_quality[vehicle_id] = float(
                np.clip(rng.normal(4.25 + category_bonus - age_penalty, 0.25), 1, 5)
            )
            vehicle_category[vehicle_id] = category
            if vehicle_number == 0:
                primary_vehicle[driver_id] = vehicle_id
            vehicle_id += 1

    return pd.DataFrame(vehicle_rows), {
        "primary_vehicle": primary_vehicle,
        "vehicle_quality": vehicle_quality,
        "vehicle_category": vehicle_category,
    }


def _event_times(
    config: SimulationConfig, rng: np.random.Generator
) -> list[datetime]:
    start, end = _simulation_bounds(config)
    day_indices = np.arange(config.simulation_days)
    trend = np.linspace(0.82, 1.18, config.simulation_days)
    weekdays = np.array(
        [(start + timedelta(days=int(day))).weekday() for day in day_indices]
    )
    day_factor = np.where(weekdays == 3, 1.12, 1.0)
    day_factor = np.where(weekdays == 4, 1.18, day_factor)
    day_factor = np.where(weekdays == 5, 1.08, day_factor)
    day_probabilities = trend * day_factor
    day_probabilities /= day_probabilities.sum()

    hour_weights = np.array(
        [
            0.20,
            0.12,
            0.08,
            0.06,
            0.08,
            0.18,
            0.45,
            0.85,
            1.20,
            1.05,
            0.85,
            0.80,
            0.88,
            0.92,
            0.95,
            1.05,
            1.30,
            1.55,
            1.65,
            1.50,
            1.25,
            0.95,
            0.65,
            0.38,
        ],
        dtype=float,
    )
    hour_weights /= hour_weights.sum()
    days = rng.choice(day_indices, size=config.offer_count, p=day_probabilities)
    hours = rng.choice(np.arange(24), size=config.offer_count, p=hour_weights)
    minutes = rng.integers(0, 60, size=config.offer_count)
    seconds = rng.integers(0, 60, size=config.offer_count)
    values = [
        start
        + timedelta(
            days=int(day),
            hours=int(hour),
            minutes=int(minute),
            seconds=int(second),
        )
        for day, hour, minute, second in zip(days, hours, minutes, seconds)
    ]
    return sorted(min(value, end) for value in values)


def _zone_probabilities(
    zone_types: dict[int, str],
    zone_weights: dict[int, float],
    hour: int,
    purpose: str,
) -> tuple[np.ndarray, np.ndarray]:
    zone_ids = np.array(sorted(zone_types), dtype=int)
    weights = np.array([zone_weights[int(zone_id)] for zone_id in zone_ids])
    for index, zone_id in enumerate(zone_ids):
        zone_type = zone_types[int(zone_id)]
        if purpose == "pickup":
            if 6 <= hour <= 10 and zone_type == "RESIDENTIAL":
                weights[index] *= 1.55
            if 16 <= hour <= 21 and zone_type in {"COMMERCIAL", "MIXED"}:
                weights[index] *= 1.40
            if hour >= 22 and zone_type == "TRANSPORT_HUB":
                weights[index] *= 1.35
        else:
            if 6 <= hour <= 11 and zone_type in {"COMMERCIAL", "MIXED"}:
                weights[index] *= 1.50
            if 16 <= hour <= 23 and zone_type == "RESIDENTIAL":
                weights[index] *= 1.55
            if zone_type == "TRANSPORT_HUB":
                weights[index] *= 1.15
    weights /= weights.sum()
    return zone_ids, weights


def _traffic_multiplier(timestamp: datetime) -> float:
    hour = timestamp.hour
    if 7 <= hour <= 10 or 16 <= hour <= 20:
        return 1.35
    if hour >= 23 or hour <= 5:
        return 0.82
    return 1.0


def _offer_failure(
    rng: np.random.Generator,
) -> tuple[str, str, str]:
    status = str(
        rng.choice(["DECLINED", "WITHDRAWN", "AUTO_CANCELLED"], p=[0.57, 0.25, 0.18])
    )
    if status == "DECLINED":
        actor = str(rng.choice(["DRIVER", "PASSENGER"], p=[0.82, 0.18]))
        reason = str(
            rng.choice(
                [
                    "PRICE_DISAGREEMENT",
                    "DRIVER_TOO_FAR",
                    "UNABLE_TO_REACH_PICKUP",
                    "CHANGE_OF_PLANS",
                ],
                p=[0.47, 0.18, 0.22, 0.13],
            )
        )
    elif status == "WITHDRAWN":
        actor = str(rng.choice(["PASSENGER", "DRIVER"], p=[0.90, 0.10]))
        reason = str(
            rng.choice(
                ["CHANGE_OF_PLANS", "WAIT_TOO_LONG", "PRICE_DISAGREEMENT"],
                p=[0.40, 0.35, 0.25],
            )
        )
    else:
        actor = "SYSTEM"
        reason = str(
            rng.choice(
                ["USER_OFFLINE_TIMEOUT", "DRIVER_BECAME_BUSY"], p=[0.62, 0.38]
            )
        )
    return status, actor, reason


def _generate_offers_and_rides(
    config: SimulationConfig,
    metadata: dict[str, Any],
    zone_metadata: dict[str, Any],
    vehicle_metadata: dict[str, Any],
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    _, simulation_end = _simulation_bounds(config)
    passenger_ids = np.array(metadata["passenger_ids"], dtype=int)
    driver_ids = np.array(metadata["driver_ids"], dtype=int)
    passenger_activity = metadata["passenger_activity"]
    passenger_home_zone = metadata["passenger_home_zone"]
    driver_quality = metadata["driver_quality"]
    driver_acceptance = metadata["driver_acceptance"]
    route_lookup = zone_metadata["route_lookup"]
    zone_types = zone_metadata["zone_types"]
    zone_weights = zone_metadata["zone_weights"]
    primary_vehicle = vehicle_metadata["primary_vehicle"]
    vehicle_category = vehicle_metadata["vehicle_category"]

    passenger_free_at = {int(value): datetime.min.replace(tzinfo=CAIRO) for value in passenger_ids}
    driver_free_at = {int(value): datetime.min.replace(tzinfo=CAIRO) for value in driver_ids}
    driver_zone = dict(metadata["driver_home_zone"])
    driver_completed = {int(value): 0 for value in driver_ids}

    activity_weights = np.array(
        [passenger_activity[int(value)] for value in passenger_ids], dtype=float
    )
    offer_rows: list[dict[str, Any]] = []
    ride_rows: list[dict[str, Any]] = []
    ride_context: dict[int, dict[str, Any]] = {}
    ride_id = 1

    for initiated_at in _event_times(config, rng):
        free_passenger_mask = np.array(
            [passenger_free_at[int(value)] <= initiated_at for value in passenger_ids]
        )
        free_passengers = passenger_ids[free_passenger_mask]
        if len(free_passengers) == 0:
            continue
        free_passenger_weights = activity_weights[free_passenger_mask]
        free_passenger_weights /= free_passenger_weights.sum()
        passenger_id = int(rng.choice(free_passengers, p=free_passenger_weights))

        pickup_zone_ids, pickup_probabilities = _zone_probabilities(
            zone_types, zone_weights, initiated_at.hour, "pickup"
        )
        if rng.random() < 0.52:
            pickup_zone_id = passenger_home_zone[passenger_id]
        else:
            pickup_zone_id = int(
                rng.choice(pickup_zone_ids, p=pickup_probabilities)
            )
        dropoff_zone_ids, dropoff_probabilities = _zone_probabilities(
            zone_types, zone_weights, initiated_at.hour, "dropoff"
        )
        dropoff_probabilities = dropoff_probabilities.copy()
        dropoff_probabilities[dropoff_zone_ids == pickup_zone_id] = 0
        dropoff_probabilities /= dropoff_probabilities.sum()
        dropoff_zone_id = int(
            rng.choice(dropoff_zone_ids, p=dropoff_probabilities)
        )

        free_drivers = [
            int(driver_id)
            for driver_id in driver_ids
            if driver_free_at[int(driver_id)] <= initiated_at
        ]
        if not free_drivers:
            continue
        requested_category = str(
            rng.choice(["ECONOMY", "COMFORT", "PREMIUM"], p=[0.78, 0.18, 0.04])
        )
        candidates: list[tuple[float, int, float]] = []
        for driver_id in free_drivers:
            current_zone = driver_zone[driver_id]
            if current_zone == pickup_zone_id:
                pickup_distance = float(rng.uniform(0.35, 1.20))
            else:
                pickup_distance = route_lookup[(current_zone, pickup_zone_id)][0]
            candidates.append((pickup_distance, driver_id, driver_quality[driver_id]))
        candidates.sort(key=lambda value: value[0])
        nearby = candidates[: min(10, len(candidates))]
        utilities = np.array(
            [
                -0.52 * distance
                + 0.60 * (quality - 4.0)
                + 0.08 * np.log1p(driver_completed[driver_id])
                + (
                    0.34
                    if vehicle_category[primary_vehicle[driver_id]] == requested_category
                    else -0.16
                )
                + rng.normal(0, 0.18)
                for distance, driver_id, quality in nearby
            ]
        )
        utility_probabilities = np.exp(utilities - utilities.max())
        utility_probabilities /= utility_probabilities.sum()
        selected_index = int(rng.choice(len(nearby), p=utility_probabilities))
        driver_pickup_distance, driver_id, _ = nearby[selected_index]
        vehicle_id = primary_vehicle[driver_id]

        route_distance, route_duration = route_lookup[
            (pickup_zone_id, dropoff_zone_id)
        ]
        traffic = _traffic_multiplier(initiated_at)
        category_factor = {
            "ECONOMY": 1.0,
            "COMFORT": 1.18,
            "PREMIUM": 1.45,
        }[vehicle_category[vehicle_id]]
        base_fare = 18 + 8.7 * route_distance + 0.62 * route_duration * traffic
        price_ratio = float(np.clip(rng.normal(0.93, 0.07), 0.78, 1.10))
        initial_fare = round(max(30.0, base_fare * price_ratio * category_factor) / 5) * 5
        acceptance_signal = (
            1.00
            + 3.10 * (price_ratio - 0.90)
            + 1.20 * (driver_acceptance[driver_id] - 0.65)
            - 0.075 * driver_pickup_distance
            - (0.18 if initiated_at.hour <= 5 else 0)
        )
        acceptance_probability = 1 / (1 + np.exp(-acceptance_signal))

        offer_id = len(offer_rows) + 1
        is_open_tail = initiated_at >= simulation_end - timedelta(minutes=12)
        if is_open_tail and rng.random() < 0.32:
            offer_status = str(rng.choice(["PENDING", "NEGOTIATING"], p=[0.65, 0.35]))
            decided_at = None
            declined_by = None
            decline_reason = None
            passenger_free_at[passenger_id] = simulation_end
            driver_free_at[driver_id] = simulation_end
        elif rng.random() > acceptance_probability:
            offer_status, declined_by, decline_reason = _offer_failure(rng)
            decided_at = initiated_at + timedelta(
                seconds=int(rng.integers(35, 330))
            )
            passenger_free_at[passenger_id] = decided_at
            driver_free_at[driver_id] = decided_at
        else:
            offer_status = "ACCEPTED"
            declined_by = None
            decline_reason = None
            decided_at = initiated_at + timedelta(
                seconds=int(rng.integers(35, 280))
            )

            pickup_minutes = max(
                2.0,
                (driver_pickup_distance / float(rng.uniform(17, 27))) * 60
                + float(rng.uniform(1, 4)),
            )
            driver_arrival = decided_at + timedelta(minutes=pickup_minutes)
            trip_start = driver_arrival + timedelta(minutes=float(rng.uniform(1, 5)))
            planned_duration = route_duration * traffic * float(rng.uniform(0.88, 1.18))
            planned_end = trip_start + timedelta(minutes=planned_duration)

            cancellation_roll = rng.random()
            if simulation_end < decided_at + timedelta(minutes=2):
                ride_status = "AWAITING_PAYMENT"
                ride_end = None
            elif simulation_end < driver_arrival:
                ride_status = "DRIVER_EN_ROUTE"
                ride_end = None
            elif simulation_end < trip_start:
                ride_status = "READY_TO_START"
                ride_end = None
            elif simulation_end < planned_end:
                ride_status = "IN_PROGRESS"
                ride_end = None
            elif cancellation_roll < 0.055:
                ride_status = "CANCELLED_BEFORE_START"
                ride_end = decided_at + timedelta(
                    minutes=float(rng.uniform(1, max(2.0, pickup_minutes + 1)))
                )
            elif cancellation_roll < 0.085:
                ride_status = "TERMINATED_EARLY"
                ride_end = trip_start + timedelta(
                    minutes=planned_duration * float(rng.uniform(0.12, 0.75))
                )
            else:
                ride_status = "COMPLETED"
                ride_end = planned_end

            final_fare: float | None
            cancellation_actor: str | None = None
            cancellation_reason: str | None = None
            cancellation_stage: str | None = None
            start_distance: float | None = None

            if ride_status in {"COMPLETED", "TERMINATED_EARLY", "IN_PROGRESS"}:
                start_distance = round(float(np.clip(rng.gamma(2.2, 14), 3, 98)), 2)
            if ride_status == "COMPLETED":
                final_fare = round(max(30.0, initial_fare * rng.normal(1.015, 0.025)), 2)
                driver_completed[driver_id] += 1
                driver_zone[driver_id] = dropoff_zone_id
            elif ride_status == "TERMINATED_EARLY":
                completion_share = max(
                    0.15,
                    (ride_end - trip_start).total_seconds()
                    / max(1, (planned_end - trip_start).total_seconds()),
                )
                final_fare = round(max(30.0, initial_fare * completion_share), 2)
                cancellation_actor = str(
                    rng.choice(["PASSENGER", "DRIVER", "SYSTEM"], p=[0.62, 0.30, 0.08])
                )
                cancellation_reason = str(
                    rng.choice(
                        [
                            "SAFETY_CONCERN",
                            "VEHICLE_PROBLEM",
                            "PASSENGER_BEHAVIOR",
                            "DRIVER_BEHAVIOR",
                            "EMERGENCY",
                        ]
                    )
                )
                cancellation_stage = "DURING_RIDE"
                driver_zone[driver_id] = dropoff_zone_id
            elif ride_status == "CANCELLED_BEFORE_START":
                final_fare = 0.0
                cancellation_actor = str(
                    rng.choice(["PASSENGER", "DRIVER", "SYSTEM"], p=[0.56, 0.39, 0.05])
                )
                if cancellation_actor == "PASSENGER":
                    cancellation_reason = str(
                        rng.choice(
                            [
                                "CHANGE_OF_PLANS",
                                "WAIT_TOO_LONG",
                                "VEHICLE_MISMATCH",
                                "WRONG_PICKUP",
                            ]
                        )
                    )
                elif cancellation_actor == "DRIVER":
                    cancellation_reason = str(
                        rng.choice(
                            [
                                "PASSENGER_NO_SHOW",
                                "UNSAFE_PICKUP",
                                "VEHICLE_PROBLEM",
                                "EMERGENCY",
                            ]
                        )
                    )
                else:
                    cancellation_reason = "SYSTEM_CANCELLATION"
                cancellation_stage = (
                    "BEFORE_DRIVER_ARRIVAL"
                    if ride_end < driver_arrival
                    else "AFTER_DRIVER_ARRIVAL"
                )
                if ride_end >= driver_arrival:
                    driver_zone[driver_id] = pickup_zone_id
            else:
                final_fare = None

            busy_until = ride_end or simulation_end
            passenger_free_at[passenger_id] = busy_until
            driver_free_at[driver_id] = busy_until
            ride_rows.append(
                {
                    "ride_id": ride_id,
                    "offer_id": offer_id,
                    "final_fare_egp": final_fare,
                    "ride_status": ride_status,
                    "started_at": _local_naive(decided_at),
                    "start_distance_metres": start_distance,
                    "completed_at": _local_naive(ride_end),
                    "cancelled_by": cancellation_actor,
                    "cancellation_reason": cancellation_reason,
                    "cancellation_stage": cancellation_stage,
                }
            )
            ride_context[ride_id] = {
                "passenger_id": passenger_id,
                "driver_id": driver_id,
                "vehicle_id": vehicle_id,
                "initial_fare": initial_fare,
                "decided_at": decided_at,
                "driver_arrival": driver_arrival,
                "trip_start": trip_start,
                "planned_end": planned_end,
                "ride_end": ride_end,
                "route_distance": route_distance,
            }
            ride_id += 1

        offer_rows.append(
            {
                "offer_id": offer_id,
                "passenger_id": passenger_id,
                "driver_id": driver_id,
                "vehicle_id": vehicle_id,
                "pickup_zone_id": pickup_zone_id,
                "dropoff_zone_id": dropoff_zone_id,
                "initial_fare_egp": float(initial_fare),
                "offer_status": offer_status,
                "initiated_at": initiated_at,
                "declined_by": declined_by,
                "decided_at": decided_at,
                "decline_reason": decline_reason,
            }
        )

    return pd.DataFrame(offer_rows), pd.DataFrame(ride_rows), {
        "ride_context": ride_context,
        "driver_completed": driver_completed,
    }


def _generate_payments_and_refunds(
    rides: pd.DataFrame,
    metadata: dict[str, Any],
    ride_metadata: dict[str, Any],
    config: SimulationConfig,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    _, simulation_end = _simulation_bounds(config)
    reliability = metadata["passenger_reliability"]
    contexts = ride_metadata["ride_context"]
    payment_rows: list[dict[str, Any]] = []
    refund_rows: list[dict[str, Any]] = []
    payment_id = 1
    refund_id = 1

    for ride in rides.itertuples(index=False):
        context = contexts[int(ride.ride_id)]
        passenger_id = context["passenger_id"]
        final_fare = float(ride.final_fare_egp) if pd.notna(ride.final_fare_egp) else 0.0
        requested_amount = round(
            max(30.0, float(context["initial_fare"]), final_fare), 2
        )
        initiated_at = context["decided_at"] + timedelta(seconds=int(rng.integers(10, 80)))
        attempt_number = 1
        failed_first = (
            ride.ride_status != "AWAITING_PAYMENT"
            and rng.random() > reliability[passenger_id]
        )
        if failed_first:
            failure_reason = str(
                rng.choice(
                    ["INSUFFICIENT_FUNDS", "PROVIDER_TIMEOUT", "AUTHENTICATION_FAILED"],
                    p=[0.50, 0.22, 0.28],
                )
            )
            payment_rows.append(
                {
                    "payment_attempt_id": payment_id,
                    "ride_id": int(ride.ride_id),
                    "attempt_number": attempt_number,
                    "payment_method": str(rng.choice(["CARD", "WALLET"], p=[0.72, 0.28])),
                    "payment_status": "FAILED",
                    "requested_amount_egp": requested_amount,
                    "authorized_amount_egp": None,
                    "captured_amount_egp": None,
                    "provider_reference": f"PAY-{payment_id:09d}",
                    "failure_reason": failure_reason,
                    "initiated_at": initiated_at,
                    "authorized_at": None,
                    "captured_at": None,
                    "released_at": None,
                }
            )
            payment_id += 1
            attempt_number += 1
            initiated_at += timedelta(minutes=float(rng.uniform(1, 4)))

        payment_status: str
        authorized_amount: float | None = None
        captured_amount: float | None = None
        authorized_at: datetime | None = None
        captured_at: datetime | None = None
        released_at: datetime | None = None
        failure_reason: str | None = None

        if ride.ride_status == "AWAITING_PAYMENT":
            if rng.random() < 0.55:
                payment_status = "INITIATED"
            else:
                payment_status = "FAILED"
                failure_reason = str(
                    rng.choice(["INSUFFICIENT_FUNDS", "PROVIDER_TIMEOUT"])
                )
        elif ride.ride_status == "CANCELLED_BEFORE_START":
            authorized_amount = requested_amount
            authorized_at = initiated_at + timedelta(seconds=int(rng.integers(5, 45)))
            if rng.random() < 0.82:
                payment_status = "RELEASED"
                released_at = context["ride_end"] + timedelta(minutes=float(rng.uniform(1, 8)))
            else:
                payment_status = "CAPTURED"
                captured_amount = requested_amount
                captured_at = authorized_at + timedelta(seconds=int(rng.integers(5, 50)))
        elif ride.ride_status in {"COMPLETED", "TERMINATED_EARLY"}:
            payment_status = "CAPTURED"
            authorized_amount = requested_amount
            captured_amount = round(float(ride.final_fare_egp), 2)
            authorized_at = initiated_at + timedelta(seconds=int(rng.integers(5, 45)))
            captured_at = context["ride_end"] + timedelta(minutes=float(rng.uniform(1, 5)))
        else:
            payment_status = "AUTHORIZED"
            authorized_amount = requested_amount
            authorized_at = initiated_at + timedelta(seconds=int(rng.integers(5, 45)))

        current_payment_id = payment_id
        payment_rows.append(
            {
                "payment_attempt_id": current_payment_id,
                "ride_id": int(ride.ride_id),
                "attempt_number": attempt_number,
                "payment_method": str(rng.choice(["CARD", "WALLET"], p=[0.72, 0.28])),
                "payment_status": payment_status,
                "requested_amount_egp": requested_amount,
                "authorized_amount_egp": authorized_amount,
                "captured_amount_egp": captured_amount,
                "provider_reference": f"PAY-{current_payment_id:09d}",
                "failure_reason": failure_reason,
                "initiated_at": initiated_at,
                "authorized_at": authorized_at,
                "captured_at": captured_at,
                "released_at": released_at,
            }
        )
        payment_id += 1

        refund_probability = 0.0
        refund_reason = None
        refund_share = 0.0
        if payment_status == "CAPTURED" and ride.ride_status == "CANCELLED_BEFORE_START":
            refund_probability = 1.0
            refund_reason = "PRE_START_CANCELLATION"
            refund_share = 1.0
        elif payment_status == "CAPTURED" and ride.ride_status == "TERMINATED_EARLY":
            refund_probability = 0.28
            refund_reason = "EARLY_TERMINATION_ADJUSTMENT"
            refund_share = float(rng.uniform(0.15, 0.65))
        elif payment_status == "CAPTURED" and ride.ride_status == "COMPLETED":
            refund_probability = 0.008
            refund_reason = "SERVICE_QUALITY_ADJUSTMENT"
            refund_share = float(rng.uniform(0.10, 0.45))

        if rng.random() < refund_probability:
            requested_at = (captured_at or context["ride_end"]) + timedelta(
                hours=float(rng.uniform(0.2, 48))
            )
            if requested_at > simulation_end:
                continue
            age_hours = (simulation_end - requested_at).total_seconds() / 3_600
            if age_hours < 2:
                refund_status = str(
                    rng.choice(["REQUESTED", "PROCESSING"], p=[0.55, 0.45])
                )
            else:
                refund_status = str(
                    rng.choice(
                        ["COMPLETED", "PROCESSING", "FAILED"], p=[0.93, 0.04, 0.03]
                    )
                )
            completed_at = None
            refund_failure_reason = None
            if refund_status == "COMPLETED":
                completed_at = requested_at + timedelta(
                    hours=float(rng.uniform(0.2, 36))
                )
            elif refund_status == "FAILED":
                refund_failure_reason = str(
                    rng.choice(["PROVIDER_REJECTION", "ACCOUNT_CLOSED"])
                )
            refund_rows.append(
                {
                    "refund_id": refund_id,
                    "payment_attempt_id": current_payment_id,
                    "refund_amount_egp": round(float(captured_amount) * refund_share, 2),
                    "refund_reason": refund_reason,
                    "refund_status": refund_status,
                    "requested_at": requested_at,
                    "completed_at": completed_at,
                    "failure_reason": refund_failure_reason,
                }
            )
            refund_id += 1

    refund_columns = [
        "refund_id",
        "payment_attempt_id",
        "refund_amount_egp",
        "refund_reason",
        "refund_status",
        "requested_at",
        "completed_at",
        "failure_reason",
    ]
    return pd.DataFrame(payment_rows), pd.DataFrame(refund_rows, columns=refund_columns)


def _rating_comment(average_score: float, rng: np.random.Generator) -> str | None:
    if rng.random() > 0.08:
        return None
    if average_score >= 4.4:
        return str(
            rng.choice(
                ["Smooth trip and respectful communication.", "Good experience overall.", "Everything went well."]
            )
        )
    if average_score <= 2.6:
        return str(
            rng.choice(
                ["The experience needs improvement.", "Communication was difficult.", "Several issues affected the trip."]
            )
        )
    return "The trip was acceptable overall."


def _generate_ratings(
    rides: pd.DataFrame,
    metadata: dict[str, Any],
    vehicle_metadata: dict[str, Any],
    ride_metadata: dict[str, Any],
    config: SimulationConfig,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    _, simulation_end = _simulation_bounds(config)
    driver_quality = metadata["driver_quality"]
    passenger_courtesy = metadata["passenger_courtesy"]
    vehicle_quality = vehicle_metadata["vehicle_quality"]
    contexts = ride_metadata["ride_context"]
    passenger_rows: list[dict[str, Any]] = []
    driver_rows: list[dict[str, Any]] = []

    for ride in rides.itertuples(index=False):
        if ride.ride_status not in {"COMPLETED", "TERMINATED_EARLY"}:
            continue
        context = contexts[int(ride.ride_id)]
        driver_id = context["driver_id"]
        passenger_id = context["passenger_id"]
        outcome_penalty = 1.25 if ride.ride_status == "TERMINATED_EARLY" else 0.0
        ended_at = context["ride_end"]

        passenger_rating_probability = 0.70 if ride.ride_status == "COMPLETED" else 0.34
        if rng.random() < passenger_rating_probability:
            attitude = _clip_score(
                rng.normal(driver_quality[driver_id] - outcome_penalty, 0.55)
            )
            driving = _clip_score(
                rng.normal(driver_quality[driver_id] - 0.1 - outcome_penalty, 0.55)
            )
            cleanliness = _clip_score(
                rng.normal(vehicle_quality[context["vehicle_id"]] - outcome_penalty * 0.35, 0.5)
            )
            comfort = _clip_score(
                rng.normal(
                    (driver_quality[driver_id] + vehicle_quality[context["vehicle_id"]]) / 2
                    - outcome_penalty * 0.65,
                    0.5,
                )
            )
            route_quality = _clip_score(
                rng.normal(driver_quality[driver_id] - outcome_penalty * 0.7, 0.6)
            )
            average = np.mean([attitude, driving, cleanliness, comfort, route_quality])
            passenger_rows.append(
                {
                    "ride_id": int(ride.ride_id),
                    "attitude_score": attitude,
                    "driving_safety_score": driving,
                    "vehicle_cleanliness_score": cleanliness,
                    "comfort_score": comfort,
                    "route_quality_score": route_quality,
                    "submitted_at": min(
                        simulation_end,
                        ended_at + timedelta(minutes=float(rng.uniform(2, 240))),
                    ),
                    "comment": _rating_comment(float(average), rng),
                }
            )

        driver_rating_probability = 0.55 if ride.ride_status == "COMPLETED" else 0.28
        if rng.random() < driver_rating_probability:
            courtesy = passenger_courtesy[passenger_id] - outcome_penalty * 0.75
            attitude = _clip_score(rng.normal(courtesy, 0.55))
            punctuality = _clip_score(rng.normal(courtesy - 0.12, 0.6))
            cooperation = _clip_score(rng.normal(courtesy - 0.05, 0.55))
            safety = _clip_score(rng.normal(courtesy, 0.5))
            average = np.mean([attitude, punctuality, cooperation, safety])
            driver_rows.append(
                {
                    "ride_id": int(ride.ride_id),
                    "attitude_score": attitude,
                    "punctuality_score": punctuality,
                    "pickup_cooperation_score": cooperation,
                    "respect_safety_score": safety,
                    "submitted_at": min(
                        simulation_end,
                        ended_at + timedelta(minutes=float(rng.uniform(2, 300))),
                    ),
                    "comment": _rating_comment(float(average), rng),
                }
            )

    passenger_columns = [
        "ride_id",
        "attitude_score",
        "driving_safety_score",
        "vehicle_cleanliness_score",
        "comfort_score",
        "route_quality_score",
        "submitted_at",
        "comment",
    ]
    driver_columns = [
        "ride_id",
        "attitude_score",
        "punctuality_score",
        "pickup_cooperation_score",
        "respect_safety_score",
        "submitted_at",
        "comment",
    ]
    return (
        pd.DataFrame(passenger_rows, columns=passenger_columns),
        pd.DataFrame(driver_rows, columns=driver_columns),
    )


def _generate_reports(
    rides: pd.DataFrame,
    ride_metadata: dict[str, Any],
    config: SimulationConfig,
    rng: np.random.Generator,
) -> pd.DataFrame:
    _, simulation_end = _simulation_bounds(config)
    contexts = ride_metadata["ride_context"]
    rows: list[dict[str, Any]] = []
    report_id = 1
    for ride in rides.itertuples(index=False):
        if ride.ride_status == "TERMINATED_EARLY":
            probability = 0.58
        elif ride.ride_status == "CANCELLED_BEFORE_START":
            probability = 0.11
        elif ride.ride_status == "COMPLETED":
            probability = 0.016
        else:
            probability = 0.0
        if rng.random() >= probability:
            continue
        context = contexts[int(ride.ride_id)]
        reports_for_ride = 2 if rng.random() < 0.06 else 1
        for _ in range(reports_for_ride):
            if ride.ride_status == "TERMINATED_EARLY":
                category = str(
                    rng.choice(
                        [
                            "PASSENGER_BEHAVIOR",
                            "DRIVER_BEHAVIOR",
                            "VEHICLE_ISSUE",
                            "PAYMENT_ISSUE",
                            "OTHER",
                        ],
                        p=[0.22, 0.31, 0.20, 0.14, 0.13],
                    )
                )
            elif ride.ride_status == "CANCELLED_BEFORE_START":
                category = str(
                    rng.choice(
                        ["PASSENGER_BEHAVIOR", "DRIVER_BEHAVIOR", "VEHICLE_ISSUE", "OTHER"],
                        p=[0.23, 0.36, 0.20, 0.21],
                    )
                )
            else:
                category = str(
                    rng.choice(
                        ["DRIVER_BEHAVIOR", "VEHICLE_ISSUE", "PAYMENT_ISSUE", "OTHER"]
                    )
                )
            opened_by = str(
                rng.choice(["PASSENGER", "DRIVER", "SYSTEM"], p=[0.68, 0.25, 0.07])
            )
            opened_at = context["ride_end"] + timedelta(
                minutes=float(rng.uniform(5, 720))
            )
            age_days = (simulation_end - opened_at).total_seconds() / 86_400
            if age_days < 2:
                report_status = str(
                    rng.choice(["OPEN", "IN_PROGRESS"], p=[0.62, 0.38])
                )
            else:
                report_status = str(
                    rng.choice(
                        ["OPEN", "IN_PROGRESS", "RESOLVED", "REJECTED"],
                        p=[0.05, 0.10, 0.72, 0.13],
                    )
                )
            resolved_at = None
            resolution_notes = None
            if report_status in {"RESOLVED", "REJECTED"}:
                resolved_at = opened_at + timedelta(days=float(rng.uniform(0.2, 6)))
                resolution_notes = (
                    "Evidence reviewed and account records updated."
                    if report_status == "RESOLVED"
                    else "Available evidence did not support further action."
                )
            descriptions = {
                "PASSENGER_BEHAVIOR": "Passenger conduct affected the trip.",
                "DRIVER_BEHAVIOR": "Driver conduct requires review.",
                "VEHICLE_ISSUE": "A vehicle condition issue was reported.",
                "PAYMENT_ISSUE": "The charged amount or payment handling was disputed.",
                "OTHER": "The incident does not match the standard categories.",
            }
            rows.append(
                {
                    "report_id": report_id,
                    "ride_id": int(ride.ride_id),
                    "opened_by": opened_by,
                    "report_category": category,
                    "other_report_category": "Route or pickup issue" if category == "OTHER" else None,
                    "description": descriptions[category],
                    "report_status": report_status,
                    "opened_at": opened_at,
                    "resolved_at": resolved_at,
                    "resolution_notes": resolution_notes,
                }
            )
            report_id += 1
    columns = [
        "report_id",
        "ride_id",
        "opened_by",
        "report_category",
        "other_report_category",
        "description",
        "report_status",
        "opened_at",
        "resolved_at",
        "resolution_notes",
    ]
    return pd.DataFrame(rows, columns=columns)


def generate_synthetic_dataset(
    config: SimulationConfig | None = None,
) -> SyntheticDataset:
    """Generate all 13 tables without modifying PostgreSQL."""
    config = config or SimulationConfig()
    rng = np.random.default_rng(config.seed)
    accounts, passengers, drivers, metadata = _generate_accounts(config, rng)
    zones, zone_routes, zone_metadata = _generate_zones_and_routes(rng)
    vehicles, vehicle_metadata = _generate_vehicles(drivers, accounts, config, rng)
    offers, rides, ride_metadata = _generate_offers_and_rides(
        config, metadata, zone_metadata, vehicle_metadata, rng
    )
    payment_attempts, refunds = _generate_payments_and_refunds(
        rides, metadata, ride_metadata, config, rng
    )
    passenger_driver_ratings, driver_passenger_ratings = _generate_ratings(
        rides, metadata, vehicle_metadata, ride_metadata, config, rng
    )
    reports = _generate_reports(rides, ride_metadata, config, rng)

    tables = {
        "accounts": accounts,
        "passengers": passengers,
        "drivers": drivers,
        "zones": zones,
        "vehicles": vehicles,
        "zone_routes": zone_routes,
        "offers": offers,
        "rides": rides,
        "payment_attempts": payment_attempts,
        "refunds": refunds,
        "passenger_driver_ratings": passenger_driver_ratings,
        "driver_passenger_ratings": driver_passenger_ratings,
        "reports": reports,
    }
    combined_metadata = {
        **metadata,
        **zone_metadata,
        **vehicle_metadata,
        **ride_metadata,
    }
    dataset = SyntheticDataset(tables=tables, config=config, metadata=combined_metadata)
    assert_valid_dataset(dataset)
    return dataset


def validation_report(dataset: SyntheticDataset) -> pd.DataFrame:
    """Return high-value structural and business consistency checks."""
    tables = dataset.tables
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    accounts = tables["accounts"]
    passengers = tables["passengers"]
    drivers = tables["drivers"]
    vehicles = tables["vehicles"]
    zones = tables["zones"]
    routes = tables["zone_routes"]
    offers = tables["offers"]
    rides = tables["rides"]
    payments = tables["payment_attempts"]
    refunds = tables["refunds"]

    add(
        "unique account contacts",
        accounts["phone_number"].is_unique and accounts["email"].is_unique,
        f"{len(accounts):,} accounts",
    )
    account_ids = set(accounts["account_id"])
    add(
        "roles reference accounts",
        set(passengers["passenger_id"]).issubset(account_ids)
        and set(drivers["driver_id"]).issubset(account_ids),
        "passenger and driver shared keys",
    )
    driver_vehicle_pairs = set(zip(vehicles["driver_id"], vehicles["vehicle_id"]))
    offer_vehicle_pairs = set(zip(offers["driver_id"], offers["vehicle_id"]))
    add(
        "offer vehicle belongs to driver",
        offer_vehicle_pairs.issubset(driver_vehicle_pairs),
        f"{len(offer_vehicle_pairs):,} used driver-vehicle pairs",
    )
    zone_ids = set(zones["zone_id"])
    add(
        "routes reference zones",
        set(routes["origin_zone_id"]).issubset(zone_ids)
        and set(routes["destination_zone_id"]).issubset(zone_ids)
        and (routes[["baseline_distance_km", "baseline_duration_minutes"]] > 0).all().all(),
        f"{len(routes):,} positive directional routes",
    )
    ride_offer_ids = set(rides["offer_id"])
    accepted_offer_ids = set(offers.loc[offers["offer_status"] == "ACCEPTED", "offer_id"])
    add(
        "accepted offers map one-to-one to rides",
        rides["offer_id"].is_unique and ride_offer_ids == accepted_offer_ids,
        f"{len(rides):,} rides from {len(offers):,} offers",
    )
    add(
        "open offers have no decision",
        offers.loc[
            offers["offer_status"].isin(["PENDING", "NEGOTIATING"]), "decided_at"
        ].isna().all(),
        "pending and negotiating rows",
    )
    amount_columns = [
        "requested_amount_egp",
        "authorized_amount_egp",
        "captured_amount_egp",
    ]
    payment_amounts_valid = all(
        payments[column].dropna().gt(25).all() for column in amount_columns
    )
    add(
        "payment amounts exceed 25 EGP",
        payment_amounts_valid,
        f"{len(payments):,} payment attempts",
    )
    add(
        "payment attempts are numbered per ride",
        not payments.duplicated(["ride_id", "attempt_number"]).any()
        and payments["provider_reference"].is_unique,
        "unique attempt numbers and provider references",
    )
    captured = payments.set_index("payment_attempt_id")["captured_amount_egp"]
    refund_valid = True
    for refund in refunds.itertuples(index=False):
        captured_amount = captured.get(refund.payment_attempt_id)
        if pd.isna(captured_amount) or refund.refund_amount_egp > captured_amount:
            refund_valid = False
            break
    add(
        "refunds do not exceed captured payments",
        refund_valid,
        f"{len(refunds):,} refunds",
    )
    rating_columns = {
        "passenger_driver_ratings": [
            "attitude_score",
            "driving_safety_score",
            "vehicle_cleanliness_score",
            "comfort_score",
            "route_quality_score",
        ],
        "driver_passenger_ratings": [
            "attitude_score",
            "punctuality_score",
            "pickup_cooperation_score",
            "respect_safety_score",
        ],
    }
    ratings_valid = True
    for table_name, columns in rating_columns.items():
        rating_table = tables[table_name]
        if not all(rating_table[column].dropna().between(1, 5).all() for column in columns):
            ratings_valid = False
    add("rating scores stay in range", ratings_valid, "all supplied scores are 1–5")
    ride_ids = set(rides["ride_id"])
    child_references_valid = (
        set(payments["ride_id"]).issubset(ride_ids)
        and set(tables["passenger_driver_ratings"]["ride_id"]).issubset(ride_ids)
        and set(tables["driver_passenger_ratings"]["ride_id"]).issubset(ride_ids)
        and set(tables["reports"]["ride_id"]).issubset(ride_ids)
    )
    add("ride child tables have no orphans", child_references_valid, "payments, ratings, reports")
    return pd.DataFrame(checks)


def assert_valid_dataset(dataset: SyntheticDataset) -> None:
    report = validation_report(dataset)
    failures = report.loc[~report["passed"]]
    if not failures.empty:
        details = "; ".join(
            f"{row.check}: {row.detail}" for row in failures.itertuples(index=False)
        )
        raise ValueError(f"Synthetic dataset validation failed: {details}")


def load_synthetic_dataset(
    dataset: SyntheticDataset,
    connection: Any,
    *,
    replace_existing: bool = False,
) -> pd.DataFrame:
    """Load a validated dataset through PostgreSQL COPY in dependency order."""
    from MAna.database import copy_from_dataframe, execute_query

    assert_valid_dataset(dataset)
    if replace_existing:
        execute_query(
            """
            TRUNCATE TABLE
                reports,
                driver_passenger_ratings,
                passenger_driver_ratings,
                refunds,
                payment_attempts,
                rides,
                offers,
                zone_routes,
                vehicles,
                zones,
                drivers,
                passengers,
                accounts
            RESTART IDENTITY CASCADE;
            """,
            connection,
        )
    else:
        existing = execute_query(
            """
            SELECT SUM(row_count) AS existing_rows
            FROM (
                SELECT COUNT(*) AS row_count FROM accounts
                UNION ALL SELECT COUNT(*) FROM offers
                UNION ALL SELECT COUNT(*) FROM rides
            ) counts;
            """,
            connection,
            return_results=True,
        )
        if int(existing.iloc[0, 0]) > 0:
            raise ValueError(
                "Target tables already contain data. Use replace_existing=True only for an intentional rebuild."
            )

    load_rows: list[dict[str, Any]] = []
    for table_name in TABLE_ORDER:
        dataframe = dataset.tables[table_name]
        inserted = copy_from_dataframe(dataframe, table_name, connection)
        load_rows.append({"table_name": table_name, "inserted_rows": inserted})

    sequence_statements = []
    for table_name, column_name in SERIAL_COLUMNS.items():
        sequence_statements.append(
            "SELECT setval(pg_get_serial_sequence('{table}', '{column}'), "
            "COALESCE((SELECT MAX({column}) FROM {table}), 1), true);".format(
                table=table_name, column=column_name
            )
        )
    execute_query("\n".join(sequence_statements), connection)
    return pd.DataFrame(load_rows)


def database_validation_queries() -> dict[str, str]:
    """SQL summaries used after loading the synthetic data."""
    return {
        "row_counts": """
            SELECT 'accounts' AS table_name, COUNT(*) AS rows FROM accounts
            UNION ALL SELECT 'passengers', COUNT(*) FROM passengers
            UNION ALL SELECT 'drivers', COUNT(*) FROM drivers
            UNION ALL SELECT 'vehicles', COUNT(*) FROM vehicles
            UNION ALL SELECT 'zones', COUNT(*) FROM zones
            UNION ALL SELECT 'zone_routes', COUNT(*) FROM zone_routes
            UNION ALL SELECT 'offers', COUNT(*) FROM offers
            UNION ALL SELECT 'rides', COUNT(*) FROM rides
            UNION ALL SELECT 'payment_attempts', COUNT(*) FROM payment_attempts
            UNION ALL SELECT 'refunds', COUNT(*) FROM refunds
            UNION ALL SELECT 'passenger_driver_ratings', COUNT(*) FROM passenger_driver_ratings
            UNION ALL SELECT 'driver_passenger_ratings', COUNT(*) FROM driver_passenger_ratings
            UNION ALL SELECT 'reports', COUNT(*) FROM reports
            ORDER BY table_name;
        """,
        "offer_outcomes": """
            SELECT offer_status, COUNT(*) AS offers,
                   ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct
            FROM offers
            GROUP BY offer_status
            ORDER BY offers DESC;
        """,
        "ride_outcomes": """
            SELECT ride_status, COUNT(*) AS rides,
                   ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct
            FROM rides
            GROUP BY ride_status
            ORDER BY rides DESC;
        """,
        "integrity": """
            SELECT
                COUNT(*) FILTER (WHERE o.offer_status <> 'ACCEPTED') AS rides_from_nonaccepted_offers,
                COUNT(*) - COUNT(DISTINCT r.offer_id) AS duplicate_offer_rides
            FROM rides r
            JOIN offers o ON o.offer_id = r.offer_id;
        """,
    }
