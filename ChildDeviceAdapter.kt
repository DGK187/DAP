package com.guardianpro.app.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.guardianpro.app.R
import com.guardianpro.app.databinding.ItemChildDeviceBinding
import com.guardianpro.app.models.ChildDevice
import com.guardianpro.app.utils.TimeUtils

class ChildDeviceAdapter(
    private val onItemClick: (ChildDevice) -> Unit,
    private val onMoreOptionsClick: (ChildDevice, View) -> Unit,
    private val onAlertsClick: (ChildDevice) -> Unit
) : ListAdapter<ChildDevice, ChildDeviceAdapter.ChildDeviceViewHolder>(ChildDeviceDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ChildDeviceViewHolder {
        val binding = ItemChildDeviceBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ChildDeviceViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ChildDeviceViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class ChildDeviceViewHolder(
        private val binding: ItemChildDeviceBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        init {
            binding.root.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onItemClick(getItem(position))
                }
            }

            binding.buttonMore.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onMoreOptionsClick(getItem(position), it)
                }
            }

            binding.chipAlerts.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onAlertsClick(getItem(position))
                }
            }
        }

        fun bind(childDevice: ChildDevice) {
            binding.apply {
                childName.text = childDevice.name
                deviceInfo.text = childDevice.deviceModel
                lastActivity.text = "Last active: ${TimeUtils.getTimeAgo(childDevice.lastActiveTimestamp)}"

                // Set status indicator color based on protection status
                val statusDrawable = when {
                    childDevice.isProtectionActive -> R.drawable.status_circle_protected
                    childDevice.hasWarnings -> R.drawable.status_circle_warning
                    else -> R.drawable.status_circle_alert
                }
                statusIndicator.setBackgroundResource(statusDrawable)

                // Configure alert chip
                val alertCount = childDevice.alertCount
                if (alertCount > 0) {
                    chipAlerts.visibility = View.VISIBLE
                    chipAlerts.text = "$alertCount ${if (alertCount == 1) "alert" else "alerts"}"
                } else {
                    chipAlerts.visibility = View.GONE
                }

                // Configure screen time chip
                val screenTimeHours = childDevice.todayScreenTimeHours
                chipScreenTime.text = "${String.format("%.1f", screenTimeHours)}h today"

                // Set avatar if available
                childDevice.avatarUri?.let {
                    // You could use Glide or another image loading library here
                    // Example: Glide.with(avatarImage).load(it).circleCrop().into(avatarImage)
                }
            }
        }
    }

    class ChildDeviceDiffCallback : DiffUtil.ItemCallback<ChildDevice>() {
        override fun areItemsTheSame(oldItem: ChildDevice, newItem: ChildDevice): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: ChildDevice, newItem: ChildDevice): Boolean {
            return oldItem == newItem
        }
    }
}