package com.guardianpro.app.models

import android.net.Uri
import java.util.UUID

data class ChildDevice(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val age: Int,
    val deviceModel: String,
    val lastActiveTimestamp: Long,
    val isProtectionActive: Boolean = true,
    val hasWarnings: Boolean = false,
    val alertCount: Int = 0,
    val todayScreenTimeHours: Double = 0.0,
    val weeklyScreenTimeHours: Double = 0.0,
    val avatarUri: Uri? = null,
    val installedApps: List<AppInfo> = emptyList(),
    val restrictedApps: List<String> = emptyList(),
    val locationTrackingEnabled: Boolean = true,
    val lastKnownLocation: Location? = null,
    val screenTimeLimit: Int = 120 // in minutes
) {
    data class Location(
        val latitude: Double,
        val longitude: Double,
        val address: String?,
        val timestamp: Long
    )

    data class AppInfo(
        val packageName: String,
        val appName: String,
        val installDate: Long,
        val isSystemApp: Boolean,
        val usageTimeToday: Long // in minutes
    )
}