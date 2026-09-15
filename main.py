import re

from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from whatsapp import send_whatsapp_notification

from database import (
    init_db,
    save_call,
    create_or_reset_session,
    update_session_quantity,
    update_session_product,
    update_session_address,
    get_session,
    save_order,
    delete_session
)

app = FastAPI()
init_db()


def extract_quantity(text: str):
    match = re.search(r"\d+", text)
    if match:
        return int(match.group())
    return None


def extract_product_type(text: str):
    text = text.lower()

    if "shisha" in text:
        return "shisha"
    if "barbecue" in text or "barbeque" in text or "bbq" in text:
        return "barbecue"

    return None


def is_yes(text: str):
    text = text.lower().strip()
    yes_words = ["yes", "yeah", "yep", "correct", "right", "confirm"]
    return any(word in text for word in yes_words)


def is_no(text: str):
    text = text.lower().strip()
    no_words = ["no", "nope", "wrong", "incorrect"]
    return any(word in text for word in no_words)


def build_gather(action_url: str, timeout_seconds: int = 5):
    return Gather(
        input="speech",
        action=action_url,
        method="POST",
        speech_timeout="auto",
        timeout=timeout_seconds,
        actionOnEmptyResult=True
    )


@app.post("/voice")
async def voice(request: Request):
    form = await request.form()
    phone_number = form.get("From", "").strip()

    create_or_reset_session(phone_number)

    response = VoiceResponse()

    gather = build_gather("/ask_quantity", 5)
    gather.say("Hello. Welcome to our charcoal ordering service.")
    gather.say("How many charcoal bags do you want?")
    response.append(gather)

    return Response(content=str(response), media_type="application/xml")


@app.post("/ask_quantity")
async def ask_quantity(request: Request):
    form = await request.form()
    speech_text = form.get("SpeechResult", "").strip()
    phone_number = form.get("From", "").strip()

    response = VoiceResponse()

    if not speech_text:
        gather = build_gather("/ask_quantity", 5)
        gather.say("I did not hear anything.")
        gather.say("Please say how many bags you want.")
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    save_call(phone_number, speech_text)

    quantity = extract_quantity(speech_text)

    if quantity is None:
        gather = build_gather("/ask_quantity", 5)
        gather.say("Sorry, I did not understand the quantity.")
        gather.say("Please say the number of bags you want, for example, 10 bags.")
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    update_session_quantity(phone_number, quantity)

    gather = build_gather("/ask_type", 5)
    gather.say("What type of charcoal do you want? Please say shisha or barbecue.")
    response.append(gather)

    return Response(content=str(response), media_type="application/xml")


@app.post("/ask_type")
async def ask_type(request: Request):
    form = await request.form()
    speech_text = form.get("SpeechResult", "").strip()
    phone_number = form.get("From", "").strip()

    response = VoiceResponse()

    if not speech_text:
        gather = build_gather("/ask_type", 5)
        gather.say("I did not hear anything.")
        gather.say("Please say shisha or barbecue.")
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    save_call(phone_number, speech_text)

    product_type = extract_product_type(speech_text)

    if product_type is None:
        gather = build_gather("/ask_type", 5)
        gather.say("Sorry, I did not understand the charcoal type.")
        gather.say("Please say shisha or barbecue.")
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    update_session_product(phone_number, product_type)

    gather = build_gather("/ask_address", 7)
    gather.say("What address should we deliver to?")
    response.append(gather)

    return Response(content=str(response), media_type="application/xml")


@app.post("/ask_address")
async def ask_address(request: Request):
    form = await request.form()
    speech_text = form.get("SpeechResult", "").strip()
    phone_number = form.get("From", "").strip()

    response = VoiceResponse()

    if not speech_text:
        gather = build_gather("/ask_address", 7)
        gather.say("I did not hear the address.")
        gather.say("Please say the delivery address again.")
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    save_call(phone_number, speech_text)

    update_session_address(phone_number, speech_text)

    session = get_session(phone_number)

    if not session:
        gather = build_gather("/ask_quantity", 5)
        gather.say("Sorry, something went wrong with your order.")
        gather.say("Let's start again. How many charcoal bags do you want?")
        response.append(gather)
        create_or_reset_session(phone_number)
        return Response(content=str(response), media_type="application/xml")

    _, quantity, product_type, address = session

    gather = build_gather("/confirm_order", 5)
    gather.say(
        f"You want {quantity} bags of {product_type} charcoal, "
        f"to be delivered to {address}. "
        f"Is that correct? Please say yes or no."
    )
    response.append(gather)

    return Response(content=str(response), media_type="application/xml")


@app.post("/confirm_order")
async def confirm_order(request: Request):
    form = await request.form()
    speech_text = form.get("SpeechResult", "").strip()
    phone_number = form.get("From", "").strip()

    response = VoiceResponse()

    if not speech_text:
        gather = build_gather("/confirm_order", 5)
        gather.say("I did not hear anything.")
        gather.say("Please say yes or no.")
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    save_call(phone_number, speech_text)

    if is_yes(speech_text):
        session = get_session(phone_number)

        if not session:
            gather = build_gather("/ask_quantity", 5)
            gather.say("Sorry, your order session was not found.")
            gather.say("Let's start again. How many charcoal bags do you want?")
            response.append(gather)
            create_or_reset_session(phone_number)
            return Response(content=str(response), media_type="application/xml")

        _, quantity, product_type, address = session

        save_order(phone_number, quantity, product_type, address)

        whatsapp_message = (
            f"New charcoal order confirmed:\n"
            f"Quantity: {quantity} bags\n"
            f"Type: {product_type}\n"
            f"Address: {address}\n"
            f"Customer phone: {phone_number}"
        )

        try:
            send_whatsapp_notification(whatsapp_message)
            response.say("Thank you. Your order has been confirmed and saved. A WhatsApp notification has been sent to the business.")
        except Exception:
            response.say("Thank you. Your order has been confirmed and saved. However, the WhatsApp notification could not be sent.")

        delete_session(phone_number)

        return Response(content=str(response), media_type="application/xml")

    if is_no(speech_text):
        delete_session(phone_number)
        create_or_reset_session(phone_number)

        gather = build_gather("/ask_quantity", 5)
        gather.say("Okay, let's start again.")
        gather.say("How many charcoal bags do you want?")
        response.append(gather)

        return Response(content=str(response), media_type="application/xml")

    gather = build_gather("/confirm_order", 5)
    gather.say("Sorry, I did not understand.")
    gather.say("Please say yes or no.")
    response.append(gather)

    return Response(content=str(response), media_type="application/xml")