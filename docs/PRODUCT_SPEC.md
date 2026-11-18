# CareerRank — Production-Ready AI Job Search Intelligence Platform

## 1. Document Purpose

This specification defines the product requirements, system architecture, ML/AI architecture, data model, APIs, infrastructure, security model, observability plan, and testing strategy for **CareerRank**, an outcome-driven AI job search intelligence platform.

The intended audience is:
- A software engineer implementing the product in Cursor or another coding agent.
- AI/ML engineers extending ranking, recommendation, and evaluation systems.
- Reviewers evaluating the project as a production-quality portfolio application.

The product must be implementable incrementally. Every major subsystem should work independently before more advanced AI/ML capabilities are added.

---

# 2. Product Vision

CareerRank helps a candidate answer:

1. Which jobs should I apply to?
2. Why is a job a strong or weak match?
3. Which resume version performs best for each role category?
4. Which skills appear most correlated with interview success?
5. Why am I not getting interviews?
6. Which future jobs are most likely to result in a positive outcome?
7. How should I adjust my application strategy based on actual outcomes?

Unlike a generic job board, CareerRank is designed around **closed-loop learning**:

```text
Candidate Profile
      ↓
Job Collection
      ↓
Job Ranking
      ↓
Application
      ↓
Outcome Tracking
      ↓
Analytics / Learning
      ↓
Improved Ranking
```

---

# 3. Core Differentiation

The product is NOT primarily:
- a generic job board,
- a resume builder,
- an autofill browser extension,
- or a chatbot wrapper.

Its differentiating systems are:

- Explainable candidate-job matching.
- Historical application outcome tracking.
- Resume-version performance tracking.
- Outcome-aware recommendation.
- Skill-gap analytics grounded in the candidate's own data.
- Candidate-specific ranking model.
- Experimentation and A/B analysis.
- AI career strategy agent backed by structured analytics tools.
- Model evaluation and monitoring dashboard.

---

# 4. Scope

## 4.1 MVP Scope

The MVP must support:

1. User authentication.
2. Resume upload.
3. Resume parsing into structured profile data.
4. Job ingestion by URL or manual entry.
5. Job parsing into structured requirements.
6. Candidate-job fit scoring.
7. Explainable match results.
8. Save / ignore / apply workflow.
9. Application outcome tracking.
10. Dashboard with funnel analytics.
11. Resume-version tracking.
12. Basic skill-gap analytics.
13. AI career strategy chat using tool calling.
14. PostgreSQL persistence.
15. Vector retrieval.
16. Background job processing.
17. Automated tests.
18. Production deployment.

## 4.2 Phase 2

- Resume A/B analysis.
- Personalized interview-probability model.
- Learning-to-rank.
- Automated job ingestion.
- Email-based outcome detection.
- Job deduplication.
- Job freshness detection.
- Feedback-driven ranking optimization.
- Team/admin observability dashboard.
- Multi-model benchmarking.

## 4.3 Explicit Non-Goals for MVP

Do not initially build:
- browser autofill,
- automatic job application submission,
- referral discovery,
- scraping protected websites in violation of terms,
- autonomous email sending,
- fully automated resume rewriting,
- custom LLM training,
- reinforcement learning.

---

# 5. User Personas

## 5.1 Primary Persona

Recent graduate or early-career SWE / AI engineer who applies to many jobs and wants data-driven guidance.

## 5.2 Secondary Persona

Experienced technical job seeker who maintains multiple resume variants and wants to optimize job targeting.

---

# 6. Main User Stories

## Authentication

- As a user, I can register.
- As a user, I can log in.
- As a user, I can reset my password.
- As a user, my data is isolated from other users.

## Resume

- As a user, I can upload PDF or DOCX resumes.
- As a user, I can create multiple resume versions.
- As a user, I can mark one resume as default.
- As a user, I can see parsed skills, roles, companies, education, projects, and experience.

## Jobs

- As a user, I can paste a job URL.
- As a user, I can manually create a job record.
- As a user, I can save jobs for later.
- As a user, I can mark jobs ignored, applied, interviewing, rejected, or offered.

## Matching

- As a user, I can see a 0-100 fit score.
- As a user, I can see why that score was assigned.
- As a user, I can inspect:
  - required skills matched,
  - missing required skills,
  - preferred skills matched,
  - seniority mismatch,
  - location mismatch,
  - experience mismatch,
  - semantic similarity,
  - resume evidence.

## Analytics

- As a user, I can view:
  - application count,
  - interview rate,
  - rejection rate,
  - offer rate,
  - response rate,
  - average match score,
  - outcomes by role category,
  - outcomes by resume version,
  - outcomes by skill.

## AI Career Agent

- As a user, I can ask:
  - "Why am I not getting interviews?"
  - "Which roles should I focus on?"
  - "Which resume performs better?"
  - "Which missing skills matter most?"
  - "Should I keep applying to ML Engineer jobs?"

The agent must answer using application data, ranking data, and analytics tools rather than relying only on raw LLM intuition.

---

# 7. Recommended Technology Stack

## Frontend

- Next.js 15+
- TypeScript
- React
- Tailwind CSS
- shadcn/ui or MUI
- TanStack Query
- Zod
- Recharts or ECharts

## Backend API

Preferred:
- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic

Alternative:
- TypeScript + NestJS

Use FastAPI if emphasizing AI engineering.

## Database

- PostgreSQL 16+
- pgvector extension

## Cache / Queue

- Redis
- Celery, Dramatiq, RQ, or Arq

Recommended:
- Celery for mature job processing.
- Redis as broker/cache.

## Object Storage

- AWS S3 or S3-compatible storage.

## AI Providers

Abstract behind provider interfaces.

Supported:
- OpenAI-compatible LLM provider
- Embedding provider
- Optional reranker provider

Do not hardcode the system to one vendor.

