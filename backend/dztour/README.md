# DZ-TourGuide Backend API

A **modular, production-oriented Django REST Framework backend** for connecting tourists with certified local tour guides across **Algeria’s 58 wilayas**.

The system is designed around **role-based access**, **JWT authentication**, **email verification**, and **extensible domain models** to support future features such as bookings, reviews, availability, payments, and moderation.

> ⚠️ **Status**: Active development — API surface and data models may evolve.

---

## API Conventions

* **Base URL**: `http://localhost:8000/api`
* **Auth Header**:

  ```http
  Authorization: Bearer <access_token>
  ```
* **Default Content-Type**: `application/json`
* **File Uploads**: `multipart/form-data`
* **Date/Time**: ISO-8601
* **Currency**: DZD (decimal string)

---

## Authentication & Users

### Roles

| Role    | Description                         |
| ------- | ----------------------------------- |
| tourist | Default user, can browse guides     |
| guide   | Can create and manage guide profile |

---

### Register

**POST** `/auth/register/`

Registers a user and sends an OTP to the email address.

**Body**

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "tourist"
}
```

**Notes**

* `role` defaults to `tourist`
* Password must meet Django validators

**Response**

```json
{
  "message": "Registration successful. Verify your email.",
  "email": "user@example.com"
}
```

---

### Verify Email (OTP)

**POST** `/auth/register/verify/`

**Body**

```json
{
  "email": "user@example.com",
  "otp": "4832"
}
```

**Response**

```json
{
  "message": "Email verified successfully.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "tourist"
  },
  "refresh": "<jwt_refresh>",
  "access": "<jwt_access>"
}
```

**Errors**

* `400` – invalid or expired OTP
* `404` – email not found

---

### Resend OTP

**POST** `/auth/register/resend-otp/`

Resends a new OTP to the user's email. Previous OTP is invalidated.

**Body**

```json
{
  "email": "user@example.com"
}
```

**Response**

```json
{
  "message": "New OTP sent successfully."
}
```

**Errors**

* `400` – email already verified
* `404` – user not found

---

### Login

**POST** `/auth/token/`

**Body**

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

**Response**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "tourist"
  },
  "refresh": "<jwt_refresh>",
  "access": "<jwt_access>"
}
```

---

### Refresh Token

**POST** `/auth/token/refresh/`

**Body**

```json
{
  "refresh": "<jwt_refresh>"
}
```

**Response**

```json
{
  "access": "<new_access_token>"
}
```

---

### Current User

**GET** `/auth/me/`

**Auth**: Required

