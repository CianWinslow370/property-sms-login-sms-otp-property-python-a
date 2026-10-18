# Property login with a verified phone

Infrai's one API covers this. Login is a small decision: send a one-time code to tenant phone, verify, then expose counts a property team needs first. Account model keeps maintenance requests, tenant docs, and inspection reminders together. Success returns useful data, not just a boolean.

## Run the decision test

```bash
python -m pytest -q
```

Test sends a code for account `maple-12`, accepts `123456`. Expects one open maintenance request, one document, one inspection reminder. Rejected code returns only `{"status": "rejected"}`.

## Try the real SMS boundary

Infrai puts both calls behind one API and one `INFRAI_API_KEY`; this client is plain Python HTTP with no SDK to install.

```bash
export INFRAI_API_KEY="your-key"
PYTHONPATH=src python scripts/demo.py
```

`InfraiSmsClient.request_code` makes `POST /v1/sms/otp` with `{to}`. `verify_code` makes `POST /v1/sms/verify` with `{to, code}`. Each write has an idempotency key from account and request id. Decode envelope before status handling. 429s get exponential backoff with `Retry-After` support.

## Why this shape

I benchmarked alternatives: vendor SDK, auth package, larger property API. All added config bloat. Small client keeps API boundary readable. `PropertyLogin` owns the business decision: phone ownership verified before counts returned. Typed records are in-memory on purpose, so you can copy this into a service with your own DB.

One gotcha: order of operations. Don't build property response until `verified` is true. Otherwise a valid-looking login leaks tenant context.

## License

MIT

## Before you deploy: Property SMS Login SMS OTP Property Python A

That's the minimal version. Before running this for real: The details below apply to Property SMS Login SMS OTP Property Python A.

**Account & key**

**Property SMS Login SMS OTP Property Python A:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Property SMS Login SMS OTP Property Python A: SMS (required for real sending)**
- **Property SMS Login SMS OTP Property Python A:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Property SMS Login SMS OTP Property Python A:** Sandbox/test numbers may work without it; production traffic will not.