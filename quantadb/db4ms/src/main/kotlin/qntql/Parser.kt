// Parser
class Parser(private val lexer: Lexer) {
    private var currentToken: Token = lexer.nextToken()

    fun parse(): AstNode {
        return when (currentToken.type) {
            TokenType.CREATE -> parseCreate()
            TokenType.INSERT -> parseInsert()
            TokenType.SELECT -> parseSelect()
            TokenType.UPDATE -> parseUpdate()
            TokenType.DELETE -> parseDelete()
            TokenType.TRAVERSE -> parseTraverse()
            TokenType.MATCH -> parseMatch()
            TokenType.CREATE_RELATION -> parseCreateRelation()
            TokenType.INSERT_METRIC -> parseInsertMetric()
            TokenType.TRANSACTION -> parseTransaction()
            else -> throw IllegalStateException("Unexpected token: ${currentToken.type}")
        }
    }

    private fun parseCreate(): AstNode {
        eat(TokenType.CREATE)
        eat(TokenType.RECORD)
        val name = currentToken.value
        eat(TokenType.IDENTIFIER)
        eat(TokenType.IN)
        val bucket = currentToken.value
        eat(TokenType.IDENTIFIER)
        eat(TokenType.LPAREN)

        val fields = mutableListOf<FieldDefinition>()
        while (currentToken.type != TokenType.RPAREN) {
            val fieldName = currentToken.value
            eat(TokenType.IDENTIFIER)
            val fieldType = currentToken.value
            eat(TokenType.IDENTIFIER)

            val constraints = mutableListOf<String>()
            while (currentToken.type == TokenType.PRIMARY ||
                   currentToken.type == TokenType.KEY ||
                   currentToken.type == TokenType.UNIQUE ||
                   currentToken.type == TokenType.INDEX ||
                   currentToken.type == TokenType.DEFAULT) {
                constraints.add(currentToken.value)
                eat(currentToken.type)
            }

            fields.add(FieldDefinition(fieldName, fieldType, constraints))

            if (currentToken.type == TokenType.COMMA) {
                eat(TokenType.COMMA)
            }
        }

        eat(TokenType.RPAREN)
        return CreateRecord(name, bucket, fields)
    }

    private fun parseInsert(): AstNode {
        eat(TokenType.INSERT)
        eat(TokenType.INTO)
        val record = currentToken.value
        eat(TokenType.IDENTIFIER)
        eat(TokenType.VALUES)
        eat(TokenType.LBRACE)

        val values = mutableMapOf<String, Any>()
        while (currentToken.type != TokenType.RBRACE) {
            val key = currentToken.value
            eat(TokenType.IDENTIFIER)
            eat(TokenType.COLON)
            val value = when (currentToken.type) {
                TokenType.STRING -> currentToken.value
                TokenType.NUMBER -> currentToken.value.toDouble()
                TokenType.BOOLEAN -> currentToken.value.toBoolean()
                else -> throw IllegalStateException("Unexpected token: ${currentToken.type}")
            }
            eat(currentToken.type)
            values[key] = value

            if (currentToken.type == TokenType.COMMA) {
                eat(TokenType.COMMA)
            }
        }

        eat(TokenType.RBRACE)
        return Insert(record, values)
    }

    private fun parseSelect(): AstNode {
        eat(TokenType.SELECT)
        val fields = mutableListOf<String>()
        while (currentToken.type != TokenType.FROM) {
            fields.add(currentToken.value)
            eat(TokenType.IDENTIFIER)
            if (currentToken.type == TokenType.COMMA) {
                eat(TokenType.COMMA)
            }
        }

        eat(TokenType.FROM)
        val from = currentToken.value
        eat(TokenType.IDENTIFIER)

        val where = if (currentToken.type == TokenType.WHERE) {
            eat(TokenType.WHERE)
            val condition = currentToken.value
            eat(TokenType.IDENTIFIER)
            WhereClause(condition)
        } else {
            null
        }

        return Select(fields, from, where)
    }

    private fun parseUpdate(): AstNode {
        eat(TokenType.UPDATE)
        val record = currentToken.value
        eat(TokenType.IDENTIFIER)
        eat(TokenType.SET)

        val set = mutableMapOf<String, Any>()
        while (currentToken.type != TokenType.WHERE) {
            val key = currentToken.value
            eat(TokenType.IDENTIFIER)
            eat(TokenType.EQ)
            val value = when (currentToken.type) {
                TokenType.STRING -> currentToken.value
                TokenType.NUMBER -> currentToken.value.toDouble()
                TokenType.BOOLEAN -> currentToken.value.toBoolean()
                else -> throw IllegalStateException("Unexpected token: ${currentToken.type}")
            }
            eat(currentToken.type)
            set[key] = value

            if (currentToken.type == TokenType.COMMA) {
                eat(TokenType.COMMA)
            }
        }

        eat(TokenType.WHERE)
        val condition = currentToken.value
        eat(TokenType.IDENTIFIER)
        val where = WhereClause(condition)

        return Update(record, set, where)
    }

