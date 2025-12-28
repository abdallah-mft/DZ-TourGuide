# DZ-TourGuide — API Endpoints Implementation Order

  

This document lists all endpoints in chronological order of implementation based on dependencies.

  

---

  

## Phase 1: Authentication & User Management ✅ (COMPLETED)

  

| # | Method | Endpoint | Status |

|---|--------|----------|--------|

| 1 | POST | `/api/auth/register/` | ✅ Done |

| 2 | POST | `/api/auth/register/verify/` | ✅ Done |

| 3 | POST | `/api/auth/register/resend-otp/` | ✅ Done |

| 4 | POST | `/api/auth/token/` | ✅ Done |

| 5 | POST | `/api/auth/token/refresh/` | ✅ Done |

| 6 | GET | `/api/auth/me/` | ✅ Done |

| 7 | PATCH | `/api/auth/me/` | ✅ Done |

| 8 | POST | `/api/auth/logout/` | ✅ Done |

| 9 | POST | `/api/auth/password/reset/` | ✅ Done |

| 10 | POST | `/api/auth/password/confirm/` | ✅ Done |

  

---

  

## Phase 2: Reference Data ✅ (COMPLETED)

  

| # | Method | Endpoint | Status |

|---|--------|----------|--------|

| 11 | GET | `/api/guides/languages/` | ✅ Done |

| 12 | GET | `/api/guides/wilayas/` | ✅ Done |

| 13 | GET | `/api/guides/communes/` | ✅ Done |

  

---

  

## Phase 3: Guide Profiles ✅ (COMPLETED)

  

| # | Method | Endpoint | Status |

|---|--------|----------|--------|

| 14 | GET | `/api/guides/profiles/` | ✅ Done |

| 15 | GET | `/api/guides/profiles/{id}/` | ✅ Done |

| 16 | POST | `/api/guides/profiles/` | ✅ Done |

| 17 | GET | `/api/guides/profiles/me/` | ✅ Done |

| 18 | PATCH | `/api/guides/profiles/me/` | ✅ Done |

| 19 | DELETE | `/api/guides/profiles/me/` | ✅ Done |

  

---

  

## Phase 4: Certifications ✅ (COMPLETED)

  

| # | Method | Endpoint | Status |

|---|--------|----------|--------|

| 20 | GET | `/api/guides/certifications/` | ✅ Done |

| 21 | POST | `/api/guides/certifications/` | ✅ Done |

| 22 | DELETE | `/api/guides/certifications/{id}/` | ✅ Done |

  

---

  

## Phase 5: Tours ✅ (COMPLETED)

  

| # | Method | Endpoint | Status |

|---|--------|----------|--------|

| 23 | GET | `/api/tours/` | ✅ Done |

| 24 | GET | `/api/tours/{id}/` | ✅ Done |

| 25 | POST | `/api/tours/` | ✅ Done |

| 26 | PATCH | `/api/tours/{id}/` | ✅ Done |

| 27 | DELETE | `/api/tours/{id}/` | ✅ Done |

| 28 | GET | `/api/tours/for-guide/` | ✅ Done |

| 29 | POST | `/api/tours/{id}/add-images/` | ✅ Done |

| 30 | DELETE | `/api/tours/delete-image/{id}/` | ✅ Done |

  

---

  

## Phase 6: Booking System ✅ (COMPLETED)

  

| # | Method | Endpoint | Status |

|---|--------|----------|--------|

| 31 | POST | `/api/tours/{tour_id}/book/` | ✅ Done |

| 32 | GET | `/api/bookings/` | ✅ Done |

| 33 | GET | `/api/bookings/{id}/` | ✅ Done |

| 34 | POST | `/api/bookings/{id}/accept/` | ✅ Done |

| 35 | POST | `/api/bookings/{id}/reject/` | ✅ Done |

| 36 | POST | `/api/bookings/{id}/suggest-new-date/` | ✅ Done |

| 37 | POST | `/api/bookings/{id}/cancel/` | ✅ Done |

| 38 | POST | `/api/tours/book-custom/` | ✅ Done |

| 39 | GET | `/api/tours/my-custom-tours/` | ✅ Done |

  

---

  

## Phase 7: Reviews & Ratings ✅ (COMPLETED)

  

| # | Method | Endpoint | Status |

|---|--------|----------|--------|

| 40 | POST | `/api/reviews/` | ✅ Done |

| 41 | GET | `/api/reviews/` | ✅ Done |

