---
id: 0010
title: Investigate AddrParseError and Password Storage Issues
stage: red
date: 2025-12-03
surface: agent
model: gemini-2.0-flash
feature: 004-personalized-auth
branch: unknown
user: mac
command: none
labels: ["investigation", "database", "schema", "migration", "prisma", "postgres"]
links:
  spec: specs/004-personalized-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/database/migrations/001_create_auth_tables.py
 - auth-server/prisma/schema.prisma
 - auth-server/src/auth/auth.config.ts
tests:
 - none
---

## Prompt

It is still giving this error:
prisma:error
Invalid `db[model].create()` invocation ... cause: Some(AddrParseError(Ip)) ...
And it's also not storing password in the neon db how is it going to authenticate then?

## Response snapshot

Investigated the persistent `AddrParseError` and missing password issue. Identified a root cause schema mismatch: the Python migration defines `ip_address` as `INET`, while the Prisma schema expects a `String`. Similarly, `password_hash` is non-nullable in the DB but optional in Prisma. Confirmed that simply updating `schema.prisma` isn't enough; the actual Postgres table must be updated via a new Alembic migration to `VARCHAR` to support the string input from `better-auth`.

## Outcome

- ✅ Impact: Identified root cause of database errors (Schema mismatch between Alembic INET and Prisma String).
- 🧪 Tests: none
- 📁 Files: Analyzed `backend/src/database/migrations/001_create_auth_tables.py` and `auth-server/prisma/schema.prisma`.
- 🔁 Next prompts: Create new Alembic migration to alter column types and fix schema sync.
- 🧠 Reflection: When using two different ORMs/migration tools (Alembic vs Prisma), they must agree perfectly on types. `INET` is stricter than `String`.

## Evaluation notes (flywheel)

- Failure modes observed: Schema drift between different backend services sharing a DB.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): standard
- Next experiment (smallest change to try): none