import streamlit as st
import json
from openai import OpenAI

# ==============================================================================
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# ==============================================================================
st.set_page_config(
    page_title="AI Buyer Persona Simulator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished business UI styling
st.markdown("""
<style>
    /* Main container theme */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .app-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
    }
    .app-header p {
        margin: 5px 0 0 0;
        font-size: 1.05rem;
        opacity: 0.9;
    }

    /* Metric Card Styling */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2a5298;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e3c72;
    }

    /* Persona quote box */
    .persona-quote {
        background-color: #eef2f7;
        border-left: 4px solid #4a90e2;
        padding: 15px 20px;
        border-radius: 0 8px 8px 0;
        font-style: italic;
        color: #2c3e50;
        font-size: 1.05rem;
        margin: 15px 0;
    }

    /* Status indicators */
    .pass-tag {
        color: #2e7d32;
        font-weight: bold;
    }
    .fail-tag {
        color: #c62828;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SIDEBAR SETUP & API KEY HANDLING
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/bullseye.png", width=60)
    st.title("Settings & Controls")
    
    # API Key Handling (Tries Streamlit Secrets first, falls back to manual entry)
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter OpenAI API Key:", type="password", help="Pass your key here if not set in .streamlit/secrets.toml")
    
    st.markdown("---")
    st.markdown("### 📋 Class Info")
    st.caption("**Course:** Principles of Marketing")
    st.caption("**Exercise:** Product Launch & Persona Fit")
    
    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    st.info("""
    1. Select or create a Persona.
    2. Input your **Marketing Mix (4 Ps)**.
    3. Run simulation to test value prop alignment.
    4. Refine your pitch to raise your intent score!
    """)

# Header Banner
st.markdown("""
<div class="app-header">
    <h1>🎯 AI Buyer Persona Simulator</h1>
    <p>Principles of Marketing | Test your Marketing Mix against real-time AI simulated consumer segments.</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. PREDEFINED PERSONAS & INPUT FORM
# ==============================================================================
PERSONA_DATABASE = {
    "Gen Z College Senior (Budget & Convenience Focus)": {
        "demographics": "Age 21-22, college senior, part-time income ($12k/yr), heavy smartphone user.",
        "psychographics": "Values convenience, speed, social proof (TikTok/IG), highly price-sensitive, eco-conscious but pragmatic.",
        "pain_points": "High cost of living, tight study/work schedules, decision fatigue."
    },
    "Busy Professional Parent (Quality & Time-Saver Focus)": {
        "demographics": "Age 34-42, dual-income family ($120k+/yr), 2 young kids.",
        "psychographics": "Prioritizes time efficiency, health, child safety, brand trust, reliability over lowest price.",
        "pain_points": "Lack of time, high stress, cluttered scheduling, balancing work and parenting."
    },
    "Eco-Conscious Millennial (Ethical & Brand Ethos Focus)": {
        "demographics": "Age 28-35, urban professional ($75k/yr), single.",
        "psychographics": "Seeks corporate transparency, sustainable sourcing, premium organic products, highly skeptical of greenwashing.",
        "pain_points": "Difficulty finding genuinely sustainable products, willingness to pay more balanced against inflation."
    }
}

col_inputs, col_results = st.columns([1, 1], gap="large")

with col_inputs:
    st.subheader("1. Select Target Persona")
    persona_choice = st.selectbox("Choose a Segment:", list(PERSONA_DATABASE.keys()))
    
    selected_persona_info = PERSONA_DATABASE[persona_choice]
    with st.expander("🔍 View Segment Profile Details", expanded=False):
        st.write(f"**Demographics:** {selected_persona_info['demographics']}")
        st.write(f"**Psychographics:** {selected_persona_info['psychographics']}")
        st.write(f"**Key Pain Points:** {selected_persona_info['pain_points']}")

    st.subheader("2. Define Marketing Mix (4 Ps)")
    
    with st.form("marketing_mix_form"):
        product_name = st.text_input("Product Name & Concept (Product)", placeholder="e.g., QuickGrind Organic Cold Brew Pods")
        price_point = st.text_input("Price Point & Model (Price)", placeholder="e.g., $14.99 per 12-pack ($1.25/cup)")
        target_channel = st.text_input("Primary Distribution/Ad Channel (Place)", placeholder="e.g., TikTok Shop & Campus Convenience Stores")
        ad_copy = st.text_area("Core Value Proposition / Messaging (Promotion)", placeholder="e.g., 'Organic, high-caffeine cold brew ready in 5 seconds. Half the price of Starbucks.'", height=100)
        
        submit_button = st.form_submit_button("🚀 Run Persona Simulation", use_container_width=True)

# ==============================================================================
# 4. LLM INFERENCE ENGINE & OUTPUT PARSING
# ==============================================================================
with col_results:
    st.subheader("3. Simulation Results & Audit")
    
    if submit_button:
        if not api_key:
            st.error("⚠️ Please enter an OpenAI API Key in the sidebar or setup secrets.toml.")
        elif not product_name or not ad_copy:
            st.warning("⚠️ Please fill in at least the Product Name and Value Proposition.")
        else:
            client = OpenAI(api_key=api_key)
            
            # System prompt forcing structured JSON output
            system_prompt = """
            You are an expert consumer psychologist and marketing faculty auditor.
            Your role is to simulate a specific consumer persona reacting to a product offer.
            
            You must evaluate the offer objectively and return a raw JSON object ONLY, formatted like this:
            {
                "purchase_intent_score": <integer from 0 to 100>,
                "persona_verdict": "<Short, 1-word reaction e.g. BUY, CONSIDER, REJECT>",
                "internal_monologue": "<2-3 sentences of first-person thought from the consumer's perspective reacting to the pitch>",
                "p_breakdown": {
                    "product": {"status": "PASS or FAIL", "comment": "<1 sentence feedback>"},
                    "price": {"status": "PASS or FAIL", "comment": "<1 sentence feedback>"},
                    "place": {"status": "PASS or FAIL", "comment": "<1 sentence feedback>"},
                    "promotion": {"status": "PASS or FAIL", "comment": "<1 sentence feedback>"}
                },
                "strategic_recommendation": "<Key strategic takeaway for the student to improve alignment>"
            }
            Do not wrap in markdown quotes. Return strictly valid JSON.
            """
            
            user_prompt = f"""
            TARGET PERSONA PROFILE:
            - Segment: {persona_choice}
            - Demographics: {selected_persona_info['demographics']}
            - Psychographics: {selected_persona_info['psychographics']}
            - Pain Points: {selected_persona_info['pain_points']}
            
            MARKETING MIX OFFER SUBMITTED BY STUDENT:
            - Product: {product_name}
            - Price: {price_point}
            - Place (Channel): {target_channel}
            - Promotion (Ad/Copy): {ad_copy}
            """
            
            with st.spinner("Simulating consumer behavior and auditing 4 Ps..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7
                    )
                    
                    # Parse JSON Output
                    raw_content = response.choices[0].message.content.strip()
                    eval_data = json.loads(raw_content)
                    
                    # Render Metric Card
                    score = eval_data.get("purchase_intent_score", 0)
                    verdict = eval_data.get("persona_verdict", "N/A")
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Purchase Intent Score & Verdict</div>
                        <div class="metric-value">{score}% <span style="font-size: 1.5rem;">({verdict})</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Render Persona Monologue
                    st.markdown("**🗣️ Consumer First-Person Reaction:**")
                    st.markdown(f'<div class="persona-quote">"{eval_data.get("internal_monologue")}"</div>', unsafe_allow_html=True)
                    
                    # Render 4 Ps Breakdown
                    st.markdown("**📋 4 Ps Strategy Audit:**")
                    p_data = eval_data.get("p_breakdown", {})
                    
                    for p_name, p_val in p_data.items():
                        status_class = "pass-tag" if p_val['status'] == "PASS" else "fail-tag"
                        st.markdown(f"- **{p_name.capitalize()}** [<span class='{status_class}'>{p_val['status']}</span>]: {p_val['comment']}", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown("**💡 Professor's Recommendation:**")
                    st.info(eval_data.get("strategic_recommendation"))
                    
                except Exception as e:
                    st.error(f"Error generating simulation: {str(e)}")
    else:
        st.info("👈 Fill out the Marketing Mix form on the left and click **Run Persona Simulation** to view feedback.")
