# M-Pesa Integration - Quick Start

## ✅ What's Been Set Up

Your M-Pesa sandbox payment integration is now complete with the following:

### Backend Configuration
- ✅ M-Pesa API credentials added to `.env`
- ✅ Payment endpoints ready at `/payments/*`
- ✅ Callback handler at `/payments/callback`
- ✅ Payment status checking
- ✅ Database models for payment tracking

### Environment Variables Configured
```
MPESA_CONSUMER_KEY=7A3lOLAZD4Q09FII8Y4JdejRQGvW6cmcLiZK3psRuYWFwbQV
MPESA_CONSUMER_SECRET=7pmRzp8lGf1ZX7gXnaAyKIGz8g60k1CNyTPNjVSJwZ1UoTfaVHbw5OLyJEpA2FX9
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=https://biasharaiq.onrender.com/payments/callback
MPESA_ENVIRONMENT=sandbox
```

---

## 🚀 Next Steps

### 1. Verify Daraja Configuration
Log into https://developer.safaricom.co.ke and confirm:
- [ ] Callback URL matches: `https://biasharaiq.onrender.com/payments/callback`
- [ ] Your Shortcode and Passkey are correct
- [ ] App is in sandbox/test mode

### 2. Test the Integration
```bash
# From project root
python test_mpesa_integration.py
```

### 3. Implement Frontend Payment UI
See `MPESA_INTEGRATION.md` for React component example

### 4. Deploy
```bash
git push  # Deploy to Render
```

---

## 📋 API Reference

### Initiate Payment
```
POST /payments/initiate
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "phone": "0712345678",
  "amount": 499
}
```

### Check Status
```
GET /payments/status/{checkout_id}
Authorization: Bearer {jwt_token}
```

### Callback (M-Pesa → Backend)
```
POST /payments/callback
(Automatically handled)
```

---

## 📚 Documentation

- **Full Integration Guide**: See `MPESA_INTEGRATION.md`
- **Daraja API Docs**: https://developer.safaricom.co.ke/
- **Testing Guide**: Run `python test_mpesa_integration.py`

---

## 🧪 Test Credentials

**Test Phone Numbers:**
- `254708374149`
- `254702881281`
- `254720000000`

**Test Amount:** Start with KES 1 to minimize risk

---

## ⚠️ Important Notes

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Test thoroughly in sandbox** before going live
3. **Callback URL must be publicly accessible** - Use localhost only for development
4. **Phone format**: Either `0712345678` or `254712345678`

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Authentication failed" | Check Consumer Key/Secret in Daraja |
| "STK Push initiation failed" | Verify phone number and amount format |
| No callback received | Check callback URL in Daraja, ensure backend is running |
| "Payment not found" | Verify database connection and Payment table exists |

For more help, see `MPESA_INTEGRATION.md` Troubleshooting section.

---

## 📞 Support

- M-Pesa Daraja Support: https://developer.safaricom.co.ke/support
- Backend Logs: `docker logs biasharaiq_backend`
- Check payment records: Query `payments` table in PostgreSQL

---

## ✨ What's Included

- Payment initiation (STK Push)
- Transaction status tracking
- Callback verification
- Automatic user upgrade to PRO plan
- Payment history & receipt tracking
- Error handling & logging

Ready to go! 🎉
