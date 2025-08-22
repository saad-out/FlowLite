# FlowLite

FlowLite is a small project inspired by FlowBrave, designed to demonstrate a workflow management system using **Neo4j** and **GraphQL**. The project allows you to model workflows, steps, documents, and agents, and provides a GraphQL API to query and explore the data.

---

## Features

- Define **Workflows** with goals.
- Define **Steps** with order, next steps, associated **Documents**, and assigned **Agents**.
- Load sample data automatically.
- Query the graph using GraphQL.
- Fully dockerized stack for easy setup.

---

## Project Structure
```bash
FlowLite/
├─ README.md
├─ docker-compose.yml
├─ graphql-server/
│ ├─ Dockerfile
│ ├─ index.js
│ ├─ neo4j.js
│ ├─ resolvers.js
│ ├─ schema.js
│ ├─ package.json
│ └─ package-lock.json
├─ neo4j/
│ ├─ conf/
│ ├─ data/
│ └─ init/
│ ├─ Dockerfile
│ ├─ load_data.py
│ └─ requirements.txt
└─ test-queries.graphql
```

---

## Neo4j Schema & Data Model

### Constraints
Uniqueness constraints ensure no duplicates:

- `Workflow.name`
- `Step.name`
- `Document.title`
- `Agent.name`

### Sample Data
...

### GraphQL Schema
```graphql
type Workflow {
  name: String!
  goal: String
  steps: [Step]
}

type Step {
  name: String!
  order: Int
  next: Step
  documents: [Document]
  agent: Agent
}

type Document {
  title: String!
}

type Agent {
  name: String!
}

type Query {
  workflows: [Workflow]
  workflow(name: String!): Workflow
  steps: [Step]
  step(name: String!): Step
}


```

### Docker Setup
The project uses Docker Compose to run the full stack:
- **Neo4j**: Graph database
- **Data Loader**: Loads sample data into Neo4j
- **GraphQL Server**: Node.js Apollo server exposing GraphQL API

### Getting Started
1. Clone the repository
```bash
git clone https://github.com/saad-out/FlowLite.git
cd FlowLite
```
2. Start the stack
```bash
docker-compose up --build
```
3. Access GraphQL Playground
Open `http://localhost:4000`in your browser to test queries.
4. Neo4j Browser
Access Neo4j Browser at `http://localhost:7474`
. Username: `neo4j`
. Password: `testTEST0`

### How It Works
1. **Neo4j Service**: Stores workflows, steps, documents, and agents.
2. **Data Loader**: Python script runs on container startup to populate sample data.
3. **GraphQL Server**: Node.js server with Apollo exposes queries to retrieve workflows and steps with their relationships.

### Technology Stack
. **Neo4j 5** — Graph database

. **Python** — Data loader

. **Node.js / Apollo Server** — GraphQL API

. **Docker & Docker Compose** — Containerized deployment
