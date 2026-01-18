import streamlit as st
import random
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timezone
import uuid

@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

st.set_page_config(page_title="BehEconExp", layout="centered")


def log_trial():
    """Log trial data to Supabase - instant and reliable"""

    row_data = {
        "participant_id": st.session_state.participant_id, 
        "order_name": st.session_state.order_name, # For block order names 
        "block": st.session_state.block_index + 1,
        "condition": st.session_state.condition,
        "round": st.session_state.round,
        "choice": st.session_state.last_choice,
        "outcome": st.session_state.last_outcome,
        "p_win": st.session_state.debug_p_win,
        "win_streak": st.session_state.win_streak,
        "loss_streak": st.session_state.loss_streak,
        "balance": st.session_state.balance,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reaction_time_ms": st.session_state.reaction_time_ms
    }

    try:
        supabase.table("experiment_data").insert(row_data).execute()
    except Exception as e:
        print(f"Database error: {e}")
        # Optionally store in session state as fallback
        if "failed_rows" not in st.session_state:
            st.session_state.failed_rows = []
        st.session_state.failed_rows.append(row_data)

# Message pools for variety in feedback
VISUAL_MESSAGES = {
    "safe": [
        "You chose the safe option. +1 added.",
        "Safe choice selected. +1 to your balance.",
        "You played it safe. +1 earned."
    ],
    "win": [
        "You chose the risky option and won. +4 added.",
        "Your risky bet paid off. +4 to your balance.",
        "You took the risk and won. +4 earned."
    ],
    "loss": [
        "You chose the risky option and lost. -2 deducted.",
        "Risky bet didn't pay off. -2 from your balance.",
        "You took the risk and lost. -2 deducted."
    ]
}

AFFECTIVE_MESSAGES = {
    "safe": [
        "😌 You chose stability. A calm +1.",
        "🛡️ Playing it safe. Steady +1 added.",
        "✓ Safe and sound. +1 to your balance."
    ],
    "win_neutral": [  # For streaks 0-2
        "🎉 Nice hit! +4 added.",
        "✨ You won the risky bet! +4 earned.",
        "💵 Risky choice paid off! +4 to your balance."
    ],
    "win_hot": [  # For streaks 3+
        "🚀 Another win! The streak keeps rolling!",
        "🔥 You're unstoppable! +4 added to the fire!",
        "⚡ The momentum continues! +4 and counting!"
    ],
    "loss_neutral": [  # For streaks 0-2
        "😬 Tough loss. -2 deducted.",
        "💸 Didn't work out this time. -2 from your balance.",
        "😕 The risk didn't pay off. -2 deducted."
    ],
    "loss_cold": [  # For streaks 3+
        "😖 Ouch, another loss. The slide continues.",
        "💔 The streak persists. -2 deducted.",
        "😣 Tough break again. -2 from your balance."
    ]
}


# ===== INITIALIZE ALL SESSION STATE VARIABLES =====
if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())

if "block_order" not in st.session_state:
    # Fixed block orders for counterbalancing (25% chance each) 
    possible_orders = [
        ["neutral", "visual", "affective", "de-salience"],      # Order 1 (NVAD)
        ["visual", "de-salience", "neutral", "affective"],      # Order 2 (VDNA)
        ["affective", "neutral", "de-salience", "visual"],      # Order 3 (ANDV)
        ["de-salience", "affective", "visual", "neutral"]       # Order 4 (DAVN)
    ]

    # Randomly assign one of the four orders
    st.session_state.block_order = random.choice(possible_orders)
    
    # Store order name for easy analysis
    order_names = {
        "neutral-visual-affective-de-salience": "Order1_NVAD",
        "visual-de-salience-neutral-affective": "Order2_VDNA",
        "affective-neutral-de-salience-visual": "Order3_ANDV",
        "de-salience-affective-visual-neutral": "Order4_DAVN"
    }
    order_key = "-".join(st.session_state.block_order)
    st.session_state.order_name = order_names.get(order_key, "Unknown")

# Initialize session state variables
if "block_index" not in st.session_state:
    st.session_state.block_index = 0

if "block" not in st.session_state:
    st.session_state.block = 0

if "round" not in st.session_state:
    st.session_state.round = 0

if "balance" not in st.session_state:
    st.session_state.balance = 20

if "condition" not in st.session_state:
    st.session_state.condition = "neutral"

if "started" not in st.session_state:
    st.session_state.started = False

if "win_streak" not in st.session_state:
    st.session_state.win_streak = 0

if "loss_streak" not in st.session_state:
    st.session_state.loss_streak = 0

if "last_risk_outcome" not in st.session_state:
    st.session_state.last_risk_outcome = None

if "last_outcome" not in st.session_state:
    st.session_state.last_outcome = None

if "last_choice" not in st.session_state:
    st.session_state.last_choice = None

if "awaiting_feedback" not in st.session_state:
    st.session_state.awaiting_feedback = False

if "in_break" not in st.session_state:
    st.session_state.in_break = False

