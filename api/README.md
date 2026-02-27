# 🏆 Athlete Achievement & Organization API

This API serves as the backbone for managing athlete portfolios, organizational hierarchies, and school affiliations. It features a robust "Medal Cabinet" system using emoji-based achievements and strict multi-table inheritance for data integrity.

**Perfect for:** Building athlete portfolio platforms, sports management dashboards, and achievement tracking applications.

## 🚀 Base Configuration

* **API LIVE URL:** `https://admin.athlumesports.com/admin`
* **API DEV URL:** `https://timig.pythonanywhere.com`

* **API Root:** `{URL}/api/`
* **Auth Root:** `{URL}/api/auth/`
* **Header Required:** `Content-Type: application/json`

---

## 🔑 Authentication Endpoints

Handled by `dj-rest-auth`. All POST requests must include `Content-Type: application/json`.

| Action | Endpoint | Method | Required Fields |
| --- | --- | --- | --- |
| **Register** | `/api/auth/registration/` | `POST` | `username`, `email`, `password`, `re_password`, `role` |
| **Login** | `/api/auth/login/` | `POST` | `username`, `password` |
| **Logout** | `/api/auth/logout/` | `POST` | (Token required in header) |
| **Password Reset** | `/api/auth/password/reset/` | `POST` | `email` |
| **User** | `/api/auth/user/` | `GET` | `` |

### Role-Based Registration

When a user registers, they **must specify a `role`** - either `athlete` or `organization`. Based on the role, the backend automatically creates the appropriate record (Athlete or Organization owner).

**Login Response Example:**
```json
{
  "key": "a1b2c3d4e5f6g7h8i9j0",
  "user": {
    "id": 7,
    "email": "alex@example.com"
  }
}
```

**Register as Athlete (Minimal):**
```json
{
  "email": "alex@example.com",
  "password": "SecurePass123!",
  "re_password": "SecurePass123!",
  "role": "athlete"
}
```

**Register as Athlete (with optional details):**
```json
{
  "email": "alex@example.com",
  "password": "SecurePass123!",
  "re_password": "SecurePass123!",
  "role": "athlete",
  "first_name": "Alex",
  "last_name": "Smith",
  "phone": "555-1234",
  "sport": "Swimming",
  "school": "Lincoln High School"
}
```

**Register as Organization Manager:**
```json
{
  "email": "martin@example.com",
  "password": "SecurePass123!",
  "re_password": "SecurePass123!",
  "role": "organization",
  "org_name": "City Aquatics Sports Club",
  "phone": "555-5678"
}
```

**Role Field Options:**
- `"athlete"` - Registers user as an athlete with profile
- `"organization"` - Registers user as an organization/school manager

**Usage:** Save the `key` value and include it in the header for all protected requests:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0
```

**User Response Example:**
```json
{
  "id": 7,
  "email": "alex@example.com",
  "role": "athlete",
  "first_name": "Alex",
  "last_name": "Smith",
}
```

---

## Core Resources (`/api/v1/`)

### 1. App Home (`/api/v1/home/`)
#### Home
**GET** `/api/v1/home/` - Returns home screen data including featured athletes, recent highlights, top schools.

**Response Example:**
```json
{
  "banner_message": "Welcome to the Athlete Portal",
  "featured_athletes": [
    {
      "id": 1,
      "sport": "Swimming",
      "organization": 3,
      "organization_name": "City Aquatics"
    }
  ],
  "top_schools": [
    {
      "id": 1,
      "name": "Lincoln High School",
      "logo": "{API_URL}/org_logos/lincoln-logo.png"
    }
  ],
  "partner_organizations": [
    {
      "id": 3,
      "name": "City Aquatics",
      "logo": "{API_URL}/org_logos/logo.png",
      "owner": 5
    }
  ],
  "recent_highlights": [
    {
      "id": 1,
      "title": "New Season Kickoff",
      "body": "Athletes gather for the start of the new season...",
      "image": "{API_URL}/highlight_images/highlight.jpg",
      "url": "https://example.com/article",
      "published": true,
      "created_at": "2024-02-01T10:30:00Z"
    }
  ]
}

