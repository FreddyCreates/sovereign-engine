# FSOS API

The current production seed ships with a stdlib JSON API for local deployment and adapter testing.

## Endpoints

### `GET /health`

Returns service status.

### `GET /v1/compliance/rules`

Returns transaction-record fields and compliance rule metadata.

### `GET /v1/demo/match`

Runs the demo carrier/load through compliance and matching.

### `POST /v1/demo/compliance`

Runs the demo compliance gate.

### `POST /v1/demo/settlement`

Request:

```json
{
  "gross_amount_usd": "650",
  "payment_mode": "quickpay_one_day",
  "prior_transactions": 0
}
```

## Production Adapter Boundary

Live deployment should replace demo endpoints with authenticated handlers backed by:

- FMCSA/SAFER authority verification;
- ELD provider webhooks;
- payment rail adapters;
- document OCR and signature services;
- append-only audit storage;
- counsel-reviewed agent/escrow contracts.

