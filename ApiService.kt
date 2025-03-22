// ApiService.kt
package com.yourname.guardianpro.api

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

data class MonitoringData(
    // Define the data you'll send to the server
    val messages: List<String>,
    val contacts: List<String>,
    val appUsage: Map<String, Long>,
    val deviceId: String
)

data class AnalysisResult(
    // Define the response from the server
    val riskLevel: Int,
    val concerns: List<String>,
    val recommendations: List<String>
)

data class Alert(
    val id: String,
    val timestamp: Long,
    val severity: String,
    val message: String,
    val details: String
)

interface ApiService {
    @POST("api/analyze")
    fun analyzeData(@Body data: MonitoringData): Call<AnalysisResult>
    
    @GET("api/alerts")
    fun getAlerts(@Query("user_id") userId: String): Call<List<Alert>>
}