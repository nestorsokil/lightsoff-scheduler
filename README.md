# LightsOff Scheduler
Imports https://poweron.loe.lviv.ua/ into Google Calendar ~~USING AI(omg-omg🔥)~~
(Turns out AI sucks at parsing precise image data, it's 99% correct but in 1% it just uses IMAGINATION, 
so I had to use good old OCR)

### Use
Public calendars:
- [Group 1.1](https://calendar.google.com/calendar/u/0?cid=YTVkMTc1MzkyOWM1NTc1NGI5YjdjMDY1MmJiYzVkZWY1ZmIyODNkMDY1NWY5NDlkNDQ4MTM4M2NjN2YwZjBmOUBncm91cC5jYWxlbmRhci5nb29nbGUuY29t)
- [Group 1.1](https://calendar.google.com/calendar/u/0?cid=YjJiY2JmNmE1Y2QxNGUzOTFkOWZlZTVkY2VlZjYxZWQ1ZTRkMTc2MTkzMTIyN2E4ZWIxMDM3MzEyNjY5ODYzOUBncm91cC5jYWxlbmRhci5nb29nbGUuY29t)
- [Group 2.1](https://calendar.google.com/calendar/u/0?cid=MDIyZjM3NjYzZDRhY2QyZjcwMmUzNGQ2MDUzMGY4Y2ZlOWRjMDljNDVmZDU5MDI2MTdhMjM4MWFlZDY0YjcxYUBncm91cC5jYWxlbmRhci5nb29nbGUuY29t)
- [Group 2.2](https://calendar.google.com/calendar/u/0?cid=MDM1ZjdhYmNjMGZhYzgyNzc5MjdlNDAzMzhjZDY4NGI5YTEwZmUyZTQyMjhiMThiODZhZDYzZjEzZWEyZmNjNUBncm91cC5jYWxlbmRhci5nb29nbGUuY29t)
- [Group 3.1](https://calendar.google.com/calendar/u/0?cid=N2RlNDE4MDAxODdmZjEzYjIxZWY4YmZlZWY3ZTY5ZmYxZDIwNTg0YmIzYTk4ZTlhMzc1NjZkMDQyZmY2ZDhjNEBncm91cC5jYWxlbmRhci5nb29nbGUuY29t)
- [Group 3.2](https://calendar.google.com/calendar/u/0?cid=ZTllZDJjMTIwOGE1MmNiMGE3N2Y2ZWFkZTYzM2Y4MmQ1YjMzNDc1MGE5ZDIzZjM1YTY1NzBhZDg5MjdjZTExMEBncm91cC5jYWxlbmRhci5nb29nbGUuY29t)

### Run

```
cp .env.template .env # update .env with values
docker-compose --build run lightsoff-scheduler
```
OR
```
python -m pip install -r requirements.txt
export $(cat .env | xargs) && python telethon_app.py
```

### Execution sample
![image](https://github.com/user-attachments/assets/526658df-353b-4495-b702-16a446e56521)
![image](https://github.com/user-attachments/assets/20c70c39-d278-4832-8597-b45076c54a98)
