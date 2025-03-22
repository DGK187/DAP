package com.guardianpro.app.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.guardianpro.app.adapters.AlertAdapter
import com.guardianpro.app.adapters.ChildDeviceAdapter
import com.guardianpro.app.databinding.FragmentDashboardBinding
import com.guardianpro.app.viewmodel.MainViewModel

class DashboardFragment : Fragment() {

    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!
    
    private lateinit var viewModel: MainViewModel
    private lateinit var alertAdapter: AlertAdapter
    private lateinit var deviceAdapter: ChildDeviceAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // Get the shared ViewModel
        viewModel = ViewModelProvider(requireActivity()).get(MainViewModel::class.java)
        
        // Set up the alerts RecyclerView
        setupAlertsRecyclerView()
        
        // Set up the devices RecyclerView
        setupDevicesRecyclerView()
        
        // Set up swipe refresh
        binding.swipeRefreshLayout.setOnRefreshListener {
            viewModel.refreshData()
        }
        
        // Observe loading state
        viewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            binding.swipeRefreshLayout.isRefreshing = isLoading
        }
        
        // Observe alerts
        viewModel.alerts.observe(viewLifecycleOwner) { alerts ->
            alertAdapter.submitList(alerts)
            
            if (alerts.isEmpty()) {
                binding.alertsCard.visibility = View.GONE
                binding.noAlertsMessage.visibility = View.VISIBLE
            } else {
                binding.alertsCard.visibility = View.VISIBLE
                binding.noAlertsMessage.visibility = View.GONE
                
                // Update alert count
                binding.alertsTitle.text = "Active Alerts (${alerts.size})"
            }
        }
        
        // Observe child devices
        viewModel.childDevices.observe(viewLifecycleOwner) { devices ->
            deviceAdapter.submitList(devices)
            
            if (devices.isEmpty()) {
                binding.devicesCard.visibility = View.GONE
                binding.noDevicesMessage.visibility = View.VISIBLE
            } else {
                binding.devicesCard.visibility = View.VISIBLE
                binding.noDevicesMessage.visibility = View.GONE
                
                // Update device stats
                val onlineCount = devices.count { it.isOnline }
                binding.deviceStats.text = "$onlineCount of ${devices.size} devices online"
            }
        }
        
        // Set up add device button
        binding.addDeviceButton.setOnClickListener {
            // Navigate to add device screen
            // For now, just show a temporary message
            binding.noDevicesMessage.text = "Add device functionality coming soon"
        }
        
        // Set up view all alerts button
        binding.viewAllAlertsButton.setOnClickListener {
            // Navigate to alerts tab
            (requireActivity() as MainActivity).navigateToAlerts()
        }
    }
    
    private fun setupAlertsRecyclerView() {
        alertAdapter = AlertAdapter(
            onDismissClick = { alertId ->
                viewModel.dismissAlert(alertId)
            },
            onReviewClick = { alertId ->
                viewModel.markAlertAsReviewed(alertId)
            }
        )
        
        binding.alertsRecyclerView.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = alertAdapter
        }
    }
    
    private fun setupDevicesRecyclerView() {
        deviceAdapter = ChildDeviceAdapter(
            onDeviceClick = { deviceId ->
                // Navigate to device detail
            }
        )
        
        binding.devicesRecyclerView.apply {
            layoutManager = LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)
            adapter = deviceAdapter
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}