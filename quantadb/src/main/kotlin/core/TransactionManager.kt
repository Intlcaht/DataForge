
// File: src/main/kotlin/com/quantadb/core/TransactionManager.kt
package com.quantadb.core

import com.quantadb.db.InfluxAdapter
import com.quantadb.db.MongoAdapter
import com.quantadb.db.Neo4jAdapter
import com.quantadb.db.PostgresAdapter
import mu.KotlinLogging
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

private val logger = KotlinLogging.logger {}

class TransactionManager {
    private val pgAdapter = PostgresAdapter()
    private val mongoAdapter = MongoAdapter()
    private val neo4jAdapter = Neo4jAdapter()
    private val influxAdapter = InfluxAdapter()
    
    private val activeTxns = ConcurrentHashMap<String, Transaction>()
    
    fun begin(): String {
        val txnId = UUID.randomUUID().toString()
        logger.info { "Beginning transaction $txnId" }
        
        // Begin transaction in each database
        val pgTxn = pgAdapter.beginTransaction()
        val mongoTxn = mongoAdapter.beginTransaction()
        val neo4jTxn = neo4jAdapter.beginTransaction()
        val influxTxn = influxAdapter.beginTransaction()
        
        // Register the transaction
        activeTxns[txnId] = Transaction(txnId, pgTxn, mongoTxn, neo4jTxn, influxTxn)
        
        return txnId
    }
    
    fun commit(txnId: String) {
        logger.info { "Committing transaction $txnId" }
        val txn = activeTxns[txnId] ?: throw IllegalArgumentException("Transaction $txnId not found")
        
        try {
            // Phase 1: Prepare
            pgAdapter.prepareCommit(txn.pgTxn)
            mongoAdapter.prepareCommit(txn.mongoTxn)
            neo4jAdapter.prepareCommit(txn.neo4jTxn)
            influxAdapter.prepareCommit(txn.influxTxn)
            
            // Phase 2: Commit
            pgAdapter.commit(txn.pgTxn)
            mongoAdapter.commit(txn.mongoTxn)
            neo4jAdapter.commit(txn.neo4jTxn)
            influxAdapter.commit(txn.influxTxn)
            
            // Remove transaction
            activeTxns.remove(txnId)
        } catch (e: Exception) {
            logger.error(e) { "Commit failed for transaction $txnId" }
            rollback(txnId)
            throw e
        }
    }
    
    fun rollback(txnId: String) {
        logger.info { "Rolling back transaction $txnId" }
        val txn = activeTxns[txnId] ?: throw IllegalArgumentException("Transaction $txnId not found")
        
        try {
            // Rollback in each database
            pgAdapter.rollback(txn.pgTxn)
            mongoAdapter.rollback(txn.mongoTxn)
            neo4jAdapter.rollback(txn.neo4jTxn)
            influxAdapter.rollback(txn.influxTxn)
        } finally {
            // Remove transaction
            activeTxns.remove(txnId)
        }
    }
}

data class Transaction(
    val id: String,
    val pgTxn: Any,
    val mongoTxn: Any,
    val neo4jTxn: Any,
    val influxTxn: Any
)
