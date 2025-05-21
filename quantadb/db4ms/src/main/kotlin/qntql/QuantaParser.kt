package com.icaht.qntql


/**
 * Main parser for QuantaQL query language
 * Converts raw query strings into structured AST representations
 */
class QuantaQLParser(private val lexer: QuantaQLLexer) {
    
    private var currentToken: Token = lexer.nextToken()
    
    /**
     * Parses a complete QuantaQL query and returns the AST
     */
    fun parse(): Statement {
        val statement = when (currentToken.type) {
            TokenType.SELECT -> parseSelectStatement()
            TokenType.INSERT -> parseInsertStatement()
            TokenType.UPDATE -> parseUpdateStatement()
            TokenType.DELETE -> parseDeleteStatement()
            TokenType.CREATE -> when (lexer.peek().type) {
                TokenType.RECORD -> parseCreateRecordStatement()
                TokenType.INDEX -> parseCreateIndexStatement()
                TokenType.RELATION -> parseCreateRelationStatement()
                else -> throw ParseException("Unexpected token after CREATE: ${lexer.peek().value}")
            }
            TokenType.ALTER -> parseAlterStatement()
            TokenType.BEGIN -> parseTransactionStatement()
            TokenType.WITH -> parseWithStatement()
            else -> throw ParseException("Unexpected token: ${currentToken.value}")
        }
        
        expect(TokenType.SEMICOLON)
        return statement
    }
    
    private fun parseSelectStatement(): SelectStatement {
        expect(TokenType.SELECT)
        
        val projections = mutableListOf<Expression>()
        do {
            projections.add(parseExpression())
            if (currentToken.type != TokenType.COMMA) break
            consume() // Consume comma
        } while (true)
        
        expect(TokenType.FROM)
        val source = parseSource()
        
        var whereClause: Expression? = null
        var groupByClause: GroupByClause? = null
        var havingClause: Expression? = null
        var orderByClause: OrderByClause? = null
        var limitClause: Int? = null
        
        while (currentToken.type != TokenType.SEMICOLON) {
            when (currentToken.type) {
                TokenType.WHERE -> {
                    consume() // Consume WHERE
                    whereClause = parseExpression()
                }
                TokenType.GROUP -> {
                    consume() // Consume GROUP
                    expect(TokenType.BY)
                    groupByClause = parseGroupByClause()
                }
                TokenType.HAVING -> {
                    consume() // Consume HAVING
                    havingClause = parseExpression()
                }
                TokenType.ORDER -> {
                    consume() // Consume ORDER
                    expect(TokenType.BY)
                    orderByClause = parseOrderByClause()
                }
                TokenType.LIMIT -> {
                    consume() // Consume LIMIT
                    limitClause = parseInt()
                }
                else -> break
            }
        }
        
        return SelectStatement(
            projections = projections,
            source = source,
            whereClause = whereClause,
            groupByClause = groupByClause,
            havingClause = havingClause,
            orderByClause = orderByClause,
            limitClause = limitClause
        )
    }
    
    private fun parseInsertStatement(): InsertStatement {
        expect(TokenType.INSERT)
        
        // Handle metric insert
        if (currentToken.type == TokenType.METRIC) {
            consume() // Consume METRIC
            expect(TokenType.INTO)
            val target = parseQualifiedName()
            expect(TokenType.VALUES)
            val metrics = parseMetricValues()
            
            var whereClause: Expression? = null
            if (currentToken.type == TokenType.WHERE) {
                consume() // Consume WHERE
                whereClause = parseExpression()
            }
            
            return InsertMetricStatement(
                target = target,
                metrics = metrics,
                whereClause = whereClause
            )
        }
        
        // Normal insert
        expect(TokenType.INTO)
        val target = parseIdentifier()
        expect(TokenType.VALUES)
        val values = parseDocumentLiteral()
        
        return InsertStatement(
            target = target,
            values = values
        )
    }
    
    private fun parseUpdateStatement(): UpdateStatement {
        expect(TokenType.UPDATE)
        val target = parseIdentifier()
        expect(TokenType.SET)
        
        val updates = mutableListOf<Assignment>()
        do {
            val path = parseQualifiedName()
            expect(TokenType.EQUALS)
            val value = parseExpression()
            updates.add(Assignment(path, value))
            
            if (currentToken.type != TokenType.COMMA) break
            consume() // Consume comma
        } while (true)
        
        var whereClause: Expression? = null
        if (currentToken.type == TokenType.WHERE) {
            consume() // Consume WHERE
            whereClause = parseExpression()
        }
        
        return UpdateStatement(
            target = target,
            updates = updates,
            whereClause = whereClause
        )
    }
    
