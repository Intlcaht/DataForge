# QuantaQL - Complete Specification

## 1. Introduction

QuantaQL is a unified query language for QuantaDB, a polyglot database system integrating multiple specialized storage engines:
- PostgreSQL (scalar data)
- MongoDB (document data)
- Neo4j (relational/graph data)
- InfluxDB (time-series/metric data)

### 1.1 Core Design Philosophy

QuantaQL abstracts storage engine complexities, providing a unified interface across diverse data models while maintaining the following principles:

- **Unified Access**: Seamless operations across heterogeneous storage engines
- **Type Awareness**: First-class support for scalar, document, relation, and metric data
- **Transactional Integrity**: ACID guarantees across diverse engines
- **Distinctive Syntax**: Clear, concise language unlike SQL, Cypher, InfluxQL, or MongoDB
- **Graph-Centricity**: Natural relationship navigation and traversal
- **Extensibility**: Support for custom logic and future engines
- **Analytics-Ready**: Built-in analytics and monitoring capabilities
- **Schema Evolution**: Flexible adaptation to changing requirements

### 1.2 Language Structure

QuantaQL uses a declarative syntax with clear, English-like commands:
- Commands are case-insensitive (convention uses UPPERCASE for keywords)
- Statements end with semicolons
- Identifiers are case-sensitive
- Whitespace is ignored except within string literals
- Comments use `--` for single line and `/* */` for multi-line

## 2. Data Model

### 2.1 Core Data Types

| Type     | Description                          | Storage Engine          |
|----------|--------------------------------------|-------------------------|
| SCALAR   | Primitive values (string, number, boolean, etc.) | PostgreSQL    |
| DOCUMENT | Nested JSON-like objects             | MongoDB                 |
| RELATION | Graph edges between records          | Neo4j                   |
| METRIC   | Time-series data points              | InfluxDB                |
| TIME     | ISO timestamps                       | All engines             |
| DURATION | Time intervals                       | All engines             |
| GEO      | Geographic coordinates or shapes     | PostgreSQL+MongoDB      |
| ARRAY    | Ordered collections of any type      | All engines             |
| MAP      | Key-value collections                | All engines             |
| CUSTOM   | User-defined composite types         | All engines (schema-dependent) |

### 2.2 Scalar Subtypes

| Subtype    | Description                  | Examples                    |
|------------|------------------------------|----------------------------|
| STRING     | Text data                    | "hello", 'world'           |
| INT        | Integer numbers              | 42, -7                     |
| FLOAT      | Floating-point numbers       | 3.14, -0.01                |
| BOOLEAN    | Boolean values               | true, false                |
| UUID       | Universally unique identifier| uuid(), "550e8400-e29b-41d4-a716-446655440000" |
| DECIMAL    | Precise decimal numbers      | decimal("123.45")          |
| BINARY     | Binary data                  | binary("base64string")     |
| ENUM       | Enumerated values            | status:["active","inactive"] |
| DATE       | Calendar date                | date("2025-05-21")         |
| TIME       | ISO timestamps               | time("2025-05-21T14:30:00Z") |
| IP         | IP address                   | ip("192.168.1.1")          |
| URL        | URL/URI                      | url("https://example.com") |
| PERCENTAGE | Percentage values            | percentage(75)             |
| CURRENCY   | Monetary values with currency| currency("USD", 10.99)     |

### 2.3 Metric Subtypes

| Subtype    | Description                  | Examples                    |
|------------|------------------------------|----------------------------|
| COUNT      | Simple counter metrics       | METRIC<COUNT>              |
| GAUGE      | Point-in-time value metrics  | METRIC<GAUGE>              |
| HISTOGRAM  | Distribution of values       | METRIC<HISTOGRAM>          |
| DURATION   | Time measurements            | METRIC<DURATION>           |
| PERCENTAGE | Percentage metrics           | METRIC<PERCENTAGE>         |
| CUSTOM     | User-defined metrics         | METRIC<CUSTOM>             |

### 2.4 Storage Engine Mapping

Each data type is optimally mapped to its specialized storage engine:

```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   PostgreSQL   │  │    MongoDB     │  │     Neo4j      │  │    InfluxDB    │
│                │  │                │  │                │  │                │
│  SCALAR types  │  │ DOCUMENT types │  │ RELATION types │  │  METRIC types  │
│                │  │                │  │                │  │                │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
         │                 │                   │                    │
         └─────────────────┴───────────────────┴────────────────────┘
                                     │
                           ┌─────────────────────┐
                           │     QuantaQL API    │
                           └─────────────────────┘
```