if "bias_rounds_left" not in st.session_state:
    st.session_state.bias_rounds_left = 0

if "bias_rounds_active" not in st.session_state:
    st.session_state.bias_rounds_active = False

if "debug_p_win" not in st.session_state:
    st.session_state.debug_p_win = None

if "round_start_time" not in st.session_state:
    st.session_state.round_start_time = datetime.now(timezone.utc)

if "reaction_time_ms" not in st.session_state:
    st.session_state.reaction_time_ms = None

# CSS for animations
# CSS for animations
st.markdown("""
<style>
@keyframes pulse {
  0% { transform: scale(1); }
  120% { transform: scale(1.05); }
  200% { transform: scale(1); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

@keyframes growShake {
  0% { transform: scale(1) rotate(0deg); }
  80% { transform: scale(1.3) rotate(-5deg); }
  120% { transform: scale(1.3) rotate(5deg); }
  160% { transform: scale(1.3) rotate(-5deg); }
  200% { transform: scale(1) rotate(0deg); }
}

@keyframes glow {
  0%, 100% { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
  50% { box-shadow: 0 6px 24px rgba(0,0,0,0.15); }
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}

.bounce {
  animation: bounce 1s ease-in-out infinite;
}

.streak-burst {
  animation: growShake 0.5s ease-out;
}

.glow-pulse {
  animation: glow 2s ease-in-out infinite;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Clean up Streamlit defaults */
.block-container {
    padding-top: 4rem;  /* <-- CHANGED from 2rem to 4rem */
    max-width: 900px;
}

/* Add spacing for metrics */
[data-testid="stMetricLabel"] {
    padding-top: 8px;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Modern metric cards at top */
[data-testid="stMetricValue"] {
    font-size: 28px;
    font-weight: 700;
}

/* MUCH LARGER betting-style buttons */
div.stButton > button {
    width: 100%;
    height: 140px;
    font-size: 24px;
    font-weight: 700;
    border-radius: 16px;
    margin: 8px 0;
    border: 3px solid #e0e0e0;
    background: linear-gradient(to bottom, #ffffff, #f8f9fa);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    border-color: #4CAF50;
}

div.stButton > button:active {
    transform: translateY(0);
}

/* Disabled button state */
div.stButton > button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Clean banner styling for visual/affective blocks */
.info-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.streak-display {
    display: inline-block;
    padding: 12px 20px;
    margin: 8px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.win-streak {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
}

.loss-streak {
    background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    color: white;
}

/* Subheader styling */
.stSubheader {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #1a1a1a;
}

/* Info/success/error messages */
.stAlert {
    border-radius: 12px;
    padding: 16px;
    font-size: 16px;
    margin: 16px 0;
}
/* Balance change animations */
@keyframes fadeInOut {
  0% { opacity: 0; transform: translateY(0); }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { opacity: 0; transform: translateY(-10px); }
}

@keyframes slideUpFade {
  0% { opacity: 0; transform: translateY(0) scale(1); }
  15% { opacity: 1; transform: translateY(-5px) scale(1.1); }
  30% { transform: scale(1); }
  100% { opacity: 0; transform: translateY(-30px); }
}

@keyframes bounceUpGlow {
  0% { opacity: 0; transform: translateY(0) scale(1); filter: brightness(1); }
  20% { opacity: 1; transform: translateY(-10px) scale(1.2); filter: brightness(1.3); }
  40% { transform: translateY(-5px) scale(1.1); }
  60% { transform: translateY(-15px) scale(1.15); }
  100% { opacity: 0; transform: translateY(-40px) scale(0.9); filter: brightness(1); }
}

@keyframes shakeFlash {
  0% { opacity: 0; transform: translateX(0) scale(1); filter: brightness(1); }
  10% { opacity: 1; transform: translateX(-5px) scale(1.1); filter: brightness(1.5); }
  20% { transform: translateX(5px); }
  30% { transform: translateX(-5px); }
  40% { transform: translateX(3px); }
  50% { transform: translateX(-3px) scale(1.05); }
  100% { opacity: 0; transform: translateX(0) translateY(-20px); filter: brightness(1); }
}

@keyframes quickFade {
  0% { opacity: 0; }
  30% { opacity: 0.6; }
  100% { opacity: 0; }
}

.balance-change-neutral {
  animation: fadeInOut 1s ease-out;
  color: #333333;
  font-size: 18px;
  font-weight: 500;
  margin-left: 8px;
  display: inline-block;
  position: relative;
}

.balance-change-visual {
  animation: slideUpFade 1.5s ease-out;
  font-size: 26px;
  font-weight: 700;
  margin-left: 12px;
  display: inline-block;
  position: relative;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.balance-change-affective-win {
  animation: bounceUpGlow 2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  font-size: 34px;
  font-weight: 800;
  margin-left: 12px;
  display: inline-block;
  position: relative;
  text-shadow: 0 0 10px currentColor, 0 4px 8px rgba(0,0,0,0.3);
}

.balance-change-affective-loss {
  animation: shakeFlash 2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  font-size: 34px;
  font-weight: 800;
  margin-left: 12px;
  display: inline-block;
  position: relative;
  text-shadow: 0 0 10px currentColor, 0 4px 8px rgba(0,0,0,0.3);
}

.balance-change-desalience {
  animation: quickFade 0.5s ease-out;
  color: #757575;
  font-size: 14px;
  font-weight: 300;
  margin-left: 6px;
  display: inline-block;
  position: relative;
  opacity: 0.7;
}

.color-safe { color: #2196F3; }
.color-win { color: #4CAF50; }
.color-loss { color: #f44336; }
.color-affective-win { color: #00E676; }
.color-affective-loss { color: #D32F2F; }
</style>
""", unsafe_allow_html=True)