## Deployment

Recommended production architecture:

- Vercel: frontend
- AWS ECS/Fargate or Render/Fly.io: backend
- AWS RDS PostgreSQL
- AWS ElastiCache Redis
- AWS S3
- Cloudflare optional
- GitHub Actions CI/CD

Simpler portfolio deployment:

- Vercel frontend
- Railway/Render backend
- Supabase PostgreSQL + pgvector
- Upstash Redis
- S3 or Supabase Storage

---

# 8. Monorepo Structure

```text
careerrank/
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── tests/
│   │
│   └── api/
│       ├── app/
│       │   ├── api/
│       │   ├── core/
│       │   ├── db/
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── services/
│       │   ├── repositories/
│       │   ├── ml/
│       │   ├── ai/
│       │   ├── workers/
│       │   └── observability/
│       └── tests/
│
├── packages/
│   ├── shared-types/
│   ├── prompts/
│   └── evals/
│
├── infra/
│   ├── docker/
│   ├── terraform/
│   └── monitoring/
│
├── scripts/
├── docs/
├── .github/workflows/
├── docker-compose.yml
└── README.md
```

---

# 9. Local Development Setup

## Prerequisites

Install:
- Node.js 22+
- Python 3.12+
- Docker Desktop
- PostgreSQL client tools
- Git
- pnpm

## Environment Variables

Create `.env.example`.

```env
# General
APP_ENV=development
APP_URL=http://localhost:3000
API_URL=http://localhost:8000

# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/careerrank

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth
JWT_SECRET=replace_me
JWT_ACCESS_TTL_MINUTES=30
JWT_REFRESH_TTL_DAYS=14

# Storage
S3_BUCKET=careerrank-dev
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# AI
LLM_PROVIDER=openai
LLM_API_KEY=
LLM_MODEL=
EMBEDDING_MODEL=
RERANKER_MODEL=

# Observability
SENTRY_DSN=
OTEL_EXPORTER_OTLP_ENDPOINT=
```

## Docker Compose Services

Must include:

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16

  redis:
    image: redis:7

  api:
    build: ./apps/api

  worker:
    build: ./apps/api
    command: celery -A app.worker worker --loglevel=info

  web:
    build: ./apps/web
```

## Setup Commands

```bash
pnpm install

cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d postgres redis

alembic upgrade head

pnpm dev
```

---

# 10. High-Level System Design

```text
                ┌─────────────────────┐
                │      Next.js UI     │
                └──────────┬──────────┘
                           │ HTTPS
                           ↓
                ┌─────────────────────┐
                │     FastAPI API     │
                └─────┬──────┬────────┘
                      │      │
          ┌───────────┘      └─────────────┐
          ↓                                ↓
┌──────────────────┐             ┌──────────────────┐
│   PostgreSQL     │             │      Redis       │
│ + pgvector       │             │ Cache / Queue    │
└────────┬─────────┘             └─────────┬────────┘
         │                                 │
         ↓                                 ↓
┌──────────────────┐             ┌──────────────────┐
│     Storage      │             │ Background Worker│
│       S3         │             │ Parse / Embed /  │
└──────────────────┘             │ Score / Evaluate │
                                 └─────────┬────────┘
                                           ↓
                                ┌──────────────────┐
                                │ AI/ML Providers  │
                                └──────────────────┘
```

---

# 11. Request Flow

## Job Ingestion

```text
POST /jobs/import
      ↓
Create pending Job
      ↓
Push background task
      ↓
Fetch / parse content
      ↓
Normalize description
      ↓
Extract structured fields
      ↓
Generate embedding
      ↓
Store job + embedding
      ↓
Run candidate matching
```

## Resume Ingestion

```text
Upload PDF/DOCX
      ↓
Store original in object storage
      ↓
Extract text
      ↓
Parse structured profile
      ↓
Normalize skills
      ↓
Generate embedding
      ↓
Persist ResumeVersion
      ↓
Update CandidateProfile
```

---

# 12. Database Schema

## users

```text
id UUID PK
email VARCHAR UNIQUE
password_hash VARCHAR
created_at TIMESTAMP
updated_at TIMESTAMP
```

## candidate_profiles

```text
id UUID PK
user_id UUID FK
headline VARCHAR
years_experience FLOAT
preferred_roles JSONB
preferred_locations JSONB
work_authorization JSONB
remote_preference VARCHAR
created_at
updated_at
```

## resumes

Logical resume identity.

```text
id UUID PK
user_id UUID FK
name VARCHAR
is_default BOOLEAN
created_at
updated_at
```

## resume_versions

```text
id UUID PK
resume_id UUID FK
version_number INT
file_url VARCHAR
raw_text TEXT
parsed_json JSONB
embedding VECTOR
created_at
```

## skills

```text
id UUID PK
canonical_name VARCHAR UNIQUE
category VARCHAR
aliases JSONB
embedding VECTOR
```

## candidate_skills

```text
candidate_profile_id UUID FK
skill_id UUID FK
proficiency FLOAT
years_experience FLOAT
source VARCHAR
evidence JSONB
```

## companies

```text
id UUID PK
name VARCHAR
domain VARCHAR
normalized_name VARCHAR
```

## jobs

```text
id UUID PK
company_id UUID FK
external_id VARCHAR NULL
source VARCHAR
source_url VARCHAR
title VARCHAR
normalized_title VARCHAR
description TEXT
location VARCHAR
remote_type VARCHAR
employment_type VARCHAR
salary_min NUMERIC NULL
salary_max NUMERIC NULL
seniority VARCHAR
status VARCHAR
posted_at TIMESTAMP NULL
expires_at TIMESTAMP NULL
structured_json JSONB
embedding VECTOR
created_at
updated_at
```

## job_skills

```text
job_id UUID FK
skill_id UUID FK
importance VARCHAR
required BOOLEAN
weight FLOAT
evidence_text TEXT
```

## matches

```text
id UUID PK
user_id UUID FK
job_id UUID FK
resume_version_id UUID FK

