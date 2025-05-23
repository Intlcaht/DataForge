
package com.icaht.routes

import com.icaht.core.BucketManager
import com.icaht.core.QueryEngine
import com.icaht.core.RecordManager
import com.icaht.core.TransactionManager
import com.icaht.model.BucketCreateRequest
import com.icaht.model.QueryRequest
import com.icaht.model.RecordSchema
import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.Serializable

fun Application.configureRouting() {
    val bucketManager = BucketManager()
    val recordManager = RecordManager()
    val queryEngine = QueryEngine()
    val transactionManager = TransactionManager()
    
    routing {
        // Health check endpoint
        get("/health") {
            call.respond(mapOf("status" to "UP"))
        }
        
        // Bucket management
        post("/bucket/create") {
            val request = call.receive<BucketCreateRequest>()
            val result = bucketManager.createBucket(request.name)
            call.respond(HttpStatusCode.Created, result)
        }
        
        // Record schema management
        post("/bucket/{name}/record") {
            val bucketName = call.parameters["name"] ?: throw IllegalArgumentException("Bucket name required")
            val schema = call.receive<RecordSchema>()
            val result = recordManager.createRecord(bucketName, schema)
            call.respond(HttpStatusCode.Created, result)
        }
        
        get("/bucket/{name}/record/{record}") {
            val bucketName = call.parameters["name"] ?: throw IllegalArgumentException("Bucket name required")
            val recordName = call.parameters["record"] ?: throw IllegalArgumentException("Record name required")
            val schema = recordManager.getRecordSchema(bucketName, recordName)
            call.respond(schema)
        }
        
        // Query execution
        post("/bucket/{name}/query") {
            val bucketName = call.parameters["name"] ?: throw IllegalArgumentException("Bucket name required")
            val queryRequest = call.receive<QueryRequest>()
            
            val result = queryEngine.executeQuery(bucketName, queryRequest.query, transactionManager)
            call.respond(result)
        }
    }
}
