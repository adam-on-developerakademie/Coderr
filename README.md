# Coderr Backend (Coderr_TEST07)

Production-ready backend copy of the Coderr Django/DRF project, prepared without test files and documented in English.

## Overview

- Framework: Django 6.0.2
- API: Django REST Framework 3.16.1
- Auth: TokenAuthentication + SessionAuthentication
- Filters: django-filter + DRF ordering/search where applicable
- Database: SQLite (default development setup)


## Quick Start

1. Create virtual environment:
	- Windows: `python -m venv .venv && .venv\Scripts\activate`
2. Install dependencies:
	- `pip install -r requirements.txt`
3. Create environment file:
	- `copy .env.example .env`
	- Generate a new `SECRET_KEY`
**⚠️ Security Notes:**
- **NEVER** commit the `.env` file to Git (already included in .gitignore)
- **Production:** Generate a new SECRET_KEY for production
- **Production:** Set `DEBUG=False`
- **Production:** Configure `ALLOWED_HOSTS` according to your domain
- **Privacy:** Use strong, unique passwords
**⚠️ IMPORTANT:** Always generate a new SECRET_KEY for your installation:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
-  Copy the generated key and replace `your-secret-key-here` in your `.env` file.

4. Apply migrations:
	- `python manage.py migrate`
5. Start server:
	- `python manage.py runserver`

Server URL: `http://127.0.0.1:8000/`

## Environment Variables

Defined in `.env.example`:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_NAME`
- `DATABASE_ENGINE`
- `LANGUAGE_CODE`
- `TIME_ZONE`

Important: never commit `.env` and never expose production secrets.

## Endpoint Contract (Frontend-Relevant)

### Authentication
- `POST /api/registration/` → object response (token + user info)
- `POST /api/login/` → object response (token + user info)

### Profile
- `GET /api/profile/{pk}/` → object
- `PATCH /api/profile/{pk}/` → object
- `GET /api/profiles/business/` → array
- `GET /api/profiles/customer/` → array

### Offers
- `GET /api/offers/` → paginated object (`count`, `next`, `previous`, `results`)
- `POST /api/offers/` → object with full `details`
- `GET /api/offers/{id}/` → object
- `PATCH /api/offers/{id}/` → object
- `DELETE /api/offers/{id}/` → 204 no content
- `GET /api/offerdetails/{id}/` → object

### Orders
- `GET /api/orders/` → array (not paginated)
- `POST /api/orders/` → object
- `PATCH /api/orders/{id}/` → object
- `DELETE /api/orders/{id}/` → 204 no content
- `GET /api/order-count/{business_user_id}/` → object
- `GET /api/completed-order-count/{business_user_id}/` → object

### Reviews
- `GET /api/reviews/` → array (not paginated)
- `POST /api/reviews/` → object
- `PATCH /api/reviews/{id}/` → object
- `DELETE /api/reviews/{id}/` → 204 no content

### Base Information
- `GET /api/base-info/` → object (`review_count`, `average_rating`, `business_profile_count`, `offer_count`)

## Permissions Summary

- Public: registration, login, base-info, offers list
- Auth required: profile, profile lists, order/review endpoints, offer details
- Business-only: create offers, update order status
- Customer-only: create orders, create reviews
- Staff-only: delete orders
- Owner-only: update/delete own offers, update/delete own reviews, edit own profile

## Project Structure

- `core/` central project config (`settings.py`, `urls.py`)
- `auth_app/` registration and login API
- `profile_app/` profile retrieval/update + profile lists
- `offers_app/` offer and offer detail endpoints
- `orders_app/` order lifecycle and counters
- `reviews_app/` review lifecycle
- `baseinfo_app/` platform aggregate statistics

Each app keeps API logic in its own `api/` package (`serializers.py`, `views.py`, `urls.py`).

## Notes for Submission/Deployment

- Keep `DEBUG=False` in production.
- Configure `ALLOWED_HOSTS` for deployment domain(s).
- Use HTTPS and secure secret handling in production.