## 3. Schema Definition

### 3.1 Records

Records are the fundamental data entities in QuantaQL, containing typed fields that map to different storage engines.

```quantaql
DEFINE RECORD record_name IN bucket_name (
  field_name: type [constraints],
  ...
);
```

Example:
```quantaql
DEFINE RECORD tasks IN task_app (
  id: SCALAR<UUID> PRIMARY,
  title: SCALAR<STRING> INDEX,
  description: DOCUMENT,
  status: SCALAR<STRING> DEFAULT "pending",
  priority: SCALAR<STRING> DEFAULT "medium",
  created_at: TIME DEFAULT NOW(),
  due_date: TIME,
  completion_time: METRIC<DURATION>,
  assignees: RELATION<users> MANY,
  project: RELATION<projects> ONE,
  tags: ARRAY<SCALAR<STRING>>
);
```

### 3.2 Field Constraints

| Constraint  | Description                                     | Example                        |
|-------------|-------------------------------------------------|--------------------------------|
| PRIMARY     | Primary identifier                              | id: SCALAR<UUID> PRIMARY       |
| UNIQUE      | Unique value across records                     | email: SCALAR<STRING> UNIQUE   |
| INDEX       | Create index for field                          | status: SCALAR<STRING> INDEX   |
| DEFAULT     | Default value if not specified                  | created_at: TIME DEFAULT NOW() |
| NOT NULL    | Value cannot be null                            | title: SCALAR<STRING> NOT NULL |
| CHECK       | Value must satisfy a condition                  | age: SCALAR<INT> CHECK > 0     |
| REFERENCES  | Foreign key reference                           | dept_id: REFERENCES departments|
| ONE         | Single relationship                             | manager: RELATION<users> ONE   |
| MANY        | Multiple relationships                          | members: RELATION<users> MANY  |
| NULLABLE    | Field can be null                               | optional: SCALAR<STRING> NULLABLE |
| IMMUTABLE   | Value cannot be changed after initial setting   | created_at: TIME IMMUTABLE     |

### 3.3 Custom Types

Define reusable composite types for structured data.

```quantaql
DEFINE TYPE type_name (
  field_name: type [constraints],
  ...
);
```

Example:
```quantaql
DEFINE TYPE TaskMetadata (
  category: SCALAR<STRING>,
  estimated_effort: DURATION,
  notes: DOCUMENT
);

ALTER RECORD tasks ADD metadata: TaskMetadata;
```

### 3.4 Indexes

QuantaQL supports various index types optimized for different storage engines.

```quantaql
CREATE INDEX record_name(field1, field2, ...);
CREATE TEXT_INDEX record_name(document_field.text);
CREATE METRIC_INDEX record_name(metric_field) RETAIN "90d";
CREATE GRAPH_INDEX record_name(relation_field) TYPE "relation_type";
CREATE GEO_INDEX record_name(geo_field);
CREATE COMPOUND_INDEX record_name(field1, field2) WHERE condition;
CREATE UNIQUE_INDEX record_name(field1, field2);
```

Example:
```quantaql
CREATE INDEX tasks(due_date, status);
CREATE TEXT_INDEX tasks(description.text);
CREATE METRIC_INDEX tasks(completion_time) RETAIN "90d";
CREATE GRAPH_INDEX tasks(assignees) TYPE "assigned_to";
CREATE GEO_INDEX locations(coordinates) MAX_DISTANCE "10km";
```

### 3.5 Buckets

Buckets are logical namespaces for records, allowing organization and access control.

```quantaql
CREATE BUCKET bucket_name;
CREATE BUCKET bucket_name WITH RETENTION "90d";
CREATE BUCKET bucket_name WITH REPLICATION 3;
DROP BUCKET bucket_name;
```

## 4. Data Operations

### 4.1 Adding Records

```quantaql
ADD record_name {
  field1: value1,
  field2: value2,
  ...
};
```

Example:
```quantaql
ADD tasks {
  id: uuid(),
  title: "Implement login feature",
  description: { text: "Add OAuth2 authentication", attachments: ["spec.pdf"] },
  status: "pending",
  priority: "high",
  due_date: time("2025-06-01"),
  metadata: { category: "development", estimated_effort: duration("4h"), notes: { details: "Use JWT tokens" } },
  assignees: [LINK users(username = "alice93")],
  project: LINK projects(name = "Auth System"),
  tags: ["auth", "backend"]
};
```