final_score FLOAT
skill_score FLOAT
semantic_score FLOAT
experience_score FLOAT
seniority_score FLOAT
location_score FLOAT
title_score FLOAT
historical_score FLOAT NULL

explanation_json JSONB
model_version VARCHAR
created_at
```

## applications

```text
id UUID PK
user_id UUID FK
job_id UUID FK
resume_version_id UUID FK
match_id UUID FK NULL
status VARCHAR
applied_at TIMESTAMP
source VARCHAR
notes TEXT
created_at
updated_at
```

## application_events

Append-only event history.

```text
id UUID PK
application_id UUID FK
event_type VARCHAR
event_at TIMESTAMP
metadata JSONB
```

Events:
- applied
- recruiter_response
- assessment
- phone_screen
- technical_interview
- onsite
- rejected
- withdrawn
- offer
- accepted

## experiments

```text
id UUID PK
user_id UUID FK
name VARCHAR
experiment_type VARCHAR
hypothesis TEXT
start_at TIMESTAMP
end_at TIMESTAMP NULL
status VARCHAR
```

## experiment_assignments

```text
experiment_id UUID FK
application_id UUID FK
variant VARCHAR
```

## agent_conversations

```text
id UUID PK
user_id UUID FK
title VARCHAR
created_at
```

## agent_messages

```text
id UUID PK
conversation_id UUID FK
role VARCHAR
content TEXT
tool_calls JSONB
created_at
```

---

# 13. Skill Normalization

Job descriptions often contain aliases:

```text
Postgres
PostgreSQL
postgresql
PG
```

Normalize to:

```text
PostgreSQL
```

Use a canonical skill registry.

Normalization flow:

```text
raw skill
   ↓
lowercase
   ↓
alias map
   ↓
exact match
   ↓
embedding similarity fallback
   ↓
LLM fallback only if uncertain
```

Never use LLM normalization for every skill due to cost and inconsistency.

---

# 14. Resume Parsing Architecture

Resume parser should extract:

```json
{
  "name": "",
  "summary": "",
  "skills": [],
  "experience": [
    {
      "company": "",
      "title": "",
      "start_date": "",
      "end_date": "",
      "bullets": []
    }
  ],
  "education": [],
  "projects": [],
  "certifications": []
}
```

Pipeline:

```text
PDF/DOCX
  ↓
Text extraction
  ↓
Cleaning
  ↓
LLM structured extraction
  ↓
Pydantic validation
  ↓
Normalization
  ↓
Persist
```

If extraction validation fails:
1. retry once with corrective prompt,
2. then mark record `needs_review`.

---

# 15. Job Parsing Architecture

Structured output:

```json
{
  "title": "",
  "normalized_title": "",
  "company": "",
  "location": "",
  "remote_type": "",
  "employment_type": "",
  "seniority": "",
  "years_experience_required": 0,
  "required_skills": [],
  "preferred_skills": [],
  "education_requirements": [],
  "responsibilities": [],
  "salary": null
}
```

Use JSON-schema-constrained model output when available.

---

# 16. Matching Engine

The initial system should be deterministic and inspectable.

## 16.1 Feature Scores

Each feature is normalized to 0-1.

```text
skill_score
semantic_score
experience_score
seniority_score
location_score
title_score
education_score
```

Initial weighted model:

```text
final_score =
    0.35 * skill_score +
    0.20 * semantic_score +
    0.15 * experience_score +
    0.10 * seniority_score +
    0.08 * title_score +
    0.07 * location_score +
    0.05 * education_score
```

Expose feature-level breakdown.

Do not allow LLM to generate the numeric final score.

---

# 17. Skill Score

Let:

```text
R = required job skills
P = preferred job skills
C = candidate skills
```

Required coverage:

```text
required_match =
sum(weight(skill) for matched required skills)
/
sum(weight(skill) for required skills)
```

Preferred coverage:

```text
preferred_match =
matched_preferred_weight
/
total_preferred_weight
```

Then:

```text
skill_score =
0.8 * required_match +
0.2 * preferred_match
```

Apply major penalty if must-have requirement is missing.

---

# 18. Semantic Similarity

Generate embeddings for:

- normalized resume profile,
- job description,
- individual experience bullets,
- job requirements.

Use cosine similarity.

Prefer evidence-based similarity:

```text
job requirement
      ↓
retrieve top-k resume evidence
      ↓
similarity
      ↓
aggregate
```

This is stronger than comparing one giant resume embedding against one giant job embedding.

---

# 19. Hybrid Retrieval

For evidence retrieval combine:

```text
BM25 keyword retrieval
+
vector similarity
+
optional reranker
```

Example:

```text
candidate evidence query:
"experience building REST APIs with Python"

Top evidence:
1. "Built FastAPI backend..."
2. "Created REST endpoints..."
3. "Integrated PostgreSQL..."
```

---

# 20. Experience Score

Example logic:

```python
if required_years is None:
    score = 1.0
elif candidate_years >= required_years:
    score = 1.0
elif candidate_years >= required_years - 1:
    score = 0.75
elif candidate_years >= required_years - 2:
    score = 0.40
else:
    score = 0.10
