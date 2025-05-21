import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOf
import java.time.Duration
import java.time.LocalDateTime
import java.util.*

// ===============================
// Root AST Node
// ===============================

sealed class QuantaQLProgram {
    abstract val statements: List<Statement>
    
    data class Program(override val statements: List<Statement>) : QuantaQLProgram()
}

// ===============================
// Base Statement Interface
// ===============================

sealed interface Statement {
    val location: SourceLocation?
}

data class SourceLocation(
    val line: Int,
    val column: Int,
    val file: String? = null
)

// ===============================
// Statement Types
// ===============================

sealed class SchemaDefinition : Statement {
    data class RecordDefinition(
        val name: Identifier,
        val bucket: Identifier,
        val fields: List<FieldDefinition>,
        override val location: SourceLocation? = null
    ) : SchemaDefinition()
    
    data class TypeDefinition(
        val name: Identifier,
        val fields: List<FieldDefinition>,
        override val location: SourceLocation? = null
    ) : SchemaDefinition()
    
    data class IndexDefinition(
        val type: IndexType,
        val name: Identifier,
        val fields: List<Identifier>,
        val options: IndexOption? = null,
        override val location: SourceLocation? = null
    ) : SchemaDefinition()
    
    data class BucketDefinition(
        val operation: BucketOperation,
        val name: Identifier,
        val options: BucketOption? = null,
        override val location: SourceLocation? = null
    ) : SchemaDefinition()
}

sealed class DataOperation : Statement {
    data class AddOperation(
        val record: Identifier,
        val assignments: List<FieldAssignment>,
        override val location: SourceLocation? = null
    ) : DataOperation()
    
    data class BatchOperation(
        val record: Identifier,
        val records: List<List<FieldAssignment>>,
        override val location: SourceLocation? = null
    ) : DataOperation()
    
    data class FindOperation(
        val returnFields: List<ReturnField>,
        val condition: Condition,
        val orderBy: List<OrderField>? = null,
        val limit: Int? = null,
        val offset: Int? = null,
        val cache: DurationExpression? = null,
        override val location: SourceLocation? = null
    ) : DataOperation()
    
    data class UpdateOperation(
        val record: Identifier,
        val assignments: List<FieldAssignment>,
        val condition: Condition,
        override val location: SourceLocation? = null
    ) : DataOperation()
    
    data class RemoveOperation(
        val record: Identifier,
        val condition: Condition,
        override val location: SourceLocation? = null
    ) : DataOperation()
    
    data class RecordMetric(
        val record: Identifier,
        val field: Identifier,
        val value: Expression,
        val timestamp: Expression,
        override val location: SourceLocation? = null
    ) : DataOperation()
}

sealed class GraphOperation : Statement {
    data class LinkOperation(
        val from: Identifier,
        val fromCondition: Condition,
        val to: Identifier,
        val toCondition: Condition,
        val relationship: StringLiteral,
        val properties: List<FieldAssignment>? = null,
        override val location: SourceLocation? = null
    ) : GraphOperation()
    
    data class UnlinkOperation(
        val from: Identifier,
        val fromCondition: Condition,
        val to: Identifier,
        val toCondition: Condition,
        val whereCondition: Condition? = null,
        override val location: SourceLocation? = null
    ) : GraphOperation()
    
    data class NavigateOperation(
        val returnFields: List<ReturnField>,
        val path: PathExpression,
        val condition: Condition,
        override val location: SourceLocation? = null
    ) : GraphOperation()
    
    data class PatternOperation(
        val returnFields: List<ReturnField>,
        val pattern: PatternExpression,
        val condition: Condition,
        val returnPath: Boolean = false,
        override val location: SourceLocation? = null
    ) : GraphOperation()
    
    data class GraphAlgorithm(
        val returnFields: List<ReturnField>,
        val algorithm: AlgorithmCall,
        val algorithmAlias: Identifier,
        val nodes: Identifier,
        val edges: PathExpression,
        val additionalClauses: List<AdditionalClause> = emptyList(),
        override val location: SourceLocation? = null
    ) : GraphOperation()
}