| 42 | GET | `/api/reviews/{id}/` | ✅ Done |

| 43 | GET | `/api/tours/{id}/reviews/` | ✅ Done |

| 44 | GET | `/api/guides/profiles/{id}/reviews/` | ✅ Done |

| 45 | PATCH | `/api/reviews/{id}/` | ✅ Done |

| 46 | DELETE | `/api/reviews/{id}/` | ✅ Done |

  

---

  

## Phase 8: Weather Integration 🔄 (TO IMPLEMENT)

  

| # | Method | Endpoint | Description |

|---|--------|----------|-------------|

| 47 | GET | `/api/tours/{id}/weather/` | Get weather forecast for tour location |

  

**Query Parameters:**

- `date` (required): YYYY-MM-DD format, must be within 5 days

  

---

  

## Phase 9: Guide Dashboard 🔄 (TO IMPLEMENT)

  

| # | Method | Endpoint | Description |

|---|--------|----------|-------------|

| 48 | GET | `/api/guides/dashboard/` | Guide statistics (bookings, earnings, reviews) |

| 49 | GET | `/api/guides/dashboard/earnings/` | Earnings breakdown |

| 50 | GET | `/api/guides/dashboard/upcoming/` | Upcoming confirmed bookings |

  

---

  

## Phase 10: Availability Calendar (ADVANCED) 🔜 (OPTIONAL)

  

| # | Method | Endpoint | Description |

|---|--------|----------|-------------|

| 51 | GET | `/api/guides/availability/` | Get guide's availability slots |

| 52 | POST | `/api/guides/availability/` | Create availability slot |

| 53 | PATCH | `/api/guides/availability/{id}/` | Update availability slot |

| 54 | DELETE | `/api/guides/availability/{id}/` | Delete availability slot |

| 55 | GET | `/api/guides/profiles/{id}/availability/` | Public view of guide's available dates |

  

---

  

## Phase 11: Messaging System (ADVANCED) 🔜 (OPTIONAL)

  

| # | Method | Endpoint | Description |

|---|--------|----------|-------------|

| 56 | GET | `/api/conversations/` | List user's conversations |

| 57 | POST | `/api/conversations/` | Start new conversation |

| 58 | GET | `/api/conversations/{id}/messages/` | Get messages in conversation |

| 59 | POST | `/api/conversations/{id}/messages/` | Send message |

  

---

  

## Phase 12: Custom Tour Requests (ADVANCED) ✅ (COMPLETED)

  

| # | Method | Endpoint | Status |

|---|--------|----------|-------------|

| 60 | POST | `/api/tours/book-custom/` | ✅ Done |

| 61 | GET | `/api/tours/my-custom-tours/` | ✅ Done |

| 62 | GET | `/api/bookings/{id}/` | ✅ Done (via bookings) |

| 63 | POST | `/api/bookings/{id}/suggest-new-date/` | ✅ Done (negotiation) |

| 64 | POST | `/api/bookings/{id}/accept/` | ✅ Done |

  

---

  

## Phase 13: Admin & Moderation 🔜 (OPTIONAL)

  

| # | Method | Endpoint | Description |

|---|--------|----------|-------------|

| 65 | GET | `/api/admin/guides/pending/` | List guides pending verification |

| 66 | POST | `/api/admin/guides/{id}/verify/` | Verify guide |

| 67 | POST | `/api/admin/guides/{id}/reject/` | Reject guide verification |

| 68 | GET | `/api/admin/reports/` | List reported content |

| 69 | POST | `/api/admin/reports/{id}/action/` | Take action on report |

  

---

  

## Implementation Priority Summary

  

### MVP (Mandatory):

1. ✅ Phases 1-7 (Auth, Reference Data, Guides, Certifications, Tours, Bookings, Reviews)

2. 🔄 Phase 8 (Weather Integration) — **NEXT PRIORITY**

3. 🔄 Phase 9 (Guide Dashboard)

  

### Advanced Features:

4. 🔜 Phase 10 (Availability Calendar)

5. 🔜 Phase 11 (Messaging)

6. ✅ Phase 12 (Custom Tour Requests) — Integrated into Bookings

7. 🔜 Phase 13 (Admin & Moderation)

  

---

  

## Legend

  

| Symbol | Meaning |

|--------|---------|

| ✅ | Completed |

| 🔄 | To Implement (MVP) |

| 🔜 | Future/Optional |