```

Do not automatically reject candidates for approximate experience mismatches.

---

# 21. Seniority Score

Map:

```text
intern = 0
new_grad = 1
junior = 2
mid = 3
senior = 4
staff = 5
```

Candidate target seniority should be compared to job seniority.

Penalty increases with distance.

---

# 22. Match Explanation System

The explanation should be grounded in deterministic score inputs.

Example:

```json
{
  "strengths": [
    {
      "skill": "Python",
      "evidence": "Built FastAPI backend..."
    }
  ],
  "missing_required_skills": ["Kafka"],
  "missing_preferred_skills": ["ClickHouse"],
  "warnings": [
    "Role requests 3+ years of experience."
  ],
  "summary": "Strong technical overlap but experience requirement is above profile."
}
```

The LLM can convert this JSON into natural language.

The LLM must not invent evidence.

---

# 23. Initial Ranking

Rank saved/discovered jobs by:

```text
rank_score =
match_score
* freshness_factor
* preference_factor
```

Possible preference signals:
- desired role
- location
- remote preference
- salary
- industry
- company size

---

# 24. Outcome-Aware ML Model

Only activate after sufficient user history.

Recommended minimum:
- 30 applications for experimental predictions.
- 75+ applications before displaying stronger confidence.

Target:

```text
P(positive_response | candidate, job, resume, match_features)
```

Possible labels:

Binary V1:

```text
0 = no response or rejected
1 = recruiter response or better
```

Binary V2:

```text
0 = no interview
1 = interview
```

Multiclass future version:

```text
0 no response
1 rejection
2 recruiter response
3 interview
4 offer
```

---

# 25. Outcome Model Features

Candidate-independent:
- job title cluster
- seniority
- company size if known
- remote type
- location
- required years
- required skill count

Candidate-specific:
- skill_score
- semantic_score
- experience_score
- title_score
- location_score
- missing required count
- resume version
- target role category

Historical:
- interview rate for role family
- interview rate for resume version
- response rate for job source
- rolling 30-day response rate

Never include post-application outcome data as prediction features.

---

# 26. Recommended Model Architecture

## Baseline

Use logistic regression first.

Why:
- interpretable,
- stable for small datasets,
- easy to debug,
- provides calibrated-ish probabilities,
- excellent baseline.

## Second Model

Gradient boosted trees:
- LightGBM or XGBoost.

Use only when sufficient data exists.

## Advanced Model

Global model trained across anonymized users + per-user features.

Do not start here.

---

# 27. Training Pipeline

```text
Application events
      ↓
Feature builder
      ↓
Training dataset
      ↓
Temporal train/validation split
      ↓
Baseline model
      ↓
Metrics
      ↓
Calibration
      ↓
Model registry
      ↓
Inference
```

Never random-split time-dependent application data by default.

Use temporal validation:

```text
first 80% of time → train
last 20% of time → validation
```

---

# 28. ML Metrics

Classification metrics:

- ROC-AUC
- PR-AUC
- log loss
- Brier score
- precision
- recall
- F1

Ranking metrics:

- NDCG@K
- Precision@K
- Recall@K
- MAP
- MRR

Calibration:
- reliability curve
- expected calibration error

Business metrics:
- interview rate among top-ranked jobs
- lift over baseline ranking
- response rate
- application-to-interview conversion

---

# 29. Learning-to-Rank Phase

After enough data exists, train model to rank jobs.

Training pairs:

```text
job A → interview
job B → rejection
```

Then teach:

```text
rank(candidate, A) > rank(candidate, B)
```

Possible models:
- LightGBM LambdaMART
- XGBoost ranking
- pairwise neural ranker

Use this only after baseline is complete.

---

# 30. Resume A/B Testing

Users may assign resume version A or B.

Track:

```text
applications
responses
interviews
offers
```

Do not claim causal superiority without sufficient sample size.

Display:

```text
Resume A interview rate: 14%
Resume B interview rate: 8%

Difference: +6 pp

Sample sizes:
A = 50
B = 47
```

Use:
- two-proportion z-test when sample size permits,
- Fisher's exact test for small samples,
- confidence intervals.

Include warning:
"Observational job outcomes contain confounding factors."

---

# 31. Skill Impact Analytics

For each skill, compare outcomes among jobs where the skill is:

- required,
- matched,
- missing.

Example:

```text
Kafka required + candidate missing:
interview rate = 2%

Kafka not required:
interview rate = 11%
```

Do not label correlation as causation.

---

# 32. AI Career Strategy Agent

Architecture:

```text
User question
    ↓
Intent detection
    ↓
Tool selection
    ↓
Structured analytics query
    ↓
Tool result
    ↓
LLM synthesis
    ↓
Grounded answer
```

---

# 33. Agent Tools

Implement explicit tools.

## get_application_statistics

Input:

```json
{
  "date_range": "last_90_days"
}
```

Output:

```json
{
  "applications": 80,
  "responses": 12,
  "interviews": 6,
  "offers": 1
}
```

## get_role_performance

Returns outcomes by role family.

## get_resume_performance

Returns application and interview counts grouped by resume version.

## get_skill_gap_analysis

Returns frequently missing skills among high-priority jobs.

## get_match_distribution

Returns score distribution and outcomes.

## get_recent_outcomes

Returns recent application event timeline.

## get_top_job_recommendations

Returns ranked jobs with deterministic scores.

The agent must never directly query arbitrary SQL.

---

# 34. Agent Safety Rules

System prompt constraints:

1. Use tools for user-specific statistics.
2. Never fabricate applications, scores, job details, or outcomes.
3. Distinguish correlation from causation.
4. Explicitly mention when sample size is small.
5. Do not claim guaranteed employment outcomes.
6. Do not expose another user's data.
7. Avoid sensitive-attribute inference.

---

# 35. REST API

Base:

```text
/api/v1
```

## Auth

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /auth/me
```

## Profiles

```text
GET    /profile
PATCH  /profile
GET    /profile/skills
```

## Resumes

```text
POST   /resumes
GET    /resumes
GET    /resumes/{id}
POST   /resumes/{id}/versions
PATCH  /resumes/{id}
DELETE /resumes/{id}
```

## Jobs

```text
POST   /jobs
POST   /jobs/import
GET    /jobs
GET    /jobs/{id}
PATCH  /jobs/{id}
DELETE /jobs/{id}
```

