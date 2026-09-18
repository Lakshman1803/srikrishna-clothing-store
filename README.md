# SRI KRISHNA — Clothing Store Management & Billing System

A working Django application for managing an offline clothing retail business
(Men / Women / Boys / Girls / Kids), covering POS billing, inventory, customers,
suppliers, purchases, payments, returns/exchanges, expenses, employees, reports,
and a public product catalog.

## What's actually built (and works end-to-end)

This is a large spec, so instead of stubbing every one of the ~40 requested
modules, the effort went into making the **core retail loop fully functional**
against a real database:

- **Public storefront**: home page, Men/Women/Boys/Girls/Kids category pages
  with subcategories, product detail pages, new arrivals, offers, search,
  about, shop location (Google Maps embed + call/WhatsApp buttons), contact form.
- **Customer login (mobile + OTP)**: OTP is simulated and shown on-screen since
  no SMS gateway is configured — wire in an SMS/OTP provider to go live.
  Customers can view their purchase history and loyalty points.
- **POS Billing**: live product/barcode search, cart, per-line GST + discount
  calculation, coupon/discount fields, Cash/UPI/Card/Bank Transfer payment,
  UPI QR code generation on the invoice, PDF invoice download, WhatsApp share
  link, printable invoice. Completing a sale **atomically**: creates the Sale,
  deducts stock per variant, logs a StockMovement, records the Payment,
  updates customer loyalty points and purchase history.
- **Inventory**: stock list with low/out-of-stock badges and filters, full
  stock movement history, manual stock adjustment.
- **Purchases (stock entry)**: recording a purchase from a supplier
  automatically increases stock and logs the movement.
- **Returns & Exchanges**: look up any invoice by number, select items and
  quantities, process a return — stock is automatically restored.
- **Customers / Suppliers**: full CRUD, purchase history, pending-payment
  tracking for suppliers.
- **Expenses**: categorized expense tracking (rent, salary, electricity, etc.).
- **Employees & Roles**: Super Admin / Shop Owner / Manager / Cashier / Staff.
  Cashiers cannot see profit/cost figures anywhere in the UI (dashboard and
  reports show "Restricted" instead) — this is enforced at the view level via
  `user.can_view_financials`, not just hidden in templates.
- **Dashboard**: today's sales/orders/profit/expenses, low-stock alerts,
  7-day sales chart, category-wise sales, payment-method split.
- **Reports**: date-range filters (today/yesterday/this week/this
  month/last month/this year), top products, employee sales, low-stock
  report, CSV export for sales/stock/expenses/purchases, print view.
- **Offers**: percentage/fixed/BOGO/festival offers with date ranges and
  category targeting; coupon codes.
- **Settings**: shop name, address, phone, WhatsApp, GSTIN, UPI ID, invoice
  prefix, business hours, Google Maps embed URL, loyalty points ratio — all
  editable from the UI and used live across invoices, storefront, etc.
- **Backup**: one-click JSON backup download (`dumpdata`); restore via
  Django's `loaddata` management command.
- **Audit log**: every login, employee change, and sensitive action is
  recorded with user, timestamp and IP.
- **Django admin**: fully configured for every model, useful for bulk data
  management (products, variants, categories, sizes, colors, brands).

## What's simplified / not implemented

Being upfront about scope, given the size of the original spec:

- **Offline-first POS / background sync**: the POS screen shows an
  ONLINE/OFFLINE/SYNCING badge (via `navigator.onLine`), but there is no
  IndexedDB-backed offline queue that actually stores bills locally and syncs
  later. Wiring this in Django/Django REST Framework + a service worker is a
  natural next step and the models (Sale, SaleItem, StockMovement) are already
  shaped to support it.
- **Real barcode scanner hardware**: the POS search box accepts scanned input
  (most USB/Bluetooth barcode scanners just "type" the barcode + Enter), but
  there's no camera-based scanning UI.
- **WhatsApp/SMS/Email gateways**: invoice-sharing uses a `wa.me` deep link
  (opens WhatsApp Web/App with a pre-filled message) rather than the WhatsApp
  Business API, since that requires a paid, approved account. OTP login is
  simulated on-screen. Wire in an API (Twilio, MSG91, Gupshup, etc.) via the
  Settings page when ready.
- **Loyalty point redemption at checkout** and **automatic offer/coupon
  application in the POS cart** are modeled (Offer, Coupon, loyalty_points
  fields) but not yet wired into the checkout discount calculation — currently
  discount is a manual "overall discount %" field at billing time.
