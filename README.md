# Veyra — Agent-Ready Commerce Layer

Make any store checkout-able inside ChatGPT, Perplexity, Gemini, Claude.

## What it does

One install → merchant store exposes:
- **OpenAI Agentic Commerce Protocol** endpoints (`/checkout_sessions` CRUD + complete + cancel + webhooks)
- **Google AP2** signing layer (JWT `checkoutSignature` + `CheckoutMandate` verification)
- **Merchant Center feed** auto-hygiene (GTIN/MPN inference, price/availability sync)
- **AI-visibility tracker** — weekly report of appearances in ChatGPT/Perplexity/Google AI shopping answers

## Wedge

Shopify auto-ships `/api/mcp` since Aug 2025 → skip MCP on Shopify. Woo/BigCommerce/Magento/Squarespace = wide open, full stack sale.

## Pricing

- Shopify tier £197/mo (ACP + AP2 + feed + tracker)
- Woo/BC/Magento tier £297/mo (full stack)
- Enterprise custom £997/mo
- Setup £497 one-time

## Halal

Merchant-neutral infrastructure. No affiliate to haram products. Refuse alcohol/gambling/adult/riba-finance at signup.

## Stack

FastAPI · Cloudflare Workers (edge endpoints) · Stripe (billing) · Postgres (D1 later) · Playwright (AI-visibility crawler).

## Status

Day 1 scaffold — pre-launch.
