
// // File: src/main/kotlin/com/quantadb/model/Models.kt
// package com.quantadb.model

// import kotlinx.serialization.Serializable

// @Serializable
// data class BucketCreateRequest(val name: String)

// @Serializable
// data class QueryRequest(val query: String)

// @Serializable
// data class QueryResult(
//     val success: Boolean,
//     val data: Map<String, Any>? = null,
//     val error: String? = null
// )

// @Serializable
// data class RecordSchema(
//     val record: String,
//     val attributes: Map<String, AttributeDefinition>
// )

// @Serializable
// data class AttributeDefinition(
//     val type: AttributeType,
//     val datatype: String? = null,
//     val target: String? = null,
//     val unit: String? = null
// )

// @Serializable
// enum class AttributeType {
//     scalar, document, relation, metric
// }