- **Multi-branch / online ordering / delivery**: intentionally left as future
  extensions per the spec, but the schema (Sale, Product, Customer) doesn't
  need structural changes to support a branch/warehouse foreign key later.

## Tech stack

- **Backend**: Python 3 / Django (project ships with the version pinned in
  `requirements.txt`)
- **Database**: SQLite by default (zero setup); PostgreSQL via environment
  variables for production
- **Frontend**: Tailwind CSS (CDN) + Alpine.js (CDN) + Chart.js (CDN) — no
  build step required
- **PDF invoices**: ReportLab
- **UPI QR codes**: `qrcode` package

## Setup instructions

```bash
cd srikrishna

# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment (optional — SQLite works with zero config)
cp .env.example .env
# edit .env if you want PostgreSQL / production settings, then:
# export $(cat .env | xargs)   # or use django-environ / python-dotenv

# 4. Run migrations
python manage.py migrate

# 5. Load realistic demo data (60 products, 360 variants, 20 customers,
#    10 suppliers, 40 sales, 15 purchases, 25 expenses, 5 returns, offers)
python manage.py seed_demo_data

# 6. Run the development server
python manage.py runserver
```

Visit:
- **Public storefront**: http://127.0.0.1:8000/
- **Staff login**: http://127.0.0.1:8000/accounts/login/
- **Django admin**: http://127.0.0.1:8000/admin/

### Demo accounts (created by `seed_demo_data`)

| Username    | Password     | Role         |
|-------------|--------------|--------------|
| `admin`     | `admin123`   | Super Admin (full access, also a Django superuser) |
| `manager1`  | `manager123` | Manager (inventory, sales, customers, reports, purchases) |
| `cashier1`  | `cashier123` | Cashier (billing, product search, customers, permitted returns) |
| `staff1`    | `staff123`   | Staff |

Customer-side login is mobile number + OTP at `/accounts/customer-login/`
(any 10-digit number starting 6-9 works; the OTP is shown on screen in this
demo since no SMS gateway is wired in).

## Production notes

- Set `DJANGO_DEBUG=False` and a strong `DJANGO_SECRET_KEY` before deploying.
- Switch to PostgreSQL by setting `DB_ENGINE=postgresql` and the `DB_*`
  variables in `.env`.
- Run `python manage.py collectstatic` behind a real web server (gunicorn +
  nginx, etc.) in production; the dev server serves static/media directly.
- Session length is capped at 4 hours (`SESSION_COOKIE_AGE`) as a basic
  auto-logout measure for shared POS terminals — tune this in
  `srikrishna/settings.py`.
- Back up regularly using Settings → Backup, or schedule
  `python manage.py dumpdata > backup.json` via cron.

## Project layout

```
srikrishna/
├── accounts/            # Custom User model, roles, audit log, employee & customer auth
├── catalog/              # Category, SubCategory, Brand, Size, Color, Product, ProductVariant
├── inventory/            # StockMovement + central stock-adjustment helper
├── customers/            # Customer model + purchase history
├── suppliers/            # Supplier model
├── purchases/            # Purchase / PurchaseItem (stock-in)
├── sales/                # Sale / SaleItem — POS billing, invoices, PDF, WhatsApp
├── payments/             # Payment records (Cash/UPI/Card/Bank Transfer)
├── expenses/             # Expense tracking
├── returns_exchanges/    # Return / ReturnItem (stock-restoring)
├── offers/               # Offer / Coupon
├── shopsettings/         # Singleton shop configuration (used site-wide)
├── dashboard/            # Admin dashboard + reports + CSV export
├── storefront/           # Public-facing website
├── templates/            # All HTML templates (Tailwind + Alpine.js)
└── static/               # CSS
```

## Database schema

All models listed in the original spec are implemented: `User`, `Employee`
(role on `User`), `Customer`, `Category`, `SubCategory`, `Brand`, `Product`,
`ProductVariant`, `Size`, `Color`, `Supplier`, `Purchase`, `PurchaseItem`,
`Sale`, `SaleItem`, `Payment`, `Expense`, `Return`, `ReturnItem`, `Offer`,
`Coupon`, `StockMovement`, `AuditLog`, `ShopSettings`. (`LoyaltyTransaction`
is simplified to a running `loyalty_points` counter on `Customer` plus
`loyalty_points_earned` per `Sale`, rather than a separate ledger table —
straightforward to split out later if a full audit trail of point
earn/redeem events is needed.)

`ProductVariant` supports arbitrary size × color combinations per product,
each with its own auto-generated SKU/barcode and independent stock count, as
specified.
