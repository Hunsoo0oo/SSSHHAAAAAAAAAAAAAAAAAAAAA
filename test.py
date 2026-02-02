# -*- coding: utf-8 -*-
import unittest, requests, time, hashlib, json
BASE_URL = "http://127.0.0.1:8000"
class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.login = f"testuser_{int(time.time())}"
        cls.password = "Password123!"
        cls.email = "test@mail.com"
        cls.token = None

    def get_hashtoken(self, body=None):
        if self.token is None: return ""
        tt = str(int(time.time()))
        body_json = json.dumps(body, separators=(",", ":"), sort_keys=True)
        data = self.token + body_json + tt
        return hashlib.sha256(data.encode()).hexdigest()

    def test_1_register(self):
        payload = {"login": self.login, "email": self.email, "password": self.password}
        response = requests.post(f"{BASE_URL}/users/", json=payload)
        self.assertEqual(response.status_code, 200)
        print("\n[OK] Registration successful")

    def test_2_auth(self):
        payload = {"login": self.login, "password": self.password}
        response = requests.post(f"{BASE_URL}/users/auth", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.__class__.token = data["Token"]
        self.assertIn("Token", data)
        print("[OK] Auth successful")

    def test_3_atbash(self):
        body = {"text": "abc"}
        headers = {'Authorization': self.get_hashtoken(body)}
        response = requests.post(f"{BASE_URL}/atbash", json=body, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], "zyx")
        print("[OK] Atbash algorithm works")

    def test_4_change_password(self):
        new_pass = "NewStrongPass123!"
        body = {"new_password": new_pass}
        headers = {'Authorization': self.get_hashtoken(body)}
        response = requests.patch(f"{BASE_URL}/users/password", json=body, headers=headers)
        self.assertEqual(response.status_code, 200)
        print("[OK] Password change successful")

if __name__ == "__main__":
    unittest.main()