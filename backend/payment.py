import stripe
from auth import set_paid

stripe.api_key = "sk_test_123456"  # badilisha

endpoint_secret = "whsec_123456"  # badilisha

def create_checkout_session(username):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": "Traffic AI SaaS Access",
                },
                "unit_amount": 500,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="http://localhost:5173",
        cancel_url="http://localhost:5173",
        metadata={"username": username}
    )

    return session.url

def handle_webhook(payload, sig_header):
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except:
        return False

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        username = session["metadata"]["username"]

        set_paid(username)

    return True