
# Freelance Notifier Bot

GitHub, Upwork (email orqali) va boshqa saytlar xatlaridan keladigan zakaz/xabarlarni Telegram bot orqali PUSH qilib turish uchun mini-sistema.

## Tuzilma

- `bot.py` — Telegram bot. Foydalanuvchini `/start` orqali roʻyxatdan oʻtkazadi va chat_id larni `chat_ids.json` faylida saqlaydi.
- `checker.py` — GitHub notificationlari va email (Upwork va boshqalar) ni tekshiradi va yangi xabar bo'lsa shu bot orqali yuboradi.
- `requirements.txt` — py kutubxonalar.
- `.env.example` — sozlamalar namuna fayli.

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`.env` faylini yaratib (`.env.example` dan nusxa olib), o'zingizning token/parollarni kiriting.

## Botni ishga tushirish

```bash
python bot.py
```

Telegramda botga `/start` yozib yuboring.

## Notifierni ishga tushirish

Bir marta sinab ko'rish uchun:

```bash
python checker.py
```

Real ishda cron (Linux) yoki Task Scheduler (Windows) bilan har 1-5 daqiqada `checker.py` ni ishga tushirib turasiz.