```
#### Search
**GET** `/api/v1/search/?q={query_param}` - Returns search results.

**Query Parameters:**
- `q` - Search string to filter athletes by name, email, sport, or organization. Returns up to 20 matching athletes.
**Response:**
```json
[
  {
    "id": 102,
    "first_name": "Marcus",
    "last_name": "Rashford",
    "email": "m.rashford@example.com",
    "sport": "Soccer",
    "school": "Manchester Academy",
    "organization_name": "United Sports Group",
    "profile_image": "{API_URL}/profile_picture/rashford.jpg"
  },
  {
    "id": 45,
    "first_name": "Alex",
    "last_name": "Morgan",
    "email": "amorgan@example.com",
    "sport": "Soccer",
    "school": "California High",
    "organization_name": "Pride Academy",
    "profile_image": null
  },
  {
    "id": 210,
    "first_name": "Sam",
    "last_name": "Kerr",
    "email": "skerr@soccerpro.au",
    "sport": "Soccer",
    "school": "Perth West",
    "organization_name": "Matildas Club",
    "profile_image": "{API_URL}/profile_picture/kerr.jpg"
  }
]
```

**Usage:**
```python
import requests

# Get home data
response = requests.get("https://example.com/api/v1/home/")
home_data = response.json()

# Search for athletes
response = requests.get(
    "https://example.com/api/v1/home/",
    params={"q": "Swimming"}
)
results = response.json()["search_results"]
```

---

### 2. Athletes (`/api/v1/athletes/`)

| Method | Endpoint | Auth Required |
| --- | --- | --- |
| `GET` | `/api/v1/athletes/` | No |
| `GET` | `/api/v1/athletes/{id}/` | No |
| `POST` | `/api/v1/athletes/` | Yes |
| `PATCH` | `/api/v1/athletes/{id}/` | Yes |
| `DELETE` | `/api/v1/athletes/{id}/` | Yes |

**Response Example:**
```json
{
  "id": 1,
  "sport": "Swimming",
  "organization": 3,
  "organization_name": "City Aquatics"
}
```

**Query Parameters:**
- `sport=Basketball` - Filter by sport
- `page=2` - Pagination
- `page_size=10` - Results per page

**POST Body Example:**
```json
{
  "user": 7,
  "sport": "Tennis",
  "organization": 2
}
```

---

### 3. Profiles (`/api/v1/profiles/`)

| Method | Endpoint | Auth Required | Purpose |
| --- | --- | --- | --- |
| `GET` | `/api/v1/profiles/{id}/` | No | Get full athlete profile with achievements & stats |
| `PATCH` | `/api/v1/profiles/{id}/` | Yes | Update profile info |

> **Note:** Athlete profile edits should be performed via a dedicated frontend form, not Django admin. The admin interface is reserved for staff management only.

**GET Response Example:**
```json
{
  "id": 1,
  "first_name": "Alex",
  "last_name": "Smith",
  "email": "alex@example.com",
  "bio": "Passionate swimmer aiming for Olympic gold!",
  "sport": "Swimming",
  "school": "Lincoln High School",
  "graduation_year": 2024,
  "organization_name": "City Aquatics",
  "profile_picture": "{API_URL}/profile_picture/profile-pic.jpg",
  "banner": "{API_URL}/profile_banner/banner.jpg",
  "youtube": "https://youtube.com/user/alexsmith",
  "facebook": "https://facebook.com/alexsmith",
  "x": "https://x.com/alexsmith",
  "instagram": "https://instagram.com/alexsmith",
  "achievements": [
    {
      "id": 1,
      "emoji": "🥇",
      "achievement": "State Champion 2023"
    }
  ],
  "stats": [
    {
      "id": 1,
      "date": "2024-01-15",
      "event": "Regional Championship",
      "performance": "1:52.34",
      "highlight": "New personal record"
    }
  ],
  "videos": [
    {
      "id": 1,
      "url": "https://youtube.com/watch?v=example1"
    }
  ]
}

