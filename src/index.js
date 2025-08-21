require('dotenv').config();
const { ApolloServer } = require('apollo-server');
const { Neo4jGraphQL } = require('@neo4j/graphql');
const neo4j = require('neo4j-driver');
const typeDefs = require('./schema');

const driver = neo4j.driver(
  process.env.NEO4J_URI,
  neo4j.auth.basic(process.env.NEO4J_USER, process.env.NEO4J_PASSWORD)
);

(async () => {
  const neoSchema = new Neo4jGraphQL({ typeDefs, driver });
  const schema = await neoSchema.getSchema();
  const server = new ApolloServer({ schema });
  const { url } = await server.listen({ port: process.env.PORT || 4000 });
  console.log(`🚀 GraphQL ready at ${url}`);
})();
