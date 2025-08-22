# FlowLite

<p align="center">
  <img src="https://github.com/saad-out/FlowLite/blob/main/FlowLite.png" style="height: 350px; width:500px;"/>
</p>

FlowLite is a small project inspired by FlowBrave, designed to demonstrate a workflow management system using **Neo4j** and **GraphQL**. The project allows you to model workflows, steps, documents, and agents, and provides a GraphQL API to query and explore the data.

---

## Features

- Define **Workflows** with goals.
- Define **Steps** with order, next steps, associated **Documents**, and assigned **Agents**.
- Load sample data automatically.
- Query the graph using GraphQL.
- Fully dockerized stack for easy setup.

---

## How the Database Is Designed

FlowLite uses a **graph database** (Neo4j) to organize information like a network of connected nodes rather than traditional tables. Here’s how it’s structured:

- **Workflow**: Represents a complete process, like "Refund Process".
- **Steps**: Each workflow is made up of steps that must be completed in order, like "Receive Request" → "Validate Receipt" → "Approve Refund".
- **Documents**: Steps may require documents, such as "Receipt Template" or "Approval Form".
- **Agents**: People or roles responsible for performing steps, like "Support Agent" or "Finance Officer".

### Relationships

The connections between these entities show how things relate:

1. **Workflow → HAS_STEP → Step**  
   Each workflow is connected to its steps in the order they should happen.

2. **Step → NEXT → Step**  
   Steps are connected sequentially to indicate the process flow.

3. **Step → NEEDS_DOC → Document**  
   Shows which documents are needed for a particular step.

4. **Step → ASSIGNED_TO → Agent**  
   Indicates who is responsible for executing a step.

### Visual Overview

```
Workflow: Refund Process
|
├─ Step: Receive Request
| |
| └─ NEXT → Step: Validate Receipt
| |
| ├─ NEEDS_DOC → Document: Receipt Template
| └─ NEXT → Step: Approve Refund
| |
| └─ ASSIGNED_TO → Agent: Finance Officer
└─ Step: Send Payment
```

In short, the database is designed as a **network of workflows, steps, documents, and agents**, all connected in a way that reflects real-world processes.

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

---

### Docker Setup
The project uses Docker Compose to run the full stack:
- **Neo4j**: Graph database
- **Data Loader**: Loads sample data into Neo4j
- **GraphQL Server**: Node.js Apollo server exposing GraphQL API
---
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
---
### How It Works
1. **Neo4j Service**: Stores workflows, steps, documents, and agents.
2. **Data Loader**: Python script runs on container startup to populate sample data.
3. **GraphQL Server**: Node.js server with Apollo exposes queries to retrieve workflows and steps with their relationships.
---
### Technology Stack
. **Neo4j 5** — Graph database

. **Python** — Data loader

. **Node.js / Apollo Server** — GraphQL API

. **Docker & Docker Compose** — Containerized deployment
