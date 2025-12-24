# DZ-TourGuide - Local Tourist Guide Booking

## Software Presentation

DZ-TourGuide is a platform that connects tourists (local and international) with certified local tourist guides for personalized and authentic visits to cities, historical sites, or natural parks in Algeria. The project aims to promote local heritage, professionalize the guide profession, and offer travelers a rewarding and secure experience. The complexity of the project lies in managing tour offerings, planning bookings, and highlighting guide credibility.

## Scope and Minimum Viable Product (MVP)

The team must focus on delivering an MVP that allows a tourist to find a guide and book a predefined tour.

### MVP Features (mandatory for validation):

- **Dual Profiles**: Registration/login for "Guides" and "Tourists".
- **Guide Profile**: A guide can create a detailed public profile (photo, biography, spoken languages, covered regions, certifications).
- **Tour Management**: A guide can create predefined visit offers, called "Tours" (e.g., "Tour of the Casbah of Algiers in 3h"). Each tour has a title, description, duration, fixed price, and photos.
- **Tour Directory**: Tourists can browse the list of all offered tours and search them by city.
- **Booking Process**: A tourist can choose a date for a specific tour and send a booking request. The guide must manually approve the request.

### Advanced Features (to implement if the MVP is solid):

- Rating and review system for guides and tours.
- Advanced availability calendar for each guide.
- Integrated messaging to discuss visit details.
- Custom "tailor-made tour" requests where the tourist describes their wishes.
- Online payment and cancellation management.

## Detailed Functional Specifications

### Guide Profiles:

- Detailed profile highlighting the guide's expertise.
- Section to upload certification documents (visible only by administrators for verification).

### Tour Catalog:

- Guides create and manage their own offers.
- Each tour is a "product sheet" with a suggested itinerary, highlights, what's included/excluded.

### Booking and Reviews:

- The tourist selects a tour, proposes a date and time.
- The guide receives the request on their dashboard and can accept, refuse, or propose another time slot.
- After the visit, the tourist is invited to leave a comment and a rating.

## Specific Business Constraints (To be implemented mandatorily)

These rules are designed to add functional and technical depth to your project.

### Flexible Pricing Grid:

- Instead of a fixed price per tour, guides must define their base pricing on their profile:
  - A price for a half-day (up to 4 hours).
  - A price for a full day (from 4 to 8 hours).
  - A price per additional hour beyond 8 hours.
- When a guide creates a predefined "Tour" (e.g., duration of 3h), the system must automatically calculate and display the price based on their pricing grid (here, the half-day price). For custom requests, the price is calculated based on the duration requested by the tourist.

### Coverage Area Management:

- On their profile, a guide must be able to define their working areas by selecting one or more wilayas from a predefined list.
- When a guide creates a "Tour", the starting location of this tour must necessarily be located in one of their coverage wilayas.
- The main search engine must allow tourists to search for guides and tours by wilaya.

## External Data Integration

This task requires you to integrate real-time data to enrich the information presented to users.

**Task:** You must integrate a free weather API (like OpenWeatherMap). You will need to register to obtain an API key.

**Requirement:**

- For each "Tour", the guide must specify the approximate GPS coordinates of the starting point.
- On a tour's detail page, if a tourist selects a visit date within the next 5 days, your application must make a real-time call to the weather API.
- Then display a small "Forecasted Weather" section with the expected temperature and an icon representing the weather (sun, clouds, rain) for the day and location of the visit.

[Non-functional specifications: page 11]

## Additional Deliverables and Project-Specific Evaluation Criteria

### 1. Architecture Decision Journal (Mandatory Deliverable)

This document must explain the reasoning behind your design choices.

**Geographical Data Modeling:**

"For managing 'coverage areas' and tour locations, you could use simple strings (e.g., 'Algiers', 'Oran') or a more structured approach with Wilayas and Communes tables and geographical coordinates. To go further, you could have used a geospatial database extension like PostGIS. Which approach did you choose? Justify your decision in terms of search accuracy, implementation complexity, and future scalability (e.g., to search for guides within 20 km of a point)."

**API Design and Performance:**

"The call to the external weather API can slow down your page loading time. Describe the strategy you adopted to manage this. Is the call made server-side (backend) or client-side (frontend)? Did you implement a caching system to avoid unnecessarily calling the API if multiple users are viewing the same tour for the same date? Provide a sequence diagram of this interaction."

### 2. "Change of Course" Section in Sprint Reports

Demonstrate your ability to adapt and solve problems.

**Example:** "Our initial idea was that tourists would book time slots directly in a guide's calendar. We realized this didn't work, as a guide might refuse a tour for many reasons (fatigue, weather, etc.). Pivot: we changed the system to a 'booking request' model. The tourist proposes a date, and the guide has 24 hours to confirm. This gives more control to the guide and better manages tourist expectations."

### 3. Evaluation during the Oral Defense

Expect a technical exploration of your work.

**Navigate your code:**

"Show us the backend function or class that calculates the price of a tour based on duration and the guide's pricing grid. Explain how you handle edge cases (e.g., a tour of exactly 4 hours)."

**Modify code live:**

"Currently, a guide defines their working areas by wilaya. I want to refine this system. A guide should be able to exclude certain communes within a wilaya where they work. Show me the changes you would make to the data model and API to allow this exclusion."

**Debug a scenario:**

"A tourist is trying to book a tour in Algiers for tomorrow, but the weather section isn't displaying. Describe your debugging process. How would you check if your API key is correct? How would you inspect the request sent to the weather API and the response received? Are there any logs in place to trace these external calls?"
