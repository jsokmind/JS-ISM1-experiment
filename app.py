import streamlit as st
import random
st.set_page_config(page_title="BehEconExp", layout="centered")

import csv
import os
from datetime import datetime, timezone
import uuid

st.session_state.participant_id = str(uuid.uuid4())

def log_trial():
    file_exists = os.path.isfile("experiment_data.csv")

    with open("experiment_data.csv", "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "participant_id",
                "block",
                "condition",
                "round",
                "choice",
                "outcome",
                "p_win",
                "win_streak",
                "loss_streak",
                "balance",
                "timestamp"
                "reaction_time_ms"
            ])

        writer.writerow([
            st.session_state.participant_id,
            st.session_state.block_index + 1,
            st.session_state.condition,
            st.session_state.round,
            "safe" if st.session_state.last_outcome == "safe" else "risk",
            st.session_state.last_outcome,
            st.session_state.debug_p_win,
            st.session_state.win_streak,
            st.session_state.loss_streak,
            st.session_state.balance,
            datetime.now(timezone.utc).isoformat(),
            st.session_state.reaction_time_ms
        ])

# ===== INITIALIZE ALL SESSION STATE VARIABLES =====
if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())

if "block_order" not in st.session_state:
    st.session_state.block_order = random.sample(
        ["neutral", "visual", "affective", "de-salience"],
        4
    )

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

#CSS for animations
#CSS for animations
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
</style>

