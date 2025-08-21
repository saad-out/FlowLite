// Clear
MATCH (n) DETACH DELETE n;

// Workflow + Steps
CREATE (w:Workflow {id: randomUUID(), name: "Returns & Refunds", goal: "Process refunds within 14 days"});

UNWIND [
  {n:"Receive Request", o:1, d:"Capture return request via form/email"},
  {n:"Warehouse Inspection", o:2, d:"Inspect item, update condition"},
  {n:"Finance Approval", o:3, d:"Verify payment + policy compliance"},
  {n:"Refund Processed", o:4, d:"Trigger refund and notify customer"}
] AS s
CREATE (st:Step {id: randomUUID(), name: s.n, order: s.o, description: s.d})
WITH st
MATCH (w:Workflow {name: "Returns & Refunds"})
CREATE (w)-[:HAS_STEP]->(st);

MATCH (w:Workflow {name: "Returns & Refunds"})
WITH w
MATCH (s:Step)<-[:HAS_STEP]-(w)
WITH w, s ORDER BY s.order
WITH w, collect(s) AS steps
FOREACH (i IN range(0, size(steps)-2) |
  FOREACH (a IN [steps[i]] | FOREACH (b IN [steps[i+1]] |
    MERGE (a)-[:NEXT]->(b)
  ))
)
WITH w, steps
MERGE (w)-[:FIRST_STEP]->(steps[0]);

// Documents
UNWIND [
  {t:"Return Policy", u:"https://example.com/return-policy", tags:["policy","returns"]},
  {t:"Warehouse Checklist", u:"https://example.com/checklist", tags:["warehouse","qa"]},
  {t:"Finance SOP", u:"https://example.com/finance-sop", tags:["finance","approval"]},
  {t:"Refund Email Template", u:"https://example.com/refund-template", tags:["email","customer"]}
] AS d
CREATE (doc:Document {id: randomUUID(), title: d.t, url: d.u, tags: d.tags});

// Link docs to steps
MATCH (w:Workflow {name:"Returns & Refunds"})-[:HAS_STEP]->(s:Step {order:1})
MATCH (d:Document {title:"Return Policy"})
CREATE (s)-[:NEEDS_DOC]->(d);

MATCH (w)-[:HAS_STEP]->(s2:Step {order:2})
MATCH (d2:Document {title:"Warehouse Checklist"})
CREATE (s2)-[:NEEDS_DOC]->(d2);

MATCH (w)-[:HAS_STEP]->(s3:Step {order:3})
MATCH (d3:Document {title:"Finance SOP"})
CREATE (s3)-[:NEEDS_DOC]->(d3);

MATCH (w)-[:HAS_STEP]->(s4:Step {order:4})
MATCH (d4:Document {title:"Refund Email Template"})
CREATE (s4)-[:NEEDS_DOC]->(d4);

// Agents
UNWIND [
  {n:"Warehouse Bot", k:"ai"},
  {n:"Finance Reviewer", k:"human"}
] AS a
CREATE (ag:Agent {id: randomUUID(), name: a.n, kind: a.k});

MATCH (w:Workflow {name:"Returns & Refunds"})-[:HAS_STEP]->(s:Step {order:2})
MATCH (ag:Agent {name:"Warehouse Bot"})
CREATE (s)-[:ASSIGNED_TO]->(ag);

MATCH (w)-[:HAS_STEP]->(s3:Step {order:3})
MATCH (ag2:Agent {name:"Finance Reviewer"})
CREATE (s3)-[:ASSIGNED_TO]->(ag2);