    private fun parseDeleteStatement(): DeleteStatement {
        expect(TokenType.DELETE)
        expect(TokenType.FROM)
        val target = parseIdentifier()
        
        var whereClause: Expression? = null
        if (currentToken.type == TokenType.WHERE) {
            consume() // Consume WHERE
            whereClause = parseExpression()
        }
        
        return DeleteStatement(
            target = target,
            whereClause = whereClause
        )
    }
    
    private fun parseCreateRecordStatement(): CreateRecordStatement {
        expect(TokenType.CREATE)
        expect(TokenType.RECORD)
        val recordName = parseIdentifier()
        expect(TokenType.IN)
        expect(TokenType.BUCKET)
        val bucketName = parseIdentifier()
        
        expect(TokenType.LEFT_PAREN)
        val fields = mutableListOf<FieldDefinition>()
        
        do {
            val fieldName = parseIdentifier()
            val fieldType = parseDataType()
            
            var constraints = mutableListOf<Constraint>()
            while (currentToken.type in listOf(
                    TokenType.PRIMARY, TokenType.UNIQUE, TokenType.DEFAULT, 
                    TokenType.REFERENCE, TokenType.INDEX)) {
                constraints.add(parseConstraint())
            }
            
            fields.add(FieldDefinition(fieldName, fieldType, constraints))
            
            if (currentToken.type != TokenType.COMMA) break
            consume() // Consume comma
        } while (true)
        
        expect(TokenType.RIGHT_PAREN)
        
        return CreateRecordStatement(
            name = recordName,
            bucket = bucketName,
            fields = fields
        )
    }
    
    private fun parseCreateIndexStatement(): CreateIndexStatement {
        expect(TokenType.CREATE)
        expect(TokenType.INDEX)
        expect(TokenType.ON)
        val target = parseIdentifier()
        
        expect(TokenType.LEFT_PAREN)
        val fields = mutableListOf<String>()
        
        do {
            fields.add(parseQualifiedName())
            if (currentToken.type != TokenType.COMMA) break
            consume() // Consume comma
        } while (true)
        
        expect(TokenType.RIGHT_PAREN)
        
        var options: Map<String, String>? = null
        if (currentToken.type == TokenType.WITH) {
            consume() // Consume WITH
            options = parseIndexOptions()
        }
        
        return CreateIndexStatement(
            target = target,
            fields = fields,
            options = options
        )
    }
    
    private fun parseCreateRelationStatement(): CreateRelationStatement {
        expect(TokenType.CREATE)
        expect(TokenType.RELATION)
        expect(TokenType.FROM)
        
        val fromRecord = parseIdentifier()
        var fromCondition: Expression? = null
        
        if (currentToken.type == TokenType.WHERE) {
            consume() // Consume WHERE
            fromCondition = parseExpression()
        }
        
        expect(TokenType.TO)
        val toRecord = parseIdentifier()
        var toCondition: Expression? = null
        
        if (currentToken.type == TokenType.WHERE) {
            consume() // Consume WHERE
            toCondition = parseExpression()
        }
        
        expect(TokenType.TYPE)
        val relationType = parseStringLiteral()
        
        var properties: DocumentLiteral? = null
        if (currentToken.type == TokenType.PROPERTIES) {
            consume() // Consume PROPERTIES
            properties = parseDocumentLiteral()
        }
        
        return CreateRelationStatement(
            fromRecord = fromRecord,
            fromCondition = fromCondition,
            toRecord = toRecord,
            toCondition = toCondition,
            type = relationType,
            properties = properties
        )
    }
    
