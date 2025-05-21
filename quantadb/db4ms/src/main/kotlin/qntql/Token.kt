sealed interface Token {
    val value: String
}

object EOF : Token {
    override val value = "<EOF>"
}

data class Keyword(override val value: String) : Token
data class Identifier(override val value: String) : Token
data class StringLiteral(override val value: String) : Token
data class NumberLiteral(override val value: String) : Token
data class Symbol(override val value: String) : Token
data class Operator(override val value: String) : Token