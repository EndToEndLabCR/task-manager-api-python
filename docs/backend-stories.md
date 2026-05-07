# Backend Engineer User Stories

## Overview

The Backend Engineer is responsible for implementing the API layer, business logic, data access, and backend services following Clean Architecture and Domain-Driven Design principles. This document contains all user stories specific to backend development work.

---

## Epic 1: User Authentication & Account Management

**Priority**: Must Have (MVP)  
**Effort**: 21 story points  
**Owner**: Backend Engineer + Frontend Engineer  
**Backend Effort**: 11 story points

### Backend Tasks

**US-BE-1.1: User Domain Model & Repository**

- **As a** Backend Engineer,
- **I want to** implement the User domain model and repository interface,
- **So that** user data can be managed following DDD principles.

**Acceptance Criteria**:

- Given the domain layer structure
- When I implement the User entity
- Then it includes all required properties (id, email, username, password_hash, preferences)
- And the repository interface defines CRUD operations
- And domain validation rules are enforced
- And the model is independent of database implementation

**Technical Notes**:

- Place in `domain/entities/user.py`
- Implement value objects for Email
- Repository interface in `domain/repositories/user_repository.py`
- Use UUID for user ID
- Include created_at, updated_at timestamps

**Effort**: 2 SP

---

**US-BE-1.2: User Registration API**

- **As a** Backend Engineer,
- **I want to** implement the user registration endpoint,
- **So that** new users can create accounts.

**Acceptance Criteria**:

- Given a POST request to `/api/v1/auth/register` with email, username, and password
- When the data is valid and unique
- Then a new user is created with hashed password (bcrypt, cost factor 12)
- And a verification email is sent
- And a 201 response with user data (excluding password) is returned
- And validation errors return 400 with details
- And duplicate email/username returns 409

**Technical Notes**:

- Implement in `presentation/api/auth.py`
- Use Pydantic models for request/response validation
- Hash password using bcrypt
- Email validation regex
- Password complexity: min 8 chars, uppercase, lowercase, number
- Send verification email via email service

**Effort**: 3 SP

**API Endpoint**:
```
POST /api/v1/auth/register
Request: { email, username, password }
Response: { id, email, username, created_at }
```

---

**US-BE-1.3: JWT Authentication Service**

- **As a** Backend Engineer,
- **I want to** implement JWT-based authentication,
- **So that** user sessions can be securely managed.

**Acceptance Criteria**:

- Given the authentication requirements
- When I implement the JWT service
- Then it can generate access tokens (24-hour expiration)
- And it can generate refresh tokens (7-day expiration)
- And it can validate and decode tokens
- And tokens include user ID and email claims
- And tokens are signed with a secure secret key

**Technical Notes**:

- Use PyJWT library
- Store secret key in environment variable
- Implement token refresh endpoint
- Include token expiration in response
- Validate token signature and expiration

**Effort**: 3 SP

---

**US-BE-1.4: User Login API**

- **As a** Backend Engineer,
- **I want to** implement the login endpoint,
- **So that** users can authenticate and receive tokens.

**Acceptance Criteria**:

- Given a POST request to `/api/v1/auth/login` with email and password
- When credentials are valid
- Then JWT access and refresh tokens are returned
- And password is verified using bcrypt
- And invalid credentials return 401
- And login attempts are logged

**Technical Notes**:

- Verify password hash matches
- Return both access and refresh tokens
- Implement rate limiting (5 attempts per minute)
- Log failed login attempts

**Effort**: 2 SP

**API Endpoint**:
```
POST /api/v1/auth/login
Request: { email, password }
Response: { access_token, refresh_token, token_type, expires_in }
```

---

**US-BE-1.5: Password Reset Endpoints**

- **As a** Backend Engineer,
- **I want to** implement password reset functionality,
- **So that** users can recover their accounts.

**Acceptance Criteria**:

