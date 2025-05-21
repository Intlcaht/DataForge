
// File: src/main/kotlin/com/quantadb/core/QueryEngine.kt
package com.quantadb.core

import com.quantadb.db.DatabaseAdapter
import com.quantadb.db.InfluxAdapter
import com.quantadb.db.MongoAdapter
import com.quantadb.db.Neo4jAdapter
import com.quantadb.db.PostgresAdapter
import com.quantadb.model.AttributeType
import com.quantadb.parser.QuantaQLParser
import mu.KotlinLogging
import kotlinx.serialization.json.JsonElement

private val logger = KotlinLogging.logger {}

class QueryEngine {
    private val parser = QuantaQLParser()
    private val recordManager = RecordManager()
    
    private val pgAdapter = PostgresAdapter()
    private val mongoAdapter = MongoAdapter()
    private val neo4jAdapter = Neo4jAdapter()
    private val influxAdapter = InfluxAdapter()
    
    fun executeQuery(bucketName: String, queryString: String, transactionManager: TransactionManager): Map<String, Any> {
        logger.info { "Executing query on bucket $bucketName: $queryString" }
        
        // Parse the query
        val parsedQuery = parser.parse(queryString)
        
        // Start transaction if needed
        val txnId = if (parsedQuery.isTransactional) {
            transactionManager.begin()
        } else null
        
        try {
            // Execute the parsed query
            val result = when (parsedQuery.operation) {
                "SELECT" -> executeSelect(bucketName, parsedQuery, txnId)
                "INSERT" -> executeInsert(bucketName, parsedQuery, txnId)
                "UPDATE" -> executeUpdate(bucketName, parsedQuery, txnId)
                "DELETE" -> executeDelete(bucketName, parsedQuery, txnId)
                else -> throw UnsupportedOperationException("Unsupported operation: ${parsedQuery.operation}")
            }
            
            // Commit if transactional
            if (txnId != null) {
                transactionManager.commit(txnId)
            }
            
            return result
        } catch (e: Exception) {
            logger.error(e) { "Query execution failed" }
            
            // Rollback if transactional
            if (txnId != null) {
                transactionManager.rollback(txnId)
            }
            
            throw e
        }
    }
    
    private fun executeSelect(bucketName: String, query: ParsedQuery, txnId: String?): Map<String, Any> {
        val recordName = query.target
        val schema = recordManager.getRecordSchema(bucketName, recordName)
        
        // Map attributes to their respective database adapters
        val results = mutableMapOf<String, Any>()
        
        query.attributes.forEach { attr ->
            // Handle nested attribute references like "customer.name"
            val parts = attr.split(".")
            val baseAttr = parts[0]
            
            val definition = schema.attributes[baseAttr] ?: 
                throw IllegalArgumentException("Attribute $baseAttr not found in record $recordName")
            
            val adapter = getAdapterForType(definition.type)
            val value = adapter.select(bucketName, recordName, attr, query.condition, txnId)
            
            results[attr] = value
        }
        
        return results
    }
    
    private fun executeInsert(bucketName: String, query: ParsedQuery, txnId: String?): Map<String, Any> {
        val recordName = query.target
        val schema = recordManager.getRecordSchema(bucketName, recordName)
        
        // Group attributes by type and send to appropriate adapters
        val grouped = query.values.entries.groupBy { (attr, _) ->
            val baseAttr = attr.split(".")[0]
            schema.attributes[baseAttr]?.type ?: 
                throw IllegalArgumentException("Attribute $baseAttr not found in record $recordName")
        }
        
        // Execute inserts on each adapter
        grouped.forEach { (type, attrs) ->
            val adapter = getAdapterForType(type)
            val filteredValues = attrs.associate { it.toPair() }
            adapter.insert(bucketName, recordName, filteredValues, txnId)
        }
        
        return mapOf("inserted" to query.values)
    }
    
    private fun executeUpdate(bucketName: String, query: ParsedQuery, txnId: String?): Map<String, Any> {
        val recordName = query.target
        val schema = recordManager.getRecordSchema(bucketName, recordName)
        
        // Group attributes by type and send to appropriate adapters
        val grouped = query.values.entries.groupBy { (attr, _) ->
            val baseAttr = attr.split(".")[0]
            schema.attributes[baseAttr]?.type ?:
                throw IllegalArgumentException("Attribute $baseAttr not found in record $recordName")
        }
        
        // Count of updated records
        var updateCount = 0
        
        // Execute updates on each adapter
        grouped.forEach { (type, attrs) ->
            val adapter = getAdapterForType(type)
            val filteredValues = attrs.associate { it.toPair() }
            val count = adapter.update(bucketName, recordName, filteredValues, query.condition, txnId)
            updateCount += count
        }
        
        return mapOf("updated" to updateCount)
    }
    
    private fun executeDelete(bucketName: String, query: ParsedQuery, txnId: String?): Map<String, Any> {
        val recordName = query.target
        
        // Delete from all adapters to ensure consistency
        val pgCount = pgAdapter.delete(bucketName, recordName, query.condition, txnId)
        mongoAdapter.delete(bucketName, recordName, query.condition, txnId)
        neo4jAdapter.delete(bucketName, recordName, query.condition, txnId)
        influxAdapter.delete(bucketName, recordName, query.condition, txnId)
        
        return mapOf("deleted" to pgCount)
    }
    
    private fun getAdapterForType(type: AttributeType): DatabaseAdapter {
        return when (type) {
            AttributeType.scalar -> pgAdapter
            AttributeType.document -> mongoAdapter
            AttributeType.relation -> neo4jAdapter
            AttributeType.metric -> influxAdapter
        }
    }
}

data class ParsedQuery(
    val operation: String,
    val target: String,
    val attributes: List<String> = emptyList(),
    val condition: String? = null,
    val values: Map<String, Any> = emptyMap(),
    val isTransactional: Boolean = false
)