sealed class MetricOperation : Statement {
    data class AggregateMetric(
        val returnFields: List<ReturnField>,
        val path: PathExpression? = null,
        val condition: Condition,
        val groupBy: List<Expression>? = null,
        val timeWindow: TimeWindowExpression? = null,
        override val location: SourceLocation? = null
    ) : MetricOperation()
    
    data class DownsampleMetric(
        val aggregation: AggregationFunction,
        val alias: Identifier,
        val condition: Condition,
        val interval: TimeInterval,
        override val location: SourceLocation? = null
    ) : MetricOperation()
    
    data class ContinuousQuery(
        val name: Identifier,
        val aggregation: AggregationFunction,
        val alias: Identifier,
        val condition: Condition,
        val interval: TimeInterval,
        val storeIn: Identifier,
        override val location: SourceLocation? = null
    ) : MetricOperation()
    
    data class AnomalyDetection(
        val returnFields: List<ReturnField>,
        val record: Identifier,
        val field: Identifier,
        val threshold: Expression,
        val condition: Condition,
        override val location: SourceLocation? = null
    ) : MetricOperation()
}

sealed class Aggregation : Statement {
    data class AggregationQuery(
        val expressions: List<AggregationExpression>,
        val path: PathExpression? = null,
        val condition: Condition,
        val groupBy: List<Expression>? = null,
        val having: Condition? = null,
        val orderBy: List<OrderField>? = null,
        val limit: Int? = null,
        override val location: SourceLocation? = null
    ) : Aggregation()
}

sealed class Transaction : Statement {
    data class StartTransaction(
        val isolationLevel: IsolationLevel? = null,
        override val location: SourceLocation? = null
    ) : Transaction()
    
    data class CommitTransaction(
        override val location: SourceLocation? = null
    ) : Transaction()
    
    data class RollbackTransaction(
        val savepoint: Identifier? = null,
        override val location: SourceLocation? = null
    ) : Transaction()
    
    data class Savepoint(
        val name: Identifier,
        override val location: SourceLocation? = null
    ) : Transaction()
}

sealed class SecurityCommand : Statement {
    data class CreateUser(
        val username: Identifier,
        val password: StringLiteral,
        override val location: SourceLocation? = null
    ) : SecurityCommand()
    
    data class DropUser(
        val username: Identifier,
        override val location: SourceLocation? = null
    ) : SecurityCommand()
    
    data class CreateRole(
        val roleName: Identifier,
        override val location: SourceLocation? = null
    ) : SecurityCommand()
    
    data class GrantRole(
        val roleName: Identifier,
        val principal: Identifier,
        override val location: SourceLocation? = null
    ) : SecurityCommand()
    
    data class RevokeRole(
        val roleName: Identifier,
        val principal: Identifier,
        override val location: SourceLocation? = null
    ) : SecurityCommand()
    
    data class GrantPermission(
        val permission: Permission,
        val obj: DatabaseObject,
        val principal: Principal,
        override val location: SourceLocation? = null
    ) : SecurityCommand()
    
    data class DenyPermission(
        val permission: Permission,
        val obj: DatabaseObject,
        val principal: Principal,
        override val location: SourceLocation? = null
    ) : SecurityCommand()
    
    data class CreatePolicy(
        val name: Identifier,
        val table: Identifier,
        val condition: Condition,
        override val location: SourceLocation? = null
    ) : SecurityCommand()
    
    data class FieldEncryption(
        val record: Identifier,
        val field: Identifier,
        val key: StringLiteral,
        override val location: SourceLocation? = null
    ) : SecurityCommand()
    
    data class EnableAudit(
        val target: Identifier,
        val operations: List<AuditOperation>,
        val logTo: StringLiteral,
        override val location: SourceLocation? = null
    ) : SecurityCommand()
}

sealed class AdvancedFeature : Statement {
    data class CommonTableExpression(
        val name: Identifier,
        val query: QueryExpression,
        val mainQuery: QueryExpression,
        override val location: SourceLocation? = null
    ) : AdvancedFeature()
    
    data class PreparedStatement(
        val name: Identifier,
        val query: QueryExpression,
        override val location: SourceLocation? = null
    ) : AdvancedFeature()
    
    data class ExecuteStatement(
        val name: Identifier,
        val parameters: List<Expression>,
        override val location: SourceLocation? = null
    ) : AdvancedFeature()
    
