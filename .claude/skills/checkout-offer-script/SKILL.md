---
name: checkout-offer-script
description: Writes the add-on offers around a checkout, the order bump on the checkout page and the upsell page after purchase, following a framework from the user's swipe file. Use when the user wants an order bump, an upsell, a one-time offer, a downsell or checkout copy.
---

# checkout-offer-script

The extra offers someone sees while buying and right after.

## Inputs (from the brief)

- The main offer, the add-on offer, and which pieces are needed (bump, upsell or both).
- The user's material: what the add-on is, its price, why it pairs with the main offer.
- **Model (optional):** a finished bump or upsell to model. It sets structure only, never wording.

## Output

- **Order bump:** a headline, 2–3 lines on why it pairs with what they're buying, and the checkbox line with the price.
- **Upsell page:** a headline, why it matters right now, what they get, the price, and the yes and no button text.

## Rules

- The add-on makes the main purchase work better or faster. Never a random extra.
- Never invent prices, deliverables or guarantees. Flag gaps as `[GAP: what's missing]`.
