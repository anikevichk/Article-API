# Article API
Author: Katsyaryna Anikevich

## About

Article API is a REST API for managing articles.  
It allows users to register and log in, create and manage articles, subscribe to authors, receive notifications about new publications, and import articles in bulk from a JSON file or an external URL.

## Features

- user registration and login
- get current authenticated user
- create, view, update, and delete articles
- view all articles
- view current user's articles
- view articles from subscribed authors
- subscribe and unsubscribe to authors
- view notifications
- mark notifications as read
- import articles from a JSON file
- import articles from an external URL
- interactive API documentation with Swagger
- persistent data storage in a PostgreSQL database hosted on Neon

## Tech stack

- **FastAPI** for building the REST API
- **SQLAlchemy** for ORM and database operations
- **PostgreSQL / Neon** as the database
- **Pydantic** for request and response validation
- **JWT** for authentication
- **HTTPX** for importing articles from external URLs
- **Pytest** for testing
- **Docker / Docker Compose** for containerized setup
- **Vercel** for deployment and HTTPS support

### Why this stack

This stack was chosen because it is simple, practical, and well-suited for building a small but complete backend application.  
FastAPI provides a clean structure, automatic Swagger documentation, and good support for validation. SQLAlchemy makes database access more organized and easier to maintain. PostgreSQL is a reliable relational database, and Neon allows it to be hosted conveniently in the cloud. Pydantic helps ensure that incoming and outgoing data is validated correctly. JWT is a simple and widely used solution for authentication in REST APIs. HTTPX is a lightweight way to work with external HTTP resources. Pytest makes it easy to write and run tests. Docker simplifies running the project in a consistent environment, and Vercel provides easy deployment with HTTPS support.

## Environment variables

The application requires the following environment variables:

- `DATABASE_URL` - full database connection string
- `SECRET_KEY` - secret key used to sign JWT tokens
- `ALGORITHM` - algorithm used for JWT generation
- `ACCESS_TOKEN_EXPIRE_MINUTES` - access token lifetime in minutes

For production deployment, the database is configured via a Neon PostgreSQL connection string.

### Example

```env
DATABASE_URL=postgresql+psycopg2://username:password@hostname/dbname?sslmode=require
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Run and deployment

The project uses an external PostgreSQL database hosted on Neon.  
Docker Compose starts only the application container, while the database connection is provided through the `DATABASE_URL` environment variable.

The application can be run locally using Docker:

```bash
docker compose up --build
```

After starting the container, the API documentation will be available at:

`http://127.0.0.1:8000/docs`

The application is also deployed online and available at:

`https://article-api-one.vercel.app/docs`

The deployed version is hosted on Vercel and uses HTTPS by default.

### Why Vercel?
I chose Vercel instead of Nginx because Vercel provides HTTPS and a valid SSL certificate automatically.
With a custom Nginx setup, I would also need to configure the server and certificate manually, and a self-signed certificate is not considered trusted, so in practice it has little value.
That is why Vercel was a simpler and more appropriate solution for this project.


## Testing

Tests are run automatically using **GitHub Actions** on every push to the `main` branch.

The CI workflow:
- sets the required environment variables from GitHub Secrets
- installs dependencies
- runs all tests with `pytest`

Tests can also be run locally with:

```bash
pytest
```
## Security

The API includes several security measures to protect authentication, access to resources, and bulk import from external sources.

### Authentication and access control

- JWT is used for authentication
- protected endpoints require a valid Bearer token
- passwords are hashed using `bcrypt`
- access tokens include an expiration time
- users can only update or delete their own articles
- users can only view and manage their own notifications

### Input validation

- request and response data is validated with Pydantic
- email, username, password, article title, and article content are validated before processing
- import requests from URL are validated as proper HTTP/HTTPS URLs

### Bulk import protection

To make article import from external URLs safer, the application applies several checks:

- only `http` and `https` URLs are allowed
- `localhost` is blocked
- private, loopback, link-local, multicast, reserved, and unspecified IP addresses are blocked
- the hostname is resolved before the request is accepted
- redirects are not followed
- the external resource must return JSON
- the response size is limited to 2 MB
- imported data must be a list of objects
- every imported article must contain both `title` and `content`

These checks help reduce the risk of importing invalid data and protect the application from requests to local or internal network resources.

### Transport security

The deployed version of the application is hosted on Vercel and uses HTTPS by default.  
This means that communication with the API takes place over a secure channel with a valid SSL/TLS certificate.

### Error handling

The API returns consistent HTTP error responses for invalid credentials, forbidden actions, missing resources, invalid import files, invalid JSON, and unsafe external URLs.

## Possible improvements

Although the application already meets the main project requirements, several improvements could be added in the future:

- add database migrations with Alembic instead of relying on automatic table creation
- add filtering and search for article lists
- improve authentication by adding refresh tokens or role-based access control
- add support for updating user profile data
