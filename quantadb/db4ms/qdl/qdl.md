#### Overview
- **Purpose**: The EBNF grammar defines the syntax of QuantaQL, a query language designed to unify operations across multiple storage engines (PostgreSQL, MongoDB, Neo4j, InfluxDB) in QuantaDB. It supports scalar, document, relational, and time-series data with a declarative, English-like syntax.
- **Structure**: The grammar is modular, with rules grouped by functionality (schema definition, data operations, graph operations, etc.), reflecting the specification's organization. Each rule is designed to be concise yet expressive, capturing the language's flexibility and extensibility.
- **Conventions**:
  - Keywords are uppercase by convention but case-insensitive in practice.
  - Statements end with semicolons (`;`).
  - Identifiers are case-sensitive and composed of letters, digits, and underscores.
  - Whitespace is ignored except in string literals.
  - Comments are supported with `--` (single-line) or `/* */` (multi-line), though not explicitly included in the grammar as they are typically handled by the lexer.

#### Key Rules

1. **Program and Statement**
   - `program = statement { ";" statement } [ ";" ] ;`
     - Represents the entire QuantaQL program, allowing multiple semicolon-separated statements.
     - The optional trailing semicolon accommodates flexible input.
     - Statements cover all major language features: schema definitions, data operations, graph operations, transactions, security, and more.

2. **Schema Definition**
   - `schema_definition` includes rules for defining records, types, indexes, and buckets.
   - `record_definition`:
     - Syntax: `DEFINE RECORD identifier IN identifier ( field_definition , ... )`
     - Example: `DEFINE RECORD tasks IN task_app (id: SCALAR<UUID> PRIMARY, title: SCALAR<STRING>)`
     - Fields are defined with a name, data type, and optional constraints (e.g., `PRIMARY`, `UNIQUE`).
   - `data_type` supports the core types: `SCALAR`, `DOCUMENT`, `RELATION`, `METRIC`, etc., each mapped to a specific storage engine.
   - `constraint` captures field constraints like `PRIMARY`, `INDEX`, or `CHECK`, ensuring data integrity.
   - `index_definition` supports various index types (`TEXT`, `METRIC`, `GRAPH`, etc.) with options like retention periods or relation types.
   - `bucket_definition` defines logical namespaces with retention or replication options.

3. **Data Operations**
   - `data_operation` includes `ADD`, `BATCH ADD`, `FIND`, `UPDATE`, `REMOVE`, and `RECORD` for manipulating records and metrics.
   - `add_operation`: Adds a single record with field assignments (e.g., `ADD tasks { id: uuid(), title: "Task" }`).
   - `find_operation`: Retrieves data with conditions, ordering, and pagination (e.g., `FIND tasks.title MATCH tasks.status = "pending" LIMIT 10`).
   - `record_metric`: Records time-series data (e.g., `RECORD tasks.completion_time("task_123", duration("3h"))`).

4. **Graph Operations**
   - `graph_operation` supports linking, unlinking, navigating, pattern matching, and graph algorithms.
   - `link_operation`: Creates relationships (e.g., `LINK tasks(id = "task_123") TO users(username = "bob42") AS "assigned_to"`).
   - `navigate_operation`: Traverses relationships (e.g., `NAVIGATE tasks -> assignees:users`).
   - `pattern_operation`: Matches graph patterns (e.g., `PATTERN (users1:users) -> [assignees*1..2] -> (users2:users)`).
   - `graph_algorithm`: Executes algorithms like PageRank (e.g., `FIND users.username, page_rank(users, 0.85, 20) AS influence_score`).

5. **Metric Operations**
   - `metric_operation` handles time-series data with aggregation, downsampling, continuous queries, and anomaly detection.
   - `aggregate_metric`: Aggregates metrics (e.g., `FIND AVG(tasks.completion_time) GROUP BY projects.name`).
   - `downsample_metric`: Reduces data granularity (e.g., `DOWNSAMPLE BY time("1d")`).
   - `anomaly_detection`: Identifies outliers (e.g., `DETECT_ANOMALY(tasks.completion_time, threshold=3.0)`).

