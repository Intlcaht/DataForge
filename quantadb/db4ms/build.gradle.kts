
plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.ktor)
}

group = "com.icaht"
version = "0.0.1"

application {
    mainClass = "io.ktor.server.netty.EngineMain"
}

repositories {
    mavenCentral()
}

dependencies {
    implementation(libs.ktor.simple.cache)
    implementation(libs.ktor.server.core)
    implementation(libs.ktor.simple.redis.cache)
    implementation(libs.ktor.server.swagger)
    implementation(libs.ktor.server.openapi)
    implementation(libs.ktor.server.caching.headers)
    implementation(libs.ktor.server.compression)
    implementation(libs.ktor.server.cors)
    implementation(libs.ktor.server.netty)
    implementation(libs.logback.classic)
    implementation(libs.ktor.server.config.yaml)
    testImplementation(libs.ktor.server.test.host)
    testImplementation(libs.kotlin.test.junit)
}

// // File: build.gradle.kts
// plugins {
//     kotlin("jvm") version "1.9.22"
//     kotlin("plugin.serialization") version "1.9.22"
//     id("io.ktor.plugin") version "2.3.7"
//     application
// }

// group = "com.quantadb"
// version = "0.1.0"

// repositories {
//     mavenCentral()
// }

// dependencies {
//     // Ktor server
//     implementation("io.ktor:ktor-server-core:2.3.7")
//     implementation("io.ktor:ktor-server-netty:2.3.7")
//     implementation("io.ktor:ktor-server-content-negotiation:2.3.7")
//     implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")
//     implementation("io.ktor:ktor-server-auth:2.3.7")
//     implementation("io.ktor:ktor-server-auth-jwt:2.3.7")
    
//     // Database drivers
//     implementation("org.postgresql:postgresql:42.6.0")
//     implementation("org.mongodb:mongodb-driver-kotlin-coroutine:4.11.0")
//     implementation("org.neo4j.driver:neo4j-java-driver:5.14.0")
//     implementation("com.influxdb:influxdb-client-kotlin:6.10.0")
    
//     // Utilities
//     implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
//     implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
//     implementation("io.github.microutils:kotlin-logging-jvm:3.0.5")
//     implementation("ch.qos.logback:logback-classic:1.4.11")
    
//     // Testing
//     testImplementation("io.ktor:ktor-server-test-host:2.3.7")
//     testImplementation("org.jetbrains.kotlin:kotlin-test:1.9.22")
// }

// application {
//     mainClass.set("com.quantadb.ApplicationKt")
// }