### 4.2 Batch Operations

```quantaql
BATCH ADD record_name [
  { field1: value1, ... },
  { field1: value2, ... },
  ...
];
```

Example:
```quantaql
BATCH ADD tasks [
  { id: uuid(), title: "Fix UI bug", status: "pending", due_date: time("2025-06-10") },
  { id: uuid(), title: "Update API docs", status: "pending", due_date: time("2025-06-15") }
];
```

### 4.3 Finding Records

```quantaql
FIND record_name.field1, record_name.field2, ...
MATCH condition
[ORDER BY fields]
[LIMIT n]
[OFFSET m]
[CACHE FOR duration];
```

Example:
```quantaql
FIND tasks.id, tasks.title, tasks.description.text, tasks.metadata.category
MATCH tasks.tags INCLUDES "auth" AND tasks.due_date > time("2025-05-01")
ORDER BY tasks.due_date ASC
LIMIT 10
OFFSET 20
CACHE FOR duration("30m");
```

### 4.4 Updating Records

```quantaql
UPDATE record_name SET field1 = value1, field2 = value2, ... MATCH condition;
```

Example:
```quantaql
UPDATE tasks SET status = "completed", completion_time = duration("3h 15m") MATCH id = "task_123";
```

### 4.5 Removing Records

```quantaql
REMOVE record_name MATCH condition;
```

Example:
```quantaql
REMOVE tasks MATCH status = "completed" AND due_date < time("2025-01-01");
```

### 4.6 Recording Metrics

```quantaql
RECORD record_name.metric_field(record_id, value);
```

Example:
```quantaql
RECORD tasks.completion_time("task_123", duration("3h 15m"));
```

## 5. Graph Operations

### 5.1 Linking Records

```quantaql
LINK record_name1(condition) TO record_name2(condition) AS "relation_type" [WITH attributes];
```

Example:
```quantaql
LINK tasks(id = "task_123") TO users(username = "bob42") AS "assigned_to" WITH { assigned_at: now(), role: "reviewer" };
```

### 5.2 Unlinking Records

```quantaql
UNLINK record_name1(condition) FROM record_name2(condition) [WHERE relation_condition];
```

Example:
```quantaql
UNLINK tasks(id = "task_123") FROM users(username = "bob42") WHERE role = "reviewer";
```

### 5.3 Traversing Relationships

```quantaql
FIND fields
NAVIGATE path_expression
MATCH condition;
```

Example:
```quantaql
FIND tasks.title, users.username
NAVIGATE tasks -> project:projects, tasks -> assignees:users
MATCH projects.name = "Auth System";
```

### 5.4 Graph Pattern Matching

```quantaql
FIND return_fields
PATTERN pattern_expression
MATCH condition;
```

Example:
```quantaql
FIND path.length, users1.username, users2.username
PATTERN (users1:users) -> [assignees*1..2] -> (users2:users)
MATCH users1.username = "alice93"
RETURN path;
```

### 5.5 Graph Algorithms

```quantaql
FIND nodes.field, algorithm(parameters) AS result
GRAPH_ALGORITHM(
  NODES record_set,
  EDGES edge_expression
)
[additional_clauses];
```

Example:
```quantaql
FIND users.username, page_rank(users, 0.85, 20) AS influence_score
GRAPH_ALGORITHM(
  NODES users,
  EDGES NAVIGATE tasks -> assignees:users
)
ORDER BY influence_score DESC
LIMIT 5;
```

## 6. Time-Series & Metrics

### 6.1 Recording Metrics

```quantaql
RECORD record_name.metric_field(record_id, value);
```

Example:
```quantaql
RECORD tasks.completion_time("task_123", duration("3h 45m"));
```

### 6.2 Aggregating Metrics

```quantaql
FIND record_name.field, AGG_FUNCTION(record_name.metric_field) AS alias
[GROUP BY expressions]
[TIME_WINDOW window_expression];
```

Example:
```quantaql
FIND projects.name, AVG(tasks.completion_time) AS avg_completion
NAVIGATE tasks -> project:projects
MATCH tasks.due_date > time("2025-01-01")
GROUP BY projects.name;
```

### 6.3 Downsampling

