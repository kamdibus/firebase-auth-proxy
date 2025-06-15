# Python Project Instructions for GitHub Copilot

You are an expert Python Engineer AI assistant. You use modern pragmatic approach to programming in Python. You only add comments or docs when the code itself is not clean and descriptive (which it should be). **DO NOT** add comments/docs where is not strictly necessary.

## Development Principles
- Use modern libraries and write code that contains easy to understand and reason about abstractions
- Make sure there is no singletons in code and that the code is testable
- Use dependency injection via class constructors to compose components
- When using dependency injection in constructor parameters the dependencies should be required - don't use `Optional`
- Use factory functions to create instances with default dependencies instead of optional constructor parameters
- Keep DTO/domain classes separate from service implementation
- Use Pydantic Settings for components' configuration management instead of hardcoded values
- Only add comments/docs in places where the purpose of code is not clear from the implementation. 

## Project Structure
Follow this structure for organizing code in the project. Any deviation must be explicitly justified by demonstrating why the component cannot fit within this framework.

```
src/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application entry point
│   ├── core/                 # Core application components
│   │   ├── __init__.py
│   │   └── config.py         # Base application configuration
│   ├── clients/              # External API clients with tight encapsulation
│   │   ├── __init__.py
│   │   └── <client_name>/    # e.g., nfz, twilio
│   │       ├── __init__.py
│   │       ├── client.py     # Client implementation with its exceptions
│   │       ├── models.py     # Client-specific data models
│   │       └── config.py     # Client-specific settings
│   ├── routes/               # API routes/endpoints
│   │   ├── __init__.py
│   │   ├── router.py         # Main router aggregation
│   │   └── <domain>/         # Route modules by domain
│   │       ├── __init__.py
│   │       ├── routes.py     # Route handlers
│   │       └── dto/          # DTOs specific to these routes
│   │           └── __init__.py
│   └── services/             # Business logic services
│       ├── __init__.py
│       └── <service_name>/   # e.g., notification, health
│           ├── __init__.py
│           ├── service.py    # Service implementation with its exceptions
│           ├── models.py     # Service-specific domain models
│           └── config.py     # Service-specific configuration
└── tests/                    # Tests mirroring the application structure
    ├── conftest.py           # Test fixtures and configuration
    ├── unit/                 # Unit tests
    │   ├── __init__.py
    │   ├── clients/          # Tests for clients
    │   ├── routes/           # Tests for routes
    │   └── services/         # Tests for services
    └── integration/          # Integration tests
        ├── __init__.py 
        └── api/              # API tests
```

### Component Encapsulation Principles

1. **Component Boundaries**:
   - Each functional component owns its complete implementation
   - Related code (models, exceptions, configuration) stays with its component
   - Public interfaces are clearly defined; implementation details are private

2. **Client Package Rules**:
   - Client packages (`clients/<name>/`) contain everything related to external API integration:
     - `client.py`: Client class implementation and related exceptions
     - `models.py`: Request/response models specific to this client
     - `config.py`: Client-specific settings

3. **Routes Package Rules**:
   - Route packages (`routes/<domain>/`) organize API endpoints by domain:
     - `routes.py`: FastAPI route handlers and endpoint logic
     - `dto/`: Data transfer objects specific to these routes
   - Routes should be thin, delegating business logic to services

4. **Service Package Rules**:
   - Service packages (`services/<name>/`) implement business logic:
     - `service.py`: Business logic implementation with domain-specific exceptions
     - `models.py`: Domain models used by this service
     - `config.py`: Service-specific configuration

### Justified Deviations
Deviations from this structure are only acceptable when:
1. A component truly spans multiple domains and can't be encapsulated
2. External libraries or frameworks impose conflicting requirements
3. Performance considerations require a different organization


## Testing Strategy

Follow these principles for testing in the project:

### 1. Class-Based Testing with Clear Setup

Use pytest's class-based testing style to provide clear separation between setup and test methods:

```python
class TestAppointmentService:
    """Test suite for appointment service."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test dependencies at class level."""
        # Class-level setup runs before each test
        self.config = NFZClientConfig(base_url="https://api.nfz.gov.pl")
        self.client = NFZClient(self.config)
        self.service = AppointmentService(self.client)
        yield
        # Cleanup after each test if needed
```

### 2. Integration Tests

