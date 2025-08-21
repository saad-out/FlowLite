// neo4j.js
const neo4j = require('neo4j-driver');

// Update these with your local Neo4j settings
const uri = 'bolt://localhost:7687';
const user = 'neo4j';
const password = 'testTEST0';

const driver = neo4j.driver(uri, neo4j.auth.basic(user, password));

module.exports = driver;