- Given endpoints for requesting and completing password reset
- When a user requests password reset with valid email
- Then a unique reset token is generated (1-hour expiration)
- And a reset email is sent with token link
- And the token can be used once to set a new password
- And expired tokens are rejected

**Technical Notes**:

- Two endpoints: request reset, complete reset
- Generate secure random token (UUID)
- Store token hash in database with expiration
- Invalidate all existing sessions after reset
- Rate limit reset requests (3 per hour per email)

**Effort**: 2 SP

**API Endpoints**:
```
POST /api/v1/auth/reset-password/request
Request: { email }
Response: { message: "Reset email sent" }

POST /api/v1/auth/reset-password/confirm
Request: { token, new_password }
Response: { message: "Password updated successfully" }
```

---

## Epic 2: Project Management

**Priority**: Must Have (MVP)  
**Effort**: 13 story points  
**Backend Effort**: 7 story points

### Backend Tasks

**US-BE-2.1: Project Domain Model & Repository**

- **As a** Backend Engineer,
- **I want to** implement the Project domain model and repository,
- **So that** projects can be managed in the application.

**Acceptance Criteria**:

- Given the domain layer structure
- When I implement the Project entity
- Then it includes all required properties (id, user_id, name, description, color, archived)
- And the repository interface defines CRUD operations
- And user ownership is enforced
- And projects can be filtered and sorted

**Technical Notes**:

- Place in `domain/entities/project.py`
- Repository interface in `domain/repositories/project_repository.py`
- Include relationship to User entity
- Support soft delete (archived flag)

**Effort**: 2 SP

---

**US-BE-2.2: Project CRUD API Endpoints**

- **As a** Backend Engineer,
- **I want to** implement CRUD endpoints for projects,
- **So that** users can manage their projects.

**Acceptance Criteria**:

- Given authenticated user
- When implementing project endpoints
- Then I create endpoints for:
  - Create project (POST /api/v1/projects)
  - List projects (GET /api/v1/projects)
  - Get project (GET /api/v1/projects/{id})
  - Update project (PUT /api/v1/projects/{id})
  - Delete project (DELETE /api/v1/projects/{id})
- And all endpoints verify user ownership
- And deleted projects cascade delete tasks
- And proper error codes are returned

**Technical Notes**:

- Implement in `presentation/api/projects.py`
- Use dependency injection for repository
- Return 403 for unauthorized access
- Include task count in list response
- Validate color format (hex code)

**Effort**: 3 SP

**API Endpoints**:
```
POST /api/v1/projects - Create project
GET /api/v1/projects - List user's projects
GET /api/v1/projects/{id} - Get project details
PUT /api/v1/projects/{id} - Update project
DELETE /api/v1/projects/{id} - Delete project
```

---

**US-BE-2.3: Project Tests**

- **As a** Backend Engineer,
- **I want to** write comprehensive tests for project functionality,
- **So that** the project features are reliable.

**Acceptance Criteria**:

- Given the project implementation
- When I write tests
- Then I include:
  - Unit tests for domain model validation
  - Integration tests for API endpoints
  - Test for ownership verification
  - Test for cascade delete
  - Test for validation errors
- And test coverage is above 80%

**Effort**: 2 SP

---

## Epic 3: Task Management

**Priority**: Must Have (MVP)  
**Effort**: 21 story points  
**Backend Effort**: 10 story points

### Backend Tasks

**US-BE-3.1: Task Domain Model & Repository**

- **As a** Backend Engineer,
- **I want to** implement the Task domain model and repository,
- **So that** tasks can be managed in the application.

**Acceptance Criteria**:

- Given the domain layer structure
- When I implement the Task entity
- Then it includes all required properties (id, project_id, title, description, status, priority, due_date, position)
- And status enum includes TODO, IN_PROGRESS, DONE
- And priority enum includes LOW, MEDIUM, HIGH, URGENT
- And the repository supports filtering and ordering

**Technical Notes**:

