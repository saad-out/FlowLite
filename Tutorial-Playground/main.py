# neo4j_basics.py
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"  # If you remapped ports, update this
USER = "neo4j"
PASSWORD = "testTEST0"
DBNAME = "neo4j"               # default database name

class Neo4jBasics:
    def __init__(self, uri, user, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    # --- SCHEMA: constraints so identical records aren't duplicated ---
    def create_constraints(self):
        """
        Cypher here:
        CREATE CONSTRAINT student_name IF NOT EXISTS
        FOR (s:Student) REQUIRE s.name IS UNIQUE

        CREATE CONSTRAINT course_code IF NOT EXISTS
        FOR (c:Course) REQUIRE c.code IS UNIQUE
        """
        with self.driver.session(database=self.database) as session:
            print("Creating constraints (if not exist)...")
            session.run("""
                CREATE CONSTRAINT student_name IF NOT EXISTS
                FOR (s:Student) REQUIRE s.name IS UNIQUE
            """)
            session.run("""
                CREATE CONSTRAINT course_code IF NOT EXISTS
                FOR (c:Course) REQUIRE c.code IS UNIQUE
            """)
            print("Constraints ready.")

    # --- LOAD DATA: nodes + relationships using MERGE (idempotent) ---
    def load_sample_data(self):
        students = [
            {"name": "Alice"},
            {"name": "Bob"},
            {"name": "Charlie"},
        ]
        courses = [
            {"code": "CS101", "title": "Intro to Computer Science"},
            {"code": "MATH100", "title": "Calculus I"},
        ]
        enrollments = [
            ("Alice", "CS101", "A"),
            ("Bob", "CS101", "B+"),
            ("Bob", "MATH100", "A-"),
            ("Charlie", "MATH100", "B"),
        ]
        friendships = [
            ("Alice", "Bob"),
            ("Bob", "Charlie"),
        ]

        with self.driver.session(database=self.database) as session:
            print("Creating Students...")
            for s in students:
                # MERGE creates if not exists, else matches existing
                session.execute_write(
                    lambda tx, s=s: tx.run(
                        """
                        MERGE (st:Student {name: $name})
                        RETURN st
                        """,
                        name=s["name"],
                    )
                )

            print("Creating Courses...")
            for c in courses:
                session.execute_write(
                    lambda tx, c=c: tx.run(
                        """
                        MERGE (co:Course {code: $code})
                        SET co.title = $title
                        RETURN co
                        """,
                        code=c["code"],
                        title=c["title"],
                    )
                )

            print("Creating ENROLLED_IN relationships...")
            for name, code, grade in enrollments:
                session.execute_write(
                    lambda tx, name=name, code=code, grade=grade: tx.run(
                        """
                        // MERGE both nodes to ensure they exist
                        MERGE (s:Student {name: $name})
                        MERGE (c:Course {code: $code})
                        // Create (or match) the relationship and set a property
                        MERGE (s)-[r:ENROLLED_IN]->(c)
                        SET r.grade = $grade
                        """,
                        name=name,
                        code=code,
                        grade=grade,
                    )
                )

            print("Creating FRIENDS_WITH relationships...")
            for a, b in friendships:
                session.execute_write(
                    lambda tx, a=a, b=b: tx.run(
                        """
                        MERGE (s1:Student {name: $a})
                        MERGE (s2:Student {name: $b})
                        // Undirected friendship: ensure only one edge by merging both ways
                        MERGE (s1)-[:FRIENDS_WITH]-(s2)
                        """,
                        a=a,
                        b=b,
                    )
                )

            print("Data load complete.")

    # --- QUERIES: simple reads with MATCH/WHERE/RETURN ---
    def query_examples(self):
        with self.driver.session(database=self.database) as session:
            print("\nAll enrollments (Student, Course, Grade):")
            result = session.execute_read(
                lambda tx: list(tx.run(
                    """
                    MATCH (s:Student)-[r:ENROLLED_IN]->(c:Course)
                    RETURN s.name AS student, c.code AS course, r.grade AS grade
                    ORDER BY student, course
                    """
                ))
            )
            for record in result:
                print(f"  {record['student']} -> {record['course']} (grade: {record['grade']})")

            print("\nClassmates of Bob (students who share any course):")
            classmates = session.execute_read(
                lambda tx: list(tx.run(
                    """
                    MATCH (b:Student {name: $name})-[:ENROLLED_IN]->(c)<-[:ENROLLED_IN]-(classmate)
                    WHERE classmate <> b
                    RETURN DISTINCT classmate.name AS name
                    ORDER BY name
                    """,
                    name="Bob",
                ))
            )
            for record in classmates:
                print(f"  {record['name']}")

            print("\nNumber of students per course:")
            counts = session.execute_read(
                lambda tx: list(tx.run(
                    """
                    MATCH (:Student)-[:ENROLLED_IN]->(c:Course)
                    RETURN c.title AS course, count(*) AS num_students
                    ORDER BY num_students DESC
                    """
                ))
            )
            for record in counts:
                print(f"  {record['course']}: {record['num_students']}")

            print("\nFriends of Alice:")
            friends = session.execute_read(
                lambda tx: list(tx.run(
                    """
                    MATCH (:Student {name: $name})-[:FRIENDS_WITH]-(f)
                    RETURN f.name AS friend
                    ORDER BY friend
                    """,
                    name="Alice",
                ))
            )
            for record in friends:
                print(f"  {record['friend']}")

def main():
    app = Neo4jBasics(URI, USER, PASSWORD, DBNAME)
    try:
        app.create_constraints()
        app.load_sample_data()
        app.query_examples()
    finally:
        app.close()

if __name__ == "__main__":
    main()
