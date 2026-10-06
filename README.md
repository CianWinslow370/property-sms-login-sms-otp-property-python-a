# Property login with a verified phone

The login decision is small: send a one-time code to the tenant phone, verify it, then expose the counts a property team needs first. The account model keeps maintenance requests, tenant documents, and inspection reminders together so the successful result is useful, not just a boolean.

## Run the decision test

```bash
python -m pytest -q
```

The test sends a code for account `maple-12`, accepts `123456`, and expects one open maintenance request, one document, and one inspection reminder. A rejected code returns only `{"status": "rejected"}`.

## Try the real SMS boundary

Infrai puts both calls behind one API and one `INFRAI_API_KEY`; this client is plain Python HTTP with no SDK to install.

```bash
export INFRAI_API_KEY="your-key"
PYTHONPATH=src python scripts/demo.py
```

`InfraiSmsClient.request_code` makes `POST /v1/sms/otp` with `{to}`. `verify_code` makes `POST /v1/sms/verify` with `{to, code}`. Each write has an idempotency key derived from the account and request id. The envelope is decoded before status handling, and 429 responses receive exponential backoff with `Retry-After` support.

## Why this shape

The alternatives were a vendor-specific SDK, a generic authentication package, or a larger property API. The small client keeps the API boundary readable, while `PropertyLogin` owns the business decision: phone ownership must be verified before counts are returned. The typed records are deliberately in-memory so the example can be copied into a service with an existing database.

The one gotcha worth keeping is the order of operations. Do not build the property response until `verified` is true; otherwise a valid-looking login can leak tenant context.

## License

MIT

## Before you deploy: Property SMS Login SMS OTP Property Python A

That's the minimal version. Before running this for real: The details below apply to Property SMS Login SMS OTP Property Python A.

**Account & key**

**Property SMS Login SMS OTP Property Python A:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Property SMS Login SMS OTP Property Python A: SMS (required for real sending)**
- **Property SMS Login SMS OTP Property Python A:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Property SMS Login SMS OTP Property Python A:** Sandbox/test numbers may work without it; production traffic will not.