## Matches

```text
POST /matches/compute/{job_id}
GET  /matches
GET  /matches/{id}
```

## Applications

```text
POST   /applications
GET    /applications
GET    /applications/{id}
PATCH  /applications/{id}
POST   /applications/{id}/events
```

## Analytics

```text
GET /analytics/funnel
GET /analytics/roles
GET /analytics/resumes
GET /analytics/skills
GET /analytics/match-outcomes
```

## Agent

```text
POST /agent/conversations
POST /agent/conversations/{id}/messages
GET  /agent/conversations/{id}
```

---

# 36. Background Jobs

Use workers for:

```text
resume.parse
resume.embed
job.fetch
job.parse
job.embed
match.compute
analytics.refresh
model.train
model.evaluate
email.process
```

Each job must be:
- idempotent,
- retriable,
- observable.

Retry policy:

```text
retry 1: 10 sec
retry 2: 30 sec
retry 3: 120 sec
```

Dead-letter failed jobs after max retries.

---

# 37. Caching

Use Redis for:

- parsed job cache,
- normalized skill cache,
- match result cache,
- analytics cache,
- rate limiting,
- session metadata if needed.

Example keys:

```text
job:{job_id}:parsed
match:{user_id}:{job_id}:{resume_version}
analytics:{user_id}:funnel
```

---

# 38. Authentication

Recommended:
- secure HTTP-only cookies,
- short-lived access token,
- rotating refresh token.

Production rules:
- Secure flag.
- SameSite=Lax or Strict.
- CSRF protection for cookie-authenticated state changes.
- Passwords hashed with Argon2id.
- Rate-limit login attempts.

Alternative:
- Clerk/Auth0/Supabase Auth for faster implementation.

---

# 39. Authorization

Every data query must scope by user ID.

Bad:

```sql
SELECT * FROM applications WHERE id = :id
```

Correct:

```sql
SELECT *
FROM applications
WHERE id = :id
AND user_id = :current_user_id
```

Use repository-layer helpers to enforce ownership.

---

# 40. Security Requirements

- TLS only in production.
- Secrets stored in secret manager.
- No API keys in frontend bundle.
- Validate upload MIME type.
- Limit file sizes.
- Virus scanning optional but recommended.
- Sanitize fetched HTML.
- Prevent SSRF for arbitrary job URLs.
- Restrict outbound fetch destinations.
- Rate limit public API.
- Use parameterized queries.
- Enable database backups.
- Log auth anomalies.
- Use least-privilege cloud IAM.
- Encrypt storage at rest.
- Never log resume contents or LLM API keys.

---

# 41. SSRF Protection for Job Import

For URL imports:

Reject:
- localhost,
- 127.0.0.0/8,
- private RFC1918 ranges,
- metadata endpoints,
- file://,
- ftp://.

Allow only:
- http,
- https.

Resolve DNS and validate final redirect destination.

---

# 42. Observability

## Logging

Structured JSON logs.

Each request includes:

```text
request_id
user_id
route
status_code
latency_ms
```

Background jobs:

```text
job_id
task_type
attempt
duration
result
```

## Metrics

Track:

```text
http_request_duration
http_error_rate
worker_queue_depth
worker_failure_rate
llm_latency
llm_error_rate
llm_tokens
embedding_latency
match_compute_latency
db_query_latency
cache_hit_rate
```

## Tracing

Use OpenTelemetry across:
- frontend request,
- API,
- database,
- queue,
- worker,
- LLM request.

## Error Tracking

Use Sentry or equivalent.

---

# 43. AI Observability

Record metadata for every model call:

```text
provider
model
prompt_version
latency
input_tokens
output_tokens
estimated_cost
status
```

Do NOT log full sensitive user content by default.

Use redacted samples for debugging.

---

# 44. Prompt Versioning

Store prompts in:

```text
packages/prompts/
```

Example:

```text
resume_parser_v1.md
job_parser_v1.md
match_explainer_v1.md
career_agent_v1.md
```

Each AI result should record:

```text
prompt_version
model_version
```

---

# 45. AI Evaluation Dataset

Create a manually reviewed evaluation set.

Example:

```text
evals/
├── resumes/
├── jobs/
├── expected_parsing.json
├── expected_skills.json
└── expected_matches.json
```

At minimum:
- 20 resumes
- 50 job descriptions
- 100 candidate-job pairs

---

# 46. Parsing Evaluation

Measure:

- skill precision
- skill recall
- title extraction accuracy
- company extraction accuracy
- years-of-experience extraction MAE
- required/preferred classification accuracy

Regression tests should prevent prompt/model changes from silently degrading output.

---

# 47. Match Evaluation

Create human labels:

```text
0 = poor fit
1 = weak fit
2 = moderate fit
3 = strong fit
```

Compare model score to evaluator labels.

Metrics:
- Spearman correlation
- pairwise ranking accuracy
- NDCG

---

# 48. Backend Unit Tests

Required examples:

## Match scoring

```text
test_perfect_skill_match_returns_high_score
test_missing_required_skill_reduces_score
test_preferred_skill_has_smaller_weight
test_experience_shortfall_penalty
test_location_mismatch_penalty
test_score_is_between_0_and_100
```

## Skill normalization

```text
test_postgres_maps_to_postgresql
test_js_maps_to_javascript
test_unknown_skill_fallback
test_case_insensitive_normalization
```

## Authorization

```text
test_user_cannot_read_other_users_resume
test_user_cannot_modify_other_users_application
test_user_cannot_access_other_users_agent_conversation
```

---

# 49. API Integration Tests

Examples:

```text
test_register_login_refresh_flow
test_resume_upload_creates_processing_job
test_job_import_creates_pending_job
test_worker_updates_job_to_ready
test_compute_match_returns_breakdown
test_application_status_event_is_recorded
test_analytics_updates_after_interview
```

