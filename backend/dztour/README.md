**Endpoints:**
```http
POST   /api/auth/register/          # Register a new user    ✔️
POST   /api/auth/token/             # Login, returns JWT     ✔️
POST   /api/auth/token/refresh/     # Refresh JWT            ✔️
GET    /api/auth/me/                # Get current user info  ✔️
PATCH    /api/auth/me/              # Update user profile    ✔️
OAuth     /api/google/login/        # Google OAuth protocole ✔️  
````


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