- Place in `domain/entities/task.py`
- Repository interface in `domain/repositories/task_repository.py`
- Include relationship to Project entity
- Support position ordering within status

**Effort**: 2 SP

---

**US-BE-3.2: Task CRUD API Endpoints**

- **As a** Backend Engineer,
- **I want to** implement CRUD endpoints for tasks,
- **So that** users can manage their tasks.

**Acceptance Criteria**:

- Given authenticated user
- When implementing task endpoints
- Then I create endpoints for:
  - Create task (POST /api/v1/projects/{project_id}/tasks)
  - List tasks (GET /api/v1/projects/{project_id}/tasks)
  - Get task (GET /api/v1/tasks/{id})
  - Update task (PATCH /api/v1/tasks/{id})
  - Delete task (DELETE /api/v1/tasks/{id})
- And all endpoints verify user owns the project
- And proper validation is performed

**Technical Notes**:

- Implement in `presentation/api/tasks.py`
- Support partial updates with PATCH
- Validate project ownership through task
- Return 404 for non-existent tasks

**Effort**: 3 SP

**API Endpoints**:
```
POST /api/v1/projects/{project_id}/tasks - Create task
GET /api/v1/projects/{project_id}/tasks - List project tasks
GET /api/v1/tasks/{id} - Get task details
PATCH /api/v1/tasks/{id} - Update task
DELETE /api/v1/tasks/{id} - Delete task
```

---

**US-BE-3.3: Task Filtering & Search**

- **As a** Backend Engineer,
- **I want to** implement task filtering and search,
- **So that** users can find tasks easily.

**Acceptance Criteria**:

- Given task list endpoint
- When implementing filtering
- Then I support query parameters:
  - status (TODO, IN_PROGRESS, DONE)
  - priority (LOW, MEDIUM, HIGH, URGENT)
  - search (title/description search)
  - due_date_from, due_date_to
  - sort_by (created_at, due_date, priority)
  - sort_order (asc, desc)
- And search is case-insensitive
- And results are paginated

**Technical Notes**:

- Use ILIKE for case-insensitive search
- Add database indexes for performance
- Implement pagination (default 50 per page)
- Consider full-text search for future

**Effort**: 2 SP

---

**US-BE-3.4: Task Status Update Optimization**

- **As a** Backend Engineer,
- **I want to** optimize task status updates for drag-and-drop,
- **So that** the kanban board performs smoothly.

**Acceptance Criteria**:

- Given task status update endpoint
- When a task status is changed
- Then the update completes in under 100ms
- And the task position is updated correctly
- And conflicts are handled (optimistic locking)
- And bulk updates are supported

**Technical Notes**:

- Use optimistic locking (version field)
- Support batch status updates
- Update position within status column
- Return updated task immediately

**Effort**: 2 SP

---

**US-BE-3.5: Task Tests**

- **As a** Backend Engineer,
- **I want to** write comprehensive tests for task functionality,
- **So that** task features are reliable.

**Acceptance Criteria**:

- Given the task implementation
- When I write tests
- Then I include:
  - Unit tests for domain model
  - Integration tests for API endpoints
  - Test for ownership verification
  - Test for filtering and search
  - Test for position ordering
- And test coverage is above 80%

**Effort**: 1 SP

---

## Epic 4: Dashboard & Visualization

**Priority**: Must Have (MVP)  
**Effort**: 13 story points  
**Backend Effort**: 3 story points

### Backend Tasks

**US-BE-4.1: Dashboard Statistics API**

- **As a** Backend Engineer,
- **I want to** implement dashboard statistics endpoint,
- **So that** the frontend can display task summaries.

**Acceptance Criteria**:

- Given authenticated user
- When requesting dashboard data
- Then I return:
  - Task counts by status (TODO, IN_PROGRESS, DONE)
  - Upcoming tasks (next 7 days)
  - Overdue tasks count
  - Recent projects
  - Task completion rate
