# Order Management System
A FastAPI-based restaurant order management system with analytics capabilities, background processing, and monitoring.

## Requirements

### Section 1

- Receive an order and store it
- Allow update of order status
- Add needed endpoint(s) for client to interact with the order(s)

### Section 2

- Design a schema that enables querying:
    - Average time spent in each status
    - Order throughput per hour
    - Number of orders per customer lifetime
- Aggregations
    - Aggregates status change events into daily/hourly metrics and store in a summary table

Example of an order:

```json
{
  "_id": "60f87ea2a52dad8a3fa4860",
  "created": "2021-07-22T20:08:02Z",
  "account": "60bfc6dc4887c9851d5a0246",
  "brandId": "60bfc6dc4887c9851d5a0245",
  "channelOrderId": "TEST1626898082",
  "customer": {
    "name": "John Doe",
    "phoneNumber": "+123456789"
  },
  "deliveryAddress": {
    "city": "Helsinki",
    "street": "Huuvatie 1",
    "postalCode": "00100"
  },
  "pickupTime": "2021-07-22T20:28:02Z",
  "items": [
    {
      "name": "Hawaii Burger",
      "plu": "CAT1-0001",
      "quantity": 1
    },
    {
      "name": "Sushi Set Large",
      "plu": "CAT2-0001",
      "quantity": 1
    }
  ],
  "status": 1,
  "statusHistory": [
    {
      "status": 4,
      "timestamp": "2021-07-22T20:08:02Z"
    },
    {
      "status": 1,
      "timestamp": "2021-07-22T20:10:00Z"
    }
  ]
}
```

## Technical Design Decisions

- Domain-Driven Design: Structured with separate domains for orders and analytics
- Async Architecture: Built on FastAPI and Tortoise ORM for high-performance async operations
- Event-Based Analytics: Uses Celery workers to aggregate metrics for performance analysis
- Data Aggregation: Hourly metrics on status durations and order throughput for efficient querying
- Type Safety: Strictly typed with Mypy for robust code quality
- Containerization: Docker-based deployment with service isolation
- Observability Stack: Prometheus and Grafana for metrics visualization
- Schema-First API Design: OpenAPI specifications for clear contract definition

## Tech Stack

- API: FastAPI for high-performance async endpoints
- ORM: Tortoise ORM for async database interactions
- Database: PostgreSQL for relational data storage
- Migrations: Aerich for database versioning
- Background Processing: Celery with Redis for task scheduling
- Monitoring: Prometheus and Grafana dashboards
- Developer Tools: Ruff (linting), Mypy (type checking), Pytest (testing)
- Documentation: OpenAPI/Swagger UI
- Containerization: Docker and Docker Compose

## Getting Started

### Running with Docker
The simplest way to run the entire stack:
```bash
make services-up # Start all services
```
```bash
docker-compose exec app python -m scripts.seed_data # seed data if needed
```
```bash
make open-docs # Access the API docs
```

### Running Locally (Debug Mode)
```bash
make install # Install dependencies
```
```bash
make db # Initialize database
```
```bash
make run-api # Start the API server
```
```bash
make run-worker # Start the workers
```
```bash
make run-beat # Start the Celery beat scheduler
```
```bash
make seed-data # Seed the database with test data
```

### Access Points
- API Documentation: http://localhost:8000/docs
- Grafana Dashboards: http://localhost:3005/dashboards
- Prometheus Metrics: http://localhost:9095/graph

### Development Commands

- Database Operations:
  - `make db`: Initialize and migrate the database
  - `make seed-data`: Load sample data


- OpenAPI:
  - `make schemas`: Generate Python models from OpenAPI schemas


- Quality Checks:
  - `make quality`: Run Ruff linting and Mypy type checking
  - `make test`: Run the test suite


- Monitoring:
  - `make monitor`: Start monitoring stack


## Future Enhancements

- Kubernetes Deployment: Helm charts would be the next step for production
- CI/CD Pipeline: Automated testing and deployment
- Event-Driven Architecture: Replace scheduled aggregation with event-driven processing
- Data Archiving: Implement archiving for historical orders to optimize database performance
- Multi-Level Aggregation: Support for daily/weekly/monthly aggregations

## Project Structure
The project follows a domain-driven design with clear separation of concerns:

- API Layer: Handles HTTP requests and responses
- Domain Layer: Core business logic for orders and analytics
- Infrastructure Layer: Database, caching, and external services
- Background Jobs: Task processing for metrics aggregation