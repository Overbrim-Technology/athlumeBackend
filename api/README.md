This `README.md` that covers all your registered routes, including the **Schools** and **App Home** endpoints.

---

# 🏆 Athlete Achievement & Organization API

This API serves as the backbone for managing athlete portfolios, organizational hierarchies, and school affiliations. It features a robust "Medal Cabinet" system using emoji-based achievements and strict multi-table inheritance for data integrity.

## 🚀 Base Configuration

* **Live URL:** `https://yourusername.pythonanywhere.com`
* **API Root:** `/api/`
* **Auth Root:** `/api/auth/`

---

## 🔑 Authentication Endpoints

Handled by `dj-rest-auth`. All POST requests must include `Content-Type: application/json`.

| Action | Endpoint | Method | Required Fields |
| --- | --- | --- | --- |
| **Register** | `/api/auth/registration/` | `POST` | `username`, `email`, `password`, `re_password` |
| **Login** | `/api/auth/login/` | `POST` | `username`, `password` |
| **Logout** | `/api/auth/logout/` | `POST` | (Token required in header) |
| **Password Reset** | `/api/auth/password/reset/` | `POST` | `email` |

> **Note:** Upon successful login, you will receive a `key`. Include this in the header of all protected requests:
> `Authorization: Token <your_key_here>`

---

## 🏟 Core Resources (`/api/`)

### 1. App Home (`/api/home/`)

* **Method:** `GET`
* **Description:** A custom dashboard view. Usually returns high-level stats (e.g., total athletes, featured achievements, or user-specific greeting).

### 2. Athletes (`/api/athletes/`)

* **Methods:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
* **Description:** The central registry of all athletes.
* **Data:** Contains `sport`, `school`, `age`, and links to the `Organization`.

### 3. Profiles (`/api/profiles/`)

* **Methods:** `GET`, `PATCH`
* **Description:** The "Enhanced Athlete" view.
* **Key Feature:** This is where the **Achievements (Emojis)** and **Bio** are managed.
* **Example Usage:** Use `GET /api/profiles/{id}/` to fetch an athlete's medal cabinet.

### 4. Organizations (`/api/organizations/`)

* **Methods:** `GET` (Public), `POST/PUT` (Admin only)
* **Description:** Managed list of sports clubs and athletic organizations.

### 5. Schools (`/api/schools/`)

* **Methods:** `GET`
* **Description:** List of schools associated with the athletes. Useful for populating dropdowns in the frontend registration/edit forms.

---

## 🛠 Example API Usage

### Fetching a Specific Athlete Profile

**Request:**
`GET /api/profiles/5/`

**Response:**

```json
{
    "id": 5,
    "first_name": "Alex",
    "last_name": "Smith",
    "sport": "Swimming",
    "school_name": "Lincoln High",
    "organization_name": "City Aquatics",
    "achievements": [
        {"title": "State Champ", "emoji": "🥇"},
        {"title": "Record Breaker", "emoji": "🚀"}
    ]
}

```

### Filtering Athletes by Sport

**Request:**
`GET /api/athletes/?sport=Basketball`

---

## ⚠️ Important Implementation Notes

1. **Multi-Table Inheritance:** Remember that an `Athlete ID` is the same as its corresponding `Profile ID`. If you have the Athlete object, you have the key to their Profile.
2. **The Emoji Guard:** The backend will reject any `Achievement` creation that contains standard alphanumeric text in the `emoji` field.
3. **CORS:** Ensure your frontend origin is whitelisted in the `CORS_ALLOWED_ORIGINS` setting on the server.

---
