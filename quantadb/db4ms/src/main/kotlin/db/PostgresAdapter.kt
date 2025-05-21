

// File: src/main/kotlin/com/quantadb/db/PostgresAdapter.kt
package com.quantadb.db

import com.quantadb.config.AppConfig
import com.quantadb.model.AttributeDefinition
import mu.KotlinLogging
import java.sql.Connection
import java.sql.DriverManager
import java.util.concurrent.ConcurrentHashMap

private val logger = KotlinLogging.logger {}

class PostgresAdapter : DatabaseAdapter {
    private val connections = ConcurrentHashMap<String, Connection>()
    
    fun createColumn(bucketName: String, recordName: String, attrName: String, definition: AttributeDefinition) {
        logger.info { "Creating PostgreSQL column $attrName for $bucketName.$recordName" }
        
        val conn = getConnection(bucketName)
        val dataType = when (definition.datatype) {
            "string" -> "VARCHAR(255)"
            "int" -> "INTEGER"
            "float" -> "FLOAT"
            "boolean" -> "BOOLEAN"
            "uuid" -> "UUID"
            "timestamp" -> "TIMESTAMP"
            else -> "VARCHAR(255)"
        }
        
        conn.createStatement().use { stmt ->
            // Create table if it doesn't exist
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS ${recordName} (
                    id VARCHAR(255) PRIMARY KEY
                )
            """.trimIndent())
            
            // Check if column exists
            val columnExists = conn.metaData.getColumns(null, null, recordName, attrName).use { rs ->
                rs.next()
            }
            
            // Add column if it doesn't exist
            if (!columnExists) {
                stmt.execute("ALTER TABLE ${recordName} ADD COLUMN ${attrName} ${dataType}")
            }
        }
    }
    
    override fun beginTransaction(): Any {
        // For simplicity we just return a new Connection as the transaction
        val conn = DriverManager.getConnection(
            AppConfig.Postgres.url,
            AppConfig.Postgres.user,
            AppConfig.Postgres.password
        )
        conn.autoCommit = false
        return conn
    }
    
    override fun prepareCommit(txn: Any) {
        // PostgreSQL doesn't have a separate prepare phase in basic mode
        // This would be replaced with XA transaction prepare in a full implementation
        logger.info { "Preparing PostgreSQL transaction for commit" }
    }
    
    override fun commit(txn: Any) {
        val conn = txn as Connection
        conn.commit()
        conn.close()
    }
    
    override fun rollback(txn: Any) {
        val conn = txn as Connection
        conn.rollback()
        conn.close()
    }
    
    override fun select(bucketName: String, recordName: String, attribute: String, condition: String?, txnId: String?): Any {
        val conn = getConnectionOrTxn(bucketName, txnId)
        
        val query = buildString {
            append("SELECT $attribute FROM $recordName")
            if (condition != null) {
                append(" WHERE $condition")
            }
        }
        
        val results = mutableListOf<Any>()
        conn.createStatement().use { stmt ->
            stmt.executeQuery(query).use { rs ->
                while (rs.next()) {
                    results.add(rs.getObject(attribute))
                }
            }
        }
        
        // Close connection if not part of transaction
        if (txnId == null) {
            (conn as? Connection)?.close()
        }
        
        return results
    }
    
    override fun insert(bucketName: String, recordName: String, values: Map<String, Any>, txnId: String?) {
        val conn = getConnectionOrTxn(bucketName, txnId)
        
        val columns = values.keys.joinToString(", ")
        val placeholders = values.keys.map { "?" }.joinToString(", ")
        
        val query = "INSERT INTO $recordName ($columns) VALUES ($placeholders)"
        
        conn.prepareStatement(query).use { stmt ->
            values.values.forEachIndexed { index, value ->
                stmt.setObject(index + 1, value)
            }
            stmt.executeUpdate()
        }
        
        // Close connection if not part of transaction
        if (txnId == null) {
            (conn as? Connection)?.close()
        }
    }
    
    override fun update(bucketName: String, recordName: String, values: Map<String, Any>, condition: String?, txnId: String?): Int {
        val conn = getConnectionOrTxn(bucketName, txnId)
        
        val setClause = values.keys.joinToString(", ") { "$it = ?" }
        
        val query = buildString {
            append("UPDATE $recordName SET $setClause")
            if (condition != null) {
                append(" WHERE $condition")
            }
        }
        
        val updateCount = conn.prepareStatement(query).use { stmt ->
            values.values.forEachIndexed { index, value ->
                stmt.setObject(index + 1, value)
            }
            stmt.executeUpdate()
        }
        
        // Close connection if not part of transaction
        if (txnId == null) {
            (conn as? Connection)?.close()
        }
        
        return updateCount
    }
    
    override fun delete(bucketName: String, recordName: String, condition: String?, txnId: String?): Int {
        val conn = getConnectionOrTxn(bucketName, txnId)
        
        val query = buildString {
            append("DELETE FROM $recordName")
            if (condition != null) {
                append(" WHERE $condition")
            }
        }
        
        val deleteCount = conn.createStatement().use { stmt ->
            stmt.executeUpdate(query)
        }
        
        // Close connection if not part of transaction
        if (txnId == null) {
            (conn as? Connection)?.close()
        }
        
        return deleteCount
    }
    
    private fun getConnection(bucketName: String): Connection {
        return connections.computeIfAbsent(bucketName) {
            val conn = DriverManager.getConnection(
                "${AppConfig.Postgres.url}$bucketName",
                AppConfig.Postgres.user,
                AppConfig.Postgres.password
            )
            conn.autoCommit = true
            conn
        }
    }
    
    private fun getConnectionOrTxn(bucketName: String, txnId: String?): Any {
        return if (txnId != null) {
            // In a full implementation, this would look up the transaction by ID
            // For now, we just create a new connection but mark it as part of a transaction
            DriverManager.getConnection(
                "${AppConfig.Postgres.url}$bucketName",
                AppConfig.Postgres.user,
                AppConfig.Postgres.password
            )
        } else {
            getConnection(bucketName)
        }
    }
}
