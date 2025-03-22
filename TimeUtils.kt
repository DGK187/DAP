package com.guardianpro.app.utils

import java.util.concurrent.TimeUnit

object TimeUtils {
    
    /**
     * Returns a human-readable string representing time passed since the given timestamp
     * Example: "5 min ago", "2 hours ago", "Yesterday", etc.
     */
    fun getTimeAgo(timestamp: Long): String {
        val now = System.currentTimeMillis()
        val diff = now - timestamp
        
        return when {
            diff < TimeUnit.MINUTES.toMillis(1) -> "Just now"
            diff < TimeUnit.HOURS.toMillis(1) -> "${TimeUnit.MILLISECONDS.toMinutes(diff)} min ago"
            diff < TimeUnit.DAYS.toMillis(1) -> "${TimeUnit.MILLISECONDS.toHours(diff)} hours ago"
            diff < TimeUnit.DAYS.toMillis(2) -> "Yesterday"
            diff < TimeUnit.DAYS.toMillis(7) -> "${TimeUnit.MILLISECONDS.toDays(diff)} days ago"
            else -> formatDate(timestamp)
        }
    }
    
    /**
     * Formats a timestamp into a readable date string
     */
    private fun formatDate(timestamp: Long): String {
        val dateFormat = java.text.SimpleDateFormat("MMM dd, yyyy", java.util.Locale.getDefault())
        return dateFormat.format(java.util.Date(timestamp))
    }
    
    /**
     * Formats duration in minutes to a readable string
     * Example: "2h 15m", "45m", etc.
     */
    fun formatDuration(minutes: Int): String {
        val hours = minutes / 60
        val mins = minutes % 60
        
        return when {
            hours > 0 && mins > 0 -> "${hours}h ${mins}m"
            hours > 0 -> "${hours}h"
            else -> "${mins}m"
        }
    }
}