- And queries are optimized with aggregates
- And response time is under 200ms

**Technical Notes**:

- Implement in `presentation/api/dashboard.py`
- Use aggregate queries (COUNT, GROUP BY)
- Add database indexes for performance
- Consider caching for frequently accessed data
- Return in single API call

**Effort**: 2 SP

**API Endpoint**:
```
GET /api/v1/dashboard/statistics
Response: {
  task_counts: { todo: 10, in_progress: 5, done: 20 },
  upcoming_tasks: [...],
  overdue_count: 3,
  recent_projects: [...],
  completion_rate: 0.67
}
```

---

**US-BE-4.2: Dashboard Tests**

- **As a** Backend Engineer,
- **I want to** write tests for dashboard functionality,
- **So that** statistics are accurate.

**Acceptance Criteria**:

- Given the dashboard implementation
- When I write tests
- Then I include:
  - Test for accurate task counts
  - Test for upcoming tasks calculation
  - Test for overdue tasks detection
  - Test for performance (response time)
- And test coverage is above 80%

**Effort**: 1 SP

---

## Epic 5: Notifications System

**Priority**: Should Have (Phase 1)  
**Effort**: 21 story points  
**Backend Effort**: 13 story points

### Backend Tasks

**US-BE-5.1: Notification Domain Model**

- **As a** Backend Engineer,
- **I want to** implement the Notification domain model,
- **So that** notifications can be stored and managed.

**Acceptance Criteria**:

- Given the domain layer structure
- When I implement the Notification entity
- Then it includes all required properties (id, user_id, task_id, type, message, read, sent_at)
- And notification type enum includes DEADLINE_APPROACHING, OVERDUE, REMINDER
- And repository interface is defined

**Technical Notes**:

- Place in `domain/entities/notification.py`
- Repository in `domain/repositories/notification_repository.py`
- Include relationships to User and Task

**Effort**: 1 SP

---

**US-BE-5.2: Notification Generation Service**

- **As a** Backend Engineer,
- **I want to** implement the notification generation service,
- **So that** notifications are created based on task deadlines.

**Acceptance Criteria**:

- Given tasks with due dates
- When the notification service runs
- Then it generates notifications for:
  - Tasks due within 24 hours (DEADLINE_APPROACHING)
  - Overdue tasks (OVERDUE)
- And duplicate notifications are not created
- And user preferences are respected
- And notifications are stored in database

**Technical Notes**:

- Implement in `application/services/notification_service.py`
- Check if notification already sent for task
- Respect user notification preferences
- Generate notification messages
- Use template system for messages

**Effort**: 3 SP

---

**US-BE-5.3: Scheduled Notification Job**

- **As a** Backend Engineer,
- **I want to** implement a scheduled job for notifications,
- **So that** notifications are generated automatically.

**Acceptance Criteria**:

- Given the notification service
- When I implement the scheduled job
- Then it runs every hour
- And it generates notifications for eligible tasks
- And it sends email notifications (if enabled)
- And errors are logged and don't stop execution

**Technical Notes**:

- Use APScheduler or Celery
- Run every hour on the hour
- Implement retry logic for failures
- Log execution results
- Monitor job health

**Effort**: 2 SP

---

**US-BE-5.4: Email Notification Service**

- **As a** Backend Engineer,
- **I want to** implement email notification sending,
- **So that** users receive email alerts.

**Acceptance Criteria**:

- Given notifications to send
- When the email service is triggered
- Then emails are sent via email provider (SendGrid/AWS SES)
- And emails use HTML templates
- And email failures are logged and retried
- And users can unsubscribe from emails

**Technical Notes**:

- Use email service API (SendGrid, AWS SES)
- Create HTML email templates
- Implement retry logic (3 attempts)
- Log email delivery status
- Implement unsubscribe mechanism

**Effort**: 2 SP

---

**US-BE-5.5: Notification API Endpoints**