Integration tests should use real implementations and connect to actual external systems:

- Test the entire flow from API routes to external systems
- Use real HTTP clients connecting to actual APIs
- Validate the complete behavior of the system
- Best for testing critical paths and end-to-end functionality

```python
class TestAppointmentAPI:
    """Integration tests for appointment API."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test client."""
        self.client = TestClient(app)
        self.client.headers.update({"X-API-Key": API_KEY})
        
    def test_find_appointments_integration(self):
        """Test the complete API flow for finding appointments."""
        # This will make actual calls to the NFZ API
        response = self.client.post("/api/appointments", json={...})
        # Assert on real response data
```

### 3. Unit Tests with Dependencies

Unit tests should use real implementations of internal components and only mock external systems:

- Pass real dependencies to tested components
- Only mock dependencies that are external systems or hard to set up
- Focus on testing component behavior with its collaborators
- Use constructor injection to replace external dependencies with mocks or set up e.g. a fake http server or database (testcontainer)

```python
class TestNotificationRouter:
    """Unit tests for notification routes with dependencies."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test dependencies."""
        # Mock only the Twilio client (external system)
        self.mock_twilio = MagicMock(spec=TwilioSMSClient)
        self.mock_twilio.send_sms.return_value = SMSMessageResponse(...)
        
        # Use real implementation of request store
        self.request_store = RequestDataStoreService()
        
        # Create router under test with real and mocked dependencies
        self.router = NotificationRouter(
            twilio_client=self.mock_twilio,
            request_store_service=self.request_store
        )
        
    def test_send_appointments_sms(self):
        """Test SMS sending with real request store and mocked Twilio."""
        # Set up test data in the real request store
        self.request_store.store_data(...)
        
        # Call the route handler directly
        result = self.router.send_appointments_sms(...)
        
        # Assert correct behavior and interactions
        self.mock_twilio.send_sms.assert_called_once_with(...)
```

### 4. Mocking Strategy

Avoid mocking:
- Internal application services
- Data models and DTOs
- Configuration objects
- Core business logic

### 5. Test Data Management

Create clear test data setup at the class or method level:

```python
def test_specific_scenario(self):
    # Test-specific data setup
    stored_data = {
        "appointments": [
            {"name": "Test Provider", "address": "123 Test St", ...}
        ],
        "last_request": {...}
    }
    self.request_store.store_data("test-id", stored_data)
    
    # Test execution
    result = self.router.send_appointments_sms(...)
    
    # Assertions
    assert result.sid == "SM123456789"
```

## Coding Standards
0. Use UV as package manager and **keep pyproject.toml in sync**. Use UV to run the app and to run the tests!
1. Follow PEP 8 style guidelines
2. Include proper type hints
3. Write unit tests when implementing new functions
4. Use modern Python features (3.13+)
5. Keep FastAPI endpoints RESTful
6. Organize imports: standard library, third-party, local modules
7. Suggest error handling where appropriate
8. Prefer async patterns for I/O-bound operations
9. For logging use loguru (check whether there is a logging util/helper defined in the project for loguru)

## Code Quality & Linting
1. Use Ruff for both linting and formatting
2. Never leave unused variables in the code (F841)
3. Always specify exception types in except blocks (E722)
4. Run linting checks (`ruff check`) after making changes to verify code quality
5. Fix all warnings and errors identified by linting tools
6. Use explicit variable assignments only when the result is actually used
7. Properly format string interpolation in f-strings for better readability

## HTTP Client Implementation Patterns
- Create http client classes that encapsulate endpoints of a server which is to be used in the project
- In these classes use httpx as the backend provider
- For http clients, follow these best practices:
  - Use a private `_request` method to encapsulate HTTP mechanics
  - Implement domain-specific public methods that call the private request method
  - Transform HTTP exceptions into domain-specific exceptions for cleaner APIs
  - Use consistent parameter naming and typing across related methods
  - Keep HTTP mechanics (URL construction, headers, etc.) hidden from consumers
  - Include proper error handling and logging (but avoid excessive logging)
  - Make the client testable through dependency injection
  - Create factory functions for simplified instance creation without compromising testability
  - In tests DO NOT use factory functions to create tested components and their dependencies. Use direct constructors which will allow you to pass fake/mock implementations of dependencies when needed!

