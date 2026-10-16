package org.campusaegis.nav

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import org.campusaegis.nav.api.RouteApiClient

/**
 * MainActivity for CampusAegis Android Navigation.
 * Provides real-time emergency map, GPS tracking, and route recalculation without chatbot interaction.
 */
class MainActivity : AppCompatActivity() {

    private val LOCATION_PERMISSION_REQ_CODE = 1001
    private val apiClient = RouteApiClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        checkAndRequestLocationPermissions()
        setupJourneyControls()
    }

    private fun checkAndRequestLocationPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION),
                LOCATION_PERMISSION_REQ_CODE
            )
        } else {
            // Permission granted; start GPS provider
            enableGpsTracking()
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == LOCATION_PERMISSION_REQ_CODE) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                enableGpsTracking()
            } else {
                Toast.makeText(
                    this,
                    "Location permission denied. You can still select origin manually on the map.",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }

    private fun enableGpsTracking() {
        // Initializes LocationClient
    }

    private fun setupJourneyControls() {
        // Bind UI buttons: Start Journey, Recalculate, Report Hazard
    }
}
