
// File: src/main/kotlin/com/quantadb/db/DatabaseAdapter.kt
package com.quantadb.db

import com.quantadb.model.AttributeDefinition

interface DatabaseAdapter {
    fun beginTransaction(): Any
    fun prepareCommit(txn: Any)
    fun commit(txn: Any)
    fun rollback(txn: Any)
    
    fun select(bucketName: String, recordName: String, attribute: String, condition: String?, txnId: String?): Any
    fun insert(bucketName: String, recordName: String, values: Map<String, Any>, txnId: String?)
    fun update(bucketName: String, recordName: String, values: Map<String, Any>, condition: String?, txnId: String?): Int
    fun delete(bucketName: String, recordName: String, condition: String?, txnId: String?): Int
}