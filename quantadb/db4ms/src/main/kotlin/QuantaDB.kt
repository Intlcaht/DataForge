
// Database configurations
    val postgreSQLConfig = PostgreSQLConfig("jdbc:postgresql://localhost:5432/mydb", "user", "password")
    val mongoDBConfig = MongoDBConfig("mongodb://localhost:27017", "mydb")
    val neo4jConfig = Neo4jConfig("bolt://localhost:7687", "neo4j", "password")
    val influxDBConfig = InfluxDBConfig("http://localhost:8086", "mytoken", "myorg", "mybucket")

    // Database connection manager
    val connectionManager = DatabaseConnectionManager()

    // Database connections
    val postgreSQLConnection = connectionManager.getPostgreSQLConnection(postgreSQLConfig)
    val mongoDBConnection = connectionManager.getMongoDBConnection(mongoDBConfig)
    val neo4jConnection = connectionManager.getNeo4jConnection(neo4jConfig)
    val influxDBConnection = connectionManager.getInfluxDBConnection(influxDBConfig)

    // Database adapters
    val postgreSQLAdapter = PostgreSQLAdapter(postgreSQLConnection)
    val mongoDBAdapter = MongoDBAdapter(mongoDBConnection)
    val neo4jAdapter = Neo4jAdapter(neo4jConnection)
    val influxDBAdapter = InfluxDBAdapter(influxDBConnection)

    // Adapters map
    val adapters = mapOf(
        "postgresql" to postgreSQLAdapter,
        "mongodb" to mongoDBAdapter,
        "neo4j" to neo4jAdapter,
        "influxdb" to influxDBAdapter
    )

fun main() {
    val query = """
        CREATE RECORD users IN BUCKET app_service (
          id SCALAR<UUID> PRIMARY KEY,
          username SCALAR<STRING> UNIQUE INDEX,
          email SCALAR<STRING> UNIQUE,
          profile DOCUMENT,
          created_at TIME DEFAULT NOW(),
          login_times METRIC<COUNT>,
          friends RELATION TO users MANY,
          manager RELATION TO users ONE
        );
    """.trimIndent()

    val lexer = Lexer(query)
    val parser = Parser(lexer)
    val ast = parser.parse()

    val callback = when (ast) {
        is CreateRecord -> CreateRecordCallback(ast, postgreSQLAdapter)
        is Insert -> InsertCallback(ast, postgreSQLAdapter)
        is Select -> SelectCallback(ast, postgreSQLAdapter)
        is Update -> UpdateCallback(ast, postgreSQLAdapter)
        is Delete -> DeleteCallback(ast, postgreSQLAdapter)
        is Traverse -> TraverseCallback(ast, neo4jAdapter)
        is Match -> MatchCallback(ast, neo4jAdapter)
        is CreateRelation -> CreateRelationCallback(ast, neo4jAdapter)
        is InsertMetric -> InsertMetricCallback(ast, influxDBAdapter)
        is Transaction -> TransactionCallback(ast, adapters)
        else -> throw IllegalStateException("Unexpected AST node: $ast")
    }

    val pipeline = Pipeline(listOf(callback))
    pipeline.execute()
}