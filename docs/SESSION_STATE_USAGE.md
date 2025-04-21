# Session State Usage Guide

## Overview

This guide documents the recommended patterns for using the `session.state` object in ADK agents. The session state provides a mechanism to store and retrieve contextual information across multiple interactions within a conversation session.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Usage Patterns](#usage-patterns)
4. [Best Practices](#best-practices)
5. [Example Implementations](#example-implementations)
6. [API Reference](#api-reference)

## Introduction

The Google ADK provides a `session.state` object within the `InvocationContext` passed to the agent's `_run_async_impl` method. This state object persists across multiple turns in a conversation, allowing agents to maintain context, store user preferences, track conversation history, and more.

```python
async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
    # Access session state
    current_state = ctx.session.state
    
    # Rest of implementation...
```

## Core Concepts

### State Persistence

- **Session Scope**: State persists for the duration of a session
- **User-specific**: Each user-session combination has its own state
- **Serializable**: State must be JSON-serializable (dictionaries, lists, strings, numbers, booleans, None)

### State Structure

The session state is a dictionary-like object that can store arbitrary key-value pairs:

```python
# Setting state values
ctx.session.state["user_name"] = "John"
ctx.session.state["preferences"] = {"theme": "dark", "language": "en"}
ctx.session.state["history"] = []

# Getting state values
user_name = ctx.session.state.get("user_name", "Guest")  # With default
```

## Usage Patterns

### 1. User Preferences

Store user preferences that affect agent behavior:

```python
# Reading preferences
language = ctx.session.state.get("language", "en")
theme = ctx.session.state.get("theme", "default")

# Setting preferences
if "set language" in user_message.lower():
    language = extract_language(user_message)
    ctx.session.state["language"] = language
    yield create_text_event(f"Language set to {language}")
```

### 2. Conversation Context

Track conversation topics, entities, or previous responses:

```python
# Initialize history if not present
if "conversation_topics" not in ctx.session.state:
    ctx.session.state["conversation_topics"] = []

# Update with new topic
if new_topic:
    ctx.session.state["conversation_topics"].append(new_topic)
    # Limit list size
    ctx.session.state["conversation_topics"] = ctx.session.state["conversation_topics"][-5:]
```

### 3. Multi-turn Tasks

Keep track of multi-step processes:

```python
# Initialize workflow state if not present
if "form_completion" not in ctx.session.state:
    ctx.session.state["form_completion"] = {
        "started": True,
        "current_step": "name",
        "steps_completed": [],
        "data": {}
    }

# Update workflow state
workflow = ctx.session.state["form_completion"]
current_step = workflow["current_step"]

if current_step == "name":
    # Process name input
    workflow["data"]["name"] = extract_name(user_message)
    workflow["steps_completed"].append("name")
    workflow["current_step"] = "email"
    
    ctx.session.state["form_completion"] = workflow  # Save updated workflow
```

### 4. Tool Context Preservation

Store context for tool usage:

```python
# Store search context
if should_search:
    ctx.session.state["last_search"] = {
        "query": search_query,
        "timestamp": time.time(),
        "results_count": len(search_results)
    }
    
# Reference previous search
if "tell me more" in user_message.lower() and "last_search" in ctx.session.state:
    last_search = ctx.session.state["last_search"]
    # Use the stored search context
```

## Best Practices

1. **Initialize State Keys**:
   Always check if a state key exists before accessing it:
   ```python
   if "user_data" not in ctx.session.state:
       ctx.session.state["user_data"] = {}
   ```

2. **Use Type Hints**:
   Add type hints to clarify state structure:
   ```python
   from typing import Dict, List, Any, TypedDict
   
   class UserData(TypedDict):
       name: str
       preferences: Dict[str, Any]
   
   # In code
   user_data: UserData = ctx.session.state.get("user_data", {"name": "", "preferences": {}})
   ```

3. **Group Related Data**:
   Group related state under a single key:
   ```python
   # Instead of separate keys
   ctx.session.state["user_name"] = "John"
   ctx.session.state["user_email"] = "john@example.com"
   
   # Group under a user key
   if "user" not in ctx.session.state:
       ctx.session.state["user"] = {}
   ctx.session.state["user"]["name"] = "John"
   ctx.session.state["user"]["email"] = "john@example.com"
   ```

4. **Document State Structure**:
   Add comments describing the expected state structure in your agent class.

5. **Handle Missing State Gracefully**:
   Always provide defaults when fetching state values that might not exist:
   ```python
   user_name = ctx.session.state.get("user_name", "Guest")
   ```

6. **Limit State Size**:
   Keep state size manageable by limiting collections and removing unnecessary data:
   ```python
   # Keep only the 10 most recent items
   history = ctx.session.state.get("history", [])
   history.append(new_item)
   ctx.session.state["history"] = history[-10:]
   ```

## Example Implementations

### Basic Product Recommendation Agent

```python
async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
    # Initialize or get state
    if "user_preferences" not in ctx.session.state:
        ctx.session.state["user_preferences"] = {
            "price_range": None,
            "categories": [],
            "previously_recommended": []
        }
    
    preferences = ctx.session.state["user_preferences"]
    
    # Extract user message
    user_message = extract_user_message(ctx)
    
    # Update preferences based on message
    if price_range := extract_price_range(user_message):
        preferences["price_range"] = price_range
        yield create_text_event(f"I'll look for products in the {price_range} range.")
    
    if categories := extract_categories(user_message):
        for category in categories:
            if category not in preferences["categories"]:
                preferences["categories"].append(category)
        yield create_text_event(f"I'll focus on these categories: {', '.join(preferences['categories'])}")
    
    # Get recommendations based on preferences
    if "recommend" in user_message.lower() and (preferences["price_range"] or preferences["categories"]):
        recommended_products = get_recommendations(
            price_range=preferences["price_range"],
            categories=preferences["categories"],
            exclude=preferences["previously_recommended"]
        )
        
        if recommended_products:
            product = recommended_products[0]
            preferences["previously_recommended"].append(product["id"])
            yield create_text_event(f"I recommend {product['name']} for ${product['price']}.")
        else:
            yield create_text_event("I don't have any recommendations matching your preferences.")
    
    # Save updated preferences to state
    ctx.session.state["user_preferences"] = preferences
```

### Multi-turn Form Completion

```python
async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
    # Initialize form state if not present
    if "form" not in ctx.session.state:
        ctx.session.state["form"] = {
            "active": False,
            "current_field": None,
            "collected_data": {},
            "required_fields": ["name", "email", "purpose"]
        }
    
    form = ctx.session.state["form"]
    user_message = extract_user_message(ctx)
    
    # Start form if requested
    if not form["active"] and "fill form" in user_message.lower():
        form["active"] = True
        form["current_field"] = "name"
        yield create_text_event("Let's fill out the form. What's your name?")
    
    # Process form input
    elif form["active"]:
        current_field = form["current_field"]
        
        # Store response to current field
        if current_field:
            form["collected_data"][current_field] = user_message
            form["current_field"] = get_next_field(form)
        
        # Prompt for next field or complete form
        if form["current_field"]:
            prompt = get_field_prompt(form["current_field"])
            yield create_text_event(prompt)
        else:
            # Form complete
            form["active"] = False
            yield create_text_event("Thank you for completing the form!")
            yield create_text_event(f"Collected information: {form['collected_data']}")
    
    # Save form state
    ctx.session.state["form"] = form
```

## API Reference

### Session State Methods

| Method | Description | Example |
|--------|-------------|---------|
| `get(key, default=None)` | Gets value for key or default if not present | `name = ctx.session.state.get("name", "Guest")` |
| `__getitem__(key)` | Gets value for key (raises KeyError if not found) | `name = ctx.session.state["name"]` |
| `__setitem__(key, value)` | Sets value for key | `ctx.session.state["name"] = "John"` |
| `__contains__(key)` | Checks if key exists | `if "name" in ctx.session.state:` |

### Common State Dictionary Structure

```python
{
    "user_info": {
        "name": str,
        "preferences": Dict[str, Any],
        "last_interaction": float  # timestamp
    },
    "conversation": {
        "topics": List[str],
        "current_topic": str,
        "messages_count": int
    },
    "workflow": {
        "stage": str,
        "data": Dict[str, Any],
        "completed_stages": List[str]
    },
    "tools": {
        "last_search": {
            "query": str,
            "results": List[Dict],
            "timestamp": float
        }
    }
}
``` 