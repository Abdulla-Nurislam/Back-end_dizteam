# Task and Event Management App

A comprehensive task and event management application built with Django. This project combines task management with calendar functionality, inspired by Google Calendar and Things3.

## Project Structure

The project contains several Django applications:
- **users**: User management and user profiles
- **tasks**: Task management with Projects, Areas, and Tags (inspired by Things3)
- **categories**: Management of task categories
- **events**: Event management with calendar integration (inspired by Google Calendar)

## Data Models

1. **User** (standard Django model)
2. **Profile** (extension of User model)
3. **Task** (tasks linked to users, categories, projects, areas, tags, and events)
4. **Category** (task categories)
5. **Event** (calendar events with repeat options and sharing capabilities)
6. **Project** (grouping mechanism for tasks)
7. **Area** (high-level organization for tasks and projects)
8. **Tag** (color-coded labels for tasks)

## ER Diagram

```
+-------------+      +------------+      +------------+
|    User     |      |  Category  |      |    Tag     |
+-------------+      +------------+      +------------+
| id          |      | id         |      | id         |
| username    |      | name       |      | name       |
| password    |      +------------+      | color      |
| email       |            ^             | owner_id   |
+-------------+            |             +------------+
      ^                    |                   ^
      |                    |                   |
      |                    |                   |
+-------------+      +------------+      +------------+
|   Profile   |      |    Task    |<---->|   Event    |
+-------------+      +------------+      +------------+
| id          |      | id         |      | id         |
| user_id     |<---->| title      |      | title      |
| bio         |      | description|      | description|
+-------------+      | deadline   |      | start_time |
                     | today_flag |      | end_time   |
                     | owner_id   |      | repeat     |
      +------------->| category_id|      | owner_id   |
      |              | project_id |<--+  +------------+
      |              | area_id    |<-+|         ^
      |              | event_id   |-+||         |
      |              +------------+ |||         |
      |                             |||         |
+------------+      +------------+  |||  +------------+
|   Project  |      |    Area    |  |||  | shared_with|
+------------+      +------------+  |||  +------------+
| id         |<-----+ id         |  |||  | event_id   |
| name       |      | name       |--+||  | user_id    |
| description|      | description|   ||  +------------+
| owner_id   |      | owner_id   |   ||
+------------+      +------------+   ||
                                     ||
              +------------+         ||
              | task_tags  |<--------+|
              +------------+          |
              | task_id    |          |
              | tag_id     |----------+
              +------------+
```

## Key Features

### Task Management
- Create, edit, and delete tasks
- Assign tasks to categories, projects, and areas
- Tag tasks with color-coded labels
- Set deadlines and mark tasks for today
- Mark tasks as completed
- Filter and search tasks

### Calendar Integration
- View tasks and events in a calendar view (day, week, month)
- Create events with start and end times
- Set up recurring events (daily, weekly, monthly, yearly)
- Link tasks to events
- Share events with other users

### Organization System
- Create projects to group related tasks
- Organize with areas (higher-level organization)
- Use tags for flexible categorization
- "Today" view for focusing on immediate tasks

### Notifications
- Email notifications for upcoming events
- Deadline reminders for tasks
- Console email backend for development
- Configuration for SMTP email in production

## Installation and Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate.bat for Windows
   ```
3. Install dependencies:
   ```
   pip install django
   ```
4. Apply migrations:
   ```
   python manage.py migrate
   ```
5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
6. Start the development server:
   ```
   python manage.py runserver
   ```
7. Go to http://127.0.0.1:8000/ to access the application
8. Go to http://127.0.0.1:8000/admin/ to access the admin panel

## Sending Notifications

For testing notifications:
```
python manage.py send_notifications
```

For production, consider setting up Celery to automate notification delivery:
1. Uncomment the Celery settings in `settings.py`
2. Install Redis and Celery
3. Configure Celery worker and beat processes

## Technologies Used

- Django
- HTML, CSS, JavaScript
- Bootstrap 5
- Font Awesome
- FullCalendar (for calendar views)
- Select2 (for tag selection)

## Future Enhancements

- Celery for background tasks
- API endpoints for mobile app integration
- Drag-and-drop task management
- Enhanced calendar sharing and permissions
- Integration with external calendars (Google, iCal) 