def continue_after_feedback():
    # Clear animation flag FIRST before any other updates
    if "animation_shown" in st.session_state:
        del st.session_state.animation_shown
    
    # Update streaks based on last outcome
    if st.session_state.last_outcome == "win":
        st.session_state.win_streak += 1
        st.session_state.loss_streak = 0
        st.session_state.last_risk_outcome = "win"

        if (
                st.session_state.win_streak == 3
                and not st.session_state.bias_rounds_active
        ):
            st.session_state.bias_rounds_left = 3
            st.session_state.bias_rounds_active = True

    elif st.session_state.last_outcome == "loss":
        st.session_state.loss_streak += 1
        st.session_state.win_streak = 0
        st.session_state.last_risk_outcome = "loss"

        if (
                st.session_state.loss_streak == 3
                and not st.session_state.bias_rounds_active
        ):
            st.session_state.bias_rounds_left = 3
            st.session_state.bias_rounds_active = True

    log_trial()  # (< 100ms)

    # Advance round
    st.session_state.round += 1

    # Clear feedback state
    st.session_state.awaiting_feedback = False
    st.session_state.last_outcome = None

    # Reset round timer for next round
    st.session_state.round_start_time = datetime.now(timezone.utc)

    # Enter break exactly once at round limit
    if st.session_state.round >= 30:
        st.session_state.in_break = True
        # Clear all feedback state when entering break 
        st.session_state.awaiting_feedback = False 
        st.session_state.last_outcome = None 
        st.session_state.last_choice = None 


def update_condition_from_block():
    st.session_state.condition = st.session_state.block_order[st.session_state.block_index]


def emotional_context(win_streak, loss_streak):
    if win_streak >= 3:
        return {
            "tone": "hot",
            "color": "#fff3cd",
            "message": "🔥 You’re on fire!",
            "sub": "Most players press their advantage here."
        }
    elif loss_streak >= 3:
        return {
            "tone": "cold",
            "color": "#f8d7da",
            "message": "😬 Rough stretch...",
            "sub": "Many players try to recover losses now."
        }
    else:
        return {
            "tone": "neutral",
            "color": "#e2e3e5",
            "message": "🤔 Momentum is building",
            "sub": "What will you do next?"
        }


def show_balance_change_animation(amount, condition, outcome_type):
    """
    Display animated balance change based on condition
    amount: +1, +2, or -2
    condition: "neutral", "visual", "affective", "de-salience"
    outcome_type: "safe", "win", "loss"
    """

    # Format the display text
    if amount > 0:
        display_text = f"+${amount}"
    else:
        display_text = f"-${abs(amount)}"

    # Determine animation class and color
    if condition == "neutral":
        anim_class = "balance-change-neutral"
        color_class = ""
        emoji = ""

    elif condition == "visual":
        anim_class = "balance-change-visual"
        if outcome_type == "safe":
            color_class = "color-safe"
        elif outcome_type == "win":
            color_class = "color-win"
        else:
            color_class = "color-loss"
        emoji = ""

    elif condition == "affective":
        if outcome_type == "win" or outcome_type == "safe":
            anim_class = "balance-change-affective-win"
            color_class = "color-affective-win"
            emoji = "💰 " if outcome_type == "win" else "✓ "
        else:
            anim_class = "balance-change-affective-loss"
            color_class = "color-affective-loss"
            emoji = "💔 "

    else:  # de-salience
        anim_class = "balance-change-desalience"
        color_class = ""
        emoji = ""

    # Generate the HTML
    animation_html = f'<span class="{anim_class} {color_class}">{emoji}{display_text}</span>'

    return animation_html

# streak logic
def biased_risk_outcome(win_streak, loss_streak, bias_rounds_left):
    """
    Returns (outcome, p_win)

    Streaks 1-3: fair 0.5 probability
    After 3-streak: cluster biases activates for exactly 3 rounds based on bias_rounds_left
    Then returns back to 0.5
    """

    # default fair probability
    p_win = 0.5

    # only apply bias if active (during the 3-round bias window)
    if bias_rounds_left > 0 and st.session_state.bias_rounds_active:

        # Win streak bias - based on how many bias rounds are left
        if win_streak >= 3:
            if bias_rounds_left == 3:  # 4th outcome in streak
                p_win = 0.75
            elif bias_rounds_left == 2:  # 5th outcome in streak
                p_win = 0.80
            elif bias_rounds_left == 1:  # 6th outcome in streak
                p_win = 0.85

        # Loss streak bias - based on how many bias rounds are left
        if loss_streak >= 3:
            if bias_rounds_left == 3:  # 4th outcome in streak
                p_win = 0.25
            elif bias_rounds_left == 2:  # 5th outcome in streak
                p_win = 0.20
            elif bias_rounds_left == 1:  # 6th outcome in streak
                p_win = 0.15

    outcome = 1 if random.random() < p_win else -1
    return outcome, p_win


