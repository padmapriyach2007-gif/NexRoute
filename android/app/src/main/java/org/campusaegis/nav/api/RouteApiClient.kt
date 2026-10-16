package org.campusaegis.nav.api

import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

/**
 * REST API client communicating with CampusAegis FastAPI backend.
 */
class RouteApiClient(private val baseUrl: String = "http://10.0.2.2:8000") {

    fun calculateRoutes(
        originLat: Double, originLon: Double,
        destLat: Double, destLon: Double,
        mode: String = "driving",
        onSuccess: (JSONObject) -> Unit,
        onError: (Exception) -> Unit
    ) {
        Thread {
            try {
                val url = URL("$baseUrl/api/route")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.doOutput = true

                val payload = JSONObject().apply {
                    put("origin_lat", originLat)
                    put("origin_lon", originLon)
                    put("dest_lat", destLat)
                    put("dest_lon", destLon)
                    put("mode", mode)
                    put("require_accessible", false)
                }

                OutputStreamWriter(conn.outputStream).use { it.write(payload.toString()) }

                val responseCode = conn.responseCode
                if (responseCode == 200) {
                    val stream = conn.inputStream.bufferedReader().use { it.readText() }
                    onSuccess(JSONObject(stream))
                } else {
                    onError(Exception("Server returned HTTP $responseCode"))
                }
            } catch (e: Exception) {
                onError(e)
            }
        }.start()
    }
}