6. **Aggregations**
   - `aggregation` supports functions like `COUNT`, `SUM`, `AVG`, and window functions.
   - `window_function`: Computes values over a window (e.g., `AVG(tasks.completion_time) OVER (PARTITION BY tasks.project.id)`).

7. **Transactions**
   - `transaction` includes `START TRANSACTION`, `COMMIT`, `ROLLBACK`, and `SAVEPOINT` for ACID compliance.
   - `isolation_level` supports standard levels (`SERIALIZABLE`, etc.) for controlling transaction behavior.

8. **Security & Access Control**
   - `security_command` manages users, roles, permissions, row-level security, encryption, and auditing.
   - `permission_management`: Grants or denies permissions (e.g., `GRANT FIND(tasks.title) TO ROLE task_user`).
   - `row_level_security`: Restricts access based on conditions (e.g., `USING current_user_id() IN ...`).

9. **Advanced Features**
   - `advanced_feature` includes CTEs, parameterized queries, custom functions, stored procedures, triggers, views, and query hints.
   - `cte`: Enables reusable subqueries (e.g., `WITH active_projects AS (...)`).
   - `custom_function`: Defines reusable logic (e.g., `DEFINE FUNCTION task_priority_score(...)`).
   - `trigger`: Automates actions on events (e.g., `CREATE TRIGGER update_project_progress AFTER UPDATE tasks`).

10. **Spatial Operations**
    - `spatial_operation` supports geographic queries using functions like `distance`, `nearby`, and `contains`.
    - `geo_expression`: Defines points, polygons, lines, and circles (e.g., `point(37.7749, -122.4194)`).

11. **Full-Text Search**
    - `full_text_search` supports text queries with options like `FUZZY` or `STEMMING`.
    - `text_function`: Includes utilities like `TEXT_SUMMARIZE` or `TEXT_SENTIMENT`.

12. **Data Migration**
    - `data_migration` supports copying, importing, and exporting data with transformations.
    - `import_operation`: Imports data from files (e.g., `IMPORT INTO tasks FROM 's3://bucket/tasks.csv' FORMAT CSV`).

13. **Monitoring & Observability**
    - `monitoring_command` includes query metrics, health checks, alerts, and explain plans.
    - `explain_plan`: Analyzes query execution (e.g., `EXPLAIN FIND tasks.title ...`).

14. **System Configuration**
    - `system_configuration` configures storage engines, query engines, and caching (e.g., `CONFIGURE CACHE SET default_ttl = duration("10m")`).

#### Design Notes
- **Extensibility**: The grammar is designed to accommodate future extensions (e.g., new data types or storage engines) by using modular rules like `data_type` and `statement`.
- **Clarity**: Rules are named descriptively (e.g., `find_operation`, `graph_algorithm`) to align with QuantaQL's English-like syntax.
- **Storage Engine Mapping**: The grammar implicitly supports the specification's storage engine mappings by allowing type-specific operations (e.g., `METRIC` for InfluxDB, `RELATION` for Neo4j).
- **Error Handling**: While not explicit in EBNF, the grammar assumes a parser will handle invalid syntax (e.g., missing semicolons) or semantic errors (e.g., invalid constraints).
- **Limitations**: The grammar does not include comment syntax (`--` or `/* */`) as this is typically handled by the lexer. Similarly, whitespace handling is assumed to be managed by the tokenizer.

#### Example Usage
The grammar supports the example queries from the specification, such as:
- `DEFINE RECORD tasks IN task_app (id: SCALAR<UUID> PRIMARY, title: SCALAR<STRING> INDEX, ...);`
- `ADD tasks { id: uuid(), title: "Implement login feature", ... };`
- `FIND tasks.title, users.username NAVIGATE tasks -> assignees:users MATCH tasks.due_date > time("2025-05-01");`
- `CREATE INDEX tasks(due_date, status);`

Each of these examples can be parsed using the corresponding rules (`record_definition`, `add_operation`, `navigate_operation`, `index_definition`).

#### Assumptions
- The grammar assumes a lexer will handle tokenization of keywords, identifiers, literals, and operators.
- Case-insensitivity for keywords is enforced at the parser level, while identifiers remain case-sensitive.
- The `character` rule in string literals is simplified; in practice, it includes any valid Unicode character, with escaping rules handled by the lexer.

