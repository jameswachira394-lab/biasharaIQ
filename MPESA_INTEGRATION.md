# M-Pesa Integration Guide

## ✅ Setup Complete

Your M-Pesa sandbox integration is now configured with the following endpoints:

### Configuration Details
- **Environment**: Sandbox
- **Backend URL**: https://biasharaiq.onrender.com
- **Callback URL**: https://biasharaiq.onrender.com/payments/callback

---

## API Endpoints

### 1. Initiate Payment (STK Push)
**POST** `/payments/initiate`

Initiates an M-Pesa STK Push popup on the customer's phone.

**Request:**
```json
{
  "phone": "0712345678",
  "amount": 499
}
```

**Response (Success):**
```json
{
  "checkout_id": "ws_CO_DMZ_123456789",
  "message": "Success. Request accepted for processing"
}
```

**Response (Error):**
```json
{
  "detail": "error_message"
}
```

**How it works:**
1. User sends their phone and amount to initiate
2. M-Pesa STK Push appears on user's phone
3. User enters M-Pesa PIN to authorize payment
4. M-Pesa sends callback with transaction status
5. Backend processes callback and upgrades user to PRO plan

---

### 2. Check Payment Status
**GET** `/payments/status/{checkout_id}`

Check the status of a specific payment.

**Response:**
```json
{
  "status": "completed",
  "amount": 499.0,
  "receipt": "QFF61234567",
  "created_at": "2024-05-10T10:30:00"
}
```

**Status values:**
- `pending` - Payment awaiting confirmation
- `completed` - Payment successful
- `failed` - Payment failed

---

### 3. Payment Callback (M-Pesa → Backend)
**POST** `/payments/callback`

**Automatically handled by M-Pesa**. This endpoint receives callbacks from M-Pesa when a transaction completes.

---

## Testing the Integration

### Prerequisites
1. Ensure `.env` file is updated with M-Pesa credentials ✅
2. Backend is running
3. Database is accessible
4. Use M-Pesa sandbox test phone numbers

### Test Phone Numbers (Sandbox)
- **254708374149** - Test number 1
- **254702881281** - Test number 2
- **254720000000** - Test number 3

### Manual Testing Steps

#### Step 1: Start Backend
```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```

#### Step 2: Test Initiate Payment
Using cURL:
```bash
curl -X POST http://localhost:8000/payments/initiate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "phone": "254708374149",
    "amount": 499
  }'
```

Using Python:
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}

payload = {
    "phone": "254708374149",
    "amount": 499
}

response = requests.post(
    "http://localhost:8000/payments/initiate",
    json=payload,
    headers=headers
)

print(response.json())
```

#### Step 3: Check Payment Status
```bash
curl http://localhost:8000/payments/status/ws_CO_DMZ_123456789 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Step 4: Monitor Callbacks
Check backend logs to see M-Pesa callbacks:
```
[timestamp] INFO [request_id] Received M-Pesa callback: {...}
```

---

## Frontend Integration

### Add Payment Button to Pricing/Upgrade UI

**Example React Component:**
```jsx
// src/components/UpgradeButton.js
import { useState } from 'react';
import { api } from '@/utils/api';

export function UpgradeButton() {
  const [loading, setLoading] = useState(false);
  const [phone, setPhone] = useState('');

  const handleUpgrade = async () => {
    if (!phone) {
      alert('Please enter your M-Pesa phone number');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/payments/initiate', {
        phone: phone,
        amount: 499
      });

      const { checkout_id } = response.data;
      
      // Show message to user
      alert('STK Push sent! Enter your M-Pesa PIN');
      
      // Poll for payment status
      let attempts = 0;
      const statusInterval = setInterval(async () => {
        try {
          const statusResponse = await api.get(
            `/payments/status/${checkout_id}`
          );
          
          if (statusResponse.data.status === 'completed') {
            clearInterval(statusInterval);
            alert('✓ Payment successful! You are now on PRO plan');
            window.location.reload();
          }
        } catch (error) {
          console.log('Waiting for payment...');
        }

        attempts++;
        if (attempts > 60) { // 5 minutes timeout
          clearInterval(statusInterval);
          alert('Payment verification timeout');
        }
      }, 5000); // Check every 5 seconds

    } catch (error) {
      alert('Error: ' + error.response?.data?.detail || error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upgrade-form">
      <input
        type="tel"
        placeholder="Enter M-Pesa number (e.g., 0712345678)"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        disabled={loading}
      />
      <button 
        onClick={handleUpgrade}
        disabled={loading}
      >
        {loading ? 'Processing...' : 'Upgrade to PRO - KES 499'}
      </button>
    </div>
  );
}
```

---

## Daraja Dashboard Configuration

### Important: Verify Callback URL in Daraja

1. Go to https://developer.safaricom.co.ke
2. Click on your app
3. Navigate to "Lipa na M-Pesa Online" → "Test Credentials"
4. Verify the **Callback URL** is set to:
   ```
   https://biasharaiq.onrender.com/payments/callback
   ```
5. Note your:
   - Consumer Key ✅ Added to .env
   - Consumer Secret ✅ Added to .env
   - Shortcode (if different from 174379)
   - Passkey (for STK Push)

### If credentials differ from .env:
Update the `.env` file accordingly and restart the backend.

---

## Troubleshooting

### Issue: "Authentication failed" error
**Cause**: Invalid Consumer Key/Secret
**Solution**: 
1. Copy fresh credentials from Daraja dashboard
2. Update `.env` file
3. Restart backend

### Issue: "STK Push initiation failed"
**Cause**: Invalid phone number or amount
**Solution**:
1. Ensure phone format: `0712345678` or `254712345678`
2. Amount must be positive integer
3. Check Daraja credentials are correct

### Issue: Callback not received
**Cause**: Callback URL not set in Daraja or network issues
**Solution**:
1. Verify callback URL in Daraja dashboard
2. Check backend logs for POST requests
3. Ensure backend is publicly accessible
4. Test with ngrok for local development

### Issue: "Payment not found" after successful transaction
**Cause**: Database sync issue
**Solution**:
1. Check database connection
2. Verify Payment table exists (run migrations)
3. Check backend logs for errors during callback

---

## Database Schema

### Payment Table
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    phone_number VARCHAR NOT NULL,
    amount FLOAT NOT NULL,
    status VARCHAR DEFAULT 'pending',
    mpesa_receipt VARCHAR,
    checkout_request_id VARCHAR UNIQUE NOT NULL,
    merchant_request_id VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Security Considerations

1. **Never expose M-Pesa credentials** - Keep `.env` file secure
2. **Validate phone numbers** - Sanitize input before sending to M-Pesa
3. **Verify callbacks** - Check callback authenticity
4. **Use HTTPS** - Always use HTTPS for production
5. **Rate limit payment endpoints** - Prevent abuse

---

## Production Migration

When ready to go live:

1. Update `.env` variables:
   ```
   MPESA_ENVIRONMENT=production
   MPESA_CALLBACK_URL=https://production-domain.com/payments/callback
   ```

2. Get production M-Pesa credentials from Daraja:
   - Update Consumer Key/Secret
   - Update Shortcode (business shortcode, not test)
   - Update Passkey

3. Update Daraja app callback URL to production domain

4. Test with real M-Pesa account first with small amounts

5. Deploy backend changes

---

## Next Steps

- [ ] Test payment endpoint with sandbox phone number
- [ ] Implement frontend payment UI
- [ ] Deploy backend to production
- [ ] Switch to production M-Pesa credentials
- [ ] Monitor payment transactions in logs
- [ ] Set up payment notifications (email/SMS)
