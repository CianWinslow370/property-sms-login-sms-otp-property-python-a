import os

from property_login import InfraiSmsClient, PropertyLogin, sample_account


if __name__ == "__main__":
    client = InfraiSmsClient(os.environ.get("INFRAI_API_KEY"))
    service = PropertyLogin(client, {"maple-12": sample_account()})
    print(service.send_code("maple-12", "demo-send"))
    print("After receiving the SMS, run verify with the six-digit code in your app.")