""", unsafe_allow_html=True)


def continue_after_feedback():

    # Update streaks based on last outcome
    if st.session_state.last_outcome == "win":
        st.session_state.win_streak += 1
        st.session_state.loss_streak = 0
        st.session_state.last_risk_outcome = "win"

        # Activate bias ONCE at streak threshold
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

    # Advance round
    st.session_state.round += 1

    # Clear feedback state
    st.session_state.awaiting_feedback = False
    st.session_state.last_outcome = None

    # Reset round timer for next round
    st.session_state.round_start_time = datetime.now(timezone.utc)
    log_trial()

    # Enter break exactly once at round limit
    if st.session_state.round >= 15:
        st.session_state.in_break = True



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

#streak logic
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
    st.title("Behavioral Econ Experiment")
    st.header("Welcome!")
    st.write(
        "Today, you will be playing the latest and greatest online betting game.\n\n"
        "Your objective is to maximize your earnings. There will be blocks of rounds, each separated by a brief break.\n\n"
        "Each round is an individual decision between a safe-option and a risk-bet whose outcomes (win / loss) are determined by a computerized random process. \n\n"
        "Thus, you may notice streaks."
    )
    st.write(f"Starting balance: {st.session_state.balance}")
    st.button("Start Experiment", on_click=_start_experiment)

# Main experiment logic
if st.session_state.started and st.session_state.in_break:
    st.header("Break Time!")
    st.write("Please take a short break before continuing to the next block.")
    st.write("When you are ready, click the button below to proceed.")

    if st.button("Continue to Next Block"):
        st.session_state.block += 1
        st.session_state.block_index += 1
        st.session_state.round = 0
        st.session_state.in_break = False

        # HARD RESET OF BIAS
        st.session_state.bias_rounds_left = 0
        st.session_state.bias_rounds_active = False

        # HARD RESET OF STREAKS
        st.session_state.win_streak = 0
        st.session_state.loss_streak = 0

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
    st.write("Thank you so much for participating in this behavioral economics study!")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Final Balance", f"${st.session_state.balance}")
    with col2:
        st.metric("Blocks Completed", 4)

    st.divider()

    st.success("✅ Your responses have been recorded successfully.")
    st.write("Your participation helps advance our understanding of decision-making under uncertainty.")
    st.write("You may now close this window.")


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
        st.metric("Round", f"{st.session_state.round + 1}/15")
    with col3:
        st.metric("Balance", st.session_state.balance)

    st.divider()


    def _choose_safe():
        st.session_state.balance += 1
        st.session_state.awaiting_feedback = True
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

        # store for debugging
        st.session_state.debug_p_win = p_win

        # decrement bias window only if active
        if st.session_state.bias_rounds_left > 0:
            st.session_state.bias_rounds_left -= 1

            if st.session_state.bias_rounds_left == 0:
                st.session_state.bias_rounds_active = False

        st.session_state.balance += outcome * 2
        st.session_state.awaiting_feedback = True
        st.session_state.last_outcome = "win" if outcome == 1 else "loss"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000

        st.session_state.reaction_time_ms = rt_ms


    # Larger buttons side by side
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.button("Safe Option\n+1", on_click=_choose_safe, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)
    with col2:
        st.button("Risky Option\n±2", on_click=_choose_risk, disabled=st.session_state.awaiting_feedback,
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
        st.metric("Round", f"{st.session_state.round + 1}/15")
    with col3:
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

        # store for debugging
        st.session_state.debug_p_win = p_win

        # decrement bias window only if active
        if st.session_state.bias_rounds_left > 0:
            st.session_state.bias_rounds_left -= 1

            if st.session_state.bias_rounds_left == 0:
                st.session_state.bias_rounds_active = False

        st.session_state.balance += outcome * 2
        st.session_state.awaiting_feedback = True
        st.session_state.last_outcome = "win" if outcome == 1 else "loss"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000

        st.session_state.reaction_time_ms = rt_ms


    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.button("Safe Option\n+1", on_click=_choose_safe, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)
    with col2:
        st.button("Risky Option\n±2", on_click=_choose_risk, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)

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
        st.metric("Round", f"{st.session_state.round + 1}/15")
    with col3:
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

        # store for debugging
        st.session_state.debug_p_win = p_win

        # decrement bias window only if active
        if st.session_state.bias_rounds_left > 0:
            st.session_state.bias_rounds_left -= 1

            if st.session_state.bias_rounds_left == 0:
                st.session_state.bias_rounds_active = False

        st.session_state.balance += outcome * 2
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

        # Put feedback message and button side-by-side
        feedback_col, button_col = st.columns([2, 1])

        with feedback_col:
            if st.session_state.last_outcome == "safe":
                st.info("😌 You chose stability. A calm +1.")
            elif st.session_state.last_outcome == "win":
                if ctx["tone"] == "hot":
                    st.success("🚀 Another win! The streak keeps rolling.")
                else:
                    st.success("🎉 Nice hit! +2 added.")
            elif st.session_state.last_outcome == "loss":
                if ctx["tone"] == "cold":
                    st.error("😖 Ouch, another loss. The slide continues.")
                else:
                    st.error("😬 Tough loss. -2 deducted.")

        with button_col:
            st.write("")  # Add spacing to align button vertically
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
        st.metric("Round", f"{st.session_state.round + 1}/15")
    with col3:
        st.metric("Balance", st.session_state.balance)

    st.divider()

    st.caption("Each round is independent. Previous outcomes do not affect future results.")



    def _choose_safe():
        st.session_state.balance += 1
        st.session_state.awaiting_feedback = True
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

        # store for debugging
        st.session_state.debug_p_win = p_win

        # decrement bias window only if active
        if st.session_state.bias_rounds_left > 0:
            st.session_state.bias_rounds_left -= 1

            if st.session_state.bias_rounds_left == 0:
                st.session_state.bias_rounds_active = False

        st.session_state.balance += outcome * 2
        st.session_state.awaiting_feedback = True
        st.session_state.last_outcome = "win" if outcome == 1 else "loss"

        click_time = datetime.now(timezone.utc)
        rt_ms = (click_time - st.session_state.round_start_time).total_seconds() * 1000

        st.session_state.reaction_time_ms = rt_ms


    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.button("Safe Option\n+1", on_click=_choose_safe, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)
    with col2:
        st.button("Risky Option\n±2", on_click=_choose_risk, disabled=st.session_state.awaiting_feedback,
                  use_container_width=True)

    if st.session_state.awaiting_feedback:
        st.divider()

        feedback_col, button_col = st.columns([2, 1])

        with feedback_col:
            if st.session_state.last_outcome == "safe":
                st.info("Outcome: +1")
            elif st.session_state.last_outcome == "win":
                st.success("Outcome: +2")
            elif st.session_state.last_outcome == "loss":
                st.error("Outcome: -2")

        with button_col:
            st.write("")
            st.button("Continue →", on_click=continue_after_feedback, use_container_width=True)