    private fun parseAlterStatement(): AlterStatement {
        expect(TokenType.ALTER)
        expect(TokenType.RECORD)
        val recordName = parseIdentifier()
        
        val operations = mutableListOf<AlterOperation>()
        
        do {
            when (currentToken.type) {
                TokenType.ADD -> {
                    consume() // Consume ADD
                    when (currentToken.type) {
                        TokenType.COLUMN -> {
                            consume() // Consume COLUMN
                            val columnName = parseIdentifier()
                            val dataType = parseDataType()
                            
                            var defaultValue: Expression? = null
                            if (currentToken.type == TokenType.DEFAULT) {
                                consume() // Consume DEFAULT
                                defaultValue = parseExpression()
                            }
                            
                            operations.add(AddColumnOperation(columnName, dataType, defaultValue))
                        }
                        TokenType.RELATION -> {
                            consume() // Consume RELATION
                            val relationName = parseIdentifier()
                            expect(TokenType.TO)
                            val targetRecord = parseIdentifier()
                            
                            val cardinality = if (currentToken.type == TokenType.ONE) {
                                consume()
                                Cardinality.ONE
                            } else if (currentToken.type == TokenType.MANY) {
                                consume()
                                Cardinality.MANY
                            } else {
                                Cardinality.MANY // Default
                            }
                            
                            operations.add(AddRelationOperation(relationName, targetRecord, cardinality))
                        }
                        else -> throw ParseException("Expected COLUMN or RELATION after ADD")
                    }
                }
                TokenType.DROP -> {
                    consume() // Consume DROP
                    expect(TokenType.COLUMN)
                    val columnName = parseIdentifier()
                    operations.add(DropColumnOperation(columnName))
                }
                TokenType.RENAME -> {
                    consume() // Consume RENAME
                    expect(TokenType.COLUMN)
                    val oldName = parseIdentifier()
                    expect(TokenType.TO)
                    val newName = parseIdentifier()
                    operations.add(RenameColumnOperation(oldName, newName))
                }
                else -> throw ParseException("Expected ADD, DROP, or RENAME in ALTER statement")
            }
            
            if (currentToken.type != TokenType.COMMA) break
            consume() // Consume comma
        } while (true)
        
        return AlterStatement(
            recordName = recordName,
            operations = operations
        )
    }
    
    private fun parseTransactionStatement(): TransactionStatement {
        expect(TokenType.BEGIN)
        expect(TokenType.TRANSACTION)
        
        val statements = mutableListOf<Statement>()
        
        while (currentToken.type != TokenType.COMMIT && 
               currentToken.type != TokenType.ROLLBACK) {
            statements.add(parse())
        }
        
        val action = if (currentToken.type == TokenType.COMMIT) {
            consume() // Consume COMMIT
            TransactionAction.COMMIT
        } else {
            consume() // Consume ROLLBACK
            TransactionAction.ROLLBACK
        }
        
        return TransactionStatement(
            statements = statements,
            action = action
        )
    }
    
    private fun parseWithStatement(): WithStatement {
        expect(TokenType.WITH)
        
        val ctes = mutableListOf<CommonTableExpression>()
        
        do {
            val name = parseIdentifier()
            expect(TokenType.AS)
            expect(TokenType.LEFT_PAREN)
            val query = parseSelectStatement()
            expect(TokenType.RIGHT_PAREN)
            
            ctes.add(CommonTableExpression(name, query))
            
            if (currentToken.type != TokenType.COMMA) break
            consume() // Consume comma
        } while (true)
        
        val mainQuery = parseSelectStatement()
        
        return WithStatement(
            ctes = ctes,
            mainQuery = mainQuery
        )
    }
    
    // Helper parsing methods
    
    private fun parseSource(): Source {
        val identifier = parseIdentifier()
        
        if (currentToken.type == TokenType.AS) {
            consume() // Consume AS
            val alias = parseIdentifier()
            return TableSource(identifier, alias)
        }
        
        if (currentToken.type == TokenType.TRAVERSE) {
            consume() // Consume TRAVERSE
            return parseTraversal(identifier)
        }
        
        return TableSource(identifier)
    }
    
    private fun parseTraversal(startNode: String): TraversalSource {
        // This is a simplified version, a full implementation would handle complex path patterns
        expect(TokenType.MINUS_BRACKET)
        val relationshipType = parseIdentifier()
        expect(TokenType.BRACKET_ARROW)
        val targetNode = parseIdentifier()
        
        var targetType: String? = null
        if (currentToken.type == TokenType.COLON) {
            consume() // Consume colon
            targetType = parseIdentifier()
        }
        
        return TraversalSource(
            startNode = startNode,
            relationshipType = relationshipType,
            targetNode = targetNode,
            targetType = targetType
        )
    }
    
    private fun parseExpression(): Expression {
        // This is highly simplified, a real implementation would handle operator precedence,
        // parentheses, function calls, etc.
        return parseLogicalExpression()
    }
    
    private fun parseLogicalExpression(): Expression {
        var left = parseComparisonExpression()
        
        while (currentToken.type in listOf(TokenType.AND, TokenType.OR)) {
            val operator = if (currentToken.type == TokenType.AND) LogicalOperator.AND else LogicalOperator.OR
            consume() // Consume operator
            val right = parseComparisonExpression()
            left = LogicalExpression(left, operator, right)
        }
        
        return left
    }
    