```quantaql
FIND AGG_FUNCTION(record_name.metric_field) AS alias
MATCH condition
DOWNSAMPLE BY time_interval;
```

Example:
```quantaql
FIND AVG(tasks.completion_time) AS daily_avg
MATCH tasks.due_date > time("2025-01-01")
DOWNSAMPLE BY time("1d");
```

### 6.4 Continuous Queries

```quantaql
CREATE CONTINUOUS QUERY query_name
COMPUTE AGG_FUNCTION(record_name.metric_field) AS result
MATCH condition
DOWNSAMPLE BY time_interval
STORE IN record_name;
```

### 6.5 Anomaly Detection

```quantaql
FIND fields
MATCH DETECT_ANOMALY(record_name.metric_field, parameters) = true
AND other_conditions;
```

Example:
```quantaql
FIND tasks.id, tasks.title, tasks.completion_time
MATCH DETECT_ANOMALY(tasks.completion_time, threshold=3.0) = true
AND tasks.due_date > time("2025-01-01");
```

## 7. Aggregations

### 7.1 Aggregation Functions

| Function   | Description                          | Example                         |
|------------|--------------------------------------|----------------------------------|
| COUNT      | Count records or values              | COUNT(*)                         |
| SUM        | Sum values                           | SUM(tasks.effort)                |
| AVG        | Average of values                    | AVG(tasks.completion_time)       |
| MIN        | Minimum value                        | MIN(tasks.due_date)              |
| MAX        | Maximum value                        | MAX(tasks.completion_time)       |
| MEDIAN     | Median value                         | MEDIAN(tasks.effort)             |
| PERCENTILE | Nth percentile                       | PERCENTILE(tasks.effort, 95)     |
| STDDEV     | Standard deviation                   | STDDEV(tasks.completion_time)    |
| VAR        | Variance                             | VAR(tasks.completion_time)       |
| ARRAY      | Collect values into array            | ARRAY(tasks.tags)                |
| DISTINCT   | Unique values                        | COUNT(DISTINCT tasks.tags)       |
| GROUP_CONCAT| Concatenate values                  | GROUP_CONCAT(tasks.title, ", ")  |
| FIRST      | First value in order                 | FIRST(tasks.completion_time)     |
| LAST       | Last value in order                  | LAST(tasks.completion_time)      |
| TOP_N      | Top N values                         | TOP_N(tasks.priority, 3)         |

### 7.2 Group By Clause

```quantaql
FIND aggregation_expressions
GROUP BY grouping_expressions
[HAVING condition];
```

Example:
```quantaql
FIND users.username, COUNT(*) AS task_count, AVG(tasks.completion_time) AS avg_completion
NAVIGATE tasks -> assignees:users
MATCH tasks.priority = "high"
GROUP BY users.username
HAVING COUNT(*) > 3
ORDER BY task_count DESC
LIMIT 5;
```

### 7.3 Window Functions

```quantaql
FIND record_name.field,
     WINDOW_FUNCTION(record_name.field) OVER (
       [PARTITION BY partition_expressions]
       [ORDER BY order_expressions]
       [window_frame_clause]
     ) AS alias
```

Example:
```quantaql
FIND tasks.title, tasks.completion_time,
     AVG(tasks.completion_time) OVER (
       PARTITION BY tasks.project.id
       ORDER BY tasks.due_date
       RANGE duration("7d") PRECEDING
     ) AS project_avg_completion
MATCH tasks.status = "completed";
```

## 8. Transactions

### 8.1 Basic Transactions

```quantaql
START TRANSACTION;
-- operations
COMMIT;
-- or
ROLLBACK;
```

Example:
```quantaql
START TRANSACTION;

ADD tasks {
  id: uuid(),
  title: "Test API endpoints",
  status: "pending",
  priority: "medium",
  due_date: time("2025-06-10"),
  project: LINK projects(name = "Auth System")
};

RECORD projects.progress(LAST_INSERT_ID(project), 0.1);

COMMIT;
```

### 8.2 Savepoints

```quantaql
START TRANSACTION;
-- operations
SAVEPOINT savepoint_name;
-- more operations
ROLLBACK TO savepoint_name;
-- or continue with other operations
COMMIT;
```

Example:
```quantaql
START TRANSACTION;

SAVEPOINT before_reassign;

LINK tasks(id = "task_123") TO users(username = "charlie01") AS "assigned_to";

-- If reassignment fails
ROLLBACK TO before_reassign;

-- Otherwise
COMMIT;
```

