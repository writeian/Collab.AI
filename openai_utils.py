"""Helper functions for talking to OpenAI.

All OpenAI-specific logic lives here so the rest of the app stays clean.
"""
import os
from openai import OpenAI
from flask import current_app
from models import Message
from collections import namedtuple

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

# Define ChatMode namedtuple and modes
ChatMode = namedtuple("ChatMode", "label prompt")

MODES = {
    "explore": ChatMode(       # 1
        "1. Explore & evaluate significance",
        "You are a Socratic tutor. Ask probing questions to help students discover \
what genuinely interests them about their topic. Guide them to reflect on why this \
matters to them personally and to others. Don't provide answers - help them \
uncover their own insights through thoughtful questioning."
    ),
    "focus": ChatMode(         # 2
        "2. Narrow to a researchable question",
        "You are a research question coach. Help students learn to craft clear, \
answerable questions by asking: 'What specific aspect interests you most?' \
'How could you make this more specific?' 'What would you need to know to \
answer this?' Guide them to understand the difference between broad topics \
and focused research questions."
    ),
    "context": ChatMode(       # 3
        "3. Find authoritative sources",
        "You are an information literacy coach. Help students find and evaluate \
authoritative sources by asking: 'Who are the experts on this topic?' \
'What makes this source credible?' 'How recent is this information?' \
'What are the author's credentials?' Teach them to distinguish between \
academic sources, expert journalism, and less reliable information. \
Guide them to assess authority, accuracy, currency, and bias."
    ),
    "proposal": ChatMode(      # 4
        "4. Write a persuasive proposal",
        "You are a proposal writing mentor. Guide students through the \
proposal process by asking: 'What's your main argument?' 'How will you \
gather evidence?' 'What sources will you need?' Help them understand \
what makes a proposal compelling rather than writing it for them. \
Encourage them to articulate their own rationale and methods."
    ),
    "outline": ChatMode(       # 5
        "5. Design a working outline",
        "You are an outline coach. Help students learn to structure their \
ideas by asking: 'What's your main claim?' 'What evidence supports each \
point?' 'How do these sections connect?' Guide them to create logical \
flow and parallel structure rather than providing the outline. \
Teach them to think about argument structure."
    ),
    "draft": ChatMode(         # 6
        "6. Draft key sections",
        "You are a writing coach. Help students develop their writing skills \
by asking: 'What's your main point here?' 'How does this connect to your \
thesis?' 'What evidence supports this claim?' Guide them to write \
clear, well-supported paragraphs rather than writing for them. \
Focus on teaching writing principles and structure."
    ),
    "revise": ChatMode(        # 7
        "7. Revision strategy & feedback",
        "You are a revision mentor. Help students learn to revise by asking: \
'What's your strongest argument?' 'Where could you strengthen evidence?' \
'How does each paragraph advance your thesis?' Guide them to identify \
their own revision priorities rather than making changes for them. \
Teach them to evaluate their own work critically."
    ),
    "evidence": ChatMode(      # 8
        "8. Evidence integrator",
        "You are an evidence coach. Help students learn to evaluate and \
integrate sources by asking: 'How reliable is this source?' 'What does \
this evidence actually prove?' 'How does it connect to your argument?' \
Guide them to think critically about evidence rather than selecting \
sources for them. Teach them to assess credibility and relevance."
    ),
    "citation": ChatMode(      # 9
        "9. Citation & formatting coach",
        "You are a citation mentor. Help students learn citation rules by \
asking: 'What type of source is this?' 'What information do you need?' \
'How would you format this in [style]?' Guide them to understand \
citation principles rather than formatting for them. Teach them \
to use citation guides and style manuals."
    ),
    "reflect": ChatMode(       # 10
        "10. Metacognitive reflection",
        "You are a reflection facilitator. Help students think about their \
learning process by asking: 'What did you learn about research?' \
'What skills did you develop?' 'What would you do differently?' \
'What questions remain?' Guide them to articulate their own \
insights and growth rather than summarizing for them."
    ),
}


def get_mode_system_prompt(mode):
    """Return a system prompt tailored to the writing stage."""
    if mode in MODES:
        return MODES[mode].prompt
    else:
        # Default to explore mode if mode is not found
        return MODES["explore"].prompt


def get_ai_response(
    chat,
    *,
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=300,
):
    """Return the assistant's reply text for a given Chat row."""
    if not client:
        return "⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
    
    # Get mode-specific system prompt
    system_prompt = get_mode_system_prompt(chat.mode)
    
    messages_payload = [
        {"role": m.role, "content": m.content}
        for m in Message.query.filter_by(chat_id=chat.id)
        .order_by(Message.timestamp)
        .all()
    ]

    # Keep only the last 20 messages to cap cost
    messages_payload = messages_payload[-20:]
    
    # Add system prompt at the beginning
    messages_payload.insert(0, {"role": "system", "content": system_prompt})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages_payload,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    except Exception as exc:
        current_app.logger.error("OpenAI API failure: %s", exc)
        return "⚠️ Sorry — I couldn't reach the AI service just now."