# show an introduction screen with brief instructions and a start button for the participant / player
def _start_experiment():
    st.session_state.started = True
    st.session_state.block = 1
    st.session_state.block_index = 0  # Start at first randomized block
    update_condition_from_block()


# Only to show title and welcome on intro screen
if not st.session_state.started:
    st.title("The Market's Pulse")
    st.header("Welcome")
    st.write(
    "In this game, you will be making a series of decisions in a simulated betting environment. "
    "Your goal is to maximize your earnings over the course of the game.\n\n"

    "In each round, you will choose between:\n"
    "- A **safe bet** that guarantees +1 \n"
    "- A **risky bet** that can result in a gain (+4) or a loss (-2) \n\n"

    "Outcomes of the risky option are determined by a computerized random process. "
    "As the game progresses, you may observe patterns or streaks in outcomes.\n\n"

    "**To be eligible for the free but random $50 participation prize, you must complete all rounds of the game** "
    "and submit the short form that will appear at the end of the experiment.\n\n"
    "Good luck!" 
    )
    st.write(f"Starting balance: {st.session_state.balance}")
    st.button("Start Experiment", on_click=_start_experiment)
    
# Initialize break timer if not exists
if "break_start_time" not in st.session_state:
    st.session_state.break_start_time = None

# Main experiment logic
if st.session_state.started and st.session_state.in_break:
    
    # Start the break timer on first entry
    if st.session_state.break_start_time is None:
        st.session_state.break_start_time = datetime.now(timezone.utc)
    
    # Calculate elapsed time
    elapsed = (datetime.now(timezone.utc) - st.session_state.break_start_time).total_seconds()
    remaining = max(0, 20 - int(elapsed))
    
    # Clear any previous content
    st.empty()
    
    st.header("Break Time!")
    st.write("Please take a short break before continuing to the next block.")
    st.write("The next block will begin automatically when the timer reaches zero.")
    
    st.divider()

    st.warning("""
    ⚠️ **New Block Starting**
    
    **Each block is independent. Your balance has been reset to $20.**
    - Do not rely on strategies from the previous block
    - Pay close attention to how information is presented in this next block
    - Make decisions based on what you observe here
    
    **Make decisions based only on what you observe in this next block.**

    Previous outcomes do not predict future results.
    """)
    
    st.divider()

    # Mindless task: Moving countdown
    if remaining > 0:
        # Generate pseudo-random but stable position based on remaining time
        # This ensures position changes each second but stays stable between reruns
        import hashlib
        position_seed = int(hashlib.md5(f"{remaining}".encode()).hexdigest(), 16)
        
        # Random position (0-80% of width to keep it visible)
        left_position = (position_seed % 80)
        top_position = ((position_seed // 100) % 60) + 20  # 20-80% of height
        
        countdown_html = f"""
        <div style="
            position: fixed;
            left: {left_position}%;
            top: {top_position}%;
            font-size: 48px;
            font-weight: 700;
            color: #4CAF50;
            background: white;
            padding: 20px 30px;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            z-index: 1000;
            transition: all 0.3s ease;
        ">
            Break over in {remaining}
        </div>
        """
        st.markdown(countdown_html, unsafe_allow_html=True)
        
        # Auto-refresh every second
        import time
        time.sleep(1)
        st.rerun()
    
    else:
        # Break is over - show continue button
        st.success("✅ Break complete! You may now continue.")
        
        st.write("")  # Add spacing
        
        if st.button("Continue to Next Block", use_container_width=True):
            st.session_state.block += 1
            st.session_state.block_index += 1
            st.session_state.round = 0
            st.session_state.in_break = False
            
            # RESET BALANCE TO STARTING AMOUNT
            st.session_state.balance = 20
            
            # HARD RESET OF BIAS
            st.session_state.bias_rounds_left = 0
            st.session_state.bias_rounds_active = False
            
            # HARD RESET OF STREAKS
            st.session_state.win_streak = 0
            st.session_state.loss_streak = 0
            
            # RESET BREAK TIMER
            st.session_state.break_start_time = None
            
            # Only update condition if not finished
            if st.session_state.block_index < 4:
                update_condition_from_block()
            
            st.rerun()

# Experiment complete screen
if (
    st.session_state.started
    and st.session_state.block > 4
):
    st.header("🎉 Experiment Complete!")
    st.success("✅ Your responses have been recorded successfully.")
    st.write("Thank you so much for participating in this behavioral economics study.")

    st.divider()

    st.link_button(
    "**To be eligible for the gift card draw, please fill out this form. It will take less than 3 minutes**",
    "https://forms.gle/sbfs6J8UXEm61aRYA"
    )

    st.divider()






# --- NEUTRAL BLOCK ---
if (
        st.session_state.started
        and not st.session_state.in_break
        and st.session_state.block <= 4
        and st.session_state.condition == "neutral"
):

    # Clean info display at top
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Block", st.session_state.block)
    with col2:
        st.metric("Round", f"{st.session_state.round + 1}/30")
    with col3:
        if (st.session_state.awaiting_feedback and st.session_state.last_outcome and "animation_shown" not in st.session_state):
            # Determine amount changed
            if st.session_state.last_outcome == "safe":
                amount = 1
                outcome_type = "safe"
            elif st.session_state.last_outcome == "win":
                amount = 4
                outcome_type = "win"
            else:
                amount = -2
                outcome_type = "loss"

            animation = show_balance_change_animation(amount, "neutral", outcome_type)
            st.markdown(
                f"<div style='font-size: 14px; color: #666; margin-bottom: 4px;'>Balance</div><div style='font-size: 28px; font-weight: 700;'>${st.session_state.balance} {animation}</div>",
                unsafe_allow_html=True)
            st.session_state.animation_shown = True
        else:
            st.metric("Balance", st.session_state.balance)

    st.divider()


    def _choose_safe():
        st.session_state.balance += 1
        st.session_state.awaiting_feedback = True
        st.session_state.last_choice = "safe"
        st.session_state.last_outcome = "safe"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000
        st.session_state.reaction_time_ms = rt_ms


    def _choose_risk():
        outcome, p_win = biased_risk_outcome(
            st.session_state.win_streak,
            st.session_state.loss_streak,
            st.session_state.bias_rounds_left
        )

        st.session_state.debug_p_win = p_win
        st.session_state.last_choice = "risk"

        # decrement bias window only if active
        if st.session_state.bias_rounds_left > 0:
            st.session_state.bias_rounds_left -= 1

            if st.session_state.bias_rounds_left == 0:
                st.session_state.bias_rounds_active = False

        if outcome == 1: 
            st.session_state.balance += 4 # Win 
        else: 
            st.session_state.balance -= 2 # Loss 
        st.session_state.awaiting_feedback = True
        st.session_state.last_outcome = "win" if outcome == 1 else "loss"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000

        st.session_state.reaction_time_ms = rt_ms


    # Larger buttons side by side
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.button("Safe Option\n\(+1)", on_click=_choose_safe, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)
    with col2:
        st.button("Risky Option\n(+4 / -2)", on_click=_choose_risk, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)

    # awaiting feedback from the player
    if st.session_state.awaiting_feedback:
        st.divider()

        feedback_col, button_col = st.columns([2, 1])

        with feedback_col:
            if st.session_state.last_outcome == "safe":
                st.info("You chose the safe option. +1 added.")
            elif st.session_state.last_outcome == "win":
                st.success("You chose the risky option and won. +2 added.")
            elif st.session_state.last_outcome == "loss":
                st.error("You chose the risky option and lost. -2 deducted.")

        with button_col:
            st.write("")
            st.button("Continue →", on_click=continue_after_feedback, use_container_width=True)

# if any block is complete, must enter a break period before the next block


# --- VISUAL BLOCK ---
if (
        st.session_state.started
        and not st.session_state.in_break
        and st.session_state.block <= 4
        and st.session_state.condition == "visual"
):

    # Clean info display at top
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Block", st.session_state.block)
    with col2:
        st.metric("Round", f"{st.session_state.round + 1}/30")
    with col3:
        if (st.session_state.awaiting_feedback and st.session_state.last_outcome and "animation_shown" not in st.session_state):
            # Determine amount changed
            if st.session_state.last_outcome == "safe":
                amount = 1
                outcome_type = "safe"
            elif st.session_state.last_outcome == "win":
                amount = 4
                outcome_type = "win"
            else:
                amount = -2
                outcome_type = "loss"

            animation = show_balance_change_animation(amount, "visual", outcome_type)
            st.markdown(
                f"<div style='font-size: 14px; color: #665; margin-bottom: 4px;'>Balance</div><div style='font-size: 28px; font-weight: 700;'>${st.session_state.balance} {animation}</div>",
                unsafe_allow_html=True)
            st.session_state.animation_shown = True
        else:
            st.metric("Balance", st.session_state.balance)

    st.divider()

    # Simple, clean streak display
    banner_html = f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 16px;
                margin-bottom: 24px;
                box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);">
        <div style="font-size: 18px; font-weight: 600; margin-bottom: 12px;">Current Streaks</div>
        <div style="display: flex; gap: 12px; justify-content: center;">
            <span class="streak-display win-streak"> Win Streak: {st.session_state.win_streak}</span>
            <span class="streak-display loss-streak"> Loss Streak: {st.session_state.loss_streak}</span>
        </div>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)


    def _choose_safe():
        st.session_state.balance += 1
        st.session_state.awaiting_feedback = True
        st.session_state.last_choice = "safe"
        st.session_state.last_outcome = "safe"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000
        st.session_state.reaction_time_ms = rt_ms


    def _choose_risk():
        outcome, p_win = biased_risk_outcome(
            st.session_state.win_streak,
            st.session_state.loss_streak,
            st.session_state.bias_rounds_left
        )

        st.session_state.debug_p_win = p_win
        st.session_state.last_choice = "risk"

        # decrement bias window only if active
        if st.session_state.bias_rounds_left > 0:
            st.session_state.bias_rounds_left -= 1

            if st.session_state.bias_rounds_left == 0:
                st.session_state.bias_rounds_active = False

        if outcome == 1: 
            st.session_state.balance += 4 # Win 
        else: 
            st.session_state.balance -= 2 # Loss 
        st.session_state.awaiting_feedback = True
        st.session_state.last_outcome = "win" if outcome == 1 else "loss"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000

        st.session_state.reaction_time_ms = rt_ms


    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.button("Safe Option\n(+1)", on_click=_choose_safe, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)
    with col2:
        st.button("Risky Option\n(+4 / -2)", on_click=_choose_risk, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)

    if st.session_state.awaiting_feedback:
        st.divider()
    
        feedback_col, button_col = st.columns([2, 1])
    
        with feedback_col:
            if st.session_state.last_outcome == "safe":
                message = random.choice(VISUAL_MESSAGES["safe"])
                st.info(message)
            elif st.session_state.last_outcome == "win":
                message = random.choice(VISUAL_MESSAGES["win"])
                st.success(message)
            elif st.session_state.last_outcome == "loss":
                message = random.choice(VISUAL_MESSAGES["loss"])
                st.error(message)
    
        with button_col:
            st.write("")
            st.button("Continue →", on_click=continue_after_feedback, use_container_width=True)

