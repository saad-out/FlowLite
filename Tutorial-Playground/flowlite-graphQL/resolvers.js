// resolvers.js
const driver = require('./neo4j');

const resolvers = {
  Query: {
    students: async () => {
      const session = driver.session();
      const result = await session.run(`MATCH (s:Student) RETURN s`);
      session.close();
      return result.records.map(record => ({ name: record.get('s').properties.name }));
    },
    student: async (_, { name }) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (s:Student {name: $name}) RETURN s`,
        { name }
      );
      session.close();
      if (result.records.length === 0) return null;
      return { name: result.records[0].get('s').properties.name };
    },
    courses: async () => {
      const session = driver.session();
      const result = await session.run(`MATCH (c:Course) RETURN c`);
      session.close();
      return result.records.map(record => ({
        code: record.get('c').properties.code,
        title: record.get('c').properties.title
      }));
    },
    course: async (_, { code }) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (c:Course {code: $code}) RETURN c`,
        { code }
      );
      session.close();
      if (result.records.length === 0) return null;
      const c = result.records[0].get('c').properties;
      return { code: c.code, title: c.title };
    }
  },
  Student: {
    courses: async (parent) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (s:Student {name: $name})-[:ENROLLED_IN]->(c:Course) RETURN c`,
        { name: parent.name }
      );
      session.close();
      return result.records.map(r => r.get('c').properties);
    },
    friends: async (parent) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (s:Student {name: $name})-[:FRIENDS_WITH]-(f) RETURN f`,
        { name: parent.name }
      );
      session.close();
      return result.records.map(r => r.get('f').properties);
    }
  },
  Course: {
    students: async (parent) => {
      const session = driver.session();
      const result = await session.run(
        `MATCH (s:Student)-[:ENROLLED_IN]->(c:Course {code: $code}) RETURN s`,
        { code: parent.code }
      );
      session.close();
      return result.records.map(r => r.get('s').properties);
    }
  }
};

module.exports = resolvers;
