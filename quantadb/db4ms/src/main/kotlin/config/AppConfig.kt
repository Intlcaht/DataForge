
package com.icaht.config

object AppConfig {
    val serverPort = System.getenv("SERVER_PORT")?.toIntOrNull() ?: 8080
    
    object Postgres {
        val url = System.getenv("PG_URL") ?: "jdbc:postgresql://localhost:5432/"
        val user = System.getenv("PG_USER") ?: "postgres"
        val password = System.getenv("PG_PASSWORD") ?: "postgres"
    }
    
    object MongoDB {
        val uri = System.getenv("MONGO_URI") ?: "mongodb://localhost:27017"
    }
    
    object Neo4j {
        val uri = System.getenv("NEO4J_URI") ?: "bolt://localhost:7687"
        val user = System.getenv("NEO4J_USER") ?: "neo4j"
        val password = System.getenv("NEO4J_PASSWORD") ?: "neo4j"
    }
    
    object InfluxDB {
        val url = System.getenv("INFLUX_URL") ?: "http://localhost:8086"
        val token = System.getenv("INFLUX_TOKEN") ?: "my-token"
        val org = System.getenv("INFLUX_ORG") ?: "my-org"
    }
}