# --- AFFECTIVE BLOCK ---
if (
        st.session_state.started
        and not st.session_state.in_break
        and st.session_state.block <= 4
        and st.session_state.condition == "affective"
):

    ctx = emotional_context(st.session_state.win_streak, st.session_state.loss_streak)

    # Clean info display at top
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Block", st.session_state.block)
    with col2:
        st.metric("Round", f"{st.session_state.round + 1}/30")
    with col3:
        if (st.session_state.awaiting_feedback and 
        st.session_state.last_outcome and 
        "animation_shown" not in st.session_state):
            # Determine amount changed
            if st.session_state.last_outcome == "safe":
                amount = 1
                outcome_type = "safe"
            elif st.session_state.last_outcome == "win":
                amount = 4
                outcome_type = "win"
            else:
                amount = -2
                outcome_type = "loss"

            animation = show_balance_change_animation(amount, "affective", outcome_type)
            st.markdown(
                f"<div style='font-size: 14px; color: #666; margin-bottom: 4px;'>Balance</div><div style='font-size: 28px; font-weight: 700;'>${st.session_state.balance} {animation}</div>",
                unsafe_allow_html=True)
            st.session_state.animation_shown = True
        else:
            st.metric("Balance", st.session_state.balance)

    st.divider()

    # Determine border styling
    if ctx["tone"] == "hot":
        border_color = "#0b6623"  # green
        border_width = "4px"
    elif ctx["tone"] == "cold":
        border_color = "#8b0000"  # red
        border_width = "4px"
    else:
        border_color = "#444444"  # neutral dark
        border_width = "2px"

    if ctx["tone"] == "hot":
        subtext = f"You're on fire! {st.session_state.win_streak} wins in a row! 🔥"
    elif ctx["tone"] == "cold":
        subtext = f"Hang in there… {st.session_state.loss_streak} losses in a row 💔"
    else:
        subtext = "Steady as she goes. Keep your focus."

    # baseline emoji size grows with streak (capped)
    win_size = min(22 + st.session_state.win_streak * 2, 32)
    loss_size = min(22 + st.session_state.loss_streak * 2, 32)

    # will trigger burst animation only immediately after outcome
    win_burst = (
            st.session_state.awaiting_feedback
            and st.session_state.last_outcome == "win"
    )
    loss_burst = (
            st.session_state.awaiting_feedback
            and st.session_state.last_outcome == "loss"
    )

    pulse_class = "pulse" if ctx['tone'] != 'neutral' else ""
    win_burst_class = "streak-burst" if win_burst else ""
    loss_burst_class = "streak-burst" if loss_burst else ""

    # affective banner
    if ctx["tone"] == "hot":
        border_color = "#0b6623"
        gradient_end = "#fff9e6"
    elif ctx["tone"] == "cold":
        border_color = "#8b0000"
        gradient_end = "#ffe6e6"
    else:
        border_color = "#444444"
        gradient_end = "#f5f5f5"

    if ctx["tone"] == "hot":
        subtext = f"You're on fire! {st.session_state.win_streak} wins in a row! 🔥"
    elif ctx["tone"] == "cold":
        subtext = f"Hang in there… {st.session_state.loss_streak} losses in a row 💔"
    else:
        subtext = "Steady as she goes. Keep your focus."

    win_size = min(22 + st.session_state.win_streak * 2, 32)
    loss_size = min(22 + st.session_state.loss_streak * 2, 32)

    win_burst = st.session_state.awaiting_feedback and st.session_state.last_outcome == "win"
    loss_burst = st.session_state.awaiting_feedback and st.session_state.last_outcome == "loss"

    pulse_class = "pulse" if ctx['tone'] != 'neutral' else ""
    win_burst_class = "streak-burst" if win_burst else ""
    loss_burst_class = "streak-burst" if loss_burst else ""

    # Determine border styling and animations
    if ctx["tone"] == "hot":
        border_color = "#0b6623"
        gradient_end = "#fff9e6"
        banner_animation = "pulse glow-pulse"
    elif ctx["tone"] == "cold":
        border_color = "#8b0000"
        gradient_end = "#ffe6e6"
        banner_animation = "pulse glow-pulse"
    else:
        border_color = "#444444"
        gradient_end = "#f5f5f5"
        banner_animation = ""

    if ctx["tone"] == "hot":
        subtext = f"You're on fire! {st.session_state.win_streak} wins in a row! 🔥"
    elif ctx["tone"] == "cold":
        subtext = f"Hang in there… {st.session_state.loss_streak} losses in a row 💔"
    else:
        subtext = "Steady as she goes. Keep your focus."

    # Progressive emoji sizing based on streak
    win_size = 22 + (st.session_state.win_streak * 3)  # Grows 3px per streak
    loss_size = 22 + (st.session_state.loss_streak * 3)

    # Trigger burst animation only on new outcome
    win_burst = st.session_state.awaiting_feedback and st.session_state.last_outcome == "win"
    loss_burst = st.session_state.awaiting_feedback and st.session_state.last_outcome == "loss"

    # Continuous bounce when streak is active
    win_continuous = "bounce" if st.session_state.win_streak >= 3 else ""
    loss_continuous = "bounce" if st.session_state.loss_streak >= 3 else ""

    # Burst takes priority over continuous
    win_animation = "streak-burst" if win_burst else win_continuous
    loss_animation = "streak-burst" if loss_burst else loss_continuous

    banner_html = f"""
    <div style="background: linear-gradient(135deg, {ctx['color']} 0%, {gradient_end} 100%); padding: 24px; border-radius: 16px; border: 3px solid {border_color}; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.08);" class="{banner_animation}">
        <div style="font-size: 24px; font-weight: 700; margin-bottom: 8px;">{ctx['message']}</div>
        <div style="font-size: 14px; opacity: 0.85; margin-bottom: 16px;">{subtext}</div>
    </div>

    <div style="display: flex; gap: 16px; margin-bottom: 20px; justify-content: center;">
        <div style="background: white; padding: 16px 24px; border-radius: 16px; font-weight: 700; display: flex; align-items: center; gap: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); flex: 1; max-width: 200px; transition: all 0.3s ease;">
            <span class="{win_animation}" style="font-size: {win_size}px; display: inline-block; transition: font-size 0.3s ease;">🔥</span>
            <div style="text-align: left;">
                <div style="font-size: 11px; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.5px;">Win Streak</div>
                <div style="font-size: 32px; color: #0b6623; line-height: 1;">{st.session_state.win_streak}</div>
            </div>
        </div>
        <div style="background: white; padding: 16px 24px; border-radius: 16px; font-weight: 700; display: flex; align-items: center; gap: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); flex: 1; max-width: 200px; transition: all 0.3s ease;">
            <span class="{loss_animation}" style="font-size: {loss_size}px; display: inline-block; transition: font-size 0.3s ease;">💔</span>
            <div style="text-align: left;">
                <div style="font-size: 11px; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.5px;">Loss Streak</div>
                <div style="font-size: 32px; color: #8b0000; line-height: 1;">{st.session_state.loss_streak}</div>
            </div>
        </div>
    </div>

    <div style="text-align: center; font-size: 13px; opacity: 0.7; font-style: italic;">Momentum like this doesn't last forever.</div>
    """

    st.markdown(banner_html, unsafe_allow_html=True)


    def _choose_safe():
        st.session_state.balance += 1
        st.session_state.awaiting_feedback = True
        st.session_state.last_choice = "safe"
        st.session_state.last_outcome = "safe"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000
        st.session_state.reaction_time_ms = rt_ms


    def _choose_risk():
        outcome, p_win = biased_risk_outcome(
            st.session_state.win_streak,
            st.session_state.loss_streak,
            st.session_state.bias_rounds_left
        )

        st.session_state.debug_p_win = p_win
        st.session_state.last_choice = "risk"

        # decrement bias window only if active
        if st.session_state.bias_rounds_left > 0:
            st.session_state.bias_rounds_left -= 1

            if st.session_state.bias_rounds_left == 0:
                st.session_state.bias_rounds_active = False

        if outcome == 1: 
            st.session_state.balance += 4 # Win 
        else: 
            st.session_state.balance -= 2 # Loss 
        st.session_state.awaiting_feedback = True
        st.session_state.last_outcome = "win" if outcome == 1 else "loss"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000

        st.session_state.reaction_time_ms = rt_ms


    safe_label = "🛑 Play it safe (+1)"
    risk_label = "🎯 Take the risk (±2)"
    if ctx["tone"] == "hot":
        risk_label = "🔥 Press the advantage (±2)"
    elif ctx["tone"] == "cold":
        risk_label = "💥 Try to bounce back (±2)"

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.button(safe_label, on_click=_choose_safe, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)
    with col2:
        st.button(risk_label, on_click=_choose_risk, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)

    if ctx["tone"] in ["hot", "cold"]:
        st.caption("⏳ Momentum like this rarely lasts.")
    else:
        st.caption("⏳ Each round is a fresh opportunity.")

    # awaiting feedback from the player
    if st.session_state.awaiting_feedback:
        st.divider()
    
        feedback_col, button_col = st.columns([2, 1])
    
        with feedback_col:
            if st.session_state.last_outcome == "safe":
                message = random.choice(AFFECTIVE_MESSAGES["safe"])
                st.info(message)
            elif st.session_state.last_outcome == "win":
                if ctx["tone"] == "hot":
                    message = random.choice(AFFECTIVE_MESSAGES["win_hot"])
                else:
                    message = random.choice(AFFECTIVE_MESSAGES["win_neutral"])
                st.success(message)
            elif st.session_state.last_outcome == "loss":
                if ctx["tone"] == "cold":
                    message = random.choice(AFFECTIVE_MESSAGES["loss_cold"])
                else:
                    message = random.choice(AFFECTIVE_MESSAGES["loss_neutral"])
                st.error(message)
    
        with button_col:
            st.write("")
            st.button("Continue →", on_click=continue_after_feedback, use_container_width=True)

