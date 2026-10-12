# âœ¨ Blessed Wigs â€” Luxury E-Commerce Web Application

A full-stack, editorial e-commerce platform built specifically for your Blessed luxury wig business. Powered by **Python & Django**, designed with a luxury palette of **Burgundy, Burnt Orange, Milk, Black, Silk Pink, and Pure White**.

---

## ðŸŽ¨ Artistic Palette & Design System

| Role | Color | Hex Code | Purpose in UI |
| :--- | :--- | :--- | :--- |
| **Pure White** | White | `#FFFFFF` | Clean background for maximum visual clarity and high-end feel |
| **Burgundy** | Deep Luxury Red | `#6B1D2F` | Headings, luxury accents, navbar logo, brand identity |
| **Burnt Orange** | Vibrant Sunset | `#D9531E` | **Key 2 (Ask button)**, discount pills, notification badges |
| **Milk / Cream** | Warm Luxury Ivory | `#FAF7F2` | Card backgrounds, subtle dividers, borders |
| **Silk Pink** | Soft Blush | `#F5C2B8` | Video preview accents, specification tags, delicate borders |
| **Black / Charcoal**| Jet Black | `#141414` | High-contrast editorial typography |
| **Emerald Green** | Rich Emerald | `#198754` | **Key 1 (Buy button)**, paid confirmation badges |

---

## ðŸ’Ž Core Features

### 1. Customer Experience
- **Personalized Greeting:** Top banner dynamically greets the visitor: *"Welcome, {Customer Name}"* with an easy 1-click name personalization remembered across visits.
- **Instagram / Social Ad Deep Linking:** Clicking any wig from an Instagram post (e.g. `https://yoursite.com/?wig=BW-101` or `/wig/raw-bone-straight-bw-101/`) automatically scrolls and pops open that exact wig.
- **Tap-to-Expand Wig Cards:** Tapping any wig photo smoothly reveals:
  - Vertical/horizontal HD video player showing hair bounce and texture.
  - Cap construction (HD lace, transparent, closure type).
  - Hair specs: length in inches, color code, origin.
  - Automatic **6% discount breakdown** showing original price crossed out and exact amount saved.
  - Stock remaining counter: e.g. *"Only 2 left in stock!"*.

### 2. The 3 Clickable Action Keys Under Each Wig
- ðŸŸ¢ **Key 1: BUY (Green):**
  - Takes customer to the dedicated payment screen.
  - Prominently displays the **2 Official Bank Accounts** with 1-click *"Copy Account Number"* buttons.
  - Collects customer shipping address, phone, email, and optional cap size notes.
  - Allows customer to upload their bank transfer screenshot/receipt.
  - Automatically dispatches an alert to your Blessed:
    > **"This product has been paid for â€” Product ID: #BW-101 (Customer: Chioma Adeyemi)"**
- ðŸŸ  **Key 2: ASK (Burnt Orange):**
  - Opens a chat inquiry drawer linked directly to that specific wig's Product ID.
  - Quick-prompt buttons: *"+ Side Part Style?"*, *"+ HD Lace type?"*, *"+ Delivery time?"*.
  - Logs the question in the admin dashboard so your Blessed can reply directly via WhatsApp or phone.
- ðŸ›’ **Key 3: CART:**
  - Adds items to the shopping cart drawer with an animated toast notification.
  - Calculates combined 6% discount savings and offers multi-wig checkout.

### 3. Customer Refund Guarantee
- Customers can request a refund for any paid product on the `/refund/` portal.
- Submits the **Product ID**, order number, and customer's bank details for reversal.
- Dispatches an automated refund alert to your Blessed:
  > **"Refund Request for Product ID: #BW-101"**

### 4. Blessed Store Command Hub
- **Blessed Portal:** Accessible at `/Blessed-portal/` for quick mobile monitoring of paid orders, transfer screenshots, customer questions, and refund requests.
- **Full Django Admin Suite:** Accessible at `/admin/` (Username: `admin`, Password: `blessedwigs2026!`). Allows your Blessed to:
  - Upload new wigs with photos, videos, length, color, and stock.
  - Edit the 2 official bank accounts anytime without touching code.
  - Update order status (*Paid*, *Processing*, *Shipped*, *Delivered*).

---

## ðŸš€ How to Run Locally

### 1. Activate the Virtual Environment
On Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Start the Development Server
```powershell
python manage.py runserver
```
Visit the store in your browser at: **`http://127.0.0.1:8000/`**

### 3. Log In to Admin
Visit **`http://127.0.0.1:8000/admin/`**  
- **Username:** `admin`  
- **Password:** `blessedwigs2026!`

---

## â˜ï¸ Cloud Deployment & Keeping It Up 24/7

### Option A: Free & Simple 1-Click Deploy on Render.com (Recommended)
1. Push this folder to a GitHub repository.
2. Sign up on [Render.com](https://render.com).
3. Click **New +** &rarr; **Blueprint** and connect your GitHub repo.
4. Render will automatically read `render.yaml`, build the application, run migrations, and provide a live URL (e.g. `https://blessed-wigs.onrender.com`).
5. Render keeps it up and running automatically with automatic SSL HTTPS certificates.

### Option B: Deploy with Docker
Run with Docker anywhere (AWS EC2, DigitalOcean, Google Cloud Run):
```bash
docker compose up -d
```
The Docker container includes automated health checks (`HEALTHCHECK`) and runs with production Gunicorn.

---

## ðŸ§ª Automated Test Suite
To verify the 6% discount mathematics, orders, and alert pipelines anytime:
```powershell
python manage.py test
```
All tests run in `< 0.2` seconds.

