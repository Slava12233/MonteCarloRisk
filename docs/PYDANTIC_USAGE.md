# Pydantic Usage Guidelines

## Current State Analysis

After reviewing the codebase, we've identified inconsistent usage of Pydantic in our agent classes. This document outlines the current state and proposes a standardized approach for future development.

### Current Implementation

#### BaseAgent Class

```python
class BaseAgent(ADKBaseAgent):
    # Define model_config for Pydantic
    model_config = {"arbitrary_types_allowed": True}

    # These are instance attributes, not Pydantic fields
    # They will be set in __init__ but not validated by Pydantic
    def __init__(
        self,
        name: str,
        model: str = DEFAULT_MODEL,
        description: str = "",
        instruction: str = "",
        tools: Optional[List[Any]] = None,
        sub_agents: Optional[List[Any]] = None,
        session_service: Optional[Any] = None,
        app_name: Optional[str] = None,
        **kwargs,
    ):
        # Initialize the parent class first
        super().__init__(
            name=name,
            description=description,
            sub_agents=sub_agents or [],
            **kwargs,
        )
        
        # Store parameters as instance attributes (not Pydantic fields)
        self._model = model
        self._instruction = instruction
        self._tools = tools or []
        self._app_name = app_name or name
        
        # ...
```

### Observations

1. Both classes define `model_config = {"arbitrary_types_allowed": True}` to allow non-Pydantic types.
2. Neither class defines Pydantic fields directly. Instead, they use regular instance attributes set in `__init__`.
3. The parent ADK `BaseAgent` class likely uses Pydantic for validation, but our extensions don't fully leverage Pydantic's validation capabilities.
4. Type hints are used consistently, which is good for IDE support and documentation.

## Proposed Standardized Approach

We propose the following standardized approach for Pydantic usage in our agent classes:

### Option 1: Full Pydantic Model Approach

```python
class BaseAgent(ADKBaseAgent):
    # Define Pydantic fields with type annotations
    model: str
    instruction: str
    tools: List[Any] = Field(default_factory=list)
    app_name: Optional[str] = None
    
    # Define model_config for Pydantic
    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow",  # Allow extra attributes not defined as fields
    }

    def __init__(
        self,
        name: str,
        model: str = DEFAULT_MODEL,
        description: str = "",
        instruction: str = "",
        tools: Optional[List[Any]] = None,
        sub_agents: Optional[List[Any]] = None,
        session_service: Optional[Any] = None,
        app_name: Optional[str] = None,
        **kwargs,
    ):
        # Initialize the parent class first
        super().__init__(
            name=name,
            description=description,
            sub_agents=sub_agents or [],
            **kwargs,
        )
        
        # Use Pydantic's model_validate to validate and set fields
        validated_data = {
            "model": model,
            "instruction": instruction,
            "tools": tools or [],
            "app_name": app_name or name,
        }
        for key, value in validated_data.items():
            setattr(self, key, value)
        
        # Create the LLM agent and other non-Pydantic fields
        self._llm_agent = LlmAgent(...)
        self._session_service = session_service or InMemorySessionService()
        self._runner = Runner(...)
```

### Option 2: Hybrid Approach (Recommended)

```python
class BaseAgent(ADKBaseAgent):
    # Define model_config for Pydantic
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        model: str = DEFAULT_MODEL,
        description: str = "",
        instruction: str = "",
        tools: Optional[List[Any]] = None,
        sub_agents: Optional[List[Any]] = None,
        session_service: Optional[Any] = None,
        app_name: Optional[str] = None,
        **kwargs,
    ):
        # Validate inputs before passing to parent class
        validated_model = self._validate_model(model)
        validated_tools = tools or []
        
        # Initialize the parent class first
        super().__init__(
            name=name,
            description=description,
            sub_agents=sub_agents or [],
            **kwargs,
        )
        
        # Store parameters as instance attributes with leading underscore
        # to indicate they are "private"
        self._model = validated_model
        self._instruction = instruction
        self._tools = validated_tools
        self._app_name = app_name or name
        
        # ...
    
    def _validate_model(self, model: Optional[str]) -> str:
        """Validate the model parameter."""
        if not model:
            return DEFAULT_MODEL
        # Add additional validation logic here
        return model
```

### Option 3: Property-Based Approach

```python
class BaseAgent(ADKBaseAgent):
    # Define model_config for Pydantic
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        model: str = DEFAULT_MODEL,
        description: str = "",
        instruction: str = "",
        tools: Optional[List[Any]] = None,
        sub_agents: Optional[List[Any]] = None,
        session_service: Optional[Any] = None,
        app_name: Optional[str] = None,
        **kwargs,
    ):
        # Initialize the parent class first
        super().__init__(
            name=name,
            description=description,
            sub_agents=sub_agents or [],
            **kwargs,
        )
        
        # Store parameters as private instance attributes
        self._model = model
        self._instruction = instruction
        self._tools = tools or []
        self._app_name = app_name or name
        
        # ...
    
    @property
    def model(self) -> str:
        """Get the model."""
        return self._model
    
    @model.setter
    def model(self, value: str) -> None:
        """Set the model with validation."""
        if not value:
            value = DEFAULT_MODEL
        # Add additional validation logic here
        self._model = value
```

## Recommendation

We recommend adopting **Option 2: Hybrid Approach** for the following reasons:

1. **Compatibility**: It maintains compatibility with the existing codebase and the ADK's BaseAgent class.
2. **Validation**: It allows for explicit validation of inputs in dedicated methods.
3. **Encapsulation**: It maintains the convention of using leading underscores for "private" attributes.
4. **Simplicity**: It doesn't require a significant refactoring of the existing code.

This approach strikes a balance between leveraging Pydantic's capabilities and maintaining the existing code structure.

## Implementation Plan

1. **Update BaseAgent**: Implement the hybrid approach in the BaseAgent class. (Done)
2. **Documentation**: Add docstrings explaining the validation methods.
3. **Testing**: Update tests to verify validation logic.

## Future Considerations

As we continue to develop the codebase, we should consider:

1. **Stricter Validation**: Adding more comprehensive validation for critical parameters.
2. **Schema Documentation**: Using Pydantic's schema generation capabilities to document the agent's configuration options.
3. **Configuration Management**: Exploring Pydantic's settings management for agent configuration.

By standardizing our approach to Pydantic usage, we'll improve code quality, maintainability, and developer experience.