# --- DE-SALIENCE BLOCK ---
if (
        st.session_state.started
        and not st.session_state.in_break
        and st.session_state.block <= 4
        and st.session_state.condition == "de-salience"
):

    # Clean info display at top
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Block", st.session_state.block)
    with col2:
        st.metric("Round", f"{st.session_state.round + 1}/30")
    with col3:
        if (st.session_state.awaiting_feedback and
            st.session_state.last_outcome and
            "animation_shown" not in st.session_state):
            # Determine amount changed
            if st.session_state.last_outcome == "safe":
                amount = 1
                outcome_type = "safe"
            elif st.session_state.last_outcome == "win":
                amount = 4
                outcome_type = "win"
            else:
                amount = -2
                outcome_type = "loss"

            animation = show_balance_change_animation(amount, "de-salience", outcome_type)
            st.markdown(
                f"<div style='font-size: 14px; color: #666; margin-bottom: 4px;'>Balance</div><div style='font-size: 28px; font-weight: 700;'>${st.session_state.balance} {animation}</div>",
                unsafe_allow_html=True)
            st.session_state.animation_shown = True

        else:
            st.metric("Balance", st.session_state.balance)

    st.divider()

    st.caption("Each round is independent. Previous outcomes do not affect future results.")


    def _choose_safe():
        st.session_state.balance += 1
        st.session_state.awaiting_feedback = True
        st.session_state.last_choice = "safe"
        st.session_state.last_outcome = "safe"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000
        st.session_state.reaction_time_ms = rt_ms


    def _choose_risk():
        outcome, p_win = biased_risk_outcome(
            st.session_state.win_streak,
            st.session_state.loss_streak,
            st.session_state.bias_rounds_left
        )

        st.session_state.debug_p_win = p_win
        st.session_state.last_choice = "risk"

        # decrement bias window only if active
        if st.session_state.bias_rounds_left > 0:
            st.session_state.bias_rounds_left -= 1

            if st.session_state.bias_rounds_left == 0:
                st.session_state.bias_rounds_active = False

        if outcome == 1: 
            st.session_state.balance += 4 # Win 
        else: 
            st.session_state.balance -= 2 # Loss 
        st.session_state.awaiting_feedback = True
        st.session_state.last_outcome = "win" if outcome == 1 else "loss"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000

        st.session_state.reaction_time_ms = rt_ms


    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.button("Safe Option\n(+1)", on_click=_choose_safe, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)
    with col2:
        st.button("Risky Option\n(+4 / -2)", on_click=_choose_risk, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)

    if st.session_state.awaiting_feedback:
        st.divider()

        feedback_col, button_col = st.columns([2, 1])

        with feedback_col:
            if st.session_state.last_outcome == "safe":
                st.info("Outcome: +1")
            elif st.session_state.last_outcome == "win":
                st.success("Outcome: +4")
            elif st.session_state.last_outcome == "loss":
                st.error("Outcome: -2")

        with button_col:
            st.write("")
            st.button("Continue →", on_click=continue_after_feedback, use_container_width=True)
