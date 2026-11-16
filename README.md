# EventHub

### **EventHub** is an event management and ticket reservation platform that built with Django Rest Framework.the platform allows organizers to create and manage events,while customers can browse published event and reserve ticket.

## Tech stack

- python 3.13
- Django
- Django Rest Framework
- PostgreSQL
- Redis
- Celery
- Docker
- Docker Compose
- JWT Authentication

## Features

### Authentication & Authorization
- Custom User Model
- JWT-based authentication
- Role-based access control (Organizer and Customer)
- permission-based API access

### Event Management
- Create,update,retrieve and delete events
- Publish and manage status
- Organizer Ownership permission
- Public access to published events
### Event Filtering
- Filter events by location, status, and date
- Search events by title
- Filter by ticket price range
- Order events by date or title
- Paginated event listings
### Ticket management
- Create and manage ticket type
- Ticket capacity management
- Ticket Price Management
- Prevent capacity reduction below sold or reserved tickets
### Order & Reservation Management
- Create ticket reservation
- Prevent overselling using database transactions and row-level locking
- Automatic reservation expiration
- Cancel Pending reservation
- Simulated payment flow
- View order history and order details

### Background Tasks
- Celery workers for asynchronous task execution
- Celery beat for periodic task scheduling
- Automatic expiration of pending orders

### Automated Testing

- Implemented API tests using django APITestCase and DRF test client

## Docker Architecture

### The application uses Docker Compose to manage its services:
- Web: Django application and REST API
- Redis: Celery message broker
- Worker: Executes background tasks
- Beat: Schedules periodic tasks 
### PostgreSQL is currently running separately on the host machine.

## Project Status
### The core backing features, Docker environment, Redis integration, and Celery task scheduling have been implemented and tested.