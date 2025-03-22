package com.guardianpro.app.models

import java.util.UUID

data class Alert(
    val id: String = UUID.randomUUID().toString(),
    val childId: String,
    val childName: String,
    val deviceId: String,
    val deviceModel: String,
    val type: Type,
    val title: String,
    val details: String,
    val timestamp: Long,
    val priority: AlertPriority,
    val isRead: Boolean = false,
    val metadata: Map<String, String> = emptyMap()
) {
    enum class Type {
        APP_INSTALLATION,
        LOCATION,
        SCREEN_TIME,
        RESTRICTED_CONTENT,
        DEVICE_USAGE,
        UNKNOWN
    }
}

enum class AlertPriority {
    LOW,
    MEDIUM,
    HIGH
}