```

**PATCH Body Example:**
```json
{
  "bio": "Updated bio text",
  "instagram": "https://instagram.com/newprofile",
  "graduation_year": 2025
}
```

---

### 4. Organizations (`/api/v1/organizations/`)

**GET** `/api/v1/organizations/` - Public list of organizations

**Response Example:**
```json
{
  "id": 1,
  "name": "City Aquatics",
  "logo": "{API_URL}/org_logos/aquatics-logo.png",
  "owner": 3
}
```

#### Organization Profile / Dashboard
Redirects to {BASE_URL}/admin/

---

### 5. Schools (`/api/v1/schools/`)

**GET** `/api/v1/schools/` - Public list (no auth required). Use for populating dropdowns.

**Response Example:**
```json
{
  "id": 1,
  "name": "Lincoln High School",
  "logo": "{API_URL}/org_logos/lincoln-logo.png"
}
```

---

## Python Examples

### Register as Athlete (with role)

```python
import requests

BASE_URL = "https://timig.pythonanywhere.com/api"

# Register as athlete - role field is REQUIRED
response = requests.post(
    f"{BASE_URL}/auth/registration/",
    json={
        "email": "alex@example.com",
        "password": "securePass123!",
        "re_password": "securePass123!",
        "role": "athlete",  # REQUIRED: 'athlete' or 'organization'
        "first_name": "Alex",
        "last_name": "Smith",
        "sport": "Swimming",
        "school": "Lincoln High School"
    }
)

if response.status_code == 201:
    token = response.json()["key"]
    print(f"Registered successfully! Token: {token}")
else:
    print(f"Error: {response.json()}")
```

### Register as Organization Manager (with role)

```python
import requests

BASE_URL = "https://timig.pythonanywhere.com/api"

# Register as organization manager
response = requests.post(
    f"{BASE_URL}/auth/registration/",
    json={
        "email": "martin@example.com",
        "password": "securePass123!",
        "re_password": "securePass123!",
        "role": "organization",  # REQUIRED: 'athlete' or 'organization'
        "org_name": "City Aquatics Sports Club",
        "phone": "555-5678"
    }
)

if response.status_code == 201:
    token = response.json()["key"]
    print(f"Organization registered successfully! Token: {token}")
```

### Login

```python
import requests

BASE_URL = "https://timig.pythonanywhere.com/api"

response = requests.post(
    f"{BASE_URL}/auth/login/",
    json={"email": "swimmer_alex@email.com", "password": "securePass123!"}
)
token = response.json()["key"]

# Use token for subsequent requests
headers = {"Authorization": f"Token {token}"}
```

### Get Athlete Profile

```python
import requests

# Fetch athlete profile (public, no auth needed)
response = requests.get("https://timig.pythonanywhere.com/api/v1/profiles/1/")
profile = response.json()

print(f"Name: {profile['first_name']} {profile['last_name']}")
print(f"Sport: {profile['sport']}")
print(f"Achievements: {[a['achievement'] for a in profile['achievements']]}")
```

### Update Profile

```python
import requests

token = "your_auth_token_here"
headers = {"Authorization": f"Token {token}"}

response = requests.patch(
    "https://timig.pythonanywhere.com/api/v1/profiles/1/",
    headers=headers,
    json={
        "bio": "New biography",
        "graduation_year": 2025,
        "instagram": "https://instagram.com/newprofile"
    }
)

if response.status_code == 200:
    updated_profile = response.json()
    print(f"Profile updated: {updated_profile['first_name']} {updated_profile['last_name']}")
```

### Get App Home Data

```python
import requests

# Fetch home screen data (featured athletes, recent highlights, top schools)
response = requests.get("https://timig.pythonanywhere.com/api/v1/home/")
home = response.json()

print(f"Featured athletes: {len(home['featured_athletes'])}")
print(f"Recent highlights: {len(home['recent_highlights'])}")
print(f"Top schools: {len(home['top_schools'])}")

# Search for athletes by name or sport
response = requests.get(
    "https://timig.pythonanywhere.com/api/v1/home/",
    params={"q": "Swimming"}
)
results = response.json().get("search_results", [])
print(f"Found {len(results)} swimming athletes")
```

### Filter Athletes by Sport

```python
import requests

