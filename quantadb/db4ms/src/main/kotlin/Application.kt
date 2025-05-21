package com.icaht

import io.ktor.server.application.*

fun main(args: Array<String>) {
    io.ktor.server.netty.EngineMain.main(args)
}

fun Application.module() {
    configureHTTP()
    configureRouting()
}

// // File: src/main/kotlin/com/quantadb/Application.kt
// package com.quantadb

// import com.quantadb.api.configureRouting
// import com.quantadb.config.AppConfig
// import io.ktor.serialization.kotlinx.json.*
// import io.ktor.server.application.*
// import io.ktor.server.engine.*
// import io.ktor.server.netty.*
// import io.ktor.server.plugins.contentnegotiation.*
// import kotlinx.serialization.json.Json

// fun main() {
//     embeddedServer(Netty, port = AppConfig.serverPort, host = "0.0.0.0") {
//         configureServer()
//     }.start(wait = true)
// }

// fun Application.configureServer() {
//     install(ContentNegotiation) {
//         json(Json {
//             prettyPrint = true
//             isLenient = true
//         })
//     }
//     configureRouting()
// }
