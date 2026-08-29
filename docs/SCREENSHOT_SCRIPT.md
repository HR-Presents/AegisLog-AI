# Terminal screenshot script

For clean project screenshots, run against synthetic fixtures:

```bash
aegislog analyze examples/auth.log
aegislog incidents examples/auth.log
aegislog analyze examples/access.log
```

Do not capture terminals containing real hostnames, usernames, internal addresses, tokens, or production log data for public documentation.
