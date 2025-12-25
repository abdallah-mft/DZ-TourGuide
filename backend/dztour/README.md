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

Returns a list of tours. Supports search and filtering by Duration rang, price range, and Wilaya.

**Query Parameters**

| Parameter      | Type             | Description                         |
| -------------- | ---------------- | ----------------------------------- |
| `search`       | string           | Search within title and description |
| `wilaya`       | string           | Filter by wilaya code               |
| `min_price`    | float            | Filter by minimum price             |
| `max_price`    | float            | Filter by maximum price             |
| `min_duration` | string (HH:MM:SS)| Filter by minimum duration          |
| `max_duration` | string (HH:MM:SS)| Filter by maximum duration          |

**Response**
```json
[
  {
    "id": 1,
    "title": "Sahara Sunset Trek",
    "description": "A 3-day journey through the dunes of Tassili.",
    "price": "25000.00",
    "duration_hours": 72,
    "wilaya": "33",
    "start_point_latitude": "24.492595",
    "start_point_longitude": "9.378052",
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

**Response**
```json
{
  "id": 1,
  "title": "Sahara Sunset Trek",
  "description": "A 3-day journey through the dunes of Tassili.",
  "price": "25000.00",
  "duration_hours": 72,
  "wilaya": "33",
  "start_point_latitude": "24.492595",
  "start_point_longitude": "9.378052",
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

**Body:**
| Field                  | Type             | Required | Description                          |
| ---------------------- | ---------------- | -------- | ------------------------------------ |
| title                  | text             | Yes      | Tour title                           |
| description            | text             | Yes      | Tour description                     |
| duration               | string (HH:MM:SS)| Yes      | Tour duration                        |
| wilaya                 | int              | Yes      | Wilaya code                          |
| start_point_latitude   | decimal          | Yes      | Start point latitude (-90 to 90)     |
| start_point_longitude  | decimal          | Yes      | Start point longitude (-180 to 180)  |

**Response:**
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
  "price": "25000.00",
  "start_point_latitude": "36.753768",
  "start_point_longitude": "3.058756"
}
```

---

### Update Tour
**PATCH** `/tours/{id}/`
**Auth**: Guide (Tour owner only)

Updates for title, description, price, or images.

---

### Delete Tour
**DELETE** `/tours/{id}/`
**Auth**: Guide (Tour owner only)

Removes the tour and associated media references.

---

### List Tours of the Authenticated Guide
**GET** `/tours/for-guide/`
**Auth**: Guide only

Returns a list of tours created by the authenticated guide.

----

### Add Tour Image
**POST** `/tours/{tour-id}/add-images/`
**Auth**: Guide (Tour owner only)

**Body:**
| Field | Type         | Required |
| ----- | ----         | -------- |
| image | List( file ) | Yes      |

**Response:**
```json
{
    "status": "Images uploaded successfully",
    "tour_id": 1,
    "count": 2,
    "images": [
        {
            "id": 1,
            "tour": 1,
            "image": "https://res.cloudinary.com/...",
            "created_at": "2025-01-01T10:00:00Z"
        },
        {
            "id": 2,
            "tour": 1,
            "image": "https://res.cloudinary.com/...",
            "created_at": "2025-01-01T10:00:00Z"
        }
    ]
}
```

---

### Delete Tour Image
**DELETE** `/tours/delete-image/{image-id}/`
**Auth**: Guide (Tour owner only)

----

## Bookings

The booking system allows tourists to book tours and guides to manage incoming booking requests. Bookings go through different status transitions based on actions from both parties.

**Status Values:**
- `pending` - Initial status when a booking is created
- `negotiated` - Date/time has been proposed by either party
- `accepted` - Guide has accepted the booking
- `rejected` - Guide has rejected the booking
- `cancelled` - Tourist has cancelled the booking

---

### Create Booking
**POST** `/tours/{tour_id}/book/`
**Auth**: Tourist only

Creates a new booking for a specific tour.

**Body:**
```json
{
  "date_time": "2025-12-30T14:00:00Z",
  "number_of_participants": 3
}
```

**Response:**
```json
{
  "id": 1,
  "tour": {
    "id": 5,
    "title": "Sahara Sunset Trek",
    "description": "A 3-day journey...",
    "price": "25000.00",
    "duration": "72:00:00",
    "guide": {
      "id": 7,
      "email": "guide@example.com",
      "first_name": "Ahmed",
      "last_name": "Benali"
    }
  },
  "tourist": {
    "id": 3,
    "email": "tourist@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "date_time": "2025-12-30T14:00:00Z",
  "number_of_participants": 3,
  "status": "pending",
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T10:00:00Z"
}
```

**Errors:**
- `403` - User is not a tourist or trying to book their own tour
- `400` - Date is in the past

---

### List Bookings
**GET** `/tours/bookings/`
**Auth**: Required

Returns bookings visible to the authenticated user:
- **Tourists** see bookings they created
- **Guides** see bookings for their tours

**Query Parameters:**

| Parameter | Type   | Description                    |
| --------- | ------ | ------------------------------ |
| `status`  | string | Filter by status (e.g., pending, accepted) |

**Response:**
```json
[
  {
    "id": 1,
    "tour": "Sahara Sunset Trek",
    "tourist": "John Doe",
    "date_time": "2025-12-30T14:00:00Z",
    "number_of_participants": 3,
    "status": "pending",
    "created_at": "2025-12-25T10:00:00Z",
    "updated_at": "2025-12-25T10:00:00Z"
  }
]
```

**Notes:**
- Results are ordered by status priority (negotiated → pending → accepted → rejected → cancelled)
- Within same status, most recently updated appear first

---

### Retrieve Booking
**GET** `/tours/bookings/{id}/`
**Auth**: Required (Tourist or Guide)

Returns detailed information about a specific booking.

**Response:**
```json
{
  "id": 1,
  "tour": {
    "id": 5,
    "title": "Sahara Sunset Trek",
    "guide": {
      "id": 7,
      "first_name": "Ahmed",
      "last_name": "Benali"
    }
  },
  "tourist": {
    "id": 3,
    "first_name": "John",
    "last_name": "Doe"
  },
  "date_time": "2025-12-30T14:00:00Z",
  "number_of_participants": 3,
  "status": "pending",
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T10:00:00Z"
}
```

---

### Update Booking
**PATCH** `/tours/bookings/{id}/`
**Auth**: Tourist (Booking creator only)

Allows tourists to update booking details before it's accepted.

**Allowed Fields:**
- `date_time` - The booking date/time
- `number_of_participants` - Number of people

**Body:**
```json
{
  "date_time": "2025-12-31T15:00:00Z",
  "number_of_participants": 4
}
```

**Response:**
```json
{
  "id": 1,
  "date_time": "2025-12-31T15:00:00Z",
  "number_of_participants": 4
}
```

**Restrictions:**
- Only bookings with status `pending` or `negotiated` can be updated
- Only the tourist who created the booking can update it
- Date cannot be in the past

**Errors:**
- `403` - User is not the booking creator
- `400` - Booking status doesn't allow updates (accepted/rejected/cancelled)
- `400` - Date is in the past

---

### Accept Booking
**POST** `/tours/bookings/{id}/accept/`
**Auth**: Guide only

Guide accepts a booking request.

**Response:**
```json
{
  "message": "Booking accepted successfully"
}
```
---

### Reject Booking
**POST** `/tours/bookings/{id}/reject/`
**Auth**: Guide only

Guide rejects a booking request.

**Response:**
```json
{
  "message": "Booking rejected successfully"
}
```
---

### Cancel Booking
**POST** `/tours/bookings/{id}/cancel/`
**Auth**: Tourist only

Tourist cancels their booking.

**Response:**
```json
{
  "message": "Booking cancelled successfully"
}
```

---

### Suggest New Date
**POST** `/tours/bookings/{id}/suggest-new-date/`
**Auth**: Tourist or Guide

Propose a new date/time for the booking. Changes status to `negotiated`.

**Body:**
```json
{
  "date_time": "2026-01-05T10:00:00Z"
}
```

**Response:**
```json
{
  "message": "New date suggested successfully"
}
```