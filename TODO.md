# TODO

## Completed
- [x] Fix login server 500 cause in `app/routers/athentication.py`:
  - `user.password` -> `user.hashed_password`
  - JWT claim `{"id": ...}` -> `{"sub": ...}`

## Remaining
- [ ] Adjust `tokenUrl` in `app/auth.py` if needed (frontend uses `/api/auth/login`, auth.py currently has `tokenUrl="/auth/login"`).
- [ ] Restart FastAPI server and verify:
  - `POST /api/auth/login` returns 200 with token
  - `GET /api/auth/me` works using Authorization: Bearer <token>

