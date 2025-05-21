// Updated Callbacks with Adapters
class CreateRecordCallback(private val record: CreateRecord, private val adapter: DatabaseAdapter) : Callback {
    override fun execute() {
        println("Creating record: ${record.name} in bucket: ${record.bucket}")
        record.fields.forEach { field ->
            println("Field: ${field.name}, Type: ${field.type}, Constraints: ${field.constraints}")
        }
        // Convert record to a map and use the adapter to create the record
        val data = mapOf("name" to record.name, "bucket" to record.bucket, "fields" to record.fields)
        adapter.create(record.name, data)
    }
}

class InsertCallback(private val insert: Insert, private val adapter: DatabaseAdapter) : Callback {
    override fun execute() {
        println("Inserting into: ${insert.record}")
        insert.values.forEach { (key, value) ->
            println("$key: $value")
        }
        adapter.create(insert.record, insert.values)
    }
}

class SelectCallback(private val select: Select, private val adapter: DatabaseAdapter) : Callback {
    override fun execute() {
        println("Selecting fields: ${select.fields} from: ${select.from}")
        select.where?.let { where ->
            println("Where: ${where.condition}")
        }
        val results = adapter.read(select.from, select.fields, select.where?.condition)
        println("Results: $results")
    }
}

class UpdateCallback(private val update: Update, private val adapter: DatabaseAdapter) : Callback {
    override fun execute() {
        println("Updating record: ${update.record}")
        update.set.forEach { (key, value) ->
            println("$key: $value")
        }
        update.where?.let { where ->
            println("Where: ${where.condition}")
        }
        adapter.update(update.record, update.set, update.where?.condition)
    }
}

class DeleteCallback(private val delete: Delete, private val adapter: DatabaseAdapter) : Callback {
    override fun execute() {
        println("Deleting from: ${delete.record}")
        delete.where?.let { where ->
            println("Where: ${where.condition}")
        }
        adapter.delete(delete.record, delete.where?.condition)
    }
}

class TraverseCallback(private val traverse: Traverse, private val adapter: DatabaseAdapter) : Callback {
    override fun execute() {
        println("Traversing path: ${traverse.path}")
        traverse.where?.let { where ->
            println("Where: ${where.condition}")
        }
        // Implement traversal logic using the adapter
    }
}

class MatchCallback(private val match: Match, private val adapter: DatabaseAdapter) : Callback {
    override fun execute() {
        println("Matching pattern: ${match.pattern}")
        match.where?.let { where ->
            println("Where: ${where.condition}")
        }
        // Implement matching logic using the adapter
    }
}

class CreateRelationCallback(private val relation: CreateRelation, private val adapter: DatabaseAdapter) : Callback {
    override fun execute() {
        println("Creating relation from: ${relation.from} to: ${relation.to} of type: ${relation.type}")
        relation.properties.forEach { (key, value) ->
            println("$key: $value")
        }
        // Implement relation creation logic using the adapter
    }
}

class InsertMetricCallback(private val metric: InsertMetric, private val adapter: DatabaseAdapter) : Callback {
    override fun execute() {
        println("Inserting metric into: ${metric.record}.${metric.field}")
        metric.values.forEach { (key, value) ->
            println("$key: $value")
        }
        metric.where?.let { where ->
            println("Where: ${where.condition}")
        }
        // Implement metric insertion logic using the adapter
    }
}

class TransactionCallback(private val transaction: Transaction, private val adapters: Map<String, DatabaseAdapter>) : Callback {
    override fun execute() {
        println("Executing transaction with ${transaction.operations.size} operations")
        transaction.operations.forEach { operation ->
            val adapter = when (operation) {
                is CreateRecord -> adapters["postgresql"]!!
                is Insert -> adapters["postgresql"]!!
                is Select -> adapters["postgresql"]!!
                is Update -> adapters["postgresql"]!!
                is Delete -> adapters["postgresql"]!!
                is Traverse -> adapters["neo4j"]!!
                is Match -> adapters["neo4j"]!!
                is CreateRelation -> adapters["neo4j"]!!
                is InsertMetric -> adapters["influxdb"]!!
                else -> throw IllegalStateException("Unexpected operation: $operation")
            }

            when (operation) {
                is CreateRecord -> CreateRecordCallback(operation, adapter).execute()
                is Insert -> InsertCallback(operation, adapter).execute()
                is Select -> SelectCallback(operation, adapter).execute()
                is Update -> UpdateCallback(operation, adapter).execute()
                is Delete -> DeleteCallback(operation, adapter).execute()
                is Traverse -> TraverseCallback(operation, adapter).execute()
                is Match -> MatchCallback(operation, adapter).execute()
                is CreateRelation -> CreateRelationCallback(operation, adapter).execute()
                is InsertMetric -> InsertMetricCallback(operation, adapter).execute()
                else -> throw IllegalStateException("Unexpected operation: $operation")
            }
        }
    }
}