### 8.3 Transaction Isolation Levels

```quantaql
START TRANSACTION ISOLATION LEVEL isolation_level;
```

Where `isolation_level` can be:
- READ UNCOMMITTED
- READ COMMITTED
- REPEATABLE READ
- SERIALIZABLE

Example:
```quantaql
START TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- critical operations
COMMIT;
```

## 9. Schema Evolution

### 9.1 Modifying Records

```quantaql
ALTER RECORD record_name
ADD field_name: type [constraints],
DROP field_name,
MODIFY field_name: new_type [constraints];
```

Example:
```quantaql
ALTER RECORD tasks
ADD completion_date: TIME,
ADD effort: SCALAR<FLOAT> DEFAULT 0.0,
DROP tags;
```

### 9.2 Renaming Fields

```quantaql
ALTER RECORD record_name
RENAME old_field_name TO new_field_name;
```

Example:
```quantaql
ALTER RECORD tasks
RENAME completion_time TO processing_duration;
```

### 9.3 Adding Relationships

```quantaql
ALTER RECORD record_name
ADD RELATION relation_name: related_record [ONE|MANY];
```

Example:
```quantaql
ALTER RECORD tasks
ADD RELATION depends_on: tasks MANY;
```

### 9.4 Modifying Custom Types

```quantaql
ALTER TYPE type_name
ADD field_name: type [constraints],
DROP field_name,
MODIFY field_name: new_type [constraints];
```

### 9.5 Record Versioning

```quantaql
CREATE VERSION record_name.v2 FROM record_name EXTENDING (
  ADD new_field: type,
  DROP old_field,
  ...
);
```

## 10. Security & Access Control

### 10.1 Users and Roles

```quantaql
CREATE USER username WITH PASSWORD 'password';
CREATE ROLE role_name;
GRANT ROLE role_name TO username;
REVOKE ROLE role_name FROM username;
```

### 10.2 Permissions

```quantaql
GRANT permission ON object TO principal;
DENY permission ON object TO principal;
```

Where:
- `permission` can be FIND, ADD, UPDATE, REMOVE, LINK, NAVIGATE, etc.
- `object` can be a record, field, bucket, etc.
- `principal` can be a user or role

Example:
```quantaql
GRANT FIND(tasks.title, tasks.status, tasks.due_date), ADD(tasks) TO ROLE task_user;
GRANT FIND(tasks.description.notes) TO ROLE public_api;
DENY NAVIGATE(tasks -> assignees) TO ROLE external_api;
```

### 10.3 Row-Level Security

```quantaql
CREATE POLICY policy_name ON record_name
USING (condition);
```

Example:
```quantaql
CREATE POLICY assignee_access ON tasks
USING (
  current_user_id() IN (
    FIND users.id NAVIGATE tasks -> assignees:users
  )
);
```

### 10.4 Field-Level Encryption

```quantaql
ALTER RECORD record_name
ENCRYPT field_name WITH KEY 'key_name';
```

Example:
```quantaql
ALTER RECORD users
ENCRYPT personal_info WITH KEY 'user_pii_key';
```

### 10.5 Audit Logging

```quantaql
ENABLE AUDIT record_name
FOR operations
LOG TO log_name;
```

Example:
```quantaql
ENABLE AUDIT tasks
FOR ADD, UPDATE, REMOVE
LOG TO "task_audit_log";
```

## 11. Advanced Features

### 11.1 Common Table Expressions (CTEs)

```quantaql
WITH cte_name AS (
  query_expression
)
main_query_using_cte;
```

Example:
```quantaql
WITH active_projects AS (
  FIND projects.id, projects.name, COUNT(*) AS task_count
  NAVIGATE tasks -> project:projects
  MATCH tasks.due_date > time("2025-01-01")
  GROUP BY projects.id, projects.name
  HAVING COUNT(*) > 5
)
FIND active_projects.name, active_projects.task_count, users.username
NAVIGATE active_projects -> owner:users
ORDER BY active_projects.task_count DESC;
```

### 11.2 Parameterized Queries

```quantaql
PREPARE query_name AS query_with_parameters;
EXECUTE query_name(param1, param2, ...);
```

Example:
```quantaql
PREPARE find_tasks_by_user AS
  FIND tasks.title, tasks.status, tasks.due_date
  NAVIGATE tasks -> assignees:users
  MATCH users.username = $1;

EXECUTE find_tasks_by_user("alice93");
```

