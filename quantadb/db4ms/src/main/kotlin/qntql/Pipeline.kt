// Pipeline
class Pipeline(private val callbacks: List<Callback>) {
    fun execute() {
        callbacks.forEach { callback ->
            callback.execute()
        }
    }
}
