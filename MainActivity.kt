package com.guardianpro.app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.guardianpro.app.databinding.ActivityMainBinding
import com.guardianpro.app.fragments.AlertsFragment
import com.guardianpro.app.fragments.DashboardFragment
import com.guardianpro.app.fragments.ReportsFragment
import com.guardianpro.app.fragments.SettingsFragment
import com.guardianpro.app.service.MonitoringService
import com.guardianpro.app.viewmodel.MainViewModel

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MainViewModel
    
    private val REQUIRED_PERMISSIONS = arrayOf(
        Manifest.permission.READ_EXTERNAL_STORAGE,
        Manifest.permission.READ_CONTACTS,
        Manifest.permission.ACCESS_NOTIFICATION_POLICY
    )
    
    // Add these permissions for Android 10+ (API 29+)
    private val ANDROID_10_PERMISSIONS = arrayOf(
        Manifest.permission.ACCESS_MEDIA_LOCATION
    )
    
    // Add these permissions for Android 11+ (API 30+)
    private val ANDROID_11_PERMISSIONS = arrayOf(
        Manifest.permission.QUERY_ALL_PACKAGES
    )
    
    private val PERMISSION_REQUEST_CODE = 123

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize View Binding
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Set up the toolbar
        setSupportActionBar(binding.toolbar)
        
        // Initialize ViewModel
        viewModel = ViewModelProvider(this).get(MainViewModel::class.java)
        
        // Set up bottom navigation
        setupBottomNavigation()
        
        // Check if this is first run
        if (viewModel.isFirstRun()) {
            // Show onboarding screens
            startActivity(Intent(this, OnboardingActivity::class.java))
            finish()
            return
        }
        
        // Check and request permissions
        if (!allPermissionsGranted()) {
            requestPermissions()
        } else {
            startMonitoringService()
        }
        
        // Observe alerts from ViewModel
        viewModel.alerts.observe(this) { alerts ->
            // Update UI with alert count
            binding.toolbar.subtitle = if (alerts.isNotEmpty()) {
                "${alerts.size} active alerts"
            } else {
                "All systems normal"
            }
        }
        
        // Set default fragment
        loadFragment(DashboardFragment())
    }
    
    private fun setupBottomNavigation() {
        binding.bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.navigation_dashboard -> loadFragment(DashboardFragment())
                R.id.navigation_alerts -> loadFragment(AlertsFragment())
                R.id.navigation_reports -> loadFragment(ReportsFragment())
                R.id.navigation_settings -> loadFragment(SettingsFragment())
                else -> false
            }
        }
    }
    
    private fun loadFragment(fragment: Fragment): Boolean {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragmentContainer, fragment)
            .commit()
        return true
    }
    
    private fun allPermissionsGranted(): Boolean {
        val requiredPermissions = REQUIRED_PERMISSIONS.toMutableList()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            requiredPermissions.addAll(ANDROID_10_PERMISSIONS)
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            requiredPermissions.addAll(ANDROID_11_PERMISSIONS)
        }
        
        return requiredPermissions.all {
            ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    private fun requestPermissions() {
        val permissionsToRequest = mutableListOf<String>()
        
        REQUIRED_PERMISSIONS.forEach {
            if (ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED) {
                permissionsToRequest.add(it)
            }
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ANDROID_10_PERMISSIONS.forEach {
                if (ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED) {
                    permissionsToRequest.add(it)
                }
            }
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            ANDROID_11_PERMISSIONS.forEach {
                if (ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED) {
                    permissionsToRequest.add(it)
                }
            }
        }
        
        if (permissionsToRequest.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                this,
                permissionsToRequest.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        }
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.isNotEmpty() && grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
                // All permissions granted
                startMonitoringService()
            } else {
                // Permission denied
                Toast.makeText(
                    this,
                    "Guardian Pro requires these permissions to protect your child",
                    Toast.LENGTH_LONG
                ).show()
                
                // Show limited functionality or guide user to settings
                viewModel.setLimitedFunctionalityMode(true)
            }
        }
    }
    
    private fun startMonitoringService() {
        val serviceIntent = Intent(this, MonitoringService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
    }
    
    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }
    
    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_refresh -> {
                viewModel.refreshData()
                true
            }
            R.id.action_help -> {
                startActivity(Intent(this, HelpActivity::class.java))
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Don't stop the monitoring service when the app is closed
        // The service should continue running in the background
    }
}