Use a real test PostgreSQL database.

Do not mock the database for repository integration tests.

---

# 50. Worker Tests

Test:

```text
parse_resume_success
parse_resume_invalid_output_retry
embed_resume_success
parse_job_success
job_fetch_timeout_retry
duplicate_task_is_idempotent
dead_letter_after_max_retries
```

---

# 51. Frontend Tests

Use:
- Vitest
- React Testing Library

Test:

```text
login_form_validation
resume_upload_state
job_card_renders_match_score
match_breakdown_renders_missing_skills
application_status_update
analytics_empty_state
agent_message_rendering
```

---

# 52. End-to-End Tests

Use Playwright.

Critical user flows:

## E2E-01 Signup

```text
register
→ verify session
→ redirect dashboard
```

## E2E-02 Resume

```text
upload resume
→ processing
→ parsed
→ profile populated
```

## E2E-03 Job

```text
add job
→ parsed
→ match score displayed
```

## E2E-04 Application

```text
mark applied
→ update status to interview
→ dashboard reflects interview
```

## E2E-05 Agent

```text
ask "which resume performs best?"
→ tool call occurs
→ grounded answer displays
```

---

# 53. Security Tests

Must include:

```text
SQL injection attempts
XSS payload in job description
oversized file upload
invalid MIME upload
SSRF localhost URL
SSRF AWS metadata URL
expired access token
refresh-token reuse
cross-user object access
rate-limit brute force
```

---

# 54. Load Testing

Use Locust or k6.

Targets for portfolio production:

```text
100 concurrent users
p95 API latency < 500 ms for normal CRUD
p95 cached analytics < 300 ms
match scoring < 2 sec excluding external LLM calls
error rate < 1%
```

For AI endpoints:
- queue async work when latency can exceed normal request limits.

---

# 55. Failure Scenarios

## LLM unavailable

Behavior:
- parsing job remains retryable.
- UI displays processing failure state.
- deterministic product remains usable.

## Embedding provider unavailable

Behavior:
- fall back to keyword-only score.
- mark semantic score unavailable.

## Redis unavailable

Behavior:
- API should still handle basic database operations where possible.
- queue-dependent jobs fail gracefully.

## PostgreSQL unavailable

Behavior:
- return 503.
- fail health readiness check.

---

# 56. Health Endpoints

```text
GET /health/live
GET /health/ready
```

Live:
- API process running.

Ready:
- PostgreSQL reachable.
- Redis reachable if required.

Do not require external LLM provider for readiness.

---

# 57. CI Pipeline

GitHub Actions:

```text
lint
type-check
unit tests
integration tests
frontend tests
security/static checks
build images
```

PR cannot merge if:
- lint fails,
- type check fails,
- tests fail,
- migration validation fails.

---

# 58. CD Pipeline

On main branch:

```text
build
→ test
→ container scan
→ push image
→ deploy staging
→ smoke tests
→ deploy production
```

Database migrations:
- run as explicit deployment job.
- backward-compatible whenever possible.

---

# 59. Database Migration Rules

Avoid destructive migrations in one release.

Use expand/contract:

```text
release 1:
add new column

release 2:
backfill

release 3:
switch application

release 4:
remove old column
```

---

# 60. Feature Flags

Add simple feature flag system.

Examples:

```text
enable_outcome_model
enable_reranker
enable_resume_experiments
enable_agent
```

This lets production deploy unfinished features safely.

---

# 61. Product Pages

## Landing

- Value proposition.
- Sign up.

## Onboarding

- Preferred roles.
- Locations.
- Work authorization.
- Resume upload.

## Dashboard

Cards:
- total applications,
- response rate,
- interview rate,
- offer rate.

Charts:
- weekly applications,
- outcomes by role,
- outcomes by resume.

## Jobs

Filters:
- status,
- score,
- role,
- location,
- company,
- seniority.

## Job Detail

Sections:
- job information,
- match score,
- score breakdown,
- strengths,
- missing skills,
- resume evidence,
- actions.

## Applications

Kanban or table:
- saved,
- applied,
- interviewing,
- rejected,
- offer.

## Resume Analytics

- resume performance,
- role performance,
- sample size,
- confidence.

## Skills

- strongest skills,
- common missing skills,
- skill/outcome correlation.

## AI Advisor

Chat interface grounded in analytics tools.

## Settings

- profile,
- resumes,
- AI preferences,
- data deletion.

---

# 62. UX Rules

Every AI-generated result must show one of:

- evidence,
- source,
- score breakdown,
- or uncertainty.

Avoid opaque statements like:

```text
"AI says you are a 92% match."
```

Prefer:

```text
Match: 82

Skills:      91
Experience:  74
Seniority:   80
Location:   100
Semantic:    79
```

---

# 63. Data Privacy

Users must be able to:

- delete resume files,
- delete their account,
- delete application history,
- export their data.

Deletion should remove:
- relational records,
- object storage files,
- embeddings,
- conversations.

---

# 64. Analytics Queries

## Funnel

```sql
SELECT
  COUNT(*) AS applications,
  COUNT(*) FILTER (
    WHERE status IN ('interviewing', 'offer')
  ) AS interviews,
  COUNT(*) FILTER (
    WHERE status = 'offer'
  ) AS offers
FROM applications
WHERE user_id = :user_id;
```

Prefer event-derived analytics when historical status transitions matter.

---

# 65. Data Quality Rules

Jobs can become stale.

Fields:

```text
jobs.status =
active
expired
removed
unknown
```

Do not recommend expired jobs.

Deduplicate by:
- canonical URL,
- external ID,
- normalized company/title/location hash.

---

# 66. Job Freshness

Freshness factor example:

```text
0-3 days:   1.00
4-7 days:   0.95
8-14 days:  0.85
15-30 days: 0.70
30+ days:   0.50
```