### 11.3 Custom Functions

```quantaql
DEFINE FUNCTION function_name(param1: type1, param2: type2, ...) RETURNS return_type AS
  function_body;
```

Example:
```quantaql
DEFINE FUNCTION task_priority_score(priority: STRING, due_date: TIME) RETURNS SCALAR<INT> AS
  CASE
    WHEN priority = "high" THEN 100
    WHEN priority = "medium" THEN 50
    WHEN priority = "low" THEN 10
    ELSE 0
  END + CASE
    WHEN due_date < now() THEN 20
    ELSE 0
  END;
```

### 11.4 Stored Procedures

```quantaql
DEFINE PROCEDURE procedure_name(param1: type1, param2: type2, ...) AS
BEGIN
  statement1;
  statement2;
  ...
END;
```

Example:
```quantaql
DEFINE PROCEDURE complete_task(task_id: UUID, completion_duration: DURATION) AS
BEGIN
  UPDATE tasks SET status = "completed" MATCH id = task_id;
  RECORD tasks.completion_time(task_id, completion_duration);
  
  -- Update project progress
  WITH task_project AS (
    FIND projects.id, projects.progress.value
    NAVIGATE tasks -> project:projects
    MATCH tasks.id = task_id
  )
  RECORD projects.progress(task_project.id, task_project.value + 0.05);
END;
```

### 11.5 Triggers

```quantaql
CREATE TRIGGER trigger_name
{BEFORE | AFTER} {event}
ON record_name
[FOR EACH {ROW | STATEMENT}]
[WHEN condition]
EXECUTE (actions);
```

Example:
```quantaql
CREATE TRIGGER update_project_progress
AFTER UPDATE tasks
FOR EACH ROW
WHEN NEW.status = "completed"
EXECUTE (
  RECORD projects.progress(NEW.project.id, OLD.progress.value + 0.05)
);
```

### 11.6 Views

```quantaql
CREATE VIEW view_name AS query_expression;
```

Example:
```quantaql
CREATE VIEW overdue_tasks AS
  FIND tasks.id, tasks.title, tasks.due_date, users.username AS assignee
  NAVIGATE tasks -> assignees:users
  MATCH tasks.status != "completed" AND tasks.due_date < now();
```

### 11.7 Query Hints

```quantaql
FIND fields
MATCH condition
HINT hint_type(hint_value);
```

Example:
```quantaql
FIND tasks.title, users.username, projects.name
NAVIGATE tasks -> assignees:users, tasks -> project:projects
MATCH tasks.due_date > time("2025-05-01")
HINT FORCE_INDEX(tasks.due_date);
```

Available hints:
- `FORCE_INDEX(index_name)`
- `PARALLEL(degree)`
- `CACHE_RESULT(duration)`
- `NO_GRAPH_CACHE`
- `PREFER_ENGINE(engine_name)`

## 12. Monitoring & Observability

### 12.1 Query Metrics

```quantaql
FIND system.query_metrics.*
MATCH conditions;
```

Example:
```quantaql
FIND system.query_metrics.query_id, system.query_metrics.execution_time, system.query_metrics.rows_scanned
MATCH system.query_metrics.executed_at > time("2025-05-01");
```

### 12.2 Health Checks

```quantaql
CHECK HEALTH [component];
```

Example:
```quantaql
CHECK HEALTH STORAGE_ENGINE(Neo4j, PostgreSQL, MongoDB, InfluxDB);
```

### 12.3 Alerts

```quantaql
CREATE ALERT alert_name
ON metric_expression
WHEN condition
OVER time_window
NOTIFY notification_target;
```

Example:
```quantaql
CREATE ALERT overdue_tasks
ON tasks.processing_duration
WHEN AVG(value) > duration("1d")
OVER time("1h")
NOTIFY webhook("https://alerts.taskapp.com");
```

### 12.4 Explain Plans

```quantaql
EXPLAIN query;
EXPLAIN ANALYZE query;
```

Example:
```quantaql
EXPLAIN
FIND tasks.title, users.username
NAVIGATE tasks -> assignees:users
MATCH tasks.due_date > time("2025-05-01");
```

## 13. Data Migration

### 13.1 Copying Records

```quantaql
COPY source_record TO target_record
TRANSFORM (
  target_field1 = expression1,
  target_field2 = expression2,
  ...
)
MATCH condition;
```

