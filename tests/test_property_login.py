from property_login import InfraiSmsClient, PropertyLogin, sample_account


class FakeSms:
    def __init__(self, verified: bool) -> None:
        self.verified = verified
        self.calls = []

    def request_code(self, phone, request_id):
        self.calls.append(("otp", phone, request_id))
        return {}

    def verify_code(self, phone, code, request_id):
        self.calls.append(("verify", phone, code, request_id))
        return {"verified": self.verified}


def test_verified_tenant_gets_property_work_queue():
    sms = FakeSms(True)
    login = PropertyLogin(sms, {"maple-12": sample_account()})

    login.send_code("maple-12", "send-1")
    result = login.verify("maple-12", "123456", "verify-1")

    assert result == {
        "status": "verified",
        "open_requests": 1,
        "documents": 1,
        "inspection_reminders": 1,
    }
    assert sms.calls[0][0] == "otp"
    assert sms.calls[1][0] == "verify"


def test_rejected_code_does_not_expose_property_data():
    login = PropertyLogin(FakeSms(False), {"maple-12": sample_account()})
    assert login.verify("maple-12", "000000", "verify-2") == {"status": "rejected"}