    private fun parseComparisonExpression(): Expression {
        val left = parseAdditiveExpression()
        
        if (currentToken.type in listOf(
                TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LESS_THAN,
                TokenType.LESS_THAN_EQUALS, TokenType.GREATER_THAN, TokenType.GREATER_THAN_EQUALS,
                TokenType.CONTAINS)) {
            
            val operator = when (currentToken.type) {
                TokenType.EQUALS -> ComparisonOperator.EQUALS
                TokenType.NOT_EQUALS -> ComparisonOperator.NOT_EQUALS
                TokenType.LESS_THAN -> ComparisonOperator.LESS_THAN
                TokenType.LESS_THAN_EQUALS -> ComparisonOperator.LESS_THAN_EQUALS
                TokenType.GREATER_THAN -> ComparisonOperator.GREATER_THAN
                TokenType.GREATER_THAN_EQUALS -> ComparisonOperator.GREATER_THAN_EQUALS
                TokenType.CONTAINS -> ComparisonOperator.CONTAINS
                else -> throw ParseException("Unexpected comparison operator: ${currentToken.value}")
            }
            
            consume() // Consume operator
            val right = parseAdditiveExpression()
            return ComparisonExpression(left, operator, right)
        }
        
        return left
    }
    
    private fun parseAdditiveExpression(): Expression {
        var left = parseMultiplicativeExpression()
        
        while (currentToken.type in listOf(TokenType.PLUS, TokenType.MINUS)) {
            val operator = if (currentToken.type == TokenType.PLUS) ArithmeticOperator.ADD else ArithmeticOperator.SUBTRACT
            consume() // Consume operator
            val right = parseMultiplicativeExpression()
            left = ArithmeticExpression(left, operator, right)
        }
        
        return left
    }
    
    private fun parseMultiplicativeExpression(): Expression {
        var left = parsePrimaryExpression()
        
        while (currentToken.type in listOf(TokenType.MULTIPLY, TokenType.DIVIDE)) {
            val operator = if (currentToken.type == TokenType.MULTIPLY) ArithmeticOperator.MULTIPLY else ArithmeticOperator.DIVIDE
            consume() // Consume operator
            val right = parsePrimaryExpression()
            left = ArithmeticExpression(left, operator, right)
        }
        
        return left
    }
    
    private fun parsePrimaryExpression(): Expression {
        return when (currentToken.type) {
            TokenType.INTEGER_LITERAL -> {
                val value = parseInt()
                IntegerLiteral(value)
            }
            TokenType.FLOAT_LITERAL -> {
                val value = parseFloat()
                FloatLiteral(value)
            }
            TokenType.STRING_LITERAL -> {
                val value = parseStringLiteral()
                StringLiteral(value)
            }
            TokenType.LEFT_BRACE -> {
                parseDocumentLiteral()
            }
            TokenType.IDENTIFIER -> {
                IdentifierExpression(parseQualifiedName())
            }
            TokenType.LEFT_PAREN -> {
                consume() // Consume left paren
                val expr = parseExpression()
                expect(TokenType.RIGHT_PAREN)
                expr
            }
            else -> throw ParseException("Unexpected token in expression: ${currentToken.value}")
        }
    }
    
    private fun parseQualifiedName(): String {
        val sb = StringBuilder(parseIdentifier())
        
        while (currentToken.type == TokenType.DOT) {
            consume() // Consume dot
            sb.append('.').append(parseIdentifier())
        }
        
        return sb.toString()
    }
    
    private fun parseIdentifier(): String {
        expect(TokenType.IDENTIFIER)
        val identifier = currentToken.value
        consume() // Consume identifier
        return identifier
    }
    
    private fun parseStringLiteral(): String {
        expect(TokenType.STRING_LITERAL)
        val value = currentToken.value
        consume() // Consume string literal
        return value.substring(1, value.length - 1) // Remove quotes
    }
    
    private fun parseInt(): Int {
        expect(TokenType.INTEGER_LITERAL)
        val value = currentToken.value.toInt()
        consume() // Consume integer literal
        return value
    }
    
    private fun parseFloat(): Float {
        expect(TokenType.FLOAT_LITERAL)
        val value = currentToken.value.toFloat()
        consume() // Consume float literal
        return value
    }
    
    private fun parseDocumentLiteral(): DocumentLiteral {
        expect(TokenType.LEFT_BRACE)
        
        val fields = mutableMapOf<String, Expression>()
        
        if (currentToken.type != TokenType.RIGHT_BRACE) {
            do {
                val key = parseIdentifier()
                expect(TokenType.COLON)
                val value = parseExpression()
                
                fields[key] = value
                
                if (currentToken.type != TokenType.COMMA) break
                consume() // Consume comma
            } while (true)
        }
        
        expect(TokenType.RIGHT_BRACE)
        
        return DocumentLiteral(fields)
    }
    
