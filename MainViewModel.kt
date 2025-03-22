package com.guardianpro.app.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.guardianpro.app.data.Alert
import com.guardianpro.app.data.ChildDevice
import com.guardianpro.app.data.repository.AlertRepository
import com.guardianpro.app.data.repository.ChildRepository
import com.guardianpro.app.data.repository.PreferencesRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val preferencesRepository = PreferencesRepository(application)
    private val alertRepository = AlertRepository(application)
    private val childRepository = ChildRepository(application)

    // LiveData for alerts
    private val _alerts = MutableLiveData<List<Alert>>()
    val alerts: LiveData<List<Alert>> = _alerts

    // LiveData for child devices
    private val _childDevices = MutableLiveData<List<ChildDevice>>()
    val childDevices: LiveData<List<ChildDevice>> = _childDevices

    // App state
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private var _limitedFunctionalityMode = MutableLiveData<Boolean>()
    val limitedFunctionalityMode: LiveData<Boolean> = _limitedFunctionalityMode

    init {
        refreshData()
    }

    fun refreshData() {
        viewModelScope.launch {
            _isLoading.value = true
            
            try {
                withContext(Dispatchers.IO) {
                    // Load alerts from repository
                    val alertList = alertRepository.getActiveAlerts()
                    _alerts.postValue(alertList)
                    
                    // Load child devices
                    val deviceList = childRepository.getAllChildDevices()
                    _childDevices.postValue(deviceList)
                }
            } catch (e: Exception) {
                // Handle errors
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun isFirstRun(): Boolean {
        return preferencesRepository.isFirstRun()
    }

    fun setFirstRunCompleted() {
        preferencesRepository.setFirstRunCompleted()
    }

    fun setLimitedFunctionalityMode(limited: Boolean) {
        _limitedFunctionalityMode.value = limited
        preferencesRepository.setLimitedFunctionalityMode(limited)
    }

    fun addChildDevice(device: ChildDevice) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                childRepository.addChildDevice(device)
            }
            refreshData()
        }
    }

    fun dismissAlert(alertId: Long) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                alertRepository.dismissAlert(alertId)
            }
            refreshData()
        }
    }

    fun markAlertAsReviewed(alertId: Long) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                alertRepository.markAlertAsReviewed(alertId)
            }
            refreshData()
        }
    }
}