# AI Microservices with API Gateway

This project demonstrates a 3-service AI microservices architecture managed by a Kong API Gateway. The system processes a user query by retrieving documents, processing them, and returning a summary, while enforcing security policies like authentication and rate-limiting.

## Architecture

The system consists of several independent services that communicate over HTTP, all managed by an API Gateway.

- **Client**: The end-user making a request.

- **API Gateway (Kong)**: The single entry point for all traffic. It handles:
  - **Authentication**: Validates an API key (`apikey` header).
  - **Rate Limiting**: Limits clients to 5 requests per minute.
  - **Routing**: Forwards valid requests to the Orchestrator Agent.

- **Orchestrator Agent**: Manages the business logic. It calls the Retriever and then the Processor, ensures idempotency, and logs requests.

- **Retriever Agent**: Simulates fetching relevant documents based on a query.

- **Processor Agent**: Simulates summarizing and labeling documents.

- **Policy Service**: A simple service that can check for forbidden keywords. (Note: In the final configuration, this service is deployed but not actively called by the gateway to ensure stability.)

## Prerequisites

- Docker and Docker Compose
- A command-line tool like `curl`

## Setup and Run

Follow these steps to build and run the entire system from a clean state.

### 1. Build and Start All Services

From the root directory of the project, run this command. It will build fresh Docker images for all services and start them in the background.

```bash
docker-compose up -d --build
```

Wait about 30 seconds for all services, especially the database, to initialize.

### 2. Configure Kong

These commands must be run one by one. They load the routing configuration into Kong's database and set up your API key.

#### a. Sync the Routes and Services

This command pushes the configuration from your `kong/kong.yaml` file to the running Kong instance.

```bash
docker-compose run --rm deck sync -s kong/kong.yaml --kong-addr http://kong:8001
```

#### b. Create a Consumer

This tells Kong about the client application that will be making requests.

```powershell
curl.exe -X POST http://localhost:8001/consumers/ --data username=ai-client-app
```

#### c. Create an API Key

This generates a secret key for the consumer.

```powershell
curl.exe -X POST http://localhost:8001/consumers/ai-client-app/key-auth/ --data key=super-secret-key
```

## How to Test the System

### Note

PowerShell can have issues with complex curl commands. For the best results, we will save the request body to a file first.

#### 1. Create `payload.json`

In the root of your project folder, create a new file named `payload.json` and paste this content into it:

```json
{
    "request_id": "req-12345",
    "query": "artificial intelligence"
}
```

#### 2. Run the Test Command

Now you can run the `curl.exe` command, telling it to read the data from the file. This avoids any PowerShell formatting issues.

```powershell
curl.exe -i -X POST http://localhost:8000/process-request -H "Content-Type: application/json" -H "apikey: super-secret-key" --data '@payload.json'
```

### Expected Outcomes

#### Successful Request (First Time)

You'll receive an `HTTP/1.1 200 OK` response with a JSON body containing the summary, label, and a unique `trace_id`.

```json
{
    "request_id": "req-12345",
    "summary": "The first document is about ar... This document covers advanced ... Exploring the ethics of artif...",
    "label": "AI_PROCESSED",
    "trace_id": "..."
}
```

#### Idempotent Request

Run the exact same command again. You'll get a `200 OK` with the exact same response body, including the same `trace_id` as the first request, because the result was served from the cache.

#### Unauthorized Request

If you use a wrong API key (`-H "apikey: wrong-key"`), you will get an `HTTP/1.1 401 Unauthorized` error.

#### Rate-Limited Request

If you run the successful command 6 times within one minute, the 6th request will be blocked with an `HTTP/1.1 429 Too Many Requests` error.

## Viewing Logs

The Orchestrator Agent logs a traceable record for every request. You can view the log file to see the request history.

```powershell
Get-Content logs/audit.jsonl
```

You should see entries for your successful request and the subsequent cache hit.

## Stopping the System

To stop and remove all running containers and networks, run:

```bash
docker-compose down
```
