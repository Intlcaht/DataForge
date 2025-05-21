// AST Classes
sealed class AstNode

data class CreateRecord(val name: String, val bucket: String, val fields: List<FieldDefinition>) : AstNode()
data class FieldDefinition(val name: String, val type: String, val constraints: List<String>) : AstNode()
data class Insert(val record: String, val values: Map<String, Any>) : AstNode()
data class Select(val fields: List<String>, val from: String, val where: WhereClause?) : AstNode()
data class WhereClause(val condition: String) : AstNode()
data class Update(val record: String, val set: Map<String, Any>, val where: WhereClause?) : AstNode()
data class Delete(val record: String, val where: WhereClause?) : AstNode()
data class Traverse(val path: String, val where: WhereClause?) : AstNode()
data class Match(val pattern: String, val where: WhereClause?) : AstNode()
data class CreateRelation(val from: String, val to: String, val type: String, val properties: Map<String, Any>) : AstNode()
data class InsertMetric(val record: String, val field: String, val values: Map<String, Any>, val where: WhereClause?) : AstNode()
data class MetricAggregation(val record: String, val field: String, val aggregations: List<Aggregation>, val groupBy: String?, val where: WhereClause?) : AstNode()
data class Aggregation(val function: String, val field: String, val alias: String) : AstNode()
data class Join(val left: String, val right: String, val on: String) : AstNode()
data class Transaction(val operations: List<AstNode>) : AstNode()
