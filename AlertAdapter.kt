package com.guardianpro.app.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.guardianpro.app.R
import com.guardianpro.app.databinding.ItemAlertBinding
import com.guardianpro.app.models.Alert
import com.guardianpro.app.models.AlertPriority
import com.guardianpro.app.utils.TimeUtils

class AlertAdapter(
    private val onDismissClick: (Alert) -> Unit,
    private val onActionClick: (Alert) -> Unit
) : ListAdapter<Alert, AlertAdapter.AlertViewHolder>(AlertDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AlertViewHolder {
        val binding = ItemAlertBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return AlertViewHolder(binding)
    }

    override fun onBindViewHolder(holder: AlertViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class AlertViewHolder(
        private val binding: ItemAlertBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        init {
            binding.buttonDismiss.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onDismissClick(getItem(position))
                }
            }

            binding.buttonAction.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onActionClick(getItem(position))
                }
            }
        }

        fun bind(alert: Alert) {
            val context = binding.root.context
            
            binding.apply {
                alertTitle.text = alert.title
                childNameDevice.text = "${alert.childName} • ${alert.deviceModel}"
                alertTime.text = TimeUtils.getTimeAgo(alert.timestamp)
                alertDetails.text = alert.details

                // Set priority indicator color
                val priorityColor = when(alert.priority) {
                    AlertPriority.HIGH -> R.color.priority_high
                    AlertPriority.MEDIUM -> R.color.priority_medium
                    AlertPriority.LOW -> R.color.priority_low
                }
                priorityIndicator.setBackgroundColor(ContextCompat.getColor(context, priorityColor))
                
                // Set alert icon based on type
                val iconResource = when (alert.type) {
                    Alert.Type.APP_INSTALLATION -> R.drawable.ic_app_installation
                    Alert.Type.LOCATION -> R.drawable.ic_location
                    Alert.Type.SCREEN_TIME -> R.drawable.ic_screen_time
                    Alert.Type.RESTRICTED_CONTENT -> R.drawable.ic_content_warning
                    Alert.Type.DEVICE_USAGE -> R.drawable.ic_device_usage
                    else -> R.drawable.ic_warning
                }
                alertIcon.setImageResource(iconResource)
                
                // Customize action button based on alert type
                when (alert.type) {
                    Alert.Type.APP_INSTALLATION -> buttonAction.text = "Block App"
                    Alert.Type.LOCATION -> buttonAction.text = "View Location"
                    Alert.Type.SCREEN_TIME -> buttonAction.text = "Limit Screen Time"
                    Alert.Type.RESTRICTED_CONTENT -> buttonAction.text = "Review Content"
                    Alert.Type.DEVICE_USAGE -> buttonAction.text = "View Details"
                    else -> buttonAction.text = "Take Action"
                }
            }
        }
    }

    class AlertDiffCallback : DiffUtil.ItemCallback<Alert>() {
        override fun areItemsTheSame(oldItem: Alert, newItem: Alert): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Alert, newItem: Alert): Boolean {
            return oldItem == newItem
        }
    }
}