- **As a** Backend Engineer,
- **I want to** implement notification API endpoints,
- **So that** the frontend can display notifications.

**Acceptance Criteria**:

- Given authenticated user
- When implementing notification endpoints
- Then I create endpoints for:
  - List notifications (GET /api/v1/notifications)
  - Mark as read (PATCH /api/v1/notifications/{id}/read)
  - Mark all as read (POST /api/v1/notifications/read-all)
  - Get unread count (GET /api/v1/notifications/unread-count)
- And notifications are sorted by created date (newest first)
- And pagination is supported

**Technical Notes**:

- Implement in `presentation/api/notifications.py`
- Support filtering by read/unread
- Return unread count in separate endpoint
- Implement batch mark as read

**Effort**: 2 SP

**API Endpoints**:
```
GET /api/v1/notifications - List notifications
PATCH /api/v1/notifications/{id}/read - Mark as read
POST /api/v1/notifications/read-all - Mark all as read
GET /api/v1/notifications/unread-count - Get unread count
```

---

**US-BE-5.6: Notification Preferences**

- **As a** Backend Engineer,
- **I want to** implement notification preferences,
- **So that** users can control their notifications.

**Acceptance Criteria**:

- Given user preferences model
- When implementing preferences
- Then users can configure:
  - Email notifications enabled/disabled
  - Deadline threshold (24h, 48h, 1 week)
  - Notification types enabled
- And preferences are stored in user model (JSON field)
- And notification service respects preferences

**Technical Notes**:

- Add preferences JSON field to User model
- Implement preferences update endpoint
- Default: email enabled, 24h threshold
- Update notification service to check preferences

**Effort**: 2 SP

---

**US-BE-5.7: Notification Tests**

- **As a** Backend Engineer,
- **I want to** write tests for notification functionality,
- **So that** notifications work reliably.

**Acceptance Criteria**:

- Given the notification implementation
- When I write tests
- Then I include:
  - Unit tests for notification generation logic
  - Test for scheduled job execution
  - Test for email sending
  - Integration tests for API endpoints
  - Test for preference handling
- And test coverage is above 80%

**Effort**: 1 SP

---

## Epic 7: Third-Party Integrations

**Priority**: Could Have (Phase 3)  
**Effort**: 21 story points  
**Backend Effort**: 13 story points

### Backend Tasks

**US-BE-7.1: Google OAuth Implementation**

- **As a** Backend Engineer,
- **I want to** implement Google OAuth flow,
- **So that** users can connect their Google accounts.

**Acceptance Criteria**:

- Given Google Cloud OAuth credentials
- When implementing OAuth flow
- Then I create endpoints for:
  - Initiate OAuth (GET /api/v1/integrations/google/authorize)
  - OAuth callback (GET /api/v1/integrations/google/callback)
  - Disconnect (DELETE /api/v1/integrations/google/disconnect)
- And access and refresh tokens are stored encrypted
- And token refresh is automatic
- And proper error handling is implemented

**Technical Notes**:

- Use Google OAuth 2.0 library
- Store tokens encrypted in database
- Implement token refresh before expiration
- Handle OAuth errors gracefully
- Redirect to frontend after OAuth

**Effort**: 3 SP

---

**US-BE-7.2: Google Calendar API Integration**

- **As a** Backend Engineer,
- **I want to** integrate with Google Calendar API,
- **So that** tasks can be synced to Google Calendar.

**Acceptance Criteria**:

- Given OAuth tokens
- When integrating with Google Calendar API
- Then I can:
  - Create calendar events
  - Update calendar events
  - Delete calendar events
  - List calendar events
- And API rate limits are handled
- And errors are logged and retried

**Technical Notes**:

- Use Google Calendar API client library
- Implement rate limiting (respect API quotas)
- Map task properties to event properties
- Handle API errors (401, 403, 429, 500)
- Implement exponential backoff for retries

**Effort**: 3 SP

---