    data class CustomFunction(
        val name: Identifier,
        val parameters: List<Parameter>,
        val returnType: DataType,
        val body: Expression,
        override val location: SourceLocation? = null
    ) : AdvancedFeature()
    
    data class StoredProcedure(
        val name: Identifier,
        val parameters: List<Parameter>,
        val body: List<Statement>,
        override val location: SourceLocation? = null
    ) : AdvancedFeature()
    
    data class Trigger(
        val name: Identifier,
        val timing: TriggerTiming,
        val event: TriggerEvent,
        val table: Identifier,
        val scope: TriggerScope? = null,
        val condition: Condition? = null,
        val body: List<Statement>,
        override val location: SourceLocation? = null
    ) : AdvancedFeature()
    
    data class View(
        val name: Identifier,
        val query: QueryExpression,
        override val location: SourceLocation? = null
    ) : AdvancedFeature()
    
    data class QueryHint(
        val returnFields: List<ReturnField>,
        val condition: Condition,
        val hint: Hint,
        override val location: SourceLocation? = null
    ) : AdvancedFeature()
}

sealed class SpatialOperation : Statement {
    data class SpatialQuery(
        val returnFields: List<ReturnField>,
        val spatialCondition: SpatialFunction,
        val value: Expression,
        val orderBy: SpatialFunction? = null,
        override val location: SourceLocation? = null
    ) : SpatialOperation()
}

sealed class FullTextSearch : Statement {
    data class TextSearchQuery(
        val returnFields: List<ReturnField>,
        val field: FieldReference,
        val searchText: StringLiteral,
        val options: TextSearchOption? = null,
        val orderByScore: Boolean = false,
        override val location: SourceLocation? = null
    ) : FullTextSearch()
    
    data class CreateTextIndex(
        val name: Identifier,
        val field: Identifier,
        val options: TextIndexOption? = null,
        override val location: SourceLocation? = null
    ) : FullTextSearch()
}

sealed class DataMigration : Statement {
    data class CopyOperation(
        val from: Identifier,
        val to: Identifier,
        val transformations: List<FieldAssignment>,
        val condition: Condition,
        override val location: SourceLocation? = null
    ) : DataMigration()
    
    data class ImportOperation(
        val target: Identifier,
        val source: StringLiteral,
        val format: FormatType,
        val transformations: List<TransformAssignment>? = null,
        override val location: SourceLocation? = null
    ) : DataMigration()
    
    data class ExportOperation(
        val source: Identifier,
        val target: StringLiteral,
        val format: FormatType,
        val condition: Condition,
        override val location: SourceLocation? = null
    ) : DataMigration()
}

sealed class MonitoringCommand : Statement {
    data class QueryMetrics(
        val metric: Identifier,
        val condition: Condition,
        override val location: SourceLocation? = null
    ) : MonitoringCommand()
    
    data class HealthCheck(
        val storageEngines: List<Identifier>? = null,
        override val location: SourceLocation? = null
    ) : MonitoringCommand()
    
    data class CreateAlert(
        val name: Identifier,
        val target: FieldReference,
        val condition: Condition,
        val timeWindow: TimeWindowExpression,
        val notification: NotificationTarget,
        override val location: SourceLocation? = null
    ) : MonitoringCommand()
    
    data class ExplainPlan(
        val analyze: Boolean = false,
        val query: QueryExpression,
        override val location: SourceLocation? = null
    ) : MonitoringCommand()
}

sealed class SystemConfiguration : Statement {
    data class ConfigureStorageEngine(
        val engine: Identifier,
        val setting: Identifier,
        val value: Expression,
        override val location: SourceLocation? = null
    ) : SystemConfiguration()
    
    data class ConfigureQueryEngine(
        val setting: Identifier,
        val value: Expression,
        override val location: SourceLocation? = null
    ) : SystemConfiguration()
    
    data class ConfigureCache(
        val setting: Identifier,
        val value: Expression,
        override val location: SourceLocation? = null
    ) : SystemConfiguration()
}

// ===============================
// Supporting Data Classes
// ===============================

data class FieldDefinition(
    val name: Identifier,
    val type: DataType,
    val constraints: List<Constraint> = emptyList()
)

