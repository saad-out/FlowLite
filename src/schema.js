const { gql } = require('apollo-server');

module.exports = gql`

enum StepStatus { TODO IN_PROGRESS DONE }
enum RunStatus { RUNNING COMPLETED }

type Workflow {
  id: ID! @id
  name: String!
  goal: String
  steps: [Step!]!
    @relationship(type: "HAS_STEP", direction: OUT)
  # first step for convenience (optional)
  firstStep: Step @relationship(type: "FIRST_STEP", direction: OUT)
}

type Step {
  id: ID! @id
  name: String!
  order: Int!      # simple ordering without path logic
  description: String
  documents: [Document!]!
    @relationship(type: "NEEDS_DOC", direction: OUT)
  agents: [Agent!]!
    @relationship(type: "ASSIGNED_TO", direction: OUT)

  # Bonus: suggest docs used by adjacent steps (simple @cypher)
  suggestedDocs: [Document!]!
    @cypher(statement: """
      MATCH (this)<-[:HAS_STEP]-(w:Workflow)-[:HAS_STEP]->(s:Step)
      WHERE abs(s.order - this.order) = 1
      MATCH (s)-[:NEEDS_DOC]->(d:Document)
      RETURN DISTINCT d LIMIT 5
    """)
}

type Document {
  id: ID! @id
  title: String!
  url: String
  tags: [String!]
}

type Agent {
  id: ID! @id
  name: String!
  kind: String!   # "human" | "ai" | "service"
}

# Runtime execution
type WorkflowRun {
  id: ID! @id
  startedAt: DateTime! @default(value: "NOW")
  status: RunStatus! @default(value: "RUNNING")
  workflow: Workflow! @relationship(type: "FOR_WORKFLOW", direction: OUT)
  stepRuns: [StepRun!]! @relationship(type: "HAS_STEP_RUN", direction: OUT)
}

type StepRun {
  id: ID! @id
  status: StepStatus! @default(value: "TODO")
  note: String
  step: Step! @relationship(type: "FOR_STEP", direction: OUT)
}

# Quality-of-life mutations
extend type Mutation {
  startWorkflowRun(workflowId: ID!): WorkflowRun
    @cypher(statement: """
      MATCH (w:Workflow {id: $workflowId})-[:HAS_STEP]->(s:Step)
      WITH w, s ORDER BY s.order
      CREATE (wr:WorkflowRun {id: randomUUID(), startedAt: datetime(), status: 'RUNNING'})
      CREATE (wr)-[:FOR_WORKFLOW]->(w)
      WITH wr, collect(s) AS steps
      UNWIND steps AS st
      CREATE (sr:StepRun {id: randomUUID(), status: 'TODO'})
      CREATE (sr)-[:FOR_STEP]->(st)
      CREATE (wr)-[:HAS_STEP_RUN]->(sr)
      RETURN wr
    """)

  advanceStepRun(stepRunId: ID!, newStatus: StepStatus!, note: String): StepRun
    @cypher(statement: """
      MATCH (sr:StepRun {id: $stepRunId})
      SET sr.status = $newStatus
      SET sr.note = $note
      RETURN sr
    """)

  completeRunIfAllDone(runId: ID!): WorkflowRun
    @cypher(statement: """
      MATCH (wr:WorkflowRun {id: $runId})-[:HAS_STEP_RUN]->(sr:StepRun)
      WITH wr, collect(sr.status) AS statuses
      WITH wr, apoc.coll.toSet(statuses) AS st
      FOREACH (_ IN CASE WHEN 'TODO' IN st OR 'IN_PROGRESS' IN st THEN [] ELSE [1] END |
        SET wr.status = 'COMPLETED'
      )
      RETURN wr
    """)
}
`;
