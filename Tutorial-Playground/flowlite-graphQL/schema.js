// schema.js
const { gql } = require('apollo-server-express');

const typeDefs = gql`
  type Student {
    name: String!
    courses: [Course]
    friends: [Student]
  }

  type Course {
    code: String!
    title: String
    students: [Student]
  }

  type Query {
    students: [Student]
    courses: [Course]
    student(name: String!): Student
    course(code: String!): Course
  }
`;

module.exports = typeDefs;