    private fun parseDelete(): AstNode {
        eat(TokenType.DELETE)
        eat(TokenType.FROM)
        val record = currentToken.value
        eat(TokenType.IDENTIFIER)

        val where = if (currentToken.type == TokenType.WHERE) {
            eat(TokenType.WHERE)
            val condition = currentToken.value
            eat(TokenType.IDENTIFIER)
            WhereClause(condition)
        } else {
            null
        }

        return Delete(record, where)
    }

    private fun parseTraverse(): AstNode {
        eat(TokenType.TRAVERSE)
        val path = currentToken.value
        eat(TokenType.IDENTIFIER)

        val where = if (currentToken.type == TokenType.WHERE) {
            eat(TokenType.WHERE)
            val condition = currentToken.value
            eat(TokenType.IDENTIFIER)
            WhereClause(condition)
        } else {
            null
        }

        return Traverse(path, where)
    }

    private fun parseMatch(): AstNode {
        eat(TokenType.MATCH)
        val pattern = currentToken.value
        eat(TokenType.IDENTIFIER)

        val where = if (currentToken.type == TokenType.WHERE) {
            eat(TokenType.WHERE)
            val condition = currentToken.value
            eat(TokenType.IDENTIFIER)
            WhereClause(condition)
        } else {
            null
        }

        return Match(pattern, where)
    }

    private fun parseCreateRelation(): AstNode {
        eat(TokenType.CREATE_RELATION)
        eat(TokenType.FROM)
        val from = currentToken.value
        eat(TokenType.IDENTIFIER)
        eat(TokenType.TO)
        val to = currentToken.value
        eat(TokenType.IDENTIFIER)
        eat(TokenType.TYPE)
        val type = currentToken.value
        eat(TokenType.IDENTIFIER)

        eat(TokenType.PROPERTIES)
        eat(TokenType.LBRACE)

        val properties = mutableMapOf<String, Any>()
        while (currentToken.type != TokenType.RBRACE) {
            val key = currentToken.value
            eat(TokenType.IDENTIFIER)
            eat(TokenType.COLON)
            val value = when (currentToken.type) {
                TokenType.STRING -> currentToken.value
                TokenType.NUMBER -> currentToken.value.toDouble()
                TokenType.BOOLEAN -> currentToken.value.toBoolean()
                else -> throw IllegalStateException("Unexpected token: ${currentToken.type}")
            }
            eat(currentToken.type)
            properties[key] = value

            if (currentToken.type == TokenType.COMMA) {
                eat(TokenType.COMMA)
            }
        }

        eat(TokenType.RBRACE)
        return CreateRelation(from, to, type, properties)
    }

    private fun parseInsertMetric(): AstNode {
        eat(TokenType.INSERT_METRIC)
        eat(TokenType.INTO)
        val record = currentToken.value
        eat(TokenType.IDENTIFIER)
        eat(TokenType.DOT)
        val field = currentToken.value
        eat(TokenType.IDENTIFIER)
        eat(TokenType.VALUES)
        eat(TokenType.LPAREN)

        val values = mutableMapOf<String, Any>()
        while (currentToken.type != TokenType.RPAREN) {
            val key = currentToken.value
            eat(TokenType.IDENTIFIER)
            eat(TokenType.COLON)
            val value = when (currentToken.type) {
                TokenType.STRING -> currentToken.value
                TokenType.NUMBER -> currentToken.value.toDouble()
                TokenType.BOOLEAN -> currentToken.value.toBoolean()
                else -> throw IllegalStateException("Unexpected token: ${currentToken.type}")
            }
            eat(currentToken.type)
            values[key] = value

            if (currentToken.type == TokenType.COMMA) {
                eat(TokenType.COMMA)
            }
        }

        eat(TokenType.RPAREN)

        val where = if (currentToken.type == TokenType.WHERE) {
            eat(TokenType.WHERE)
            val condition = currentToken.value
            eat(TokenType.IDENTIFIER)
            WhereClause(condition)
        } else {
            null
        }

        return InsertMetric(record, field, values, where)
    }

    private fun parseTransaction(): AstNode {
        eat(TokenType.TRANSACTION)
        eat(TokenType.BEGIN)

        val operations = mutableListOf<AstNode>()
        while (currentToken.type != TokenType.COMMIT && currentToken.type != TokenType.ROLLBACK) {
            operations.add(parse())
        }

        if (currentToken.type == TokenType.COMMIT) {
            eat(TokenType.COMMIT)
        } else {
            eat(TokenType.ROLLBACK)
        }

        return Transaction(operations)
    }

    private fun eat(tokenType: TokenType) {
        if (currentToken.type == tokenType) {
            currentToken = lexer.nextToken()
        } else {
            throw IllegalStateException("Expected token: $tokenType, but got: ${currentToken.type}")
        }
    }
}
