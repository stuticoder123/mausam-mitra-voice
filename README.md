# Mausam Mitra

<div align="center">

## Real-Time Voice AI Agent for Weather

**Speak naturally. Ask about the weather. Let the agent fetch the real-world answer.**

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pipecat](https://img.shields.io/badge/Pipecat-Voice%20AI-7C3AED?style=for-the-badge)](https://github.com/pipecat-ai/pipecat)
[![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge)](https://groq.com/)
[![Sarvam AI](https://img.shields.io/badge/Sarvam%20AI-STT%20%2B%20TTS-FF4F8B?style=for-the-badge)](https://www.sarvam.ai/)
[![WebRTC](https://img.shields.io/badge/WebRTC-Real--Time-333333?style=for-the-badge&logo=webrtc)](https://webrtc.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

**[Features](#features) · [Architecture](#architecture) · [Quick Start](#quick-start) · [Tech Stack](#tech-stack) · [Roadmap](#roadmap)**

</div>

---

# Overview

**Mausam Mitra** is a real-time Voice AI Agent that combines conversational AI with live weather data.

Instead of asking an LLM to generate weather information from its internal knowledge, Mausam Mitra uses external APIs to retrieve current weather conditions and provides the result through a natural voice conversation.

The agent can:

- Understand natural voice input
- Convert speech into text
- Reason about the user's request
- Decide when a weather tool is required
- Access the user's current browser location
- Retrieve live weather data
- Retrieve weather for a specific city
- Convert the final response into natural speech

### Core Idea

A traditional chatbot generally follows:

```text
User
  |
  v
Message
  |
  v
LLM
  |
  v
Response
```

For information that changes in the real world, relying only on the LLM can result in outdated or inaccurate answers.

Mausam Mitra introduces external tools into the conversational loop:

```text
Voice Input
    |
    v
Speech-to-Text
    |
    v
LLM Reasoning
    |
    v
Tool Selection
    |
    v
Weather API
    |
    v
Live Weather Data
    |
    v
LLM Response
    |
    v
Text-to-Speech
    |
    v
Voice Response
```

### Design Principle

> **LLM = Reasoning**  
> **Tools = Real-world information**

The LLM determines what needs to happen.

The weather service is responsible for retrieving the actual current information.

---

# Features

| Feature | Description |
|---|---|
| Real-Time Voice | Conversational voice interaction through Pipecat and WebRTC |
| Speech-to-Text | Converts user speech into text using Sarvam AI |
| Intelligent Tool Calling | The LLM can invoke the appropriate weather function based on the user's request |
| Live Location | Uses browser geolocation for location-aware weather requests |
| Current Weather | Retrieves live weather data from OpenWeatherMap |
| City-Based Weather | Supports weather queries for a specified city |
| Reverse Geocoding | Converts geographic coordinates into a readable location |
| Async API Calls | Uses asynchronous HTTP requests through `aiohttp` |
| Backend Validation | Validates tool parameters before making external API requests |
| Graceful Failure | Handles API and location failures without exposing raw technical errors |
| Text-to-Speech | Converts the final response into natural speech using Sarvam AI |

---

# Agent Capabilities

Mausam Mitra currently uses weather and location-related tools to interact with external services.

## `get_current_location()`

Retrieves the user's current browser coordinates and uses reverse geocoding to determine the corresponding location.

This allows the agent to understand requests such as:

> "Where am I?"

or:

> "What's the weather around me?"

---

## `get_current_weather()`

Retrieves the current weather using the user's latest available coordinates.

Example:

```text
User:
"What's the weather around me?"

        |
        v

Get Current Location
        |
        v
Latitude + Longitude
        |
        v
OpenWeatherMap
        |
        v
Current Weather
```

---

## `get_weather_by_location(city: str)`

Retrieves current weather for a specific city.

Example:

```text
User:
"What's the weather in Jaipur?"

        |
        v

City Name
        |
        v
Geocoding
        |
        v
Latitude + Longitude
        |
        v
OpenWeatherMap
        |
        v
Current Weather
```

---

# Architecture

## High-Level Architecture

```text
                         USER
                          |
                          | Voice
                          v
                 +-------------------+
                 |      WebRTC       |
                 |     Transport    |
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 |     Sarvam STT    |
                 |   Speech -> Text  |
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 |      Groq LLM     |
                 |                   |
                 | Intent Reasoning  |
                 | + Tool Selection  |
                 +---------+---------+
                           |
                 +---------+---------+
                 |                   |
                 v                   v
        +----------------+   +----------------+
        | Location Tool  |   | Weather Tool   |
        +-------+--------+   +--------+-------+
                |                     |
                v                     v
        +---------------+     +---------------+
        |   Geoapify    |     | OpenWeather   |
        |   Geocoding   |     |     API       |
        +-------+-------+     +-------+-------+
                |                     |
                +----------+----------+
                           |
                           v
                  +----------------+
                  |   Tool Results |
                  |   Live Data    |
                  +-------+--------+
                          |
                          v
                 +-------------------+
                 |    Sarvam TTS     |
                 |   Text -> Speech  |
                 +---------+---------+
                           |
                           v
                         USER
```

---

# Request Lifecycle

Consider the following request:

> "What's the weather around me?"

The request travels through the system as follows:

```text
01  Voice Input
        |
        v
02  Sarvam converts speech to text
        |
        v
03  Groq identifies the user's intent
        |
        v
04  LLM selects the required weather/location tool
        |
        v
05  Browser location is retrieved
        |
        v
06  Coordinates are used to query the weather service
        |
        v
07  OpenWeatherMap returns current weather
        |
        v
08  LLM processes the tool result
        |
        v
09  Sarvam converts the response into speech
        |
        v
10  User hears the result
```

The fundamental agent loop is:

```text
UNDERSTAND
    |
    v
DECIDE
    |
    v
CALL TOOL
    |
    v
GET REAL DATA
    |
    v
PROCESS RESULT
    |
    v
RESPOND
```

---

# Location Intelligence

Mausam Mitra uses the browser's Geolocation API to obtain the user's current coordinates.

```javascript
navigator.geolocation.getCurrentPosition(
  (position) => {
    const { latitude, longitude } = position.coords;

    sendToBackend(latitude, longitude);
  }
);
```

The location flow is:

```text
Browser
   |
   | GPS
   v
Latitude + Longitude
   |
   v
Location Store
   |
   v
Reverse Geocoding
   |
   v
Readable Location
```

The retrieved coordinates can then be used for location-aware weather requests.

---

# Weather Intelligence

Mausam Mitra supports two primary weather flows.

## Weather Around the User

For a request such as:

> "What's the weather around me?"

The system follows:

```text
Voice Request
     |
     v
Browser GPS
     |
     v
Latitude + Longitude
     |
     v
OpenWeatherMap
     |
     v
Current Weather
     |
     v
Voice Response
```

---

## Weather for a Specific City

For a request such as:

> "What's the weather in Jaipur?"

The system follows:

```text
Voice Request
     |
     v
City Name
     |
     v
Geoapify Geocoding
     |
     v
Latitude + Longitude
     |
     v
OpenWeatherMap
     |
     v
Current Weather
     |
     v
Voice Response
```

Weather information can include:

- Temperature
- Feels-like temperature
- Weather condition
- Humidity
- Wind
- Precipitation
- Location

---

# Tool Calling

One of the important concepts demonstrated by Mausam Mitra is **LLM-driven function calling**.

The LLM does not directly retrieve weather information.

Instead, it determines which function needs to be executed based on the user's request.

For example:

```text
User:
"What's the weather in Jaipur?"

        |
        v

LLM
 |
 | Determines that weather data is required
 v

get_weather_by_location("Jaipur")
        |
        v
Geocoding API
        |
        v
Coordinates
        |
        v
Weather API
        |
        v
Live Weather
        |
        v
LLM
        |
        v
Voice Response
```

This creates a clear separation between:

```text
LLM
Reasoning + Decision Making

        +

Tools
External Data + Deterministic Operations
```

---

# Async-First Design

Mausam Mitra uses asynchronous HTTP requests through `aiohttp`.

External operations include:

```text
Weather API
Geocoding API
Reverse Geocoding
```

The general execution pattern is:

```text
Async Request
     |
     v
External API
     |
     v
Await Result
     |
     v
Continue Conversation
```

This is particularly useful for real-time voice applications because blocking external requests can negatively affect responsiveness.

---

# Backend Validation

Model-generated parameters should not be trusted blindly.

Tool inputs are validated before they are used to make external API requests.

The architecture follows:

```text
LLM Output
    |
    v
Backend Validation
    |
    v
Validated Parameters
    |
    v
External API
```

This creates a useful engineering boundary:

> **The model suggests. The backend validates.**

---

# Graceful Failure

External services can fail because of:

- Network issues
- API errors
- Invalid responses
- Missing location permissions
- Invalid parameters
- Service unavailability

Mausam Mitra handles these failures at the tool/service layer.

```text
                 External API
                      |
                +-----+-----+
                |           |
             Success      Failure
                |           |
                v           v
            Real Data   Controlled Error
                |           |
                +-----+-----+
                      |
                      v
                Natural Reply
```

The agent should not invent live weather information when the required external service cannot provide reliable data.

---

# Voice Experience

A real-time voice agent should provide conversational feedback while external operations are being performed.

For example:

```text
"Let me check the live weather for you."

"Let me check your current location."

"Give me a moment while I fetch the latest weather."
```

These short responses make the interaction feel more conversational while the agent performs external operations.

---

# Project Structure

```text
mausam-mitra-voice/
|
├── main.py
|   └── Pipecat voice pipeline
|
├── functions.py
|   └── AI tools and function calling
|
├── location_service.py
|   └── GPS, geocoding and reverse geocoding
|
├── weather_service.py
|   └── OpenWeatherMap integration
|
├── client.html
|   └── Browser voice client and GPS
|
├── requirements.txt
|   └── Python dependencies
|
├── .env
|   └── Local API credentials
|
└── README.md
```

---

# Tech Stack

| Category | Technology |
|---|---|
| Agent Framework | Pipecat |
| Speech-to-Text | Sarvam AI |
| Text-to-Speech | Sarvam AI |
| LLM | Groq |
| Voice Activity Detection | Silero VAD |
| Real-Time Transport | WebRTC |
| Backend | Python |
| HTTP Client | aiohttp |
| Weather | OpenWeatherMap |
| Geocoding | Geoapify |
| Location | Browser Geolocation API |
| Logging | Loguru |
| Configuration | python-dotenv |

---

# Environment Variables

Create a `.env` file in the project root:

```env
SARVAM_API_KEY=your_sarvam_api_key
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
GEOAPIFY_API_KEY=your_geoapify_api_key
```

## API Responsibilities

| Variable | Purpose |
|---|---|
| `SARVAM_API_KEY` | Speech-to-Text and Text-to-Speech |
| `GROQ_API_KEY` | LLM inference |
| `OPENWEATHER_API_KEY` | Live weather data |
| `GEOAPIFY_API_KEY` | Geocoding and reverse geocoding |

> Never commit real API keys to GitHub.

Add `.env` to your `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

---

# Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/stuticoder123/mausam-mitra-voice.git

cd mausam-mitra-voice
```

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a `.env` file:

```env
SARVAM_API_KEY=
GROQ_API_KEY=
OPENWEATHER_API_KEY=
GEOAPIFY_API_KEY=
```

Add your API credentials.

## 5. Start the Agent

```bash
python main.py
```

Then open:

```text
client.html
```

Allow access to:

```text
Microphone
Location
```

Once permissions are granted, start speaking to the agent.

---

# Try It Yourself

| Voice Request | Agent Flow |
|---|---|
| "What's the weather around me?" | GPS → Weather |
| "Where am I?" | GPS → Reverse Geocoding |
| "What's the weather in Jaipur?" | Geocoding → Weather |
| "Tell me the current temperature in Delhi" | Geocoding → Weather |
| "How does the weather feel right now?" | Current Location → Weather |

---

# Engineering Principles

## 1. Don't Make the LLM Do Everything

The LLM is responsible for reasoning and tool selection.

Deterministic operations are delegated to specialized services.

```text
LLM
 |
 +-- Reason
 |
 +-- Decide
 |
 +-- Select Tool
        |
        v
      Tool
        |
        v
 External Service
```

---

## 2. Real-World Information Should Come From Real-World Sources

An LLM should not be expected to know the current temperature.

Instead:

```text
Need live information?
        |
        v
Call the appropriate tool.
        |
        v
Use the returned data.
```

---

## 3. Location Should Come From Actual Coordinates

For location-aware weather requests, the system uses browser-provided coordinates instead of assuming the user's location.

---

## 4. Keep I/O Asynchronous

Voice applications are sensitive to latency.

External API calls should avoid unnecessarily blocking the conversational pipeline.

---

## 5. Validate Model-Generated Parameters

LLM output is treated as input.

Model-generated values should be validated before reaching external services or internal business logic.

---

## 6. Fail Gracefully

External services can fail.

A production-oriented agent should transform technical failures into understandable user-facing responses rather than exposing raw stack traces or generating fabricated information.

---

# Agent Design Philosophy

The architecture can be summarized as:

```text
                 AI AGENT
                    |
        +-----------+-----------+
        |                       |
        v                       v
    Reasoning                 Tools
        |                       |
        |                       v
        |                 External APIs
        |                       |
        +-----------+-----------+
                    |
                    v
              Real-World Data
                    |
                    v
              Voice Response
```

Or more simply:

```text
UNDERSTAND
    |
    v
DECIDE
    |
    v
ACT
    |
    v
OBSERVE
    |
    v
RESPOND
```

Mausam Mitra is built around this agent loop.

---

# Roadmap

## Weather

- [ ] Hourly forecast
- [ ] 7-day forecast
- [ ] Weather alerts
- [ ] Air Quality Index
- [ ] UV index
- [ ] Rain probability

## Location Intelligence

- [ ] Improved location refresh
- [ ] Better location permission handling
- [ ] Location history within a conversation
- [ ] More location-aware weather queries

## Agent Intelligence

- [ ] Multi-step tool chaining
- [ ] Conversational memory
- [ ] Personalized weather insights
- [ ] More advanced weather reasoning

## Voice Experience

- [ ] Hindi support
- [ ] Hinglish support
- [ ] Additional multilingual support
- [ ] Improved interruption handling
- [ ] Better conversational context
- [ ] Lower perceived latency

---

# Current Status

```text
Core Voice Pipeline          Complete
LLM Tool Calling             Complete
Browser GPS                  Complete
Live Weather                 Complete
Geocoding                    Complete
Reverse Geocoding            Complete
Async API Integration        Complete
Error Handling               Complete

Additional capabilities      In Progress
```

---

# What I Learned

Building Mausam Mitra helped me understand an important distinction:

> **A voice chatbot talks. An AI agent can act.**

Connecting an LLM to a microphone is only the beginning.

The interesting engineering starts when the model needs to:

```text
Hear
  |
  v
Understand
  |
  v
Choose a Tool
  |
  v
Interact with the Real World
  |
  v
Process the Result
  |
  v
Speak
```

This project became my exploration of that complete loop.

It helped me understand how voice interfaces, LLM reasoning, function calling, external APIs, location intelligence, asynchronous programming, validation, and real-time user experience come together to build a practical AI agent.

---

# Support

If you are interested in : **Voice AI · AI Agents · Pipecat · Function Calling · WebRTC · Real-Time AI** consider giving the repository a star.

It helps the project reach other developers exploring real-time AI agents and tool-based architectures.

---

<div align="center">

## Speak. Ask. Explore.

**That's Mausam Mitra.**

<br/>

### Made by **Stuti Gupta**

**AI/ML × Full Stack Developer · Voice AI Explorer · Open Source Contributor**

*I learn by building, and I build to understand how things actually work.*

<br/>

<a href="https://www.linkedin.com/in/stuticoder1">LinkedIn</a>
&nbsp; · &nbsp;
<a href="https://github.com/stuticoder123">GitHub</a>

</div>
