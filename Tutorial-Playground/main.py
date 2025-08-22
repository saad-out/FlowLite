# flowlite_basics.py
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"  # Adjust if ports differ
USER = "neo4j"
PASSWORD = "testTEST0"
DBNAME = "neo4j"

class FlowLiteBasics:
    def __init__(self, uri, user, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    # --- SCHEMA: constraints ---
    def create_constraints(self):
        """
        Creates uniqueness constraints for nodes
        """
        with self.driver.session(database=self.database) as session:
            print("Creating constraints (if not exist)...")
            session.run("""
                CREATE CONSTRAINT workflow_name IF NOT EXISTS
                FOR (w:Workflow) REQUIRE w.name IS UNIQUE
            """)
            session.run("""
                CREATE CONSTRAINT step_name IF NOT EXISTS
                FOR (s:Step) REQUIRE s.name IS UNIQUE
            """)
            session.run("""
                CREATE CONSTRAINT document_title IF NOT EXISTS
                FOR (d:Document) REQUIRE d.title IS UNIQUE
            """)
            session.run("""
                CREATE CONSTRAINT agent_name IF NOT EXISTS
                FOR (a:Agent) REQUIRE a.name IS UNIQUE
            """)
            print("Constraints ready.")

    # --- LOAD SAMPLE DATA: workflow, steps, docs, agents ---
    def load_sample_data(self):
        workflows = [
            {"name": "Refund Process", "goal": "Handle customer refunds within 7 days"},
        ]
        steps = [
            {"name": "Receive Request", "order": 1},
            {"name": "Validate Receipt", "order": 2},
            {"name": "Approve Refund", "order": 3},
            {"name": "Send Payment", "order": 4},
        ]
        documents = [
            {"title": "Refund Policy PDF"},
            {"title": "Receipt Template"},
            {"title": "Approval Form"},
        ]
        agents = [
            {"name": "Support Agent"},
            {"name": "Finance Officer"},
        ]

        with self.driver.session(database=self.database) as session:
            print("Creating Workflow...")
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MERGE (w:Workflow {name: $name})
                    SET w.goal = $goal
                    RETURN w
                    """,
                    name=workflows[0]["name"],
                    goal=workflows[0]["goal"],
                )
            )

            print("Creating Steps...")
            for s in steps:
                session.execute_write(
                    lambda tx, s=s: tx.run(
                        """
                        MERGE (st:Step {name: $name})
                        SET st.order = $order
                        RETURN st
                        """,
                        name=s["name"],
                        order=s["order"],
                    )
                )

            print("Creating Documents...")
            for d in documents:
                session.execute_write(
                    lambda tx, d=d: tx.run(
                        """
                        MERGE (doc:Document {title: $title})
                        RETURN doc
                        """,
                        title=d["title"],
                    )
                )

            print("Creating Agents...")
            for a in agents:
                session.execute_write(
                    lambda tx, a=a: tx.run(
                        """
                        MERGE (ag:Agent {name: $name})
                        RETURN ag
                        """,
                        name=a["name"],
                    )
                )

            print("Creating Relationships...")
            # Workflow -> Steps
            for s in steps:
                session.execute_write(
                    lambda tx, s=s: tx.run(
                        """
                        MATCH (w:Workflow {name: $wname})
                        MATCH (st:Step {name: $sname})
                        MERGE (w)-[:HAS_STEP]->(st)
                        """,
                        wname=workflows[0]["name"],
                        sname=s["name"],
                    )
                )

            # Step ordering
            for i in range(len(steps) - 1):
                session.execute_write(
                    lambda tx, s1=steps[i], s2=steps[i+1]: tx.run(
                        """
                        MATCH (s1:Step {name: $s1name})
                        MATCH (s2:Step {name: $s2name})
                        MERGE (s1)-[:NEXT]->(s2)
                        """,
                        s1name=s1["name"],
                        s2name=s2["name"],
                    )
                )

            # Assign docs + agents
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (s:Step {name: "Validate Receipt"})
                    MATCH (d:Document {title: "Receipt Template"})
                    MERGE (s)-[:NEEDS_DOC]->(d)
                    """
                )
            )
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (s:Step {name: "Approve Refund"})
                    MATCH (a:Agent {name: "Finance Officer"})
                    MERGE (s)-[:ASSIGNED_TO]->(a)
                    """
                )
            )

            print("Sample data load complete.")

    # --- QUERIES ---
    def query_examples(self):
        with self.driver.session(database=self.database) as session:
            print("\nWorkflow with steps in order:")
            result = session.execute_read(
                lambda tx: list(tx.run(
                    """
                    MATCH (w:Workflow {name: "Refund Process"})-[:HAS_STEP]->(s:Step)
                    RETURN s.name AS step, s.order AS order
                    ORDER BY s.order
                    """
                ))
            )
            for record in result:
                print(f"  Step {record['order']}: {record['step']}")

            print("\nSteps and their documents:")
            result = session.execute_read(
                lambda tx: list(tx.run(
                    """
                    MATCH (s:Step)-[:NEEDS_DOC]->(d:Document)
                    RETURN s.name AS step, d.title AS doc
                    ORDER BY s.name
                    """
                ))
            )
            for record in result:
                print(f"  {record['step']} needs {record['doc']}")

            print("\nSteps and their agents:")
            result = session.execute_read(
                lambda tx: list(tx.run(
                    """
                    MATCH (s:Step)-[:ASSIGNED_TO]->(a:Agent)
                    RETURN s.name AS step, a.name AS agent
                    ORDER BY s.name
                    """
                ))
            )
            for record in result:
                print(f"  {record['step']} assigned to {record['agent']}")

def main():
    app = FlowLiteBasics(URI, USER, PASSWORD, DBNAME)
    try:
        app.create_constraints()
        app.load_sample_data()
        app.query_examples()
    finally:
        app.close()

if __name__ == "__main__":
    main()
