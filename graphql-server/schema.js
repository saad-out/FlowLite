// schema.js
const { gql } = require('apollo-server-express');

const typeDefs = gql`
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
`;

module.exports = typeDefs;