sealed class DataType {
    data class ScalarType(val subtype: ScalarSubtype) : DataType()
    data object DocumentType : DataType()
    data class RelationType(val target: Identifier, val cardinality: RelationCardinality) : DataType()
    data class MetricType(val subtype: MetricSubtype) : DataType()
    data object TimeType : DataType()
    data object DurationType : DataType()
    data object GeoType : DataType()
    data class ArrayType(val elementType: DataType) : DataType()
    data class MapType(val keyType: ScalarSubtype, val valueType: DataType) : DataType()
    data class CustomType(val name: Identifier) : DataType()
}

enum class ScalarSubtype {
    STRING, INT, FLOAT, BOOLEAN, UUID, DECIMAL, BINARY, ENUM, DATE, TIME, IP, URL, PERCENTAGE, CURRENCY
}

enum class MetricSubtype {
    COUNT, GAUGE, HISTOGRAM, DURATION, PERCENTAGE, CUSTOM
}

enum class RelationCardinality { ONE, MANY }

sealed class Constraint {
    data object Primary : Constraint()
    data object Unique : Constraint()
    data object Index : Constraint()
    data class Default(val value: Expression) : Constraint()
    data object NotNull : Constraint()
    data class Check(val condition: Expression) : Constraint()
    data class References(val table: Identifier) : Constraint()
    data object One : Constraint()
    data object Many : Constraint()
    data object Nullable : Constraint()
    data object Immutable : Constraint()
}

enum class IndexType { TEXT, METRIC, GRAPH, GEO, COMPOUND, UNIQUE, STANDARD }

sealed class IndexOption {
    data class Retain(val value: StringLiteral) : IndexOption()
    data class Type(val value: StringLiteral) : IndexOption()
    data class MaxDistance(val value: StringLiteral) : IndexOption()
    data class Where(val condition: Condition) : IndexOption()
}

enum class BucketOperation { CREATE, DROP }

sealed class BucketOption {
    data class Retention(val value: StringLiteral) : BucketOption()
    data class Replication(val value: Int) : BucketOption()
}

data class FieldAssignment(val field: Identifier, val value: Expression)

sealed class ReturnField {
    data class FieldReference(val table: Identifier? = null, val field: Identifier) : ReturnField()
    data class AggregationField(val function: AggregationFunction) : ReturnField()
}

data class OrderField(
    val table: Identifier? = null,
    val field: Identifier,
    val direction: OrderDirection = OrderDirection.ASC
)

enum class OrderDirection { ASC, DESC }

// ===============================
// Conditions and Expressions
// ===============================

sealed class Condition {
    data class ExpressionCondition(val expression: Expression) : Condition()
    data class AndCondition(val left: Condition, val right: Condition) : Condition()
    data class OrCondition(val left: Condition, val right: Condition) : Condition()
    data class NotCondition(val condition: Condition) : Condition()
    data class ComparisonCondition(
        val left: Identifier,
        val operator: ComparisonOperator,
        val right: Expression
    ) : Condition()
    data class InCondition(val field: Identifier, val values: List<Expression>) : Condition()
    data class IncludesCondition(val field: Identifier, val value: Expression) : Condition()
    data class SpatialCondition(val function: SpatialFunction) : Condition()
    data class TextCondition(val function: TextFunction) : Condition()
    data class AnomalyCondition(
        val record: Identifier,
        val field: Identifier,
        val threshold: Expression
    ) : Condition()
}

sealed class Expression {
    data class LiteralExpression(val literal: Literal) : Expression()
    data class FieldExpression(val table: Identifier? = null, val field: Identifier) : Expression()
    data class FunctionCall(val name: Identifier, val args: List<Expression>) : Expression()
    data class BinaryOperation(val left: Expression, val operator: Operator, val right: Expression) : Expression()
    data class CaseExpression(
        val whenClauses: List<WhenClause>,
        val elseClause: Expression? = null
    ) : Expression()
    data class GeoExpression(val geo: GeoExpression) : Expression()
    data class DurationExpression(val duration: DurationExpression) : Expression()
    data class TimeExpression(val time: TimeExpression) : Expression()
}