# Get all swimming athletes
response = requests.get(
    "https://timig.pythonanywhere.com/api/v1/athletes/",
    params={"sport": "Swimming", "page_size": 10}
)
athletes = response.json()["results"]

for athlete in athletes:
    print(f"{athlete['first_name']} - {athlete['sport']}")
```

---

| Status Code | Meaning |
| --- | --- |
| `200 OK` | Request succeeded, data returned |
| `201 Created` | Resource created successfully |
| `204 No Content` | Request succeeded, no data to return |
| `400 Bad Request` | Invalid request data |
| `401 Unauthorized` | Missing or invalid token |
| `403 Forbidden` | Not permitted to access |
| `404 Not Found` | Resource doesn't exist |
| `500 Server Error` | Backend error |

---

## Pagination & Filtering

**List endpoints return paginated results:**

```
GET /api/v1/athletes/?page=2&page_size=10
```

Response includes:
- `results` - Array of items
- `count` - Total number of records
- `next` - URL for next page
- `previous` - URL for previous page

**Filter by query parameters:**

```
GET /api/v1/athletes/?sport=Swimming
GET /api/v1/athletes/?sport=Basketball&page_size=5
```

---

## Important Notes

1. **Token Storage:** Store the authentication token securely (environment variable, secure session, etc.).

2. **Multi-Table Inheritance:** An `Athlete ID` is the same as its corresponding `Profile ID`. Use the same ID to fetch full profile data.

3. **The Emoji Guard:** The backend validates that the `emoji` field contains actual emoji characters (🥇, 🏆, 💪, etc.). Standard text will be rejected.

4. **CORS:** Ensure your frontend origin is whitelisted in `CORS_ALLOWED_ORIGINS` on the server.

5. **Token Expiration:** If you receive `401 Unauthorized`, the token has expired—prompt the user to log in again.

6. **Athlete Profile Editing:** Athletes should update their profiles via a dedicated frontend form using the `PATCH /api/v1/profiles/{id}/` endpoint. Django admin is **not** intended for athlete use.

---

## Field Reference

### Profile Fields

| Field | Type | Readonly | Notes |
| --- | --- | --- | --- |
| `id` | Integer | ✓ | Unique identifier |
| `first_name` | String | ✗ | Required for profile completeness |
| `last_name` | String | ✗ | Required for profile completeness |
| `email` | String | ✓ | From user account |
| `bio` | String | ✗ | Max 500 characters recommended |
| `sport` | String | ✗ | e.g., "Swimming", "Basketball" |
| `school` | String | ✗ | School name or ID |
| `graduation_year` | Integer | ✗ | e.g., 2024, 2025 |
| `profile_picture` | URL | ✗ | Image URL |
| `banner` | URL | ✗ | Banner image URL |
| `youtube` | URL | ✗ | Full URL |
| `facebook` | URL | ✗ | Full URL |
| `x` | URL | ✗ | Full URL (formerly Twitter) |
| `instagram` | URL | ✗ | Full URL |
| `achievements` | Array | ✓ | Nested achievement objects |
| `stats` | Array | ✓ | Nested performance stat objects |
| `videos` | Array | ✓ | Nested video objects |

### Achievement Fields

| Field | Type | Notes |
| --- | --- | --- |
| `id` | Integer | Unique identifier |
| `emoji` | String | Must be an actual emoji character |
| `achievement` | String | Title/name of the achievement |

### Stat Fields

| Field | Type | Notes |
| --- | --- | --- |
| `id` | Integer | Unique identifier |
| `date` | Date | Format: YYYY-MM-DD |
| `event` | String | Event name/description |
| `performance` | String | Performance metric (time, score, etc.) |
| `highlight` | String | Notable performance detail |

---

## 📚 Additional Resources

* **Authentication:** Uses token-based auth from `dj-rest-auth`
* **API Framework:** Built with Django REST Framework
* **Database:** SQLite (development), PostgreSQL (production)
* **Documentation:** See individual endpoint docstrings for detailed parameter info

For questions or issues, contact the backend team or open an issue in the repository.

