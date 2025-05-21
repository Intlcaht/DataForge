
// ===============================
// Flow-based Query Execution
// ===============================

/**
 * Interface for executing QuantaQL queries with Flow support for streaming results
 */
interface QuantaQLExecutor {
    suspend fun execute(statement: Statement): Flow<QueryResult>
    suspend fun executeQuery(query: QueryExpression): Flow<QueryResult>
    suspend fun executeBatch(statements: List<Statement>): Flow<BatchResult>
}

sealed class QueryResult {
    data class SuccessResult(val data: Any, val metadata: QueryMetadata? = null) : QueryResult()
    data class ErrorResult(val error: String, val code: Int? = null) : QueryResult()
    data class StreamingResult(val data: Flow<Any>) : QueryResult()
}

data class BatchResult(
    val results: List<QueryResult>,
    val success: Boolean,
    val failedStatements: List<Int> = emptyList()
)

data class QueryMetadata(
    val executionTime: Duration,
    val recordsAffected: Long? = null,
    val queryPlan: String? = null,
    val warnings: List<String> = emptyList()
)

/**
 * Flow-based query builder for constructing QuantaQL queries programmatically
 */
class QuantaQLQueryBuilder {
    private val statements = mutableListOf<Statement>()
    
    fun addStatement(statement: Statement): QuantaQLQueryBuilder {
        statements.add(statement)
        return this
    }
    
    fun find(vararg fields: String): FindBuilder {
        return FindBuilder(fields.map { ReturnField.FieldReference(field = Identifier(it)) })
    }
    
    fun build(): QuantaQLProgram = QuantaQLProgram.Program(statements.toList())
    
    inner class FindBuilder(private val returnFields: List<ReturnField>) {
        fun match(condition: Condition): FindBuilder {
            val findOp = DataOperation.FindOperation(
                returnFields = returnFields,
                condition = condition
            )
            statements.add(findOp)
            return this
        }
        
        fun orderBy(vararg fields: OrderField): FindBuilder {
            // Update the last statement if it's a FindOperation
            val lastStatement = statements.lastOrNull()
            if (lastStatement is DataOperation.FindOperation) {
                statements[statements.size - 1] = lastStatement.copy(orderBy = fields.toList())
            }
            return this
        }
        
        fun limit(count: Int): FindBuilder {
            val lastStatement = statements.lastOrNull()
            if (lastStatement is DataOperation.FindOperation) {
                statements[statements.size - 1] = lastStatement.copy(limit = count)
            }
            return this
        }
    }
}

