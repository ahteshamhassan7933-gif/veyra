# Veyra Deploy — Founder Punch List

## Autonomously done
- Landing page live on GitHub Pages: https://ahteshamhassan7933-gif.github.io/veyra/
- Landing CTAs point to cal.com/ahteshamhassan/15min (booking flow)
- Dockerfile + fly.toml + render.yaml scaffolded (ready to launch)
- WordPress plugin scaffold at plugins/wordpress/ (ready to submit to wordpress.org)

## Founder gate — 5 tasks, ~90 min total

### 1. Register veyra.dev (~$15/yr, 5 min)
```
https://www.cloudflare.com/products/registrar/
Search: veyra.dev → Register → point to Cloudflare nameservers
```
Then add DNS CNAME: `www` → `ahteshamhassan7933-gif.github.io`, and A records for GitHub Pages IPs (185.199.108.153 etc).

### 2. LemonSqueezy signup (~30 min)
```
https://app.lemonsqueezy.com/register
```
- Verify UK LTD (Response Ldn or personal sole trader)
- Create 3 products:
  - "Veyra Shopify" £197/mo recurring
  - "Veyra Woo/BC/Magento" £297/mo recurring + £497 one-time setup
  - "Veyra Enterprise" £997/mo recurring
- Copy each hosted checkout URL, paste into landing/index.html in place of cal.com CTAs on pricing tier "Start" buttons (or keep booking flow + collect payment on demo)

### 3. Deploy API to Fly.io (~15 min)
```
curl -L https://fly.io/install.sh | sh
export FLY_API_TOKEN=<get from fly.io/user/personal_access_tokens>
cd /home/ubuntu/veyra
fly launch --copy-config --now  # uses fly.toml
```
Then update WordPress plugin `VEYRA_ACP_ENDPOINT` to the Fly.io URL.

### 4. OpenAI ACP merchant application (~15 min)
```
https://chatgpt.com/merchants
```
Fill form as "Veyra — Agent-Ready Commerce Integrator". Attach public repo URL, describe non-Shopify (Woo/BC/Magento/custom) merchant network you'll bring.

### 5. WordPress plugin submission (~20 min)
Zip `plugins/wordpress/` → submit at:
```
https://wordpress.org/plugins/developers/add/
```
Review takes 2-14 days. Free listing = free lead gen forever.

## Non-halal red flags to avoid
- Do NOT enable Stripe Capital, Paddle Advance, or any "get paid early" advance-on-receivables (riba-adjacent).
- Do NOT accept merchants selling alcohol, gambling, adult content, insurance, or riba products. Reject at signup.

## Fastest path to first £297
1. Landing live at github pages URL above (already done)
2. LemonSqueezy checkout live in ~30 min
3. Fire 10 warm Woo/BC agency DMs on LinkedIn with pitch:
   > "We add ChatGPT Instant Checkout to your Woo store in 48hrs. £297/mo + £497 setup. First install free if you post the case study. Interested?"
4. Book demo → close on call → LemonSqueezy checkout → cash in 7 days.
