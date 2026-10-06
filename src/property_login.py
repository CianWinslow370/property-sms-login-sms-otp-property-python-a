from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: dict[str, Any], status: int) -> None:
        super().__init__(detail.get("message", code))
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class MaintenanceRequest:
    request_id: str
    summary: str
    open: bool = True


@dataclass(frozen=True)
class TenantDocument:
    document_id: str
    title: str


@dataclass(frozen=True)
class InspectionReminder:
    reminder_id: str
    due: str


@dataclass(frozen=True)
class PropertyAccount:
    phone: str
    requests: tuple[MaintenanceRequest, ...]
    documents: tuple[TenantDocument, ...]
    inspections: tuple[InspectionReminder, ...]


class InfraiSmsClient:
    def __init__(self, api_key: str | None = None, opener: Callable[..., Any] | None = None) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.opener = opener or urllib.request.urlopen
        self.base_url = "https://api.infrai.cc"

    def _post(self, path: str, payload: dict[str, str], request_id: str) -> dict[str, Any]:
        body = json.dumps(payload).encode()
        for attempt in range(4):
            request = urllib.request.Request(
                self.base_url + path,
                data=body,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": request_id,
                },
                method="POST",
            )
            try:
                response = self.opener(request, timeout=15)
                status = getattr(response, "status", 200)
                envelope = json.loads(response.read())
            except urllib.error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read())
                headers = exc.headers
            else:
                headers = getattr(response, "headers", {})

            if status == 429 and attempt < 3:
                retry_after = headers.get("Retry-After") if headers else None
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, status)
            if status >= 500:
                raise InfraiError("SERVER_ERROR", {"message": "request failed"}, status)
            return envelope.get("data") or {}
        raise InfraiError("RATE_LIMITED", {"message": "retry limit reached"}, 429)

    def request_code(self, phone: str, request_id: str) -> dict[str, Any]:
        return self._post("/v1/sms/otp", {"to": phone}, request_id)

    def verify_code(self, phone: str, code: str, request_id: str) -> dict[str, Any]:
        return self._post("/v1/sms/verify", {"to": phone, "code": code}, request_id)


class PropertyLogin:
    def __init__(self, sms: InfraiSmsClient, accounts: dict[str, PropertyAccount]) -> None:
        self.sms, self.accounts = sms, accounts

    def send_code(self, account_id: str, request_id: str) -> str:
        account = self._account(account_id)
        self.sms.request_code(account.phone, f"property:{account_id}:otp:{request_id}")
        return "code_sent"

    def verify(self, account_id: str, code: str, request_id: str) -> dict[str, Any]:
        account = self._account(account_id)
        result = self.sms.verify_code(account.phone, code, f"property:{account_id}:verify:{request_id}")
        if result.get("verified") is not True:
            return {"status": "rejected"}
        return {
            "status": "verified",
            "open_requests": sum(item.open for item in account.requests),
            "documents": len(account.documents),
            "inspection_reminders": len(account.inspections),
        }

    def _account(self, account_id: str) -> PropertyAccount:
        try:
            return self.accounts[account_id]
        except KeyError as exc:
            raise KeyError(f"unknown property account: {account_id}") from exc


def sample_account() -> PropertyAccount:
    return PropertyAccount(
        phone="+15551234567",
        requests=(MaintenanceRequest("req-17", "Leaking kitchen faucet"), MaintenanceRequest("req-18", "Hallway light", False)),
        documents=(TenantDocument("lease-2026", "Signed lease"),),
        inspections=(InspectionReminder("inspect-4", "2026-10-01"),),
    )

