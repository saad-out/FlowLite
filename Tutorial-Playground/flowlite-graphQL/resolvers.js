// resolvers.js
const driver = require('./neo4j');

const resolvers = {
  Query: {
    workflows: async () => {
      const session = driver.session();
      const result = await session.run(`MATCH (w:Workflow) RETURN w`);
      session.close();
      return result.records.map(record => ({
        name: record.get('w').properties.name,
        goal: record.get('w').properties.goal
      }));
    },

    workflow: async (_, { name }) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (w:Workflow {name: $name}) RETURN w`,
        { name }
      );
      session.close();
      if (result.records.length === 0) return null;
      const w = result.records[0].get('w').properties;
      return { name: w.name, goal: w.goal };
    },

    steps: async () => {
      const session = driver.session();
      const result = await session.run(`MATCH (s:Step) RETURN s`);
      session.close();
      return result.records.map(record => ({
        name: record.get('s').properties.name,
        order: record.get('s').properties.order?.toInt() || null
      }));
    },

    step: async (_, { name }) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (s:Step {name: $name}) RETURN s`,
        { name }
      );
      session.close();
      if (result.records.length === 0) return null;
      const s = result.records[0].get('s').properties;
      return { name: s.name, order: s.order?.toInt() || null };
    }
  },

  Workflow: {
    steps: async (parent) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (w:Workflow {name: $name})-[:HAS_STEP]->(s:Step)
         RETURN s ORDER BY s.order`,
        { name: parent.name }
      );
      session.close();
      return result.records.map(r => ({
        name: r.get('s').properties.name,
        order: r.get('s').properties.order?.toInt() || null
      }));
    }
  },

  Step: {
    next: async (parent) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (s:Step {name: $name})-[:NEXT]->(n:Step) RETURN n`,
        { name: parent.name }
      );
      session.close();
      if (result.records.length === 0) return null;
      const n = result.records[0].get('n').properties;
      return { name: n.name, order: n.order?.toInt() || null };
    },

    documents: async (parent) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (s:Step {name: $name})-[:NEEDS_DOC]->(d:Document) RETURN d`,
        { name: parent.name }
      );
      session.close();
      return result.records.map(r => ({
        title: r.get('d').properties.title
      }));
    },

    agent: async (parent) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (s:Step {name: $name})-[:ASSIGNED_TO]->(a:Agent) RETURN a`,
        { name: parent.name }
      );
      session.close();
      if (result.records.length === 0) return null;
      const a = result.records[0].get('a').properties;
      return { name: a.name };
    }
  }
};

module.exports = resolvers;
