import unittest
from src.nearby_places_service import NearbyPlacesService, PlaceCategory, haversine_km


class TestNearbyPlacesService(unittest.TestCase):

    def test_haversine_accuracy(self):
        # Distance between Tenali (16.2400, 80.6400) and Guntur (16.3067, 80.4365) is approx 22-23 km
        d = haversine_km(16.2400, 80.6400, 16.3067, 80.4365)
        self.assertTrue(20.0 < d < 25.0)

    def test_healthcare_classification_rules(self):
        # Never classify clinic or PHC as multispeciality hospital
        phc_cat, phc_icon, phc_desc = NearbyPlacesService.classify_healthcare(
            "Kollipara Primary Health Centre (PHC)", {"amenity": "hospital"}
        )
        self.assertEqual(phc_cat, "Primary Health Centre (PHC)")
        self.assertIn("PHC", phc_cat)
        self.assertNotIn("Multispeciality", phc_cat)

        clinic_cat, clinic_icon, clinic_desc = NearbyPlacesService.classify_healthcare(
            "Sai Dental & Skin Clinic", {"amenity": "clinic"}
        )
        self.assertEqual(clinic_cat, "Local Clinic & Dispensary")
        self.assertNotIn("Multispeciality", clinic_cat)

        # Multispeciality hospital classification
        multi_cat, multi_icon, multi_desc = NearbyPlacesService.classify_healthcare(
            "Apollo Multispeciality Hospital", {"amenity": "hospital"}
        )
        self.assertEqual(multi_cat, "Multispeciality Hospital")

        # Government hospital
        govt_cat, govt_icon, govt_desc = NearbyPlacesService.classify_healthcare(
            "Government Area Hospital", {"amenity": "hospital"}
        )
        self.assertTrue("Government" in govt_cat or "General" in govt_cat)

    def test_no_fabrication_on_empty_remote(self):
        # At ocean coordinates (0, 0), zero places exist, must NOT fabricate imaginary places
        places = NearbyPlacesService.get_nearby_places(
            lat=0.0,
            lon=0.0,
            radius_km=2.0,
            category=PlaceCategory.ALL,
            location_name="Ocean"
        )
        self.assertEqual(places, [])


if __name__ == "__main__":
    unittest.main()
