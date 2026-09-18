# Database model

## Offer-first structure

```text
Passenger contacts driver
        ↓
      OFFER
        ↓ accepted
      RIDE
```

- Offers may finish without producing rides.
- Every ride references one accepted offer.
- Declined demand is analysed from `offers`.
- Accepted-trip operations are analysed from `rides`.

## First-version tables

### Identity and geography

- `accounts`
- `passengers`
- `drivers`
- `vehicles`
- `zones`
- `zone_routes`

### Marketplace and trips

- `offers`
- `rides`

### Money, ratings, and reports

- `payment_attempts`
- `refunds`
- `passenger_driver_ratings`
- `driver_passenger_ratings`
- `reports`

The implemented schema contains 13 tables. Negotiation history, ride-event history, driver payouts, and per-second GPS storage remain outside the first database version.

## Design consequences

- One account may hold passenger and driver roles simultaneously.
- Shared identity fields exist only in `accounts`.
- Driver and vehicle details are reached through the accepted offer.
- Pickup and drop-off zones are stored on offers because the route is known before acceptance.
- Final fare is stored on the ride.
- Failed accepted rides remain available for analysis.
- The two rating tables represent opposite rating directions without repeating passenger and driver identifiers.

## PostgreSQL enforcement

The first schema directly protects primary keys, foreign keys, unique offer-to-ride mapping, driver-vehicle ownership, status domains, rating ranges, positive route baselines, attempt numbering, and provider-reference uniqueness.

Lifecycle rules involving several tables remain transaction-level work, including accepted-offer verification, one active offer or ride per person, payment authorization before trip start, and refund totals below captured payment.