**Response**

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "tourist",
  "is_email_verified": true
}
```

---

### Update User

**PATCH** `/auth/me/`

**Auth**: Required

**Body**

```json
{
  "first_name": "Updated",
  "last_name": "Name"
}
```

Only provided fields are updated.

---

### Logout

**POST** `/auth/logout/`

Blacklists the refresh token.

**Body**

```json
{
  "refresh": "<jwt_refresh>"
}
```

---

### Password Reset Request

**POST** `/auth/password/reset/`

Sends a 4-digit OTP to the user's email for password reset.

**Body**

```json
{
  "email": "user@example.com"
}
```

**Response**

```json
{
  "detail": "If the email exists, a reset code has been sent."
}
```

**Notes**

* Does not reveal if email exists (security)
* OTP expires in 15 minutes
* User must be verified to reset password

---

### Password Reset Confirm

**POST** `/auth/password/confirm/`

Resets the user's password using the OTP received via email.

**Body**

```json
{
  "email": "user@example.com",
  "otp": "4821",
  "new_password": "NewSecurePass123!"
}
```

**Response**

```json
{
  "detail": "Password reset successful."
}
```

**Errors**

* `400` – invalid/expired OTP, weak password, or missing fields
* `404` – user not found

**Password Requirements**

* Minimum 8 characters
* Cannot be too similar to user info
* Cannot be a common password
* Cannot be entirely numeric

---

## Guides Domain

---

## Reference Data (Public)

### Languages

**GET** `/guides/languages/`

```json
[
  { "id": 1, "code": "ar", "name": "Arabic" },
  { "id": 2, "code": "fr", "name": "French" }
]
```

---

### Wilayas

**GET** `/guides/wilayas/`

```json
[
  { "code": "16", "name_fr": "Alger", "name_ar": "الجزائر" }
]
```

---

### Communes

**GET** `/guides/communes/?wilaya=16`

```json
[
  {
    "code": "1601",
    "name_fr": "Bab El Oued",
    "name_ar": "باب الواد",
    "wilaya": "16"
  }
]
```

---

## Guide Profiles

---

### List Guides (Public)

**GET** `/guides/profiles/`

Supports pagination and future filtering.

```json
[
  {
    "id": 3,
    "user": {
      "id": 7,
      "first_name": "Ahmed",
      "last_name": "Benali"
    },
    "bio": "Licensed guide in Algiers",
    "price_for_day": "10000.00",
    "languages_spoken": ["ar", "fr"],
    "wilaya_covered": ["16"],
    "is_verified": false
  }
]
```

---

### Guide Detail (Public)

**GET** `/guides/profiles/{id}/`

---

### Create Guide Profile

**POST** `/guides/profiles/`
**Auth**: Guide only
**Content-Type**: `multipart/form-data`

| Field               | Type  | Required |
| ------------------- | ----- | -------- |
| bio                 | text  | No       |
| price_for_half_day  | text  | No       |
| price_for_day       | text  | No       |
| price_for_sup_hours | text  | No       |
| phone_number        | text  | No       |
| whatsapp_number     | text  | No       |
| instagram_account   | text  | No       |
| languages_spoken    | int[] | No       |
| wilaya_covered      | int[] | No       |
| commune_covered     | int[] | No       |
| id_document         | file  | No       |

**Notes**

* Arrays are submitted as repeated form keys
* Only **one profile per guide**

---

### My Guide Profile

**GET** `/guides/profiles/me/`

---

### Update My Profile

**PATCH** `/guides/profiles/me/`
**Content-Type**: `multipart/form-data`

Partial updates supported.

---

### Delete My Profile

**DELETE** `/guides/profiles/me/`

Irreversible.

---

## Certifications

---

### List Certifications

**GET** `/guides/certifications/`

---

### Add Certification

**POST** `/guides/certifications/`
**Content-Type**: `multipart/form-data`

| Field | Type | Required |
| ----- | ---- | -------- |
| name  | text | Yes      |
| file  | file | Yes      |

---

### Delete Certification

**DELETE** `/guides/certifications/{id}/`

---

## Media & Uploads

* Stored via **Cloudinary**
* MIME type validation enforced
* Size limits configurable
* Designed for moderation workflows

---
## Tours

---

### List Tours
**GET** `/tours/`
**Auth**: Public

Supports pagination and filtering by `wilaya`, `category`, and `price_range`.

```json
[
  {
    "id": 1,
    "title": "Sahara Sunset Trek",
    "description": "A 3-day journey through the dunes of Tassili.",
    "price": "25000.00",
    "duration_hours": 72,
    "wilaya": "33",
    "guide": {
      "id": 7,
      "first_name": "Ahmed"
    },
    "main_image": "https://res.cloudinary.com/..."
  }
]
```

---

### Tour Detail
**GET** `/tours/{id}/`
**Auth**: Public

```json
{
  "id": 1,
  "title": "Sahara Sunset Trek",
  "description": "A 3-day journey through the dunes of Tassili.",
  "price": "25000.00",
  "duration_hours": 72,
  "wilaya": "33",
  "guide": {
    "id": 7,
    "first_name": "Ahmed"
  },
  "main_image": "https://res.cloudinary.com/..."
}
```

---

### Create Tour
**POST** `/tours/`
**Auth**: Guide only

| Field       | Type             | Required |
| ----------- | ---------------- | -------- |
| title       | text             | Yes      |
| description | text             | Yes      |
| duration    | string (HH:MM:SS)| Yes      |
| wilaya      | int              | Yes      |
| images      | files            | No       |

**Response**
```json
{
  "id": 1,
  "guide": {
    "id": 7,
    "email": "guide@example.com",
    "full_name": "Ahmed Guide",
    "role": "guide",
    "phone": "+213123456789",
    "created_at": "2025-01-01T10:00:00Z",
    "profile_picture": null,
    "is_active": true
  },
  "pictures": [],
  "title": "Sahara Sunset Trek",
  "description": "A 3-day journey through the dunes of Tassili",
  "duration": "72:00:00",
  "price": "25000.00"
}
```

---

### Update Tour
**PATCH** `/tours/{id}/`
**Auth**: Guide (Tour owner only)

Partial updates for title, description, price, or images.

---

### Delete Tour
**DELETE** `/tours/{id}/`
**Auth**: Guide (Tour owner only)

Removes the tour and associated media references.
