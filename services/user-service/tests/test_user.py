
def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/users/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "password" not in data
    assert "password_hash" not in data

def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username fails"""
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",  # Already exists
            "email": "another@example.com",
            "password": "password123",
            "first_name": "Another",
            "last_name": "User"
        }
    )
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]

def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/users/login",
        json={
            "username_or_email": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Test login with wrong password fails"""
    response = client.post(
        "/users/login",
        json={
            "username_or_email": "testuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_get_current_user(client, test_user):
    """Test getting current user profile with JWT token"""
    # Login to get token
    login_response = client.post(
        "/users/login",
        json={"username_or_email": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Get profile with token
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_get_current_user_without_token(client):
    """Test accessing protected route without token fails"""
    response = client.get("/users/me")
    assert response.status_code == 403

def test_update_profile(client, test_user):
    """Test updating user profile"""
    # Login to get token
    login_response = client.post(
        "/users/login",
        json={"username_or_email": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Update profile
    response = client.put(
        "/users/me",
        json={"first_name": "Updated", "last_name": "Name"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"

def test_change_password(client, test_user):
    """Test changing password"""
    # Login to get token
    login_response = client.post(
        "/users/login",
        json={"username_or_email": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Change password
    response = client.post(
        "/users/change-password",
        json={"old_password": "password123", "new_password": "newpassword123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Verify old password doesn't work
    old_login = client.post(
        "/users/login",
        json={"username_or_email": "testuser", "password": "password123"}
    )
    assert old_login.status_code == 401
    
    # Verify new password works
    new_login = client.post(
        "/users/login",
        json={"username_or_email": "testuser", "password": "newpassword123"}
    )
    assert new_login.status_code == 200

def test_delete_account(client, test_user):
    """Test account deletion"""
    # Login to get token
    login_response = client.post(
        "/users/login",
        json={"username_or_email": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Delete account
    response = client.request(
        "DELETE",
        "/users/me",
        json={"password": "password123", "confirm": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Account deactivated successfully" in response.json()["message"]