data class WhenClause(val condition: Condition, val result: Expression)

sealed class Literal {
    data class StringLiteral(val value: String) : Literal()
    data class IntLiteral(val value: Int) : Literal()
    data class FloatLiteral(val value: Double) : Literal()
    data class BooleanLiteral(val value: Boolean) : Literal()
    data object NullLiteral : Literal()
    data class ArrayLiteral(val elements: List<Expression>) : Literal()
    data class MapLiteral(val entries: Map<Identifier, Expression>) : Literal()
}

enum class Operator {
    PLUS, MINUS, MULTIPLY, DIVIDE, EQUALS, NOT_EQUALS, 
    LESS_THAN, GREATER_THAN, LESS_EQUAL, GREATER_EQUAL, AND, OR
}

enum class ComparisonOperator {
    EQUALS, NOT_EQUALS, LESS_THAN, GREATER_THAN, LESS_EQUAL, GREATER_EQUAL
}

// ===============================
// Aggregation and Functions
// ===============================

sealed class AggregationExpression {
    data class Function(val function: AggregationFunction) : AggregationExpression()
    data class WindowFunction(val function: WindowFunction) : AggregationExpression()
    data class Field(val table: Identifier? = null, val field: Identifier) : AggregationExpression()
}

data class AggregationFunction(
    val name: AggregationFunctionType,
    val args: List<Expression>,
    val alias: Identifier? = null
)

enum class AggregationFunctionType {
    COUNT, SUM, AVG, MIN, MAX, MEDIAN, PERCENTILE, STDDEV, VAR, 
    ARRAY, DISTINCT, GROUP_CONCAT, FIRST, LAST, TOP_N
}

data class WindowFunction(
    val name: WindowFunctionType,
    val expression: Expression,
    val partitionBy: List<Expression>? = null,
    val orderBy: List<Expression>? = null,
    val frame: WindowFrameClause? = null,
    val alias: Identifier
)

enum class WindowFunctionType { AVG, SUM, COUNT, MIN, MAX, RANK, DENSE_RANK }

data class WindowFrameClause(
    val type: WindowFrameType,
    val duration: DurationExpression,
    val direction: WindowFrameDirection
)

enum class WindowFrameType { RANGE, ROWS }
enum class WindowFrameDirection { PRECEDING, FOLLOWING }

// ===============================
// Graph and Path Expressions
// ===============================

data class PathExpression(val segments: List<PathSegment>)

data class PathSegment(
    val node: Identifier,
    val edge: EdgeSpec? = null
)

data class EdgeSpec(val type: Identifier, val label: Identifier)

data class PatternExpression(
    val startNode: NodePattern,
    val path: List<EdgePattern>,
    val endNode: NodePattern
)

data class NodePattern(val variable: Identifier, val label: Identifier)
data class EdgePattern(val type: Identifier, val quantifier: EdgeQuantifier? = null)
data class EdgeQuantifier(val min: Int, val max: Int? = null)

data class AlgorithmCall(val name: Identifier, val args: List<Expression>)

sealed class AdditionalClause {
    data class OrderClause(val fields: List<OrderField>) : AdditionalClause()
    data class LimitClause(val limit: Int) : AdditionalClause()
    data class OffsetClause(val offset: Int) : AdditionalClause()
    data class CacheClause(val duration: DurationExpression) : AdditionalClause()
}

// ===============================
// Spatial Operations
// ===============================

sealed class SpatialFunction {
    data class Distance(val geo1: GeoExpression, val geo2: GeoExpression) : SpatialFunction()
    data class Contains(val geo1: GeoExpression, val geo2: GeoExpression) : SpatialFunction()
    data class Intersects(val geo1: GeoExpression, val geo2: GeoExpression) : SpatialFunction()
    data class Nearby(val field: Identifier, val point: GeoExpression, val distance: StringLiteral) : SpatialFunction()
}

sealed class GeoExpression {
    data class Point(val x: Expression, val y: Expression) : GeoExpression()
    data class Polygon(val points: List<Point>) : GeoExpression()
    data class Line(val points: List<Point>) : GeoExpression()
    data class Circle(val center: Point, val radius: Expression) : GeoExpression()
}

data class Point(val x: Expression, val y: Expression)