Example:
```quantaql
COPY old_tasks TO tasks
TRANSFORM (
  id = old_tasks.id,
  title = old_tasks.task_name,
  description = { text: old_tasks.details },
  status = old_tasks.state
)
MATCH old_tasks.state != "archived";
```

### 13.2 Bulk Import/Export

```quantaql
IMPORT INTO record_name
FROM 'file_path'
FORMAT format_type
[TRANSFORM (transformations)];

EXPORT FROM record_name
TO 'file_path'
FORMAT format_type
MATCH condition;
```

Example:
```quantaql
IMPORT INTO tasks
FROM 's3://bucket/tasks.csv'
FORMAT CSV
TRANSFORM (
  id = uuid(),
  title = $1,
  description = { text: $2 },
  due_date = parse_time($3, "YYYY-MM-DD")
);

EXPORT FROM tasks
TO 'hdfs://cluster/completed_tasks.json'
FORMAT JSON
MATCH status = "completed";
```

## 14. System Configuration

### 14.1 Storage Engine Configuration

```quantaql
CONFIGURE STORAGE_ENGINE engine_name
SET parameter = value;
```

Example:
```quantaql
CONFIGURE STORAGE_ENGINE MongoDB
SET connection_pool_size = 100;
```

### 14.2 Query Processing

```quantaql
CONFIGURE QUERY_ENGINE
SET parameter = value;
```

Example:
```quantaql
CONFIGURE QUERY_ENGINE
SET max_parallel_queries = 8;
```

### 14.3 Caching

```quantaql
CONFIGURE CACHE
SET parameter = value;
```

Example:
```quantaql
CONFIGURE CACHE
SET default_ttl = duration("10m");
```

## 15. Spatial Operations

### 15.1 Geo Types

```quantaql
point(latitude, longitude)
polygon([[lat1, lon1], [lat2, lon2], ...])
line([[lat1, lon1], [lat2, lon2], ...])
circle(latitude, longitude, radius)
```

### 15.2 Geo Functions

```quantaql
distance(geo1, geo2)
contains(geo1, geo2)
intersects(geo1, geo2)
nearby(geo, center, max_distance)
```

Example:
```quantaql
FIND locations.name, locations.address
MATCH nearby(locations.coordinates, point(37.7749, -122.4194), "5km")
ORDER BY distance(locations.coordinates, point(37.7749, -122.4194)) ASC;
```

## 16. Full-Text Search

### 16.1 Text Search

```quantaql
FIND record_name.field
MATCH TEXT_SEARCH(record_name.text_field, "search terms")
[WITH FUZZY | EXACT | STEMMING];
```

Example:
```quantaql
FIND tasks.title, tasks.description
MATCH TEXT_SEARCH(tasks.description.text, "authentication oauth") WITH STEMMING
ORDER BY TEXT_SCORE DESC;
```

### 16.2 Text Indexes

```quantaql
CREATE TEXT_INDEX record_name(field) [WITH options];
```

Example:
```quantaql
CREATE TEXT_INDEX tasks(description.text) WITH LANGUAGE "english", ANALYZER "standard";
```

### 16.3 Text Functions

| Function        | Description                                | Example                                |
|-----------------|--------------------------------------------|----------------------------------------|
| TEXT_SCORE      | Relevance score for text search results    | ORDER BY TEXT_SCORE DESC               |
| TEXT_CONTAINS   | Check if text contains a substring         | TEXT_CONTAINS(description, "urgent")   |
| TEXT_EXTRACT    | Extract patterns from text                 | TEXT_EXTRACT(email, "email")           |
| TEXT_SUMMARIZE  | Generate a summary of text                 | TEXT_SUMMARIZE(article.content, 100)   |
| TEXT_SENTIMENT  | Calculate sentiment score                  | TEXT_SENTIMENT(comment.text)           |
| TEXT_ENTITIES   | Extract named entities                     | TEXT_ENTITIES(document.content)        |
| TEXT_CLASSIFY   | Classify text into categories              | TEXT_CLASSIFY(description, "topics")   |

Example:
```quantaql
FIND tasks.title, TEXT_SUMMARIZE(tasks.description.text, 50) AS summary
MATCH TEXT_SEARCH(tasks.description.text, "important feature") 
AND TEXT_SENTIMENT(tasks.description.text) > 0.5;
```