**US-BE-7.3: Task-Calendar Sync Service**

- **As a** Backend Engineer,
- **I want to** implement bidirectional sync between tasks and calendar events,
- **So that** changes are reflected in both systems.

**Acceptance Criteria**:

- Given tasks with due dates and connected Google Calendar
- When sync service runs
- Then it:
  - Creates calendar events for new tasks with due dates
  - Updates events when task details change
  - Deletes events when tasks are deleted or completed
  - Updates tasks when events are modified in Google Calendar
  - Handles conflicts (last write wins)
- And sync mapping is stored in database
- And sync runs every 5 minutes

**Technical Notes**:

- Implement in `application/services/calendar_sync_service.py`
- Store task-event mapping in database
- Use webhook for real-time updates (future)
- Implement conflict resolution strategy
- Handle sync failures gracefully

**Effort**: 3 SP

---

**US-BE-7.4: Webhook Handler for Calendar Changes**

- **As a** Backend Engineer,
- **I want to** implement webhook handler for Google Calendar changes,
- **So that** task updates happen in real-time.

**Acceptance Criteria**:

- Given Google Calendar webhook registration
- When a calendar event is modified
- Then the webhook endpoint receives notification
- And the corresponding task is updated
- And invalid webhooks are rejected

**Technical Notes**:

- Implement webhook endpoint (POST /api/v1/webhooks/google-calendar)
- Verify webhook signature
- Register for push notifications with Google
- Handle event modifications, deletions
- Renew webhook subscription before expiration

**Effort**: 2 SP

---

**US-BE-7.5: Integration Tests**

- **As a** Backend Engineer,
- **I want to** write tests for Google Calendar integration,
- **So that** the integration works reliably.

**Acceptance Criteria**:

- Given the integration implementation
- When I write tests
- Then I include:
  - Unit tests for sync logic
  - Integration tests with mocked Google API
  - Test for OAuth flow
  - Test for error handling
  - Test for conflict resolution
- And test coverage is above 80%

**Effort**: 2 SP

---

## Summary

### Total Backend Engineer Effort by Epic

| Epic | Backend Story Points | Phase |
|------|---------------------|-------|
| Epic 1: User Authentication | 11 SP | MVP |
| Epic 2: Project Management | 7 SP | MVP |
| Epic 3: Task Management | 10 SP | MVP |
| Epic 4: Dashboard | 3 SP | MVP |
| Epic 5: Notifications | 13 SP | Phase 1 |
| Epic 7: Google Calendar | 13 SP | Phase 3 |
| **Total** | **57 SP** | |

### Key Technical Responsibilities

1. **Domain Layer**: Implement domain models, entities, value objects, and repository interfaces
2. **Application Layer**: Implement use cases, application services, and business logic orchestration
3. **Infrastructure Layer**: Implement repository implementations, external service integrations, database access
4. **Presentation Layer**: Implement API endpoints, request/response models, validation
5. **Testing**: Write comprehensive unit and integration tests (80%+ coverage)
6. **Security**: Implement authentication, authorization, input validation, and data encryption
7. **Performance**: Optimize database queries, implement caching, ensure API response times

### Technology Stack

- **Framework**: FastAPI with async/await support
- **Language**: Python 3.10+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: bcrypt
- **Testing**: pytest with fixtures and mocks
- **Code Quality**: black, flake8, mypy, bandit
- **Background Jobs**: APScheduler or Celery
- **Email**: SendGrid or AWS SES
- **External APIs**: Google Calendar API

### Architecture Principles

- Follow **Clean Architecture** with clear layer separation
- Apply **Domain-Driven Design** (DDD) principles
- Implement **SOLID** principles
- Use **dependency injection** for testability
- Keep domain logic **framework-agnostic**
- Write **testable code** with high coverage
- Follow **TDD** (Test-Driven Development) when possible

---

**Last Updated**: November 11, 2025  
**Version**: 1.0