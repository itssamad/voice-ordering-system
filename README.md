# Automated Voice Ordering System

An end-to-end voice-automation system that lets customers place orders over a phone call — no app, no website, just a normal phone call. Built to replace a manual, error-prone phone-ordering process for a real small business (a charcoal supplier), and later developed further as my Computer Science final year project.

## How it works

A customer calls a dedicated number. The system, powered by Twilio Voice and a FastAPI backend, has a short conversation with them using speech recognition:

1. Greets the caller and asks how many bags they'd like to order
2. Asks which product type (e.g. shisha or barbecue charcoal)
3. Asks for the delivery address
4. Reads the full order back and asks for confirmation
5. On confirmation, saves the order to a database and sends an instant WhatsApp notification to the business with the order details

If the caller says something the system doesn't understand at any step, it asks again rather than failing silently — the conversation is designed to recover gracefully from unclear speech.

## Architecture

- **`main.py`** — FastAPI application exposing the call-flow endpoints (`/voice`, `/ask_quantity`, `/ask_type`, `/ask_address`, `/confirm_order`) that Twilio calls as the conversation progresses. Each endpoint returns TwiML (Twilio's XML response format) that tells Twilio what to say and listen for next.
- **`database.py`** — SQLite persistence layer: logs every call, tracks in-progress order "sessions" per phone number, and stores confirmed orders.
- **`whatsapp.py`** — Sends a WhatsApp notification via the Twilio API the moment an order is confirmed.
- **`view_db.py`** — Small CLI utility to inspect logged calls and orders during development/testing.

## Tech stack

Python · FastAPI · Twilio Voice API · Twilio WhatsApp API · SQLite

## Getting started

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your own Twilio credentials
uvicorn main:app --reload
```

You'll need a Twilio account with a phone number configured to point its voice webhook at `/voice` on a publicly reachable URL (e.g. via ngrok during development).

## Result

Passed 100% of functional test cases during development and was used to automate real order intake for a live small business, removing a manual bottleneck in the ordering process.