    private fun parseMetricValues(): MetricValues {
        expect(TokenType.LEFT_PAREN)
        
        var value: Expression? = null
        var timestamp: Expression? = null
        
        do {
            val fieldName = parseIdentifier()
            expect(TokenType.COLON)
            
            when (fieldName) {
                "value" -> value = parseExpression()
                "timestamp" -> timestamp = parseExpression()
                else -> throw ParseException("Unexpected metric field name: $fieldName")
            }
            
            if (currentToken.type != TokenType.COMMA) break
            consume() // Consume comma
        } while (true)
        
        expect(TokenType.RIGHT_PAREN)
        
        if (value == null) {
            throw ParseException("Metric value is required")
        }
        
        return MetricValues(value, timestamp)
    }
    
    private fun parseDataType(): DataType {
        val baseType = parseIdentifier()
        
        var subtype: String? = null
        if (currentToken.type == TokenType.LESS_THAN) {
            consume() // Consume <
            subtype = parseIdentifier()
            expect(TokenType.GREATER_THAN)
        }
        
        // Parse relation cardinality if needed
        if (baseType == "RELATION") {
            expect(TokenType.TO)
            val targetType = parseIdentifier()
            
            val cardinality = if (currentToken.type == TokenType.ONE) {
                consume()
                Cardinality.ONE
            } else if (currentToken.type == TokenType.MANY) {
                consume()
                Cardinality.MANY
            } else {
                Cardinality.MANY // Default
            }
            
            return RelationDataType(targetType, cardinality)
        }
        
        return BasicDataType(baseType, subtype)
    }
    
    private fun parseConstraint(): Constraint {
        return when (currentToken.type) {
            TokenType.PRIMARY -> {
                consume() // Consume PRIMARY
                expect(TokenType.KEY)
                PrimaryKeyConstraint()
            }
            TokenType.UNIQUE -> {
                consume() // Consume UNIQUE
                var isIndex = false
                if (currentToken.type == TokenType.INDEX) {
                    consume() // Consume INDEX
                    isIndex = true
                }
                UniqueConstraint(isIndex)
            }
            TokenType.DEFAULT -> {
                consume() // Consume DEFAULT
                val value = parseExpression()
                DefaultConstraint(value)
            }
            TokenType.REFERENCE -> {
                consume() // Consume REFERENCE
                val targetTable = parseIdentifier()
                expect(TokenType.LEFT_PAREN)
                val targetColumn = parseIdentifier()
                expect(TokenType.RIGHT_PAREN)
                ReferenceConstraint(targetTable, targetColumn)
            }
            TokenType.INDEX -> {
                consume() // Consume INDEX
                IndexConstraint()
            }
            else -> throw ParseException("Unknown constraint type: ${currentToken.value}")
        }
    }
    
    private fun parseGroupByClause(): GroupByClause {
        val expressions = mutableListOf<Expression>()
        
        do {
            expressions.add(parseExpression())
            if (currentToken.type != TokenType.COMMA) break
            consume() // Consume comma
        } while (true)
        
        return GroupByClause(expressions)
    }
    
    private fun parseOrderByClause(): OrderByClause {
        val items = mutableListOf<OrderByItem>()
        
        do {
            val expression = parseExpression()
            val direction = if (currentToken.type == TokenType.ASC) {
                consume() // Consume ASC
                SortDirection.ASCENDING
            } else if (currentToken.type == TokenType.DESC) {
                consume() // Consume DESC
                SortDirection.DESCENDING
            } else {
                SortDirection.ASCENDING // Default
            }
            
            items.add(OrderByItem(expression, direction))
            
            if (currentToken.type != TokenType.COMMA) break
            consume() // Consume comma
        } while (true)
        
        return OrderByClause(items)
    }
    
    private fun parseIndexOptions(): Map<String, String> {
        expect(TokenType.LEFT_PAREN)
        
        val options = mutableMapOf<String, String>()
        
        do {
            val key = parseStringLiteral()
            expect(TokenType.COLON)
            val value = parseStringLiteral()
            
            options[key] = value
            
            if (currentToken.type != TokenType.COMMA) break
            consume() // Consume comma
        } while (true)
        
        expect(TokenType.RIGHT_PAREN)
        
        return options
    }
    
    // Token handling methods
    
    private fun expect(expectedType: TokenType) {
        if (currentToken.type != expectedType) {
            throw ParseException("Expected $expectedType but got ${currentToken.type}")
        }
        consume()
    }
    
    private fun consume() {
        currentToken = lexer.nextToken()
    }
}

class ParseException(message: String) : Exception(message)