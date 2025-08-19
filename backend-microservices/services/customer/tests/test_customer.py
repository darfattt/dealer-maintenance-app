"""
Basic tests for customer service
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models.customer_validation_request import CustomerValidationRequest, Base
from app.models.dealer_config import DealerConfig
from app.schemas.customer_validation_request import CustomerValidationRequestCreate
from app.repositories.customer_validation_request_repository import CustomerValidationRequestRepository
from app.repositories.dealer_config_repository import DealerConfigRepository
from app.controllers.customer_controller import CustomerController

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_customer.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_test_db():
    """Get test database session"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


@pytest.fixture
def sample_customer_request():
    """Sample customer validation request data"""
    return CustomerValidationRequestCreate(
        nama_pembawa="Adit",
        nomor_telepon_pembawa="082148523421",
        tipe_unit="BeAT Street",
        nomor_polisi="D 123 AD",
        kode_ahass="00999",
        nama_ahass="Test AHASS",
        alamat_ahass="Test Address",
        nomor_mesin="TEST123456",
        created_time="31/12/2019 15:40:50",
        modified_time="31/12/2019 15:40:50"
    )


@pytest.fixture
def mock_dealer_config():
    """Mock dealer configuration"""
    dealer = Mock(spec=DealerConfig)
    dealer.dealer_id = "0009999"
    dealer.dealer_name = "Test Dealer"
    dealer.fonnte_api_key = "test_api_key"
    dealer.fonnte_api_url = "https://api.fonnte.com/send"
    dealer.is_active = True
    dealer.has_fonnte_configuration.return_value = True
    return dealer


class TestCustomerValidationRequestRepository:
    """Test customer validation request repository"""
    
    def test_create_customer_request(self, test_db, sample_customer_request):
        """Test creating customer validation request"""
        repo = CustomerValidationRequestRepository(test_db)
        
        # Create request
        request = repo.create(sample_customer_request, dealer_id="test_dealer", created_by="test")
        
        # Verify
        assert request.id is not None
        assert request.dealer_id == "test_dealer"  # From dealer_id parameter
        assert request.nama_pembawa == sample_customer_request.nama_pembawa
        assert request.nomor_telepon_pembawa == sample_customer_request.nomor_telepon_pembawa
        assert request.request_status == "PENDING"
        assert request.whatsapp_status == "NOT_SENT"
    
    def test_get_by_id(self, test_db, sample_customer_request):
        """Test getting request by ID"""
        repo = CustomerValidationRequestRepository(test_db)
        
        # Create and retrieve
        created_request = repo.create(sample_customer_request, dealer_id="test_dealer", created_by="test")
        retrieved_request = repo.get_by_id(str(created_request.id))
        
        # Verify
        assert retrieved_request is not None
        assert retrieved_request.id == created_request.id
        assert retrieved_request.nama_pembawa == sample_customer_request.nama_pembawa
    
    def test_update_status(self, test_db, sample_customer_request):
        """Test updating request status"""
        repo = CustomerValidationRequestRepository(test_db)
        
        # Create and update
        created_request = repo.create(sample_customer_request, dealer_id="test_dealer", created_by="test")
        updated_request = repo.update_status(
            request_id=str(created_request.id),
            request_status="PROCESSED",
            whatsapp_status="SENT",
            fonnte_response={"status": "success"},
            modified_by="system"
        )
        
        # Verify
        assert updated_request is not None
        assert updated_request.request_status == "PROCESSED"
        assert updated_request.whatsapp_status == "SENT"
        assert updated_request.fonnte_response == {"status": "success"}


class TestDealerConfigRepository:
    """Test dealer config repository"""
    
    def test_validate_dealer_exists(self, test_db):
        """Test dealer validation"""
        repo = DealerConfigRepository(test_db)
        
        # Test with mock - in real implementation, you'd create test dealer data
        with patch.object(repo, 'get_by_dealer_id') as mock_get:
            mock_get.return_value = Mock()
            result = repo.validate_dealer_exists("test_dealer")
            assert result is True
            
            mock_get.return_value = None
            result = repo.validate_dealer_exists("nonexistent")
            assert result is False
    
    def test_get_fonnte_config(self, test_db, mock_dealer_config):
        """Test getting Fonnte configuration"""
        repo = DealerConfigRepository(test_db)
        
        with patch.object(repo, 'get_by_dealer_id') as mock_get:
            mock_get.return_value = mock_dealer_config
            
            config = repo.get_fonnte_config("0009999")
            
            assert config is not None
            assert config["api_key"] == "test_api_key"
            assert config["api_url"] == "https://api.fonnte.com/send"
            assert config["dealer_name"] == "Test Dealer"


class TestCustomerController:
    """Test customer controller"""
    
    @pytest.mark.asyncio
    async def test_validate_customer_success(self, test_db, sample_customer_request):
        """Test successful customer validation"""
        controller = CustomerController(test_db)
        
        # Mock dependencies
        with patch.object(controller.dealer_repo, 'validate_dealer_exists', return_value=True), \
             patch.object(controller.dealer_repo, 'validate_dealer_fonnte_config', return_value=(True, None)), \
             patch.object(controller.customer_repo, 'create') as mock_create, \
             patch.object(controller.whatsapp_service, 'send_customer_validation_message') as mock_send:
            
            # Setup mocks
            mock_request = Mock()
            mock_request.id = "test-id"
            mock_create.return_value = mock_request
            
            mock_response = Mock()
            mock_response.success = True
            mock_response.response_data = {"status": "sent"}
            mock_send.return_value = mock_response
            
            # Execute
            result = await controller.validate_customer(sample_customer_request)
            
            # Verify
            assert result.status == 1
            assert result.message["confirmation"] == "Data berhasil diproses"
    
    @pytest.mark.asyncio
    async def test_validate_customer_dealer_not_found(self, test_db, sample_customer_request):
        """Test customer validation with dealer not found"""
        controller = CustomerController(test_db)
        
        with patch.object(controller.dealer_repo, 'validate_dealer_exists', return_value=False):
            result = await controller.validate_customer(sample_customer_request)
            
            assert result.status == 0
            assert "tidak ditemukan" in result.message["error"]
    
    @pytest.mark.asyncio
    async def test_validate_customer_no_fonnte_config(self, test_db, sample_customer_request):
        """Test customer validation without Fonnte configuration"""
        controller = CustomerController(test_db)
        
        with patch.object(controller.dealer_repo, 'validate_dealer_exists', return_value=True), \
             patch.object(controller.dealer_repo, 'validate_dealer_fonnte_config', return_value=(False, "No config")):
            
            result = await controller.validate_customer(sample_customer_request)
            
            assert result.status == 0
            assert "WhatsApp tidak tersedia" in result.message["error"]


class TestCustomerAPI:
    """Test customer API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/health/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "customer-service"
    
    @patch('app.dependencies.get_db')
    def test_validate_customer_endpoint(self, mock_get_db, client, sample_customer_request):
        """Test validate customer endpoint"""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock successful validation
        with patch('app.controllers.customer_controller.CustomerController') as mock_controller_class:
            mock_controller = AsyncMock()
            mock_controller_class.return_value = mock_controller
            
            mock_response = Mock()
            mock_response.status = 1
            mock_response.message = {"confirmation": "Data berhasil diproses"}
            mock_response.data = None
            mock_controller.validate_customer.return_value = mock_response
            
            # Make request
            response = client.post(
                "/api/v1/customer/validate-customer",
                json=sample_customer_request.dict()
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == 1
            assert data["message"]["confirmation"] == "Data berhasil diproses"


class TestSchemaValidation:
    """Test Pydantic schema validation"""
    
    def test_valid_customer_request(self):
        """Test valid customer request creation"""
        data = {
            "nama_pembawa": "Adit",
            "nomor_telepon_pembawa": "082148523421",
            "tipe_unit": "BeAT Street",
            "nomor_polisi": "D 123 AD",
            "kode_ahass": "00999",
            "nama_ahass": "Test AHASS",
            "alamat_ahass": "Test Address",
            "nomor_mesin": "TEST123456",
            "created_time": "31/12/2019 15:40:50",
            "modified_time": "31/12/2019 15:40:50"
        }
        
        request = CustomerValidationRequestCreate(**data)
        assert request.nama_pembawa == "Adit"
        assert request.nomor_telepon_pembawa == "082148523421"
    
    def test_invalid_phone_number(self):
        """Test invalid phone number validation"""
        data = {
            "nama_pembawa": "Adit",
            "nomor_telepon_pembawa": "123",  # Invalid phone number
            "tipe_unit": "BeAT Street",
            "nomor_polisi": "D 123 AD",
            "kode_ahass": "00999",
            "nama_ahass": "Test AHASS",
            "alamat_ahass": "Test Address",
            "nomor_mesin": "TEST123456",
            "created_time": "31/12/2019 15:40:50",
            "modified_time": "31/12/2019 15:40:50"
        }
        
        with pytest.raises(ValueError):
            CustomerValidationRequestCreate(**data)
    
    def test_invalid_datetime_format(self):
        """Test invalid datetime format validation"""
        data = {
            "nama_pembawa": "Adit",
            "nomor_telepon_pembawa": "082148523421",
            "tipe_unit": "BeAT Street",
            "nomor_polisi": "D 123 AD",
            "kode_ahass": "00999",
            "nama_ahass": "Test AHASS",
            "alamat_ahass": "Test Address",
            "nomor_mesin": "TEST123456",
            "created_time": "invalid-date",  # Invalid format
            "modified_time": "31/12/2019 15:40:50"
        }
        
        with pytest.raises(ValueError):
            CustomerValidationRequestCreate(**data)


if __name__ == "__main__":
    pytest.main([__file__])