## GoodFoods Reservation System

### Overview
GoodFoods is a conversational AI that helps users discover restaurants and book tables across Bangalore. It uses OpenAI function-calling to search restaurants and confirm reservations via a FastAPI backend, wrapped in a modern Streamlit chat UI.

### Repository Structure
- `app_goodfoods.py`: Streamlit frontend (chat UI, live agent trace, theming)
- `agent/conversation_engine.py`: Agent core (OpenAI calls, tool handling)
- `agent/toolkit.py`: Tool definitions (OpenAI function schemas)
- `agent/prompt_library.py`: System prompts and few-shot examples
- `data/service_api.py`: FastAPI backend (search and reservation endpoints)
- `data/restaurant_list.json`: Restaurant catalog
- `data/bookings_list.json`: Stored reservations
- `start.py`: One-command launcher (starts API then UI)

## Sample Converstions
### Insufficient information
<img width="1704" height="836" alt="Screenshot 2025-11-02 at 10 04 10 PM" src="https://github.com/user-attachments/assets/044ee91f-5032-447e-8614-40937abe33a8" />

### Cuisine based
<img width="1704" height="1006" alt="Screenshot 2025-11-02 at 10 02 04 PM" src="https://github.com/user-attachments/assets/af3a7f8f-cecd-499f-8514-b3cc1bfff6f3" />

### Incorrect information
<img width="1386" height="918" alt="Screenshot 2025-11-02 at 10 17 41 PM" src="https://github.com/user-attachments/assets/c00b1d9c-358f-462f-a11a-11e850c505ec" />

### Guardrail (Max party size check)
<img width="1389" height="918" alt="Screenshot 2025-11-02 at 10 05 28 PM" src="https://github.com/user-attachments/assets/3272b4f8-fd54-4085-8341-2cc14c330df6" />

### Setup Instructions
1) Python 3.9+ recommended
2) Install dependencies:
   - `pip install -r requirements.txt`
3) Configure environment:
   - Create `.env` with `OPENAI_API_KEY=YOUR_KEY`
4) Optional data edits:
   - Update `data/restaurant_list.json` for your venues
5) Run the stack:
   - `python start.py`

### How It Works (High-Level)
1) UI collects user input and maintains `st.session_state.messages`.
2) First model call (tools enabled) plans and may return tool calls.
3) Tools are executed via FastAPI and results appended to the chat.
4) Second model call (tools disabled) generates the final assistant reply.
5) The “Agent thinking & tool activity (live)” panel shows plan, tool args, results, and finalization.

### Tools (Function-Calling)
- `lookup_dining_options`:
  - Inputs: any of name, location, cuisine, operating_hours, operating_days, capacities
  - Output: ranked restaurant matches (or curated top list if empty query)
- `confirm_table_booking`:
  - Inputs: restaurant_id, orderer_name, orderer_contact, party_size, reservation_date, reservation_time
  - Output: reservation confirmation with `order_id` (or capacity/validation error)

### Documentation of Prompt Engineering Approach
- Purpose framing + brand context (GoodFoods in Bangalore)
- Clear “Typical Task” flow: discover → decide → collect details → confirm
- Tool descriptions with when-to-use, required fields, and guardrails
- Few-shot examples to steer behavior (handling missing info, capacity issues)
- Inline constraints (don’t hallucinate, avoid placeholders, friendly tone)

### Business Strategy Summary
- Problem: Manual reservation workflows are slow and costly.
- Solution: AI agent that handles discovery and booking end-to-end, 24/7.
- Value:
  - Increase conversion (guided flows + quick suggestions)
  - Reduce staffing costs (self-serve bookings)
  - Improve CX (consistent answers, instant confirmations)
- KPIs: conversion rate, bookings completed, average time-to-book, deflection from human agents.

### Assumptions
- Users intend to discover/book GoodFoods restaurants in Bangalore.
- Prototype uses JSON files as data stores (no external DB).
- Single-tenant brand and city context (GoodFoods Bangalore).

### Limitations
- No sequential/parallel multi-tool planning within a single model turn (tools are executed sequentially between turns).
- No dedicated date/time validation tool; relies on prompt guidance and backend checks.
- No cancellation or modification of existing reservations.
- Basic phone validation; no OTP verification.

### Future Enhancements
- Parallel/Sequential tool strategies inside the agent loop for faster decisions.
- Separate DB schema and endpoints for menus, enabling food/menu Q&A and upsell flows.
- Proper date/time interpretation service (holidays, closures, slotting).
- Reservation lifecycle: edit/cancel, notifications, reminders, no-show handling.
- Authentication for staff dashboards and rate limiting/spam controls.

### Current Technical Implementation
- LLM: OpenAI GPT-4o via `openai` SDK
- Tool Calling: OpenAI function-calling → FastAPI endpoints
- Guardrails: function-text leakage detection and placeholder checks
- Frontend: Streamlit chat UI with live trace (`app_goodfoods.py`)
- Data: JSON-based catalog and booking store (prototype)
- Launcher: `start.py` boots `data/service_api.py` then `app_goodfoods.py`

### API Endpoints
- `POST /restaurants/search` → `search_restaurant_information`
- `POST /reservations` → `make_new_order`

### Example Conversations
See `agent/prompt_library.py` few-shot examples for guided flows (missing info, capacity, validation).