Do not silently hide older jobs; expose age.

---

# 67. Model Registry

Create table:

```text
model_versions
```

Fields:

```text
id
model_name
version
artifact_uri
metrics JSONB
training_window_start
training_window_end
created_at
is_active
```

---

# 68. Model Serving

MVP:
- Python model loaded into FastAPI process.

Later:
- dedicated inference service.

Use request schema:

```json
{
  "candidate_id": "...",
  "job_id": "...",
  "resume_version_id": "..."
}
```

Return:

```json
{
  "probability": 0.17,
  "model_version": "interview_model_v3"
}
```

---

# 69. Model Fallback

If personalized outcome model unavailable:

```text
historical_score = null
```

Final ranking falls back to deterministic matching.

Never fake probability.

---

# 70. Explainability

For logistic regression:
- show top contributing features.

For tree models:
- compute SHAP values offline or on demand.

Example:

```text
Positive:
+ strong Python match
+ target role aligns
+ preferred location

Negative:
- missing Kafka
- years requirement exceeds profile
```

---

# 71. Cost Controls

AI usage can become expensive.

Implement:

- async parsing,
- caching,
- prompt compression,
- structured extraction,
- batch embeddings,
- retry limits,
- per-user quotas,
- token telemetry.

Avoid calling LLM on:
- every dashboard load,
- every score display,
- deterministic analytics.

---

# 72. Rate Limits

Example:

```text
auth/login: 10/minute/IP
jobs/import: 20/hour/user
resume/upload: 10/hour/user
agent/message: 30/hour/user
```

---

# 73. Search

Use PostgreSQL full-text search initially.

Search fields:
- job title
- company
- description
- location
- skills

Use vector search only when semantic search adds value.

---

# 74. Recommended Indexes

```sql
CREATE INDEX idx_jobs_user_status
ON applications(user_id, status);

CREATE INDEX idx_applications_applied_at
ON applications(user_id, applied_at DESC);

CREATE INDEX idx_jobs_company
ON jobs(company_id);

CREATE INDEX idx_job_skills_job
ON job_skills(job_id);

CREATE INDEX idx_matches_user_score
ON matches(user_id, final_score DESC);
```

Add vector ANN index when dataset is large enough.

---

# 75. Production Readiness Checklist

Before calling the app production ready:

- Auth complete.
- Authorization audited.
- Database migrations tested.
- HTTPS enforced.
- Upload limits configured.
- SSRF protection implemented.
- Rate limits enabled.
- Background jobs retry safely.
- Logs structured.
- Error tracking enabled.
- Metrics exported.
- Health checks implemented.
- Backups enabled.
- CI passing.
- E2E critical path passing.
- LLM failures handled.
- Data deletion supported.
- Secrets not committed.
- `.env.example` included.
- README documents setup.
- Demo seed data available.

---

# 76. Suggested Development Phases

## Phase 0 — Foundation

Build:
- monorepo,
- auth,
- database,
- Docker,
- CI,
- health checks.

Exit criteria:
- register/login works,
- migrations run,
- tests run in CI.

## Phase 1 — Resume Intelligence

Build:
- resume upload,
- storage,
- parsing,
- candidate skill profile,
- resume versions.

Exit criteria:
- parsed resume visible in UI.

## Phase 2 — Job Intelligence

Build:
- manual job create,
- URL import,
- parsing,
- normalized skills.

Exit criteria:
- structured job page exists.

## Phase 3 — Matching Engine

Build:
- deterministic feature scoring,
- embeddings,
- evidence retrieval,
- explanation.

Exit criteria:
- score is reproducible,
- breakdown visible.

## Phase 4 — Application Tracker

Build:
- statuses,
- event history,
- dashboard.

Exit criteria:
- funnel analytics work.

## Phase 5 — AI Career Agent

Build:
- tool schemas,
- agent routing,
- grounded answers.

Exit criteria:
- agent can answer analytics questions without hallucinating data.

## Phase 6 — Experimentation

Build:
- resume versions,
- experiment groups,
- comparative outcomes.

Exit criteria:
- resume comparison dashboard.

## Phase 7 — ML Personalization

Build:
- dataset builder,
- baseline logistic regression,
- temporal validation,
- model registry,
- inference.

Exit criteria:
- model beats trivial baseline before activation.

## Phase 8 — Production Hardening

Build:
- observability,
- load tests,
- security tests,
- backup validation,
- staging,
- deployment automation.

---

# 77. Seed Data

Provide developer seed script:

```bash
python scripts/seed.py
```

Seed:
- one demo user,
- three resume versions,
- 50 jobs,
- 40 applications,
- 10 interview outcomes,
- realistic score variation.

Never use seed data in production environment.

---

# 78. Testing Pyramid

Recommended ratio:

```text
60% unit
25% integration
10% E2E
5% specialized security/performance/evals
```

---

# 79. Definition of Done for a Feature

A feature is done when:

1. API schema is defined.
2. Validation exists.
3. Authorization exists.
4. DB migration exists if required.
5. Unit tests pass.
6. Integration tests pass.
7. Error handling exists.
8. Logs/metrics exist.
9. UI has loading/error/empty states.
10. Documentation is updated.

---

# 80. Cursor Implementation Instructions

Use this specification as the source of truth.

When implementing:

1. Do not implement the entire platform in one change.
2. Work phase by phase.
3. Before each phase, summarize:
   - files to add,
   - files to change,
   - migration changes,
   - API endpoints,
   - tests.
4. Use strict typing.
5. Avoid placeholders in production paths.
6. Do not suppress exceptions without logging.
7. Never hardcode secrets.
8. Every endpoint must validate input.
9. Every user-owned resource must enforce ownership.
10. Every background task must be idempotent.
11. AI output must be schema-validated.
12. ML scores must be reproducible and versioned.
13. Add tests in the same change as implementation.
14. Do not proceed to advanced ML until deterministic baseline works.
15. Preserve backwards compatibility between phases.

