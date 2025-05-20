

```markdown
# QuantaDB Specification

## 🧠 Overview

**QuantaDB** is a distributed polyglot database orchestration system built using **Ktor**, designed to manage logical **Buckets** of databases per microservice.

Each bucket contains:
- A **PostgreSQL** database for structured (relational) data
- A **MongoDB** database for documents
- A **Neo4j** graph database for relationships
- An **InfluxDB** database for metrics and time-series

Buckets are used as **logical namespaces**, each containing multiple **Records** (similar to tables). Every record can define a custom schema with various **typed attributes**, each mapped to the appropriate underlying data engine.

The system also introduces **QuantaQL**, a unified query language that:
- Interacts with all underlying engines
- Supports **ACID-like transactions**
- Offers expressive syntax for querying, inserting, and updating data across records

---

## 📦 Bucket & Record Model

### Buckets

A **Bucket** is a logical database unit for each microservice and contains multiple **Records** (like tables).

```

Bucket: <service-name>
├── Record: users
│   ├── scalar attributes → PostgreSQL
│   ├── document attributes → MongoDB
│   ├── relationship attributes → Neo4j
│   └── metric attributes → InfluxDB
├── Record: orders
├── Record: payments
└── ...

````

---

### Record Definition

A **Record** is a structured data model with typed attributes:

```json
{
  "record": "orders",
  "attributes": {
    "id": { "type": "scalar", "datatype": "string" },
    "customer": { "type": "document" },
    "total_cost": { "type": "scalar", "datatype": "float" },
    "delivery_route": { "type": "relation", "target": "routes" },
    "delivered_by": { "type": "relation", "target": "drivers" },
    "delivery_time": { "type": "metric", "unit": "duration" }
  }
}
````

---

## 🗣 QuantaQL - Query Language

### Language Goals

* Unified access to all data models
* Support for multiple records per bucket
* ACID-like transactional semantics
* Type-safe and composable syntax
* Easy to extend with custom operators or modules

---

### Language Features

| Primitive       | Description                             | Target DB  |
| --------------- | --------------------------------------- | ---------- |
| `scalar`        | Basic values (int, string, float, etc.) | PostgreSQL |
| `document`      | Nested JSON object                      | MongoDB    |
| `relation`      | Edges to other records                  | Neo4j      |
| `metric`        | Time-series values                      | InfluxDB   |
| `time(...)`     | ISO timestamp                           | All        |
| `duration(...)` | Range format                            | InfluxDB   |

---

## 🧾 Example Queries

### 1. Insert with Multi-type Attributes

```quantaql
BEGIN TRANSACTION;

INSERT INTO orders {
  id: "order_123",
  customer: {
    id: "cust_001",
    name: "Alice",
    address: "123 Market St"
  },
  total_cost: 89.50,
  delivery_time: duration("1d 3h"),
  delivered_by: relation("driver_004"),
  delivery_route: relation("route_789")
};

COMMIT;
```

---

### 2. Select Records Across Types

```quantaql
SELECT id, customer.name, total_cost, delivery_time
FROM orders
WHERE delivery_time > duration("1d")
  AND delivered_by.name = "Bob";
```

---

### 3. Update Record with New Metric

```quantaql
BEGIN TRANSACTION;

UPDATE orders
SET delivery_time = duration("2d 5h")
WHERE id = "order_123";

COMMIT;
```

---

### 4. Traverse Graph

```quantaql
SELECT id, delivery_route
FROM orders
WHERE path(delivery_route -> stops -> zones).name = "Zone A";
```

---

## 🔄 Transactional Model

### Transaction Coordinator

* Based on 2PC (Two-Phase Commit)
* Orchestrates calls to PostgreSQL, MongoDB, Neo4j, and InfluxDB
* Ensures rollback consistency

```quantaql
BEGIN TRANSACTION;

<statements...>

COMMIT;
-- OR
ROLLBACK;
```

---

## 🛠 System Architecture

### Key Modules

| Module               | Role                                       |
| -------------------- | ------------------------------------------ |
| `BucketManager`      | Creates/deletes buckets, handles isolation |
| `RecordManager`      | Manages schema per record in each bucket   |
| `QueryEngine`        | Parses and validates QuantaQL              |
| `TransactionManager` | Ensures commit/rollback across DBs         |
| `DBAdapters`         | Interface layer to each database engine    |
| `SchemaRegistry`     | Stores all bucket+record schema metadata   |
| `KtorAPI`            | HTTP/REST/GraphQL interface                |

---

### Architecture Diagram

```text
[Client] --> [Ktor API Layer]
               |
               V
         [QueryEngine + TxnManager]
               |
    -------------------------------
    |       |        |         |
 [PG]    [Mongo]   [Neo4j]  [Influx]
```

---

## 📘 Schema Management

Each record schema is defined per bucket and stored in the registry:

```json
{
  "record": "payments",
  "bucket": "service_orders",
  "attributes": {
    "id": { "type": "scalar", "datatype": "uuid" },
    "status": { "type": "scalar", "datatype": "string" },
    "payment_details": { "type": "document" },
    "processed_by": { "type": "relation", "target": "employees" },
    "processing_time": { "type": "metric", "unit": "duration" }
  }
}
```

---

## 📡 API Endpoints

| Method | Path                           | Description              |
| ------ | ------------------------------ | ------------------------ |
| POST   | `/bucket/create`               | Create new bucket        |
| POST   | `/bucket/:name/record`         | Define new record schema |
| GET    | `/bucket/:name/record/:record` | Fetch record schema      |
| POST   | `/bucket/:name/query`          | Execute a QuantaQL query |

---

## 🔐 Security

* OAuth2/JWT for authentication
* Bucket-level API keys
* Record-level RBAC
* Field-level permission enforcement (optional)

---

## 🧪 Example Use Case

### Bucket: `ecommerce_service`

#### Records:

* `users`
* `orders`
* `products`
* `deliveries`

Each record stores attributes in their best-fit engine:

* **Scalar (PostgreSQL)** for core fields
* **Document (MongoDB)** for user profile or item config
* **Relation (Neo4j)** for delivery routes, social graph
* **Metric (InfluxDB)** for delivery times, processing latency

---

## 📈 Metrics & Observability

* Internal performance metrics written to Prometheus
* Query latency and DB coordination times logged
* Built-in `/health` and `/metrics` endpoints

---

## 📘 Future Enhancements

* 🔁 Stream-based writes with Kafka
* 🧠 QuantaQL autocomplete & schema-aware IDE
* 📦 Distributed record sharding
* ⛓ Pluggable backends (Redis, Cassandra, etc.)
* 🔄 Schema versioning and migrations

---

## 📦 Project Tech Stack

| Component    | Stack                                |
| ------------ | ------------------------------------ |
| Runtime      | Kotlin + Ktor                        |
| Parser       | ANTLR or custom Kotlin DSL           |
| Persistence  | PostgreSQL, MongoDB, Neo4j, InfluxDB |
| Deployment   | Docker + K8s                         |
| Config Store | Redis or Vault                       |

---

## 🏁 Summary

QuantaDB allows you to define **multiple record types per service bucket**, with **attributes stored in the most suitable database engine**. It provides **QuantaQL**, a powerful, unified query language with **ACID-like transaction support** over polyglot backends. The system is modular, scalable, and built for modern microservice architectures.

---

```