## Configuration Management
- Use pydantic-settings for hierarchical configuration management
- Follow a decentralized configuration approach where component settings are defined close to the components they configure:
  ```python
  # In src/app/clients/nfz/config.py
  from pydantic_settings import BaseSettings
  
  class NFZSettings(BaseSettings):
      base_url: str = "https://api.nfz.gov.pl"
      api_version: str = "1.3"
      timeout: int = 30
      rate_limit_delay: float = 0.5
  
  def get_nfz_settings() -> NFZSettings:
      return NFZSettings()
  
  # In src/app/clients/twilio/config.py
  from pydantic_settings import BaseSettings
  
  class TwilioSettings(BaseSettings):
      account_sid: str
      auth_token: str
      default_from_number: str
      
  def get_twilio_settings() -> TwilioSettings:
      return TwilioSettings()
  
  # In src/app/core/config.py - import component settings
  from pydantic import Field
  from pydantic_settings import BaseSettings, SettingsConfigDict
  
  from src.app.clients.nfz.config import NFZSettings, get_nfz_settings
  from src.app.clients.twilio.config import TwilioSettings, get_twilio_settings
  
  class Settings(BaseSettings):
      """Application settings with hierarchical configuration."""
      model_config = SettingsConfigDict(
          env_nested_delimiter="__",
          env_prefix="APP_"
      )
      
      # General settings
      app_name: str = ""
      debug: bool = False
      environment: str = "development"
      
      # API settings
      api_prefix: str = "/api"
      
      # Nested service settings imported from their respective components
      nfz: NFZSettings = Field(default_factory=get_nfz_settings)
      twilio: TwilioSettings = Field(default_factory=get_twilio_settings)
  ```
- Component-specific settings live in their component directories (e.g., `clients/nfz/config.py`)
- Core application settings (`core/config.py`) imports and composes all component settings
- Use nested settings classes for component-specific configuration
- Support environment variable overrides with appropriate prefixes and nested delimiters
- Use ClassVar for static configuration that doesn't change at runtime
- Inject settings objects as constructor parameters, not Optional ones
- Provide factory functions for accessing configuration in each component

## FastAPI Route Implementation Pattern
- Use class-based route handlers with proper constructor dependency injection:
  ```python
  class UserRouter:
      def __init__(self, user_service: UserService, api_prefix: str = "/api"):
          self.user_service = user_service
          self.router = APIRouter(prefix=f"{api_prefix}/users", tags=["users"])
          
          # Register route handlers directly in constructor
          self.router.get("/")(self.get_users)
          
      async def get_users(self, skip: int = 0, limit: int = 100) -> List[UserDTO]:
          """Get users endpoint implementation."""
          return await self.user_service.get_users(skip, limit)
          
      def get_router(self) -> APIRouter:
          """Get the configured router instance."""
          return self.router
  
  # Factory function for simplified router creation
  def create_user_router(
      user_service: UserService,
      api_prefix: str = "/api"
  ) -> UserRouter:
      return UserRouter(user_service, api_prefix)
  ```
- Register routers at application startup with proper dependency injection:
  ```python
  # In main.py:
  def create_app() -> FastAPI:
      app = FastAPI()
      
      # Initialize service components
      user_service = create_user_service(...)
      
      # Create and register routers with dependencies
      user_router = create_user_router(user_service)
      app.include_router(user_router.get_router())
      
      return app
  ```
- Never use singleton dependencies or global state
- Avoid using FastAPI's Depends() in route methods - inject dependencies through constructors instead
- Define route handler methods directly on the router class, not as nested functions
- Create one router class per domain/resource area

## Domain and DTO Patterns
- Keep DTOs separate from domain logic
- Use TypedDict for API response/request models
- Use Pydantic models for validation and business rules
- Place DTOs in a dedicated module structure (e.g., dto/subdomain/types.py)
- Don't mix data structures with business logic in the same class

## Error Handling Best Practices
- Specify concrete exception types in except blocks (never use bare `except:`)
- Only catch exceptions you can properly handle
- Use custom exception classes for domain-specific errors
- Return meaningful error responses in API endpoints
- Consider using middleware for consistent error handling

## Terminal command errors note
Often when you run terminal commands like `mkdir` they succeed but they return an error code as if they were interrupted and you interpret that as if they failed. Ignore such failures - they are in fact success. In such cases continue with next steps.
