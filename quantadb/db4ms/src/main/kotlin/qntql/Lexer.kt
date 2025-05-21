// Lexer
enum class TokenType {
    CREATE, RECORD, IN, BUCKET, SCALAR, DOCUMENT, RELATION, METRIC, TIME, DURATION, GEO,
    PRIMARY, KEY, UNIQUE, INDEX, DEFAULT, NOW, REFERENCE, INSERT, INTO, VALUES, SELECT,
    FROM, WHERE, CONTAINS, UPDATE, SET, DELETE, TRAVERSE, MATCH, PATH, RETURN, CREATE_RELATION,
    TO, TYPE, PROPERTIES, INSERT_METRIC, METRIC, AGGREGATION, GROUP_BY, HAVING, JOIN, ON,
    TRANSACTION, BEGIN, COMMIT, ROLLBACK, SAVEPOINT, IDENTIFIER, STRING, NUMBER, BOOLEAN,
    LPAREN, RPAREN, LBRACE, RBRACE, LBRACKET, RBRACKET, COMMA, DOT, EQ, NEQ, LT, GT, LTE, GTE,
    AND, OR, NOT, PLUS, MINUS, MULT, DIV, MOD, EOF
}

data class Token(val type: TokenType, val value: String)

class Lexer(private val input: String) {
    private var position = 0

    fun nextToken(): Token {
        if (position >= input.length) return Token(TokenType.EOF, "")

        val currentChar = input[position]
        when {
            currentChar.isWhitespace() -> {
                position++
                return nextToken()
            }
            currentChar.isLetter() -> return readIdentifier()
            currentChar.isDigit() -> return readNumber()
            currentChar == '\'' -> return readString()
            else -> {
                return when (currentChar) {
                    '(' -> Token(TokenType.LPAREN, "(")
                    ')' -> Token(TokenType.RPAREN, ")")
                    '{' -> Token(TokenType.LBRACE, "{")
                    '}' -> Token(TokenType.RBRACE, "}")
                    '[' -> Token(TokenType.LBRACKET, "[")
                    ']' -> Token(TokenType.RBRACKET, "]")
                    ',' -> Token(TokenType.COMMA, ",")
                    '.' -> Token(TokenType.DOT, ".")
                    '=' -> Token(TokenType.EQ, "=")
                    '!' -> {
                        if (position + 1 < input.length && input[position + 1] == '=') {
                            position++
                            Token(TokenType.NEQ, "!=")
                        } else {
                            Token(TokenType.NOT, "!")
                        }
                    }
                    '<' -> {
                        if (position + 1 < input.length && input[position + 1] == '=') {
                            position++
                            Token(TokenType.LTE, "<=")
                        } else {
                            Token(TokenType.LT, "<")
                        }
                    }
                    '>' -> {
                        if (position + 1 < input.length && input[position + 1] == '=') {
                            position++
                            Token(TokenType.GTE, ">=")
                        } else {
                            Token(TokenType.GT, ">")
                        }
                    }
                    '&' -> {
                        if (position + 1 < input.length && input[position + 1] == '&') {
                            position++
                            Token(TokenType.AND, "&&")
                        } else {
                            throw IllegalStateException("Unexpected character: $currentChar")
                        }
                    }
                    '|' -> {
                        if (position + 1 < input.length && input[position + 1] == '|') {
                            position++
                            Token(TokenType.OR, "||")
                        } else {
                            throw IllegalStateException("Unexpected character: $currentChar")
                        }
                    }
                    '+' -> Token(TokenType.PLUS, "+")
                    '-' -> Token(TokenType.MINUS, "-")
                    '*' -> Token(TokenType.MULT, "*")
                    '/' -> Token(TokenType.DIV, "/")
                    '%' -> Token(TokenType.MOD, "%")
                    else -> throw IllegalStateException("Unexpected character: $currentChar")
                }.also { position++ }
            }
        }
    }

    private fun readIdentifier(): Token {
        val start = position
        while (position < input.length && (input[position].isLetterOrDigit() || input[position] == '_')) {
            position++
        }
        val identifier = input.substring(start, position)
        return when (identifier.uppercase()) {
            "CREATE" -> Token(TokenType.CREATE, identifier)
            "RECORD" -> Token(TokenType.RECORD, identifier)
            "IN" -> Token(TokenType.IN, identifier)
            "BUCKET" -> Token(TokenType.BUCKET, identifier)
            "SCALAR" -> Token(TokenType.SCALAR, identifier)
            "DOCUMENT" -> Token(TokenType.DOCUMENT, identifier)
            "RELATION" -> Token(TokenType.RELATION, identifier)
            "METRIC" -> Token(TokenType.METRIC, identifier)
            "TIME" -> Token(TokenType.TIME, identifier)
            "DURATION" -> Token(TokenType.DURATION, identifier)
            "GEO" -> Token(TokenType.GEO, identifier)
            "PRIMARY" -> Token(TokenType.PRIMARY, identifier)
            "KEY" -> Token(TokenType.KEY, identifier)
            "UNIQUE" -> Token(TokenType.UNIQUE, identifier)
            "INDEX" -> Token(TokenType.INDEX, identifier)
            "DEFAULT" -> Token(TokenType.DEFAULT, identifier)
            "NOW" -> Token(TokenType.NOW, identifier)
            "REFERENCE" -> Token(TokenType.REFERENCE, identifier)
            "INSERT" -> Token(TokenType.INSERT, identifier)
            "INTO" -> Token(TokenType.INTO, identifier)
            "VALUES" -> Token(TokenType.VALUES, identifier)
            "SELECT" -> Token(TokenType.SELECT, identifier)
            "FROM" -> Token(TokenType.FROM, identifier)
            "WHERE" -> Token(TokenType.WHERE, identifier)
            "CONTAINS" -> Token(TokenType.CONTAINS, identifier)
            "UPDATE" -> Token(TokenType.UPDATE, identifier)
            "SET" -> Token(TokenType.SET, identifier)
            "DELETE" -> Token(TokenType.DELETE, identifier)
            "TRAVERSE" -> Token(TokenType.TRAVERSE, identifier)
            "MATCH" -> Token(TokenType.MATCH, identifier)
            "PATH" -> Token(TokenType.PATH, identifier)
            "RETURN" -> Token(TokenType.RETURN, identifier)
            "CREATE_RELATION" -> Token(TokenType.CREATE_RELATION, identifier)
            "TO" -> Token(TokenType.TO, identifier)
            "TYPE" -> Token(TokenType.TYPE, identifier)
            "PROPERTIES" -> Token(TokenType.PROPERTIES, identifier)
            "INSERT_METRIC" -> Token(TokenType.INSERT_METRIC, identifier)
            "AGGREGATION" -> Token(TokenType.AGGREGATION, identifier)
            "GROUP_BY" -> Token(TokenType.GROUP_BY, identifier)
            "HAVING" -> Token(TokenType.HAVING, identifier)
            "JOIN" -> Token(TokenType.JOIN, identifier)
            "ON" -> Token(TokenType.ON, identifier)
            "TRANSACTION" -> Token(TokenType.TRANSACTION, identifier)
            "BEGIN" -> Token(TokenType.BEGIN, identifier)
            "COMMIT" -> Token(TokenType.COMMIT, identifier)
            "ROLLBACK" -> Token(TokenType.ROLLBACK, identifier)
            "SAVEPOINT" -> Token(TokenType.SAVEPOINT, identifier)
            else -> Token(TokenType.IDENTIFIER, identifier)
        }
    }

    private fun readNumber(): Token {
        val start = position
        while (position < input.length && input[position].isDigit()) {
            position++
        }
        if (position < input.length && input[position] == '.') {
            position++
            while (position < input.length && input[position].isDigit()) {
                position++
            }
        }
        return Token(TokenType.NUMBER, input.substring(start, position))
    }

    private fun readString(): Token {
        position++ // Skip opening quote
        val start = position
        while (position < input.length && input[position] != '\'') {
            position++
        }
        val string = input.substring(start, position)
        position++ // Skip closing quote
        return Token(TokenType.STRING, string)
    }
}
