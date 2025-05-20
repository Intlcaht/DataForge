
// File: src/main/kotlin/com/quantadb/core/RecordManager.kt
package com.quantadb.core

import com.quantadb.db.InfluxAdapter
import com.quantadb.db.MongoAdapter
import com.quantadb.db.Neo4jAdapter
import com.quantadb.db.PostgresAdapter
import com.quantadb.model.AttributeDefinition
import com.quantadb.model.AttributeType
import com.quantadb.model.RecordSchema
import mu.KotlinLogging

private val logger = KotlinLogging.logger {}

class RecordManager {
    private val pgAdapter = PostgresAdapter()
    private val mongoAdapter = MongoAdapter()
    private val neo4jAdapter = Neo4jAdapter()
    private val influxAdapter = InfluxAdapter()
    
    private val recordSchemas = mutableMapOf<String, RecordSchema>()
    
    fun createRecord(bucketName: String, schema: RecordSchema): RecordSchema {
        logger.info { "Creating record ${schema.record} in bucket $bucketName" }
        
        val key = "${bucketName}:${schema.record}"
        if (recordSchemas.containsKey(key)) {
            throw IllegalArgumentException("Record ${schema.record} already exists in bucket $bucketName")
        }
        
        // Create appropriate storage for each attribute type
        schema.attributes.forEach { (attrName, definition) ->
            when (definition.type) {
                AttributeType.scalar -> pgAdapter.createColumn(bucketName, schema.record, attrName, definition)
                AttributeType.document -> mongoAdapter.createCollection(bucketName, schema.record, attrName, definition)
                AttributeType.relation -> neo4jAdapter.createRelationship(bucketName, schema.record, attrName, definition)
                AttributeType.metric -> influxAdapter.createMeasurement(bucketName, schema.record, attrName, definition)
            }
        }
        
        // Register the schema
        recordSchemas[key] = schema
        
        return schema
    }
    
    fun getRecordSchema(bucketName: String, recordName: String): RecordSchema {
        val key = "${bucketName}:${recordName}"
        return recordSchemas[key] ?: throw IllegalArgumentException("Record $recordName not found in bucket $bucketName")
    }
}