---

# 81. Recommended Initial Cursor Prompt

```text
You are implementing CareerRank from the provided specification.

Start with Phase 0 only.

Requirements:
- Create the monorepo structure.
- Create Next.js frontend.
- Create FastAPI backend.
- Add PostgreSQL + pgvector.
- Add Redis.
- Add Docker Compose.
- Add SQLAlchemy and Alembic.
- Add User and CandidateProfile models.
- Implement register/login/refresh/logout/me.
- Use secure password hashing.
- Implement ownership-ready repository patterns.
- Add /health/live and /health/ready.
- Add backend unit and integration tests.
- Add GitHub Actions for lint, type checking, and tests.
- Add .env.example.
- Add README setup instructions.

Before writing code:
1. Show the exact file tree you will create.
2. State architectural assumptions.
3. State all dependencies.
4. Then implement the files.

Do not implement resumes, jobs, matching, agent, or ML yet.
```

---

# 82. Recommended Phase 1 Cursor Prompt

```text
Implement Phase 1: Resume Intelligence.

Use the existing CareerRank codebase.

Build:
- resume model,
- resume version model,
- S3-compatible storage abstraction,
- PDF and DOCX upload validation,
- async parsing job,
- structured resume parser,
- Pydantic schema validation,
- candidate skill extraction,
- skill normalization,
- resume processing states,
- resume management UI,
- unit/integration/E2E tests.

Requirements:
- Max upload size must be configurable.
- Reject unsupported MIME types.
- Store original file outside PostgreSQL.
- Every resume query must be user-scoped.
- AI parsing must be behind a provider interface.
- Parsed output must record prompt/model version.
- Background jobs must be idempotent.
- Add failure/retry UI states.
```

---

# 83. Recommended Phase 2 Cursor Prompt

```text
Implement Phase 2: Job Intelligence.

Build:
- Company model.
- Job model.
- JobSkill model.
- Manual job creation.
- URL job import.
- SSRF-safe fetch service.
- Job parser with structured output.
- Skill normalization.
- Job processing worker.
- Search/list/detail UI.
- Duplicate detection.
- Tests for SSRF, parsing, deduplication, and authorization.
```

---

# 84. Recommended Phase 3 Cursor Prompt

```text
Implement Phase 3: Candidate-Job Matching.

Build:
- Match model.
- Deterministic feature scoring.
- Required/preferred skill scoring.
- Experience scoring.
- Seniority scoring.
- Location scoring.
- Title similarity.
- Resume/job embedding provider.
- pgvector retrieval.
- Evidence retrieval.
- Match explanation JSON.
- Job ranking endpoint.
- UI score breakdown.

Rules:
- LLM may explain score but may not determine final numeric score.
- Every score must be reproducible.
- Record scoring model version.
- Add regression tests for scoring.
```

---

# 85. Recommended Phase 4 Cursor Prompt

```text
Implement Phase 4: Application Tracking and Analytics.

Build:
- Application model.
- ApplicationEvent model.
- Saved/applied/interview/rejected/offer flow.
- Event timeline.
- Funnel analytics.
- Role performance analytics.
- Resume performance analytics.
- Match-score outcome analytics.
- Dashboard.
- Tests for state transitions and analytics accuracy.
```

---

# 86. Recommended Phase 5 Cursor Prompt

```text
Implement Phase 5: AI Career Strategy Agent.

The agent must use structured application analytics tools.

Build tools:
- get_application_statistics
- get_role_performance
- get_resume_performance
- get_skill_gap_analysis
- get_match_distribution
- get_recent_outcomes
- get_top_job_recommendations

Requirements:
- Agent cannot issue arbitrary SQL.
- User-specific facts must come from tools.
- Tool inputs and outputs must use typed schemas.
- Persist conversation history.
- Add tool call logs.
- Add prompt/model version tracking.
- Add tests verifying the agent does not fabricate analytics.
```

---

# 87. Recommended Phase 6-8 Cursor Prompt

```text
Implement the remaining CareerRank phases incrementally.

Phase 6:
Resume experiments and A/B analytics.

Phase 7:
Outcome-aware ML.
- temporal dataset builder
- logistic regression baseline
- evaluation metrics
- calibration
- model registry
- inference
- fallback behavior

Do not activate the model unless it beats baseline and has enough training data.

Phase 8:
Production hardening.
- OpenTelemetry
- Sentry
- rate limiting
- load testing
- security tests
- backup documentation
- production Docker build
- staging CI/CD
```

---

# 88. Portfolio-Level Success Criteria

The project should eventually let you truthfully state:

- Built a full-stack AI job intelligence platform using Next.js, FastAPI, PostgreSQL, pgvector, Redis, Docker, and cloud infrastructure.
- Designed an explainable hybrid candidate-job ranking system combining skill coverage, semantic retrieval, experience signals, and candidate preferences.
- Implemented async resume/job ingestion pipelines with structured LLM extraction and schema validation.
- Built an AI career advisor using tool calling over real application analytics rather than unconstrained generation.
- Developed an outcome-aware interview prediction model using temporal validation and model versioning.
- Created resume experiment analytics and application funnel dashboards.
- Added production observability, security controls, automated tests, CI/CD, and failure recovery.

---

# 89. Final Architectural Principle

CareerRank should be built as a **software system that uses AI**, not an AI demo surrounded by a UI.

The priority order should remain:

```text
Correctness
    ↓
Reliable data
    ↓
Deterministic baseline
    ↓
Observability
    ↓
Evaluation
    ↓
AI augmentation
    ↓
Personalized ML
```

If any AI component fails, the application should degrade gracefully instead of becoming unusable.

That engineering discipline is one of the primary qualities that makes this project valuable as a production portfolio application.