// ===============================
// Full-Text Search
// ===============================

sealed class TextFunction {
    data object TextScore : TextFunction()
    data class TextContains(val field: Identifier, val text: StringLiteral) : TextFunction()
    data class TextExtract(val field: Identifier, val pattern: StringLiteral) : TextFunction()
    data class TextSummarize(val field: Identifier, val length: Int) : TextFunction()
    data class TextSentiment(val field: Identifier) : TextFunction()
    data class TextEntities(val field: Identifier) : TextFunction()
    data class TextClassify(val field: Identifier, val model: StringLiteral) : TextFunction()
}

enum class TextSearchOption { FUZZY, EXACT, STEMMING }

data class TextIndexOption(val language: StringLiteral, val analyzer: StringLiteral)

// ===============================
// Time and Duration
// ===============================

sealed class TimeExpression {
    data class TimeFromString(val value: StringLiteral) : TimeExpression()
    data object Now : TimeExpression()
}

sealed class DurationExpression {
    data class DurationFromString(val value: StringLiteral) : DurationExpression()
}

sealed class TimeWindowExpression {
    data class TimeWindow(val value: StringLiteral) : TimeWindowExpression()
}

sealed class TimeInterval {
    data class Interval(val value: StringLiteral) : TimeInterval()
}

// ===============================
// Security and Permissions
// ===============================

sealed class Permission {
    data object Find : Permission()
    data object Add : Permission()
    data object Update : Permission()
    data object Remove : Permission()
    data object Link : Permission()
    data object Navigate : Permission()
    data class Custom(val name: Identifier) : Permission()
}

sealed class DatabaseObject {
    data class Table(val name: Identifier) : DatabaseObject()
    data class Field(val table: Identifier, val field: Identifier) : DatabaseObject()
    data class Custom(val name: Identifier) : DatabaseObject()
}

sealed class Principal {
    data class User(val name: Identifier) : Principal()
    data class Role(val name: Identifier) : Principal()
}

enum class AuditOperation { ADD, UPDATE, REMOVE }

// ===============================
// Transaction Support
// ===============================

enum class IsolationLevel {
    READ_UNCOMMITTED, READ_COMMITTED, REPEATABLE_READ, SERIALIZABLE
}

// ===============================
// Advanced Features
// ===============================

data class Parameter(val name: Identifier, val type: DataType)

enum class TriggerTiming { BEFORE, AFTER }
enum class TriggerEvent { ADD, UPDATE, REMOVE }
enum class TriggerScope { ROW, STATEMENT }

sealed class Hint {
    data class ForceIndex(val index: Expression) : Hint()
    data class Parallel(val threads: Expression) : Hint()
    data class CacheResult(val duration: Expression) : Hint()
    data object NoGraphCache : Hint()
    data class PreferEngine(val engine: Expression) : Hint()
}

// ===============================
// Data Migration
// ===============================

enum class FormatType { CSV, JSON }

data class TransformAssignment(val field: Identifier, val expression: Expression)

// ===============================
// Monitoring
// ===============================

sealed class NotificationTarget {
    data class Webhook(val url: StringLiteral) : NotificationTarget()
}

// ===============================
// Query Expressions
// ===============================

sealed class QueryExpression {
    data class Find(val operation: DataOperation.FindOperation) : QueryExpression()
    data class Navigate(val operation: GraphOperation.NavigateOperation) : QueryExpression()
    data class Pattern(val operation: GraphOperation.PatternOperation) : QueryExpression()
    data class Algorithm(val operation: GraphOperation.GraphAlgorithm) : QueryExpression()
    data class Metric(val operation: MetricOperation.AggregateMetric) : QueryExpression()
    data class Downsample(val operation: MetricOperation.DownsampleMetric) : QueryExpression()
    data class Spatial(val operation: SpatialOperation.SpatialQuery) : QueryExpression()
    data class TextSearch(val operation: FullTextSearch.TextSearchQuery) : QueryExpression()
}

// ===============================
// Common Types
// ===============================

data class Identifier(val name: String) {
    override fun toString(): String = name
}

// Extension for string literals
typealias StringLiteral = String

data class FieldReference(val table: Identifier? = null, val field: Identifier)
