
import streamlit as st

import json
import io
from datetime import datetime, date, time
import time as time_module
import time
import hashlib

from pathlib import Path
from openai import OpenAI
import speech_recognition as sr
import requests

import base64
from tavily import TavilyClient

tavily = TavilyClient(
    api_key=st.secrets["TAVILY_API_KEY"]
)
# ============================================================
# 💾 NEXA RECENT CHATS - PERMANENT STORAGE
# ============================================================

RECENT_CHATS_FILE = Path(__file__).parent / "recent_chats.json"


def load_recent_chats():
    try:
        if RECENT_CHATS_FILE.exists():
            with open(RECENT_CHATS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return data

    except Exception:
        pass

    return []


def save_recent_chats(chats):
    try:
        with open(RECENT_CHATS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                chats,
                f,
                ensure_ascii=False,
                indent=2
            )
    except Exception:
        pass

def web_search(query):
    try:
        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )

        results = response.get("results", [])

        if not results:
            return "No web search results found."

        formatted = []

        for result in results:
            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")

            formatted.append(
                f"### {title}\n"
                f"URL: {url}\n"
                f"{content}\n"
            )

        return "\n\n".join(formatted)

    except Exception as e:
        return f"Web search error: {e}"
st.set_page_config(
    page_title="Nexa AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#7C3AED">

<script>
if ("serviceWorker" in navigator) {
    window.addEventListener("load", function() {
        navigator.serviceWorker.register("/sw.js")
            .then(function() {
                console.log("Nexa AI PWA Service Worker registered");
            })
            .catch(function(error) {
                console.log("PWA registration failed:", error);
            });
    });
}
</script>
""", unsafe_allow_html=True)
# ============================================================
# 👤 NEXA ACCOUNT SYSTEM
# ============================================================

from pathlib import Path

USERS_FILE = Path(__file__).parent / "users.json"


# ============================================================
# 🔐 PASSWORD HASHING
# ============================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

def load_users():

    try:

        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    except FileNotFoundError:

        st.error(f"users.json not found: {USERS_FILE}")
        return {}

    except json.JSONDecodeError as e:

        st.error(f"users.json mein JSON error hai: {e}")
        return {}
    # ============================================================
# 👥 USERS DATABASE
# ============================================================

users = load_users()


# ============================================================
# 💾 SAVE USERS
# ============================================================

def save_users(users):

    with open(
        USERS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            users,
            f,
            indent=4
        )





# ============================================================
# 🔐 LOGIN STATE
# ============================================================

if "account_logged_in" not in st.session_state:

    st.session_state.account_logged_in = False


if "logged_username" not in st.session_state:

    st.session_state.logged_username = None


# ============================================================
# 🔑 LOGIN / CREATE ACCOUNT SCREEN
# ============================================================

if not st.session_state.account_logged_in:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:45px 10px 20px 10px;
        ">
            <h1>🚀 NEXA AI</h1>
            <p>Think • Create • Build</p>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # 📑 LOGIN / CREATE ACCOUNT TABS
    # ========================================================

    login_tab, create_tab = st.tabs(
        [
            "🔐 Login",
            "✨ Create Account"
        ]
    )


    # ========================================================
    # 🔐 LOGIN
    # ========================================================

    with login_tab:

        st.markdown("### 🔐 Welcome Back")

        login_username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )


        if st.button(
            "🔓 Login",
            use_container_width=True,
            key="login_button"
        ):

            username = login_username.strip()


            if not username:

                st.error(
                    "Please enter your username."
                )

            elif username not in users:

                st.error(
                    "Username not found. Please create an account first."
                )

            elif users[username]["password"] != hash_password(
                login_password
            ):

                st.error(
                    "Incorrect password."
                )

            else:

                st.session_state.account_logged_in = True

                st.session_state.logged_username = username

                st.session_state.subscription_plan = users[
                    username
                ].get(
                    "plan",
                    "Free"
                )

                st.session_state.subscription_usage = users[
                    username
                ].get(
                    "usage",
                    {
                        "messages": 0,
                        "images": 0,
                        "voice": 0
                    }
                )

                st.success(
                    "Login successful! 🚀"
                )

                st.rerun()


    # ========================================================
    # ✨ CREATE ACCOUNT
    # ========================================================

    with create_tab:

        st.markdown("### ✨ Create Your Nexa Account")

        new_username = st.text_input(
            "Create Username",
            placeholder="Choose any username",
            key="create_username"
        )

        new_password = st.text_input(
            "Create Password",
            type="password",
            placeholder="Choose any password",
            key="create_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Enter password again",
            key="confirm_password"
        )


        if st.button(
            "🚀 Create Account",
            use_container_width=True,
            key="create_account_button"
        ):

            username = new_username.strip()


            # ------------------------------------------------
            # USERNAME CHECK
            # ------------------------------------------------

            if not username:

                st.error(
                    "Please enter a username."
                )


            elif username in users:

                st.error(
                    "This username already exists. Please choose another."
                )


            # ------------------------------------------------
            # PASSWORD CHECK
            # ------------------------------------------------

            elif not new_password:

                st.error(
                    "Please enter a password."
                )


            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )


            # ------------------------------------------------
            # CREATE USER
            # ------------------------------------------------

            else:

                users[username] = {

                    "username": username,

                    "password": hash_password(
                        new_password
                    ),

                    "plan": "Free",

                    "usage": {
                        "messages": 0,
                        "images": 0,
                        "voice": 0
                    },

                    "usage_date": str(
                        date.today()
                    )
                }


                # Save account
                save_users(users)


                # Login automatically
                st.session_state.account_logged_in = True

                st.session_state.logged_username = username

                st.session_state.subscription_plan = "Free"

                st.session_state.subscription_usage = {
                    "messages": 0,
                    "images": 0,
                    "voice": 0
                }


                st.success(
                    "Account created successfully! 🚀"
                )

                st.rerun()


    # Stop app until user logs in
    st.stop()


# ============================================================
# 👤 CURRENT LOGGED-IN USER
# ============================================================

current_user = st.session_state.logged_username


# Safety check
if current_user not in users:

    st.session_state.account_logged_in = False

    st.session_state.logged_username = None

    st.rerun()


user_data = users[current_user]


# ============================================================
# 💳 NEXA SUBSCRIPTION PLANS
# ============================================================

PLANS = {

    "Free": {

        "price": 0,

        "period": "Forever",

        "daily_messages": 10,

        "image_generation": 2,

        "voice_call": 5
    },


    "Pro": {

        "price": 1399,

        "period": "month",

        "daily_messages": 100,

        "image_generation": 20,

        "voice_call": 50
    },


    "Business": {

        "price": 4999,

        "period": "month",

        "daily_messages": 500,

        "image_generation": 100,

        "voice_call": 200
    }
}


# ============================================================
# 💳 LOAD USER PLAN
# ============================================================

saved_plan = user_data.get(
    "plan",
    "Free"
)


if saved_plan not in PLANS:

    saved_plan = "Free"

    user_data["plan"] = "Free"


st.session_state.subscription_plan = saved_plan

current_plan = st.session_state.subscription_plan

current_plan_data = PLANS[current_plan]


# ============================================================
# 📊 LOAD USER USAGE
# ============================================================

saved_usage = user_data.get(
    "usage",
    {
        "messages": 0,
        "images": 0,
        "voice": 0
    }
)


saved_usage.setdefault(
    "messages",
    0
)

saved_usage.setdefault(
    "images",
    0
)

saved_usage.setdefault(
    "voice",
    0
)


st.session_state.subscription_usage = saved_usage


# ============================================================
# 📅 DAILY USAGE RESET
# ============================================================

today = str(
    date.today()
)


saved_date = user_data.get(
    "usage_date",
    today
)


if saved_date != today:

    st.session_state.subscription_usage = {

        "messages": 0,

        "images": 0,

        "voice": 0
    }


    user_data["usage"] = (
        st.session_state.subscription_usage
    )

    user_data["usage_date"] = today

    save_users(users)


# ============================================================
# 💾 UPDATE USER DATA
# ============================================================

user_data["plan"] = (
    st.session_state.subscription_plan
)

user_data["usage"] = (
    st.session_state.subscription_usage
)

user_data["usage_date"] = today


# ============================================================
# 👤 ACCOUNT SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("### 👤 Account")


    st.write(
        f"**{current_user}**"
    )


    st.markdown("---")


    # Current plan
    st.markdown(
        f"**💳 Plan:** {current_plan}"
    )


    if current_plan_data["price"] == 0:

        st.caption(
            "Free • Forever"
        )

    else:

        st.caption(
            f"Rs. {current_plan_data['price']:,} / month"
        )


    st.markdown("---")


    # ========================================================
    # 🔐 ACCOUNT SETTINGS
    # ========================================================

    with st.expander(
        "⚙️ Account Settings"
    ):

        st.markdown(
            "### ✏️ Change Username"
        )


        new_username = st.text_input(
            "New Username",
            placeholder="Enter new username",
            key="change_username"
        )


        if st.button(
            "💾 Change Username",
            use_container_width=True,
            key="change_username_button"
        ):

            new_username = new_username.strip()


            if not new_username:

                st.error(
                    "Please enter a new username."
                )

            elif new_username == current_user:

                st.warning(
                    "This is already your username."
                )

            elif new_username in users:

                st.error(
                    "This username is already taken."
                )

            else:

                # Copy user data
                users[new_username] = user_data.copy()

                users[new_username]["username"] = (
                    new_username
                )


                # Delete old username
                del users[current_user]


                # Update session
                st.session_state.logged_username = (
                    new_username
                )


                # Save
                save_users(users)


                st.success(
                    "Username changed successfully! ✅"
                )

                st.rerun()


        st.markdown("---")


        st.markdown(
            "### 🔑 Change Password"
        )


        current_password = st.text_input(
            "Current Password",
            type="password",
            key="current_password"
        )


        new_password_change = st.text_input(
            "New Password",
            type="password",
            key="new_password_change"
        )


        confirm_password_change = st.text_input(
            "Confirm New Password",
            type="password",
            key="confirm_password_change"
        )


        if st.button(
            "🔐 Change Password",
            use_container_width=True,
            key="change_password_button"
        ):

            if not current_password:

                st.error(
                    "Please enter your current password."
                )

            elif user_data["password"] != hash_password(
                current_password
            ):

                st.error(
                    "Current password is incorrect."
                )

            elif not new_password_change:

                st.error(
                    "Please enter a new password."
                )

            elif new_password_change != confirm_password_change:

                st.error(
                    "New passwords do not match."
                )

            else:

                user_data["password"] = hash_password(
                    new_password_change
                )


                save_users(users)


                st.success(
                    "Password changed successfully! ✅"
                )


    st.markdown("---")


    # ========================================================
    # 🚪 LOGOUT
    # ========================================================

    if st.button(
        "🚪 Logout",
        use_container_width=True,
        key="account_logout"
    ):

        st.session_state.account_logged_in = False

        st.session_state.logged_username = None

        st.session_state.pop(
            "subscription_plan",
            None
        )

        st.session_state.pop(
            "subscription_usage",
            None
        )

        st.rerun()


# ============================================================
# 📊 CURRENT USAGE
# ============================================================

current_usage = (
    st.session_state.subscription_usage
)


# ============================================================
# 📋 SUBSCRIPTION LIMITS
# ============================================================

MESSAGE_LIMIT = (
    current_plan_data["daily_messages"]
)

IMAGE_LIMIT = (
    current_plan_data["image_generation"]
)

VOICE_LIMIT = (
    current_plan_data["voice_call"]
)


# ============================================================
# 📊 USAGE CHECK FUNCTIONS
# ============================================================

def can_use_message():

    return (
        st.session_state.subscription_usage.get(
            "messages",
            0
        )
        < MESSAGE_LIMIT
    )


def can_generate_image():

    return (
        st.session_state.subscription_usage.get(
            "images",
            0
        )
        < IMAGE_LIMIT
    )


def can_use_voice():

    return (
        st.session_state.subscription_usage.get(
            "voice",
            0
        )
        < VOICE_LIMIT
    )


# ============================================================
# ➕ USAGE INCREMENT FUNCTIONS
# ============================================================

def use_message():

    if not can_use_message():

        return False


    st.session_state.subscription_usage[
        "messages"
    ] += 1


    user_data["usage"] = (
        st.session_state.subscription_usage
    )


    save_users(users)


    return True


def use_image():

    if not can_generate_image():

        return False


    st.session_state.subscription_usage[
        "images"
    ] += 1


    user_data["usage"] = (
        st.session_state.subscription_usage
    )


    save_users(users)


    return True


def use_voice():

    if not can_use_voice():

        return False


    st.session_state.subscription_usage[
        "voice"
    ] += 1


    user_data["usage"] = (
        st.session_state.subscription_usage
    )


    save_users(users)


    return True


# ============================================================
# 💳 PLAN CHANGE FUNCTION
# ============================================================

def change_subscription(plan_name):

    if plan_name not in PLANS:

        return False


    st.session_state.subscription_plan = (
        plan_name
    )


    user_data["plan"] = plan_name


    save_users(users)


    return True
# ============================================================
# 📱💻 NEXA AI — FULL RESPONSIVE DESIGN
# ============================================================

st.markdown("""
<style>

/* =========================================================
   GLOBAL RESPONSIVE SETTINGS
   ========================================================= */

html, body, [class*="css"] {
    box-sizing: border-box;
}

*,
*::before,
*::after {
    box-sizing: border-box;
}

body {
    overflow-x: hidden;
}

/* Main Streamlit app */
.stApp {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
}

/* Main content area */
section[data-testid="stMain"] {
    width: 100%;
    max-width: 100%;
}

/* Content container */
.block-container {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    padding-top: 2rem;
    padding-bottom: 3rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* =========================================================
   IMAGES / VIDEOS
   ========================================================= */

img,
video,
iframe {
    max-width: 100%;
    height: auto;
}

[data-testid="stImage"] img {
    max-width: 100%;
    height: auto;
    object-fit: contain;
}

/* =========================================================
   TEXT RESPONSIVE
   ========================================================= */

h1 {
    font-size: clamp(28px, 4vw, 44px) !important;
}

h2 {
    font-size: clamp(24px, 3.5vw, 36px) !important;
}

h3 {
    font-size: clamp(19px, 2.5vw, 28px) !important;
}

p,
label,
.stMarkdown {
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* =========================================================
   STREAMLIT COLUMNS
   ========================================================= */

[data-testid="column"] {
    min-width: 0 !important;
}

/* Prevent long content from breaking layout */
[data-testid="column"] > div {
    max-width: 100%;
}

/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button,
.stDownloadButton > button {
    width: 100%;
    min-height: 44px;
    white-space: normal;
    word-wrap: break-word;
}

/* =========================================================
   INPUTS
   ========================================================= */

input,
textarea,
select {
    max-width: 100%;
}

textarea {
    width: 100% !important;
}

/* =========================================================
   CODE BLOCKS
   ========================================================= */

pre {
    max-width: 100%;
    overflow-x: auto !important;
    white-space: pre !important;
}

code {
    word-break: normal;
}

/* =========================================================
   BUILDER CARDS
   ========================================================= */

.nexa-builder-card {
    width: 100%;
    max-width: 100%;
    overflow: hidden;
}

/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    min-width: 280px;
    max-width: 320px;
}

section[data-testid="stSidebar"] > div {
    width: 100%;
}

/* =========================================================
   TABLET
   768px - 1100px
   ========================================================= */

@media (max-width: 1100px) {

    .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
    }

    section[data-testid="stSidebar"] {
        min-width: 260px;
        max-width: 280px;
    }

    .nexa-builder-card {
        padding: 18px !important;
    }

}

/* =========================================================
   MOBILE
   767px AND BELOW
   ========================================================= */

@media (max-width: 767px) {

    /* Main page spacing */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    /* Hide horizontal overflow */
    .stApp,
    section[data-testid="stMain"],
    .main {
        overflow-x: hidden !important;
    }

    /* -----------------------------------------------------
       COLUMNS → STACK VERTICALLY
       ----------------------------------------------------- */

    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
    }

    /* Give stacked columns some breathing room */
    [data-testid="column"] + [data-testid="column"] {
        margin-top: 0.75rem;
    }

    /* -----------------------------------------------------
       SIDEBAR
       ----------------------------------------------------- */

    section[data-testid="stSidebar"] {
        min-width: 0 !important;
        max-width: 85vw !important;
        width: 85vw !important;
    }

    /* -----------------------------------------------------
       HEADINGS
       ----------------------------------------------------- */

    h1 {
        font-size: 28px !important;
        line-height: 1.2 !important;
    }

    h2 {
        font-size: 24px !important;
        line-height: 1.25 !important;
    }

    h3 {
        font-size: 20px !important;
        line-height: 1.3 !important;
    }

    /* -----------------------------------------------------
       BUTTONS
       ----------------------------------------------------- */

    .stButton > button,
    .stDownloadButton > button {
        width: 100% !important;
        min-height: 46px !important;
        font-size: 14px !important;
    }

    /* -----------------------------------------------------
       INPUTS
       ----------------------------------------------------- */

    .stTextInput,
    .stTextArea,
    .stSelectbox,
    .stMultiSelect,
    .stDateInput,
    .stTimeInput {
        width: 100% !important;
    }

    /* -----------------------------------------------------
       BUILDER
       ----------------------------------------------------- */

    .nexa-builder-title {
        font-size: 28px !important;
        text-align: center;
    }

    .nexa-builder-subtitle {
        font-size: 14px !important;
        text-align: center;
        line-height: 1.5;
    }

    .nexa-builder-card {
        width: 100% !important;
        padding: 18px !important;
        margin-bottom: 15px;
    }

    /* -----------------------------------------------------
       ABOUT / PROFILE
       ----------------------------------------------------- */

    .about-box {
        width: 100% !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
        padding: 12px !important;
    }

    .profile-title {
        font-size: 19px !important;
    }

    /* -----------------------------------------------------
       EXPANDERS
       ----------------------------------------------------- */

    [data-testid="stExpander"] {
        width: 100% !important;
    }

    /* -----------------------------------------------------
       DATA / CODE
       ----------------------------------------------------- */

    [data-testid="stCodeBlock"] {
        max-width: 100% !important;
        overflow-x: auto !important;
    }

    /* -----------------------------------------------------
       ALERTS
       ----------------------------------------------------- */

    [data-testid="stAlert"] {
        width: 100% !important;
        font-size: 13px !important;
    }

    /* -----------------------------------------------------
       CAMERA / FILE UPLOAD
       ----------------------------------------------------- */

    [data-testid="stCameraInput"],
    [data-testid="stFileUploader"] {
        width: 100% !important;
    }

}

/* =========================================================
   VERY SMALL MOBILE
   480px AND BELOW
   ========================================================= */

@media (max-width: 480px) {

    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    h1 {
        font-size: 24px !important;
    }

    h2 {
        font-size: 21px !important;
    }

    h3 {
        font-size: 18px !important;
    }

    .nexa-builder-title {
        font-size: 24px !important;
    }

    .nexa-builder-card {
        padding: 15px !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        font-size: 13px !important;
        min-height: 44px !important;
    }

}

/* =========================================================
   LARGE DESKTOP / LCD
   ========================================================= */

@media (min-width: 1600px) {

    .block-container {
        max-width: 1500px;
        padding-left: 4rem;
        padding-right: 4rem;
    }

}

/* =========================================================
   PREVENT HORIZONTAL SCROLL
   ========================================================= */

html,
body,
.stApp,
.main,
section[data-testid="stMain"] {
    max-width: 100%;
    overflow-x: hidden !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 👤 NEXA AI — PROFILE SIDEBAR
# ============================================================

# Profile session state
if "show_profile" not in st.session_state:
    st.session_state.show_profile = False

if "profile_saved" not in st.session_state:
    st.session_state.profile_saved = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "profession" not in st.session_state:
    st.session_state.profession = ""

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True

if "privacy_mode" not in st.session_state:
    st.session_state.privacy_mode = "Private"

if "color_scheme" not in st.session_state:
    st.session_state.color_scheme = "Purple"


# ============================================================
# 🎨 PROFILE SIDEBAR CSS
# ============================================================

st.markdown("""
<style>

.nexa-sidebar-brand {
    font-size: 22px;
    font-weight: 800;
    color: #A855F7;
    margin-bottom: 2px;
}

.nexa-tagline {
    font-size: 14px;
    color: #CBD5E1;
    margin-bottom: 15px;
}

.profile-title {
    font-size: 20px;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 12px;
}

.about-box {
    background: #151B2B;
    border: 1px solid #7C3AED;
    border-radius: 12px;
    padding: 14px;
    color: #E2E8F0;
    font-size: 14px;
    line-height: 1.6;
    margin-top: 8px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 🚀 NEXA AI BRANDING
# ============================================================

st.markdown(
    """
    <div class="nexa-sidebar-brand">
        🚀 Nexa AI
    </div>
    <div class="nexa-tagline">
        Think • Create • Build
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 👤 ADD PROFILE BUTTON
# ============================================================

if st.button(
    "＋ Add Profile",
    use_container_width=True,
    key="add_profile_btn"
):
    st.session_state.show_profile = not st.session_state.show_profile


# ============================================================
# 👤 PROFILE PANEL
# ============================================================

if st.session_state.show_profile:

    st.markdown(
        '<div class="profile-title">👤 Add Profile</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Username
    # --------------------------------------------------------

    username = st.text_input(
        "Username",
        value=st.session_state.username,
        placeholder="Enter your username",
        key="profile_username"
    )

    # --------------------------------------------------------
    # Profession
    # --------------------------------------------------------

    profession = st.text_input(
        "Profession",
        value=st.session_state.profession,
        placeholder="Enter your profession",
        key="profile_profession"
    )

    # --------------------------------------------------------
    # About
    # --------------------------------------------------------

    st.markdown("### About")

    st.markdown(
        """
        <div class="about-box">
        Nexa AI is created by Ayyan Ali Khan, an AI Engineer & Digital Marketer from Pakistan.
        He created Nexa AI at the age of 17 with the vision of building an intelligent AI
        platform to help people learn, create, grow, and solve problems with the power of AI.
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # 🧠 Memory
    # --------------------------------------------------------

    st.markdown("### 🧠 Memory")

    memory_enabled = st.toggle(
        "Enable Memory",
        value=st.session_state.memory_enabled,
        key="profile_memory"
    )

    # --------------------------------------------------------
    # 🔒 Privacy
    # --------------------------------------------------------

    st.markdown("### 🔒 Privacy")

    privacy_mode = st.selectbox(
        "Privacy Mode",
        [
            "Private",
            "Standard"
        ],
        index=(
            0
            if st.session_state.privacy_mode == "Private"
            else 1
        ),
        key="profile_privacy"
    )

    # --------------------------------------------------------
    # 🎨 Color Scheme
    # --------------------------------------------------------

    st.markdown("### 🎨 Color Scheme")

    color_scheme = st.selectbox(
        "Choose Color Scheme",
        [
            "Purple",
            "Blue",
            "Cyan",
            "Green",
            "Red"
        ],
        index=[
            "Purple",
            "Blue",
            "Cyan",
            "Green",
            "Red"
        ].index(st.session_state.color_scheme),
        key="profile_color"
    )

    # --------------------------------------------------------
    # 💾 SAVE PROFILE
    # --------------------------------------------------------

    if st.button(
        "💾 Save Profile",
        use_container_width=True,
        key="save_profile_btn"
    ):

        st.session_state.username = username
        st.session_state.profession = profession
        st.session_state.memory_enabled = memory_enabled
        st.session_state.privacy_mode = privacy_mode
        st.session_state.color_scheme = color_scheme
        st.session_state.profile_saved = True

        st.success("Profile saved successfully!")

        st.rerun()


NEXA_CREATOR_INFO = """
Nexa AI was created by Ayyan Ali Khan, an AI Engineer & Digital Marketer from Pakistan.
He created Nexa AI at the age of 17 with the vision of building an intelligent AI platform
for creativity, learning, business, and technology.
"""


# =========================================================
# 🧩 NEXA REMINDER PLUGIN
# =========================================================

REMINDER_FILE = Path(__file__).parent / "reminders.json"


# =========================================================
# 📂 LOAD REMINDERS
# =========================================================

def load_nexa_reminders():

    try:

        if not REMINDER_FILE.exists():
            return []

        with open(REMINDER_FILE, "r", encoding="utf-8") as f:
            reminders = json.load(f)

        return reminders if isinstance(reminders, list) else []

    except Exception:

        return []


# =========================================================
# 💾 SAVE REMINDERS
# =========================================================

def save_nexa_reminders(reminders):

    data = []

    for reminder in reminders:

        item = reminder.copy()

        if isinstance(item.get("datetime"), datetime):
            item["datetime"] = item["datetime"].isoformat()

        data.append(item)

    with open(REMINDER_FILE, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# ➕ ADD REMINDER
# =========================================================

def reminder_plugin_add(text, reminder_datetime):

    reminders = load_nexa_reminders()

    reminders.append({

        "id": int(time_module.time() * 1000),

        "text": text,

        "datetime": reminder_datetime.isoformat(),

        "done": False

    })

    save_nexa_reminders(reminders)


# =========================================================
# 🔔 NEXA REMINDER UI
# =========================================================

st.markdown("## 🔔 Nexa Reminders")


# =========================================================
# ➕ ADD NEW REMINDER
# =========================================================

with st.expander("➕ Add New Reminder"):

    reminder_text = st.text_input(
        "📝 What should Nexa remind you about?",
        placeholder="Example: Complete my Python project",
        key="plugin_reminder_text"
    )


    reminder_date = st.date_input(
        "📅 Reminder Date",
        value=date.today(),
        key="plugin_reminder_date"
    )


    reminder_time = st.time_input(
        "⏰ Reminder Time",
        value=datetime.strptime(
            "19:15",
            "%H:%M"
        ).time(),
        key="plugin_reminder_time"
    )


    # =====================================================
    # 🕐 CURRENT SYSTEM TIME
    # =====================================================

    current_system_time = datetime.now()

    st.caption(
        "Current system time: "
        + current_system_time.strftime(
            "%d %B %Y — %I:%M:%S %p"
        )
    )


    # =====================================================
    # 🔔 SET REMINDER
    # =====================================================

    if st.button(
        "🔔 Set Reminder",
        use_container_width=True,
        key="plugin_set_reminder"
    ):

        if not reminder_text.strip():

            st.warning(
                "⚠️ Please enter a reminder."
            )

        else:

            reminder_datetime = datetime.combine(
                reminder_date,
                reminder_time
            )

            current_time = datetime.now()


            # =================================================
            # ⏳ FUTURE TIME CHECK
            # =================================================

            if reminder_datetime <= current_time:

                st.warning(
                    "⚠️ Please select a future date and time."
                )

            else:

                reminder_plugin_add(
                    reminder_text.strip(),
                    reminder_datetime
                )

                st.success(
                    "✅ Reminder set for "
                    + reminder_datetime.strftime(
                        "%d %B %Y at %I:%M %p"
                    )
                )

                st.rerun()


# =========================================================
# 📋 ACTIVE REMINDERS
# =========================================================

reminders = load_nexa_reminders()

active_reminders = [
    r
    for r in reminders
    if not r.get("done", False)
]


if active_reminders:

    st.markdown("### 📋 Active Reminders")

    for reminder in active_reminders:

        try:

            reminder_dt = datetime.fromisoformat(
                reminder["datetime"]
            )

            formatted_time = reminder_dt.strftime(
                "%d %B %Y at %I:%M %p"
            )

        except Exception:

            formatted_time = reminder["datetime"]


        st.info(
            f"⏰ **{formatted_time}**\n\n"
            f"📝 {reminder['text']}"
        )

else:

    st.caption("No active reminders.")


# =========================================================
# 🔔 BROWSER NOTIFICATION + SOUND ENGINE
# =========================================================

import streamlit.components.v1 as components


# Convert Python reminders into JavaScript-safe JSON
reminder_json = json.dumps(
    active_reminders,
    ensure_ascii=False
)


components.html(
    f"""
    <div id="nexa-reminder-box"
         style="
            font-family:Arial,sans-serif;
            padding:12px;
            border-radius:12px;
            background:#111827;
            color:#F8FAFC;
            border:1px solid #374151;
         ">

        <div style="
            font-size:15px;
            font-weight:700;
            margin-bottom:8px;
        ">
            🔔 Nexa Notification System
        </div>

        <button
            id="enable-nexa-alerts"
            style="
                width:100%;
                padding:10px;
                border:none;
                border-radius:8px;
                background:#7C3AED;
                color:white;
                font-weight:700;
                cursor:pointer;
            "
        >
            🔔 Enable Notifications & Sound
        </button>

        <div
            id="nexa-status"
            style="
                margin-top:8px;
                font-size:12px;
                color:#94A3B8;
            "
        >
            Notifications are not enabled yet.
        </div>

    </div>


    <script>

    // =====================================================
    // 📋 REMINDERS FROM PYTHON
    // =====================================================

    const nexaReminders = {reminder_json};


    // =====================================================
    // 🔐 STORAGE KEY
    // =====================================================

    const STORAGE_KEY = "nexa_triggered_reminders";


    function getTriggeredReminders() {{

        try {{

            return JSON.parse(
                localStorage.getItem(STORAGE_KEY) || "[]"
            );

        }} catch (error) {{

            return [];

        }}

    }}


    function saveTriggeredReminder(id) {{

        let triggered = getTriggeredReminders();

        if (!triggered.includes(id)) {{

            triggered.push(id);

            localStorage.setItem(
                STORAGE_KEY,
                JSON.stringify(triggered)
            );

        }}

    }}


    // =====================================================
    // 🔊 SOUND
    // =====================================================

    let audioContext = null;


    function enableSound() {{

        try {{

            audioContext = new (
                window.AudioContext ||
                window.webkitAudioContext
            )();

            if (audioContext.state === "suspended") {{

                audioContext.resume();

            }}

        }} catch (error) {{

            console.log(
                "Nexa sound initialization error:",
                error
            );

        }}

    }}


    function playNexaSound() {{

        try {{

            if (!audioContext) {{

                enableSound();

            }}

            const oscillator =
                audioContext.createOscillator();

            const gain =
                audioContext.createGain();


            oscillator.type = "sine";

            oscillator.frequency.setValueAtTime(
                880,
                audioContext.currentTime
            );

            oscillator.frequency.setValueAtTime(
                660,
                audioContext.currentTime + 0.25
            );

            oscillator.frequency.setValueAtTime(
                880,
                audioContext.currentTime + 0.50
            );


            gain.gain.setValueAtTime(
                0.0001,
                audioContext.currentTime
            );

            gain.gain.exponentialRampToValueAtTime(
                0.4,
                audioContext.currentTime + 0.05
            );

            gain.gain.exponentialRampToValueAtTime(
                0.0001,
                audioContext.currentTime + 1.0
            );


            oscillator.connect(gain);

            gain.connect(audioContext.destination);


            oscillator.start();

            oscillator.stop(
                audioContext.currentTime + 1.0
            );


        }} catch (error) {{

            console.log(
                "Nexa sound error:",
                error
            );

        }}

    }}


    // =====================================================
    // 🔔 BROWSER NOTIFICATION
    // =====================================================

    function sendNexaNotification(text) {{

        if ("Notification" in window) {{

            if (Notification.permission === "granted") {{

                new Notification(
                    "🔔 Nexa AI Reminder",
                    {{
                        body: text,
                        icon: "https://cdn-icons-png.flaticon.com/512/1827/1827392.png",
                        requireInteraction: true
                    }}
                );

            }}

        }}

    }}


    // =====================================================
    // 🔘 ENABLE BUTTON
    // =====================================================

    document
        .getElementById("enable-nexa-alerts")
        .addEventListener("click", async function() {{

            enableSound();


            if ("Notification" in window) {{

                try {{

                    const permission =
                        await Notification.requestPermission();


                    const status =
                        document.getElementById(
                            "nexa-status"
                        );


                    if (permission === "granted") {{

                        status.innerHTML =
                            "✅ Notifications and sound enabled.";

                        status.style.color =
                            "#22C55E";


                        playNexaSound();

                    }}

                    else {{

                        status.innerHTML =
                            "⚠️ Browser notification permission was denied.";

                        status.style.color =
                            "#F59E0B";

                    }}

                }} catch (error) {{

                    console.log(error);

                }}

            }}

            else {{

                document.getElementById(
                    "nexa-status"
                ).innerHTML =
                    "⚠️ This browser does not support notifications.";

            }}

        }});


    // =====================================================
    // ⏰ CHECK REMINDERS EVERY SECOND
    // =====================================================

    function checkNexaReminders() {{

        const now = new Date();

        const triggered =
            getTriggeredReminders();


        nexaReminders.forEach(function(reminder) {{

            if (reminder.done) {{

                return;

            }}


            if (triggered.includes(reminder.id)) {{

                return;

            }}


            const reminderTime =
                new Date(reminder.datetime);


            if (now >= reminderTime) {{

                console.log(
                    "🔔 Nexa reminder triggered:",
                    reminder.text
                );


                // Browser notification
                sendNexaNotification(
                    reminder.text
                );


                // Sound
                playNexaSound();


                // Prevent duplicate alerts
                saveTriggeredReminder(
                    reminder.id
                );


                // Visual alert inside component
                const status =
                    document.getElementById(
                        "nexa-status"
                    );


                status.innerHTML =
                    "🔔 Reminder triggered: "
                    + reminder.text;

                status.style.color =
                    "#F59E0B";

            }}

        }});

    }}


    // Start immediately
    checkNexaReminders();


    // Check every second
    setInterval(
        checkNexaReminders,
        1000
    );

    </script>
    """,
    height=150
)






client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)
# ============================================================
# 🔎 NEXA WEB SEARCH
# ============================================================

from tavily import TavilyClient

tavily = TavilyClient(
    api_key=st.secrets["TAVILY_API_KEY"]
)

def web_search(query):

    try:

        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )

        results = response.get("results", [])

        if not results:
            return "No web search results found."

        formatted_results = []

        for result in results:

            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")

            formatted_results.append(
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Content: {content}"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:

        return f"Web Search Error: {type(e).__name__}: {str(e)}"
    # ============================================================
# 🧠 NEXA WEB SEARCH DETECTOR
# ============================================================

def needs_web_search(user_input):

    text = user_input.lower()

    web_keywords = [
        "latest",
        "today",
        "current",
        "right now",
        "recent",
        "news",
        "price",
        "weather",
        "score",
        "update",
        "updates",
        "2026",
        "search",
        "online",
        "website",
        "web",
        "internet",
        "what happened",
        "find",
        "available",
        "availability"
    ]

    return any(keyword in text for keyword in web_keywords)
# =========================================================
# 🤖 NEXA AI MODELS
# =========================================================

MAIN_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

BUILDER_MODEL = "poolside/laguna-s-2.1:free"

DIFFICULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
VISION_MODEL = "google/gemma-4-26b-a4b-it:free"
# ============================================================
# 🖼️ NEXA IMAGE ANALYSIS
# ============================================================

import base64

def analyze_image(image_file, user_prompt):

    try:

        image_bytes = image_file.getvalue()

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        response = client.chat.completions.create(

            model=VISION_MODEL,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Nexa AI Vision Assistant. "
                        "Analyze the uploaded image carefully. "
                        "Understand objects, people, text, colors, "
                        "design, environment and visual details. "
                        "Answer accurately and clearly. "
                        "Use emojis and these headings when appropriate:\n\n"
                        "🎯 GOAL\n"
                        "🔍 ANALYSIS\n"
                        "⚠️ CHALLENGES\n"
                        "🚀 ACTION PLAN\n"
                        "👉 FIRST ACTION\n"
                        "💡 EXTRA IDEA"
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    "data:"
                                    + image_file.type
                                    + ";base64,"
                                    + image_base64
                                )
                            }
                        }
                    ]
                }
            ],

            max_tokens=1500
        )

        if not response or not response.choices:
            return "❌ Nexa returned no analysis."

        result = response.choices[0].message.content

        if not result:
            return "❌ Nexa returned an empty response."

        return result.strip()

    except Exception as e:

        return (
            "❌ Image Analysis Error\n\n"
            f"{type(e).__name__}: {str(e)}"
        )
    
# ============================================================
# 🤖 NEXA MARKETING AI FUNCTION
# ============================================================

def nexa_marketing_ai(prompt):

    try:

        response = client.chat.completions.create(
            model=MAIN_MODEL,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Nexa AI, an expert digital marketing "
                        "assistant. Generate professional, practical "
                        "and ready-to-use marketing content.\n\n"

                        "CREATOR INFORMATION:\n"
                        f"{NEXA_CREATOR_INFO}\n\n"

                        "If the user asks who created, founded, or built Nexa AI, "
                        "use the creator information above."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            max_tokens=1800
        )

        # ---------------------------------------------
        # SAFE RESPONSE CHECK
        # ---------------------------------------------

        if response is None:
            return "❌ AI returned an empty response."

        if not hasattr(response, "choices") or not response.choices:
            return f"❌ AI returned no choices.\n\nRaw response: {response}"

        message = response.choices[0].message

        if message is None:
            return "❌ AI returned an empty message."

        content = getattr(message, "content", None)

        if content is None:
            return "❌ AI returned no text content."

        return content.strip()

    except Exception as e:

        return (
            "❌ Nexa AI Error\n\n"
            f"{type(e).__name__}: {str(e)}"
        )
# =========================
# 🔔 NEXA REMINDER STORAGE
# =========================

REMINDER_FILE = Path(__file__).parent / "reminders.json"
# =========================
# 🧠 NEXA PERMANENT MEMORY
# =========================

MEMORY_FILE = Path(__file__).parent / "nexa_memory.json"


def load_nexa_memory():
    try:
        if MEMORY_FILE.exists():
            return json.loads(
                MEMORY_FILE.read_text(encoding="utf-8")
            )
        return []
    except Exception:
        return []


def save_nexa_memory(memory):
    MEMORY_FILE.write_text(
        json.dumps(memory, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

if not REMINDER_FILE.exists():
    REMINDER_FILE.write_text("[]", encoding="utf-8")


def load_nexa_reminders():
    try:
        return json.loads(
            REMINDER_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        return []


def save_nexa_reminders(reminders):

    reminders_to_save = []

    for reminder in reminders:

        reminders_to_save.append({
            "text": reminder["text"],
            "datetime": reminder["datetime"].isoformat()
                if isinstance(reminder["datetime"], datetime)
                else reminder["datetime"],
            "done": reminder["done"]
        })

    REMINDER_FILE.write_text(
        json.dumps(reminders_to_save, indent=4),
        encoding="utf-8"
    )

    # ============================================================
# 🚀 NEXA AI CREATION HUB
# ============================================================

st.markdown("## 🚀 Nexa AI Creation Hub")

creation_category = st.selectbox(
    "What do you want to create?",
    [
        "🔥 Explore",
        "📈 Digital Marketing",
        
    ],
    key="creation_category"
)

# ============================================================
# 🚀 NEXA AI — PROFESSIONAL BUILDERS
# ============================================================

# Builder navigation state
if "nexa_builder" not in st.session_state:
    st.session_state.nexa_builder = None



# ============================================================
# 🏠 BUILDER SELECTOR
# ============================================================

if st.session_state.nexa_builder is None:

    st.markdown(
        '<div class="nexa-builder-title">🚀 Nexa AI Builder</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="nexa-builder-subtitle">'
        'Build professional websites and apps with the power of AI.'
        '</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # 🌐 WEBSITE + 📱 APP BUILDER
    # ========================================================

    col1, col2 = st.columns(2, gap="large")

    # --------------------------------------------------------
    # 🌐 WEBSITE BUILDER
    # --------------------------------------------------------

    with col1:

        with st.container(border=True):

            st.markdown(
                """
                <div style="text-align:center; font-size:52px;">
                    🌐
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                "<h3 style='text-align:center;'>Website Builder</h3>",
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <p style="text-align:center; opacity:0.7;">
                Create beautiful, responsive websites from a simple
                text prompt. Build business websites, portfolios,
                landing pages and more with AI.
                </p>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                "🌐 Open Website Builder",
                use_container_width=True,
                key="open_website_builder"
            ):
                st.session_state.nexa_builder = "website"
                st.rerun()

    # --------------------------------------------------------
    # 📱 APP BUILDER
    # --------------------------------------------------------

    with col2:

        with st.container(border=True):

            st.markdown(
                """
                <div style="text-align:center; font-size:52px;">
                    📱
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                "<h3 style='text-align:center;'>App Builder</h3>",
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <p style="text-align:center; opacity:0.7;">
                Create powerful interactive applications from a
                simple idea. Build dashboards, SaaS apps,
                productivity tools and more with AI.
                </p>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                "📱 Open App Builder",
                use_container_width=True,
                key="open_app_builder"
            ):
                st.session_state.nexa_builder = "app"
                st.rerun()
 # ============================================================
# 🌐 WEBSITE BUILDER
# ============================================================

elif st.session_state.nexa_builder == "website":

    # ========================================================
    # 🔙 NAVIGATION
    # ========================================================

    nav_col1, nav_col2 = st.columns([1, 5])

    with nav_col1:

        if st.button(
            "← Back",
            use_container_width=True,
            key="website_back"
        ):

            st.session_state.nexa_builder = None

            if "generated_website" in st.session_state:
                del st.session_state["generated_website"]

            st.rerun()

    st.markdown("---")

    # ========================================================
    # 📝 WEBSITE INFORMATION
    # ========================================================

    st.markdown("### 📝 Website Information")

    website_prompt = st.text_area(
        "💡 What website do you want to build?",
        placeholder=(
            "Example:\n"
            "Create a professional digital marketing agency website "
            "for AAK Digital Marketer. Include a hero section, services, "
            "about us, portfolio, testimonials, pricing and contact form."
        ),
        height=180,
        key="website_prompt"
    )

    # ========================================================
    # ⚙️ WEBSITE SETTINGS
    # ========================================================

    settings_col1, settings_col2 = st.columns(2)

    with settings_col1:

        website_type = st.selectbox(
            "🌐 Website Type",
            [
                "Landing Page",
                "Business Website",
                "Portfolio",
                "Agency Website",
                "E-commerce",
                "Blog",
                "Personal Website",
                "SaaS Website",
                "Restaurant Website",
                "Real Estate Website"
            ],
            key="website_type"
        )

    with settings_col2:

        website_style = st.selectbox(
            "🎨 Design Style",
            [
                "Modern",
                "Professional",
                "Minimal",
                "Luxury",
                "Dark Premium",
                "Glassmorphism",
                "Gradient",
                "Corporate",
                "Creative",
                "Futuristic"
            ],
            key="website_style"
        )

    pages_col1, pages_col2 = st.columns(2)

    with pages_col1:

        website_pages = st.selectbox(
            "📄 Website Pages",
            [
                "Single Page",
                "2 Pages",
                "3 Pages",
                "4 Pages",
                "5 Pages"
            ],
            key="website_pages"
        )

    with pages_col2:

        website_responsive = st.selectbox(
            "📱 Responsive Design",
            [
                "Desktop + Mobile + Tablet",
                "Desktop + Mobile",
                "Desktop Only"
            ],
            key="website_responsive"
        )

    # ========================================================
    # 🎯 OPTIONAL BRAND DETAILS
    # ========================================================

    with st.expander(
        "⚙️ Advanced Website Options",
        expanded=False
    ):

        brand_col1, brand_col2 = st.columns(2)

        with brand_col1:

            brand_name = st.text_input(
                "🏷️ Brand / Business Name",
                placeholder="Example: AAK Digital Marketer",
                key="website_brand_name"
            )

        with brand_col2:

            primary_color = st.text_input(
                "🎨 Main Color",
                placeholder="Example: Gold, Blue, Purple",
                key="website_primary_color"
            )

        website_features = st.text_area(
            "✨ Extra Features",
            placeholder=(
                "Example: WhatsApp button, pricing cards, "
                "FAQ section, testimonials, contact form, "
                "animations, newsletter section..."
            ),
            height=120,
            key="website_features"
        )

    # ========================================================
    # 🤖 WEBSITE GENERATION FUNCTION
    # ========================================================

    def generate_nexa_website():

        if not website_prompt.strip():

            st.warning(
                "⚠️ Please describe the website you want to build."
            )

            return

        # ----------------------------------------------------
        # FINAL AI PROMPT
        # ----------------------------------------------------

        final_website_prompt = f"""
You are Nexa AI Professional Website Builder.

Your job is to create a complete, production-quality,
responsive website from the user's requirements.

USER WEBSITE REQUEST:
{website_prompt.strip()}

WEBSITE TYPE:
{website_type}

DESIGN STYLE:
{website_style}

NUMBER OF PAGES:
{website_pages}

RESPONSIVE TARGET:
{website_responsive}

BRAND NAME:
{brand_name.strip() if brand_name.strip() else "Use a suitable professional brand name"}

PRIMARY COLOR:
{primary_color.strip() if primary_color.strip() else "Choose a professional color palette"}

EXTRA FEATURES:
{website_features.strip() if website_features.strip() else "Use appropriate professional website features"}

IMPORTANT DESIGN REQUIREMENTS:

1. Create a beautiful modern professional website.

2. Use semantic HTML5.

3. Include a complete HTML document.

4. Put ALL CSS inside the <style> tag.

5. Put ALL JavaScript inside the <script> tag.

6. Do not require React, Vue, Angular, Node.js,
   npm or any build system.

7. The generated result must work as a standalone HTML file.

8. Make the website responsive.

9. Create a professional navigation bar.

10. Create a strong hero section.

11. Use attractive typography.

12. Use modern cards, buttons and sections.

13. Add smooth hover effects.

14. Add subtle animations where appropriate.

15. Make spacing and layout professional.

16. Include appropriate call-to-action buttons.

17. Include footer.

18. If appropriate, include:
    - About
    - Services
    - Features
    - Portfolio
    - Pricing
    - Testimonials
    - FAQ
    - Contact
    - Newsletter

19. For images, use reliable remote image URLs only when
    appropriate. Otherwise use beautiful CSS placeholders.

20. Do not use broken image paths.

21. Do not use lorem ipsum.

22. Generate realistic professional content.

23. Ensure text is readable and accessible.

24. Buttons should look clickable.

25. Forms should have proper labels and inputs.

26. Add JavaScript interactions where useful.

27. Navigation should work on the page.

28. Mobile navigation should work with JavaScript
    if necessary.

29. Avoid unnecessary external dependencies.

30. Make the final design look like a professionally
    designed commercial website.

CRITICAL OUTPUT RULE:

Return ONLY the complete HTML document.

Do NOT explain the code.

Do NOT use Markdown.

Do NOT wrap the answer in ```html.

Start directly with <!DOCTYPE html>
and end with </html>.
"""

        try:

            with st.spinner(
                "🤖 Nexa AI is designing your website..."
            ):

                response = client.chat.completions.create(

                    model="poolside/laguna-s-2.1:free",

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Nexa AI, a professional "
                                "AI website builder. Create clean, "
                                "modern, responsive standalone "
                                "HTML websites."
                            )
                        },
                        {
                            "role": "user",
                            "content": final_website_prompt
                        }
                    ],

                    temperature=0.7,

                    max_tokens=12000
                )

                generated_website = (
                    response.choices[0].message.content
                )

                # ------------------------------------------------
                # CLEAN AI MARKDOWN FENCES
                # ------------------------------------------------

                generated_website = (
                    generated_website
                    .replace("```html", "")
                    .replace("```HTML", "")
                    .replace("```Html", "")
                    .replace("```", "")
                    .strip()
                )

                # ------------------------------------------------
                # REMOVE TEXT BEFORE HTML
                # ------------------------------------------------

                html_start = generated_website.lower().find(
                    "<!doctype html>"
                )

                if html_start == -1:

                    html_start = generated_website.lower().find(
                        "<html"
                    )

                if html_start > 0:

                    generated_website = (
                        generated_website[html_start:]
                    )

                # ------------------------------------------------
                # SAVE WEBSITE
                # ------------------------------------------------

                st.session_state.generated_website = (
                    generated_website
                )

                st.session_state.website_generated = True

            st.success(
                "✅ Website successfully generated!"
            )

        except Exception as e:

            st.error(
                f"❌ Website generation failed: {e}"
            )


    # ========================================================
    # 🚀 GENERATE BUTTON
    # ========================================================

    generate_col1, generate_col2 = st.columns(2)

    with generate_col1:

        if st.button(
            "✨ Generate Website",
            use_container_width=True,
            type="primary",
            key="generate_nexa_website"
        ):

            generate_nexa_website()

    with generate_col2:

        if st.button(
            "🔄 Regenerate Website",
            use_container_width=True,
            key="regenerate_nexa_website"
        ):

            if website_prompt.strip():

                generate_nexa_website()

            else:

                st.warning(
                    "⚠️ Please enter a website description first."
                )

    # ========================================================
    # 🖥️ WEBSITE WORKSPACE
    # ========================================================

    if (
        "generated_website" in st.session_state
        and st.session_state.generated_website
    ):

        generated_website = (
            st.session_state.generated_website
        )

        st.markdown("---")

        st.markdown("## 🖥️ Website Workspace")

        # ====================================================
        # LIVE PREVIEW
        # ====================================================

        st.markdown("### 👁️ Live Website Preview")

        st.components.v1.html(
            generated_website,
            height=720,
            scrolling=True
        )

        st.markdown("---")

        # ====================================================
        # CODE VIEW
        # ====================================================

        st.markdown("### 💻 Website Source Code")

        st.code(
            generated_website,
            language="html"
        )

        st.markdown("---")

        # ====================================================
        # EXPORT
        # ====================================================

        st.markdown("### 📦 Export Website")

        export_col1, export_col2 = st.columns(2)

        with export_col1:

            st.download_button(
                "⬇️ Download HTML Website",
                data=generated_website,
                file_name="nexa_website.html",
                mime="text/html",
                use_container_width=True,
                key="download_nexa_website"
            )

        with export_col2:

            if st.button(
                "🧹 Clear Website",
                use_container_width=True,
                key="clear_nexa_website"
            ):

                if "generated_website" in st.session_state:

                    del st.session_state[
                        "generated_website"
                    ]

                if "website_generated" in st.session_state:

                    del st.session_state[
                        "website_generated"
                    ]

                st.rerun()

        st.info(
            "💡 Your HTML file contains the website structure, "
            "CSS and JavaScript together, so it can be opened "
            "directly in a browser."
        )



# ============================================================
# 📱 NEXA AI — PROFESSIONAL APP BUILDER
# ============================================================

elif st.session_state.nexa_builder == "app":

    st.markdown("## 📱 Nexa AI App Builder")

    st.caption(
        "Describe your app idea and Nexa AI will create "
        "a professional app prototype with UI and code."
    )

    # ========================================================
    # 🔙 BACK BUTTON
    # ========================================================

    if st.button(
        "← Back to Builders",
        use_container_width=True,
        key="app_builder_back"
    ):

        st.session_state.nexa_builder = None

        if "generated_app" in st.session_state:
            del st.session_state["generated_app"]

        st.rerun()

    st.markdown("---")

    # ========================================================
    # 📝 APP DESCRIPTION
    # ========================================================

    st.markdown("### 📝 App Information")

    app_prompt = st.text_area(
        "💡 What app do you want to build?",
        placeholder=(
            "Example:\n"
            "Create a modern task management app where users "
            "can add tasks, mark tasks as completed, delete tasks "
            "and filter tasks by status."
        ),
        height=180,
        key="app_prompt"
    )

    # ========================================================
    # ⚙️ APP SETTINGS
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        app_type = st.selectbox(
            "📱 App Type",
            [
                "Web App",
                "Dashboard",
                "SaaS App",
                "Business App",
                "E-commerce App",
                "Productivity App",
                "Education App",
                "Finance App",
                "Social App",
                "AI Tool",
                "Mobile App Prototype"
            ],
            key="app_type"
        )

    with col2:

        app_style = st.selectbox(
            "🎨 App Design",
            [
                "Modern",
                "Professional",
                "Minimal",
                "Dark Premium",
                "Glassmorphism",
                "Futuristic",
                "Gradient",
                "Corporate",
                "Creative"
            ],
            key="app_style"
        )

    col3, col4 = st.columns(2)

    with col3:

        app_platform = st.selectbox(
            "💻 Target Platform",
            [
                "Web Browser",
                "Desktop",
                "Mobile",
                "Responsive Web"
            ],
            key="app_platform"
        )

    with col4:

        app_complexity = st.selectbox(
            "⚡ App Complexity",
            [
                "Simple",
                "Medium",
                "Advanced"
            ],
            key="app_complexity"
        )

    # ========================================================
    # 🎯 ADVANCED APP OPTIONS
    # ========================================================

    with st.expander(
        "⚙️ Advanced App Options",
        expanded=False
    ):

        app_name = st.text_input(
            "🏷️ App Name",
            placeholder="Example: Nexa Tasks",
            key="app_name"
        )

        app_features = st.text_area(
            "✨ Required Features",
            placeholder=(
                "Example:\n"
                "Login screen, dashboard, add task, task list, "
                "search, notifications, profile, settings..."
            ),
            height=140,
            key="app_features"
        )

        app_color = st.text_input(
            "🎨 Main App Color",
            placeholder="Example: Purple, Blue, Gold",
            key="app_color"
        )

    # ========================================================
    # 🤖 APP GENERATION FUNCTION
    # ========================================================

    def generate_nexa_app():

        if not app_prompt.strip():

            st.warning(
                "⚠️ Please describe the app you want to build."
            )

            return

        # ----------------------------------------------------
        # FINAL AI PROMPT
        # ----------------------------------------------------

        final_app_prompt = f"""
You are Nexa AI Professional App Builder.

Create a complete professional app prototype based
on the user's requirements.

USER APP REQUEST:
{app_prompt.strip()}

APP TYPE:
{app_type}

DESIGN STYLE:
{app_style}

TARGET PLATFORM:
{app_platform}

COMPLEXITY:
{app_complexity}

APP NAME:
{app_name.strip() if app_name.strip() else "Nexa App"}

MAIN COLOR:
{app_color.strip() if app_color.strip() else "Choose a professional color palette"}

REQUIRED FEATURES:
{app_features.strip() if app_features.strip() else "Choose appropriate useful features"}

IMPORTANT REQUIREMENTS:

1. Create a professional modern application UI.

2. Generate a complete standalone HTML application.

3. Use HTML5.

4. Use modern CSS.

5. Use JavaScript for application interactions.

6. Put CSS inside <style>.

7. Put JavaScript inside <script>.

8. Do not use React.

9. Do not use Vue.

10. Do not use Angular.

11. Do not require Node.js.

12. Do not require npm.

13. Do not require a build system.

14. The generated app must run by opening
    the HTML file directly in a browser.

15. Make the interface responsive.

16. Create a professional navigation/sidebar.

17. Create a modern dashboard or main application screen
    when appropriate.

18. Implement the requested interactions using JavaScript.

19. Buttons should actually perform useful UI actions.

20. Forms should work on the frontend.

21. Add realistic sample data where necessary.

22. Add search/filter functionality when appropriate.

23. Add modal/dialog functionality when useful.

24. Add notifications/toasts where appropriate.

25. Use localStorage for frontend data persistence
    when appropriate.

26. Create a polished professional UI.

27. Use smooth animations.

28. Use hover effects.

29. Make the app mobile responsive.

30. Avoid broken external dependencies.

31. Do not use lorem ipsum.

32. Use realistic professional text.

33. Keep the code clean and organized.

34. Make the application look like a real commercial
    software product.

CRITICAL OUTPUT RULE:

Return ONLY the complete HTML document.

Do NOT explain the code.

Do NOT use Markdown.

Do NOT wrap the response in ```html.

Start directly with <!DOCTYPE html>
and end with </html>.
"""

        try:

            with st.spinner(
                "🤖 Nexa AI is building your app..."
            ):

                response = client.chat.completions.create(

                    model="poolside/laguna-s-2.1:free",

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Nexa AI Professional "
                                "App Builder. Create modern, "
                                "interactive, responsive and "
                                "standalone HTML applications."
                            )
                        },
                        {
                            "role": "user",
                            "content": final_app_prompt
                        }
                    ],

                    temperature=0.7,

                    max_tokens=12000
                )

                generated_app = (
                    response.choices[0].message.content
                )

                # ------------------------------------------------
                # CLEAN MARKDOWN CODE BLOCKS
                # ------------------------------------------------

                generated_app = (
                    generated_app
                    .replace("```html", "")
                    .replace("```HTML", "")
                    .replace("```Html", "")
                    .replace("```", "")
                    .strip()
                )

                # ------------------------------------------------
                # FIND HTML START
                # ------------------------------------------------

                html_start = generated_app.lower().find(
                    "<!doctype html>"
                )

                if html_start == -1:

                    html_start = generated_app.lower().find(
                        "<html"
                    )

                if html_start > 0:

                    generated_app = (
                        generated_app[html_start:]
                    )

                # ------------------------------------------------
                # SAVE GENERATED APP
                # ------------------------------------------------

                st.session_state.generated_app = (
                    generated_app
                )

                st.session_state.app_generated = True

            st.success(
                "✅ App successfully generated!"
            )

        except Exception as e:

            st.error(
                f"❌ App generation failed: {e}"
            )

    # ========================================================
    # 🚀 GENERATE / REGENERATE
    # ========================================================

    generate_col1, generate_col2 = st.columns(2)

    with generate_col1:

        if st.button(
            "🚀 Generate App",
            use_container_width=True,
            type="primary",
            key="generate_nexa_app"
        ):

            generate_nexa_app()

    with generate_col2:

        if st.button(
            "🔄 Regenerate App",
            use_container_width=True,
            key="regenerate_nexa_app"
        ):

            if app_prompt.strip():

                generate_nexa_app()

            else:

                st.warning(
                    "⚠️ Please enter an app description first."
                )

    # ========================================================
    # 🖥️ APP WORKSPACE
    # ========================================================

    if (
        "generated_app" in st.session_state
        and st.session_state.generated_app
    ):

        generated_app = (
            st.session_state.generated_app
        )

        st.markdown("---")

        st.markdown("## 🖥️ App Workspace")

        # ====================================================
        # LIVE APP PREVIEW
        # ====================================================

        st.markdown("### 👁️ Live App Preview")

        st.components.v1.html(
            generated_app,
            height=720,
            scrolling=True
        )

        st.markdown("---")

        # ====================================================
        # GENERATED CODE
        # ====================================================

        st.markdown("### 💻 Generated App Code")

        st.code(
            generated_app,
            language="html"
        )

        st.markdown("---")

        # ====================================================
        # EXPORT
        # ====================================================

        st.markdown("### 📦 Export App")

        export_col1, export_col2 = st.columns(2)

        with export_col1:

            st.download_button(
                "⬇️ Download App",
                data=generated_app,
                file_name="nexa_app.html",
                mime="text/html",
                use_container_width=True,
                key="download_nexa_app"
            )

        with export_col2:

            if st.button(
                "🧹 Clear App",
                use_container_width=True,
                key="clear_nexa_app"
            ):

                if "generated_app" in st.session_state:

                    del st.session_state[
                        "generated_app"
                    ]

                if "app_generated" in st.session_state:

                    del st.session_state[
                        "app_generated"
                    ]

                st.rerun()

        st.info(
            "💡 Your generated app is a standalone HTML file "
            "containing HTML, CSS and JavaScript."
        )





# ============================================================
# 🔥 EXPLORE CATEGORY
# ============================================================

if creation_category == "🔥 Explore":

    st.session_state.selected_creation = "explore"

    st.markdown("## 🔥 Explore Nexa Creations")

    st.info(
        "Discover AI-powered creation tools and featured models."
    )

    

    # ============================================================
    # 📷 CAMERA
    # ============================================================

    st.markdown("### 📷 Nexa Camera")

    camera_photo = st.camera_input(
        "Take a picture",
        key="nexa_camera"
    )

    if camera_photo is not None:

        st.success("✅ Photo captured!")

        st.image(
            camera_photo,
            caption="📸 Your Photo",
            use_container_width=True
        )

    
# ============================================================
# 📈 DIGITAL MARKETING CATEGORY — AI POWERED
# ============================================================

elif creation_category == "📈 Digital Marketing":

    st.markdown("## 📈 Nexa AI Digital Marketing Studio")

    st.info(
        "🚀 Generate Social Posts, Captions, Hashtags, Ads, SEO, "
        "Emails, Strategies, Campaigns and more with Nexa AI."
    )

    


    # ========================================================
    # 🛠️ MARKETING TOOL SELECTOR
    # ========================================================

    marketing_tool = st.selectbox(

        "🛠️ Choose Marketing Tool",

        [
            "📱 Social Media Post",
            "✍️ Caption Generator",
            "#️⃣ Hashtag Generator",
            "📢 Ad Copy Generator",
            "🎯 Target Audience",
            "🔍 SEO Keywords",
            "📝 SEO Blog Writer",
            "📧 Email Marketing",
            "🛍️ Product Description",
            "📅 Content Calendar",
            "💡 Campaign Ideas",
            "📊 Marketing Strategy",
            "🏆 Competitor Analysis",
            "🔥 CTA Generator"
        ],

        key="nexa_marketing_tool"
    )

    st.divider()


    if marketing_tool == "📱 Social Media Post":

         st.subheader("📱 Social Media Post Generator")

    platform = st.selectbox(
        "Platform",
        [
            "Facebook",
            "Instagram",
            "LinkedIn",
            "X / Twitter",
            "TikTok"
        ],
        key="nexa_social_platform"
    )

    topic = st.text_area(
        "What should the post be about?",
        placeholder="Example: AI tools for small businesses",
        key="nexa_social_topic"
    )

    tone = st.selectbox(
        "Tone",
        [
            "Professional",
            "Friendly",
            "Funny",
            "Luxury",
            "Persuasive"
        ],
        key="nexa_social_tone"
    )

    if st.button(
        "🚀 Generate Social Post",
        use_container_width=True,
        key="generate_social_post"
    ):

        if not topic.strip():

            st.warning("⚠️ Please enter a topic.")

        else:

            prompt = f"""
Create a high-quality social media post.

Platform: {platform}

Topic:
{topic}

Tone:
{tone}

Requirements:

- Create an attention-grabbing hook
- Write engaging content
- Make it suitable for {platform}
- Include a clear call-to-action
- Use suitable emojis
- Add relevant hashtags
- Make it ready to publish

Return ONLY the final social media post.
"""

            with st.spinner("🤖 Nexa AI is creating your post..."):

                result = nexa_marketing_ai(prompt)

            st.markdown("### 🤖 Nexa AI Result")

            if result.startswith("❌"):

                st.error(result)

            else:

                st.markdown(result)


    # ========================================================
    # 2️⃣ CAPTION GENERATOR
    # ========================================================

    elif marketing_tool == "✍️ Caption Generator":

        st.subheader("✍️ Caption Generator")

        topic = st.text_area(
            "Caption topic",
            placeholder="Example: New digital marketing service",
            key="nexa_caption_topic"
        )

        style = st.selectbox(
            "Caption Style",
            ["Professional", "Viral", "Short", "Storytelling", "Luxury"],
            key="nexa_caption_style"
        )

        if st.button(
            "✨ Generate Caption",
            use_container_width=True,
            key="generate_caption"
        ):

            if not topic.strip():

                st.warning("⚠️ Enter a caption topic.")

            else:

                prompt = f"""
Generate an engaging social media caption.

Topic:
{topic}

Style:
{style}

Create a ready-to-post caption with:
- Strong hook
- Engaging body
- CTA
- Relevant hashtags
"""

                with st.spinner("🤖 Generating caption..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI Caption")
                st.write(result)


    # ========================================================
    # 3️⃣ HASHTAG GENERATOR
    # ========================================================

    elif marketing_tool == "#️⃣ Hashtag Generator":

        st.subheader("#️⃣ Hashtag Generator")

        topic = st.text_area(
            "Topic / Niche",
            placeholder="Example: Digital marketing in Pakistan",
            key="nexa_hashtag_topic"
        )

        platform = st.selectbox(
            "Platform",
            ["Instagram", "TikTok", "Facebook", "LinkedIn", "X / Twitter"],
            key="nexa_hashtag_platform"
        )

        if st.button(
            "🔥 Generate Hashtags",
            use_container_width=True,
            key="generate_hashtags"
        ):

            if not topic.strip():

                st.warning("⚠️ Enter a topic.")

            else:

                prompt = f"""
Generate powerful hashtags.

Topic:
{topic}

Platform:
{platform}

Give:
- 10 high-volume hashtags
- 10 niche hashtags
- 10 low-competition hashtags
- Best recommended hashtag combination
"""

                with st.spinner("🤖 Finding hashtags..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI Hashtags")
                st.write(result)


    # ========================================================
    # 4️⃣ AD COPY
    # ========================================================

    elif marketing_tool == "📢 Ad Copy Generator":

        st.subheader("📢 Ad Copy Generator")

        product = st.text_area(
            "Product / Service",
            placeholder="Example: SEO services for small businesses",
            key="nexa_ad_product"
        )

        platform = st.selectbox(
            "Ad Platform",
            ["Facebook Ads", "Instagram Ads", "Google Ads", "TikTok Ads"],
            key="nexa_ad_platform"
        )

        audience = st.text_input(
            "Target Audience",
            placeholder="Example: Small business owners",
            key="nexa_ad_audience"
        )

        if st.button(
            "📢 Generate Ad Copy",
            use_container_width=True,
            key="generate_ad_copy"
        ):

            if not product.strip():

                st.warning("⚠️ Enter your product/service.")

            else:

                prompt = f"""
Create high-converting advertising copy.

Product/Service:
{product}

Platform:
{platform}

Target Audience:
{audience}

Create:
1. Primary text
2. Headline
3. Description
4. CTA
5. Short version
6. Strong emotional hook
"""

                with st.spinner("🤖 Creating ad copy..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI Ad Copy")
                st.write(result)


    # ========================================================
    # 5️⃣ TARGET AUDIENCE
    # ========================================================

    elif marketing_tool == "🎯 Target Audience":

        st.subheader("🎯 Target Audience Generator")

        product = st.text_area(
            "Product / Service",
            placeholder="Example: Online graphic design course",
            key="nexa_audience_product"
        )

        if st.button(
            "🎯 Find Target Audience",
            use_container_width=True,
            key="generate_target_audience"
        ):

            if not product.strip():

                st.warning("⚠️ Enter your product/service.")

            else:

                prompt = f"""
Analyze the ideal target audience for:

{product}

Give detailed information about:

- Age
- Gender
- Location
- Interests
- Problems
- Pain points
- Buying behavior
- Income level
- Online platforms
- Customer motivations
- Best advertising angle
- Best content strategy
"""

                with st.spinner("🤖 Analyzing audience..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI Target Audience")
                st.write(result)


    # ========================================================
    # 6️⃣ SEO KEYWORDS
    # ========================================================

    elif marketing_tool == "🔍 SEO Keywords":

        st.subheader("🔍 SEO Keyword Research")

        topic = st.text_area(
            "Website / Business Topic",
            placeholder="Example: Digital marketing services",
            key="nexa_seo_topic"
        )

        country = st.text_input(
            "Target Country",
            value="Pakistan",
            key="nexa_seo_country"
        )

        if st.button(
            "🔎 Generate SEO Keywords",
            use_container_width=True,
            key="generate_seo_keywords"
        ):

            if not topic.strip():

                st.warning("⚠️ Enter your topic.")

            else:

                prompt = f"""
Perform SEO keyword research.

Topic:
{topic}

Target Country:
{country}

Generate:

- 20 primary keywords
- 20 long-tail keywords
- 10 commercial keywords
- 10 informational keywords
- 10 local keywords
- Search intent
- Suggested page for each keyword
- SEO content opportunities
"""

                with st.spinner("🤖 Researching keywords..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI SEO Keywords")
                st.write(result)


    # ========================================================
    # 7️⃣ SEO BLOG WRITER
    # ========================================================

    elif marketing_tool == "📝 SEO Blog Writer":

        st.subheader("📝 SEO Blog Writer")

        topic = st.text_input(
            "Blog Topic",
            placeholder="Example: Best digital marketing strategies",
            key="nexa_blog_topic"
        )

        length = st.selectbox(
            "Blog Length",
            ["Short", "Medium", "Long", "2000+ Words"],
            key="nexa_blog_length"
        )

        keyword = st.text_input(
            "Main SEO Keyword",
            placeholder="Example: digital marketing services",
            key="nexa_blog_keyword"
        )

        if st.button(
            "✍️ Generate SEO Blog",
            use_container_width=True,
            key="generate_seo_blog"
        ):

            if not topic.strip():

                st.warning("⚠️ Enter blog topic.")

            else:

                prompt = f"""
Write a complete SEO-optimized blog article.

Topic:
{topic}

Length:
{length}

Main Keyword:
{keyword}

Include:

- SEO title
- Meta description
- Introduction
- H1
- H2 headings
- H3 headings
- Useful detailed content
- Bullet points
- FAQs
- Conclusion
- CTA

Write naturally and avoid keyword stuffing.
"""

                with st.spinner("🤖 Writing SEO blog..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI SEO Blog")
                st.write(result)


    # ========================================================
    # 8️⃣ EMAIL MARKETING
    # ========================================================

    elif marketing_tool == "📧 Email Marketing":

        st.subheader("📧 Email Marketing Generator")

        goal = st.selectbox(
            "Email Goal",
            [
                "Product Promotion",
                "Welcome Email",
                "Sales Email",
                "Newsletter",
                "Abandoned Cart",
                "Customer Retention"
            ],
            key="nexa_email_goal"
        )

        product = st.text_area(
            "Product / Business",
            key="nexa_email_product"
        )

        if st.button(
            "📧 Generate Email",
            use_container_width=True,
            key="generate_email"
        ):

            if not product.strip():

                st.warning("⚠️ Enter product/business details.")

            else:

                prompt = f"""
Write a professional marketing email.

Goal:
{goal}

Product/Business:
{product}

Include:

- Subject line
- Preview text
- Personalized greeting
- Strong opening
- Main message
- Benefits
- CTA
- Professional closing

Make it persuasive but natural.
"""

                with st.spinner("🤖 Writing email..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI Email")
                st.write(result)


    # ========================================================
    # 9️⃣ PRODUCT DESCRIPTION
    # ========================================================

    elif marketing_tool == "🛍️ Product Description":

        st.subheader("🛍️ Product Description Generator")

        product_name = st.text_input(
            "Product Name",
            key="nexa_product_name"
        )

        details = st.text_area(
            "Product Details",
            placeholder="Features, benefits, price, audience etc.",
            key="nexa_product_details"
        )

        if st.button(
            "🛍️ Generate Description",
            use_container_width=True,
            key="generate_product_description"
        ):

            if not product_name.strip():

                st.warning("⚠️ Enter product name.")

            else:

                prompt = f"""
Create a high-converting product description.

Product:
{product_name}

Details:
{details}

Include:

- Short description
- Full description
- Key features
- Customer benefits
- Emotional selling points
- SEO keywords
- CTA

Make it suitable for an online store.
"""

                with st.spinner("🤖 Creating product description..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI Product Description")
                st.write(result)


    # ========================================================
    # 🔟 CONTENT CALENDAR
    # ========================================================

    elif marketing_tool == "📅 Content Calendar":

        st.subheader("📅 AI Content Calendar")

        business = st.text_input(
            "Business / Niche",
            placeholder="Example: Real estate",
            key="nexa_calendar_business"
        )

        days = st.selectbox(
            "Calendar Duration",
            ["7 Days", "14 Days", "30 Days"],
            key="nexa_calendar_days"
        )

        if st.button(
            "📅 Generate Content Calendar",
            use_container_width=True,
            key="generate_content_calendar"
        ):

            if not business.strip():

                st.warning("⚠️ Enter business/niche.")

            else:

                prompt = f"""
Create a social media content calendar.

Business:
{business}

Duration:
{days}

For each day provide:

- Day
- Content idea
- Platform
- Post type
- Caption idea
- CTA
- Hashtags
"""

                with st.spinner("🤖 Planning content calendar..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI Content Calendar")
                st.write(result)


    # ========================================================
    # 1️⃣1️⃣ CAMPAIGN IDEAS
    # ========================================================

    elif marketing_tool == "💡 Campaign Ideas":

        st.subheader("💡 Marketing Campaign Ideas")

        business = st.text_area(
            "Business / Product",
            placeholder="Example: Clothing brand",
            key="nexa_campaign_business"
        )

        if st.button(
            "💡 Generate Campaign Ideas",
            use_container_width=True,
            key="generate_campaign_ideas"
        ):

            if not business.strip():

                st.warning("⚠️ Enter business details.")

            else:

                prompt = f"""
Generate 10 creative marketing campaign ideas.

Business:
{business}

For every campaign provide:

- Campaign name
- Main idea
- Target audience
- Platform
- Content concept
- Offer
- CTA
- Expected goal
"""

                with st.spinner("🤖 Creating campaign ideas..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI Campaign Ideas")
                st.write(result)


    # ========================================================
    # 1️⃣2️⃣ MARKETING STRATEGY
    # ========================================================

    elif marketing_tool == "📊 Marketing Strategy":

        st.subheader("📊 Marketing Strategy Generator")

        business = st.text_area(
            "Business",
            placeholder="Describe your business...",
            key="nexa_strategy_business"
        )

        goal = st.text_input(
            "Main Goal",
            placeholder="Example: Get 100 new customers",
            key="nexa_strategy_goal"
        )

        if st.button(
            "📊 Generate Marketing Strategy",
            use_container_width=True,
            key="generate_marketing_strategy"
        ):

            if not business.strip():

                st.warning("⚠️ Enter business details.")

            else:

                prompt = f"""
Create a complete digital marketing strategy.

Business:
{business}

Main Goal:
{goal}

Include:

1. Business analysis
2. Target audience
3. Positioning
4. Content strategy
5. Social media strategy
6. SEO strategy
7. Paid advertising strategy
8. Lead generation
9. Conversion strategy
10. Retention strategy
11. 30-day action plan
12. KPIs
"""

                with st.spinner("🤖 Building marketing strategy..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI Marketing Strategy")
                st.write(result)


    # ========================================================
    # 1️⃣3️⃣ COMPETITOR ANALYSIS
    # ========================================================

    elif marketing_tool == "🏆 Competitor Analysis":

        st.subheader("🏆 Competitor Analysis")

        business = st.text_input(
            "Your Business",
            key="nexa_competitor_business"
        )

        competitors = st.text_area(
            "Competitor Names",
            placeholder="Example: Competitor A, Competitor B",
            key="nexa_competitor_names"
        )

        if st.button(
            "🏆 Analyze Competitors",
            use_container_width=True,
            key="analyze_competitors"
        ):

            if not business.strip():

                st.warning("⚠️ Enter your business.")

            else:

                prompt = f"""
Create a competitor marketing analysis.

My Business:
{business}

Competitors:
{competitors}

Analyze:

- Competitor positioning
- Strengths
- Weaknesses
- Content strategy
- Social media opportunities
- SEO opportunities
- Advertising opportunities
- Customer pain points
- Market gaps
- How my business can differentiate
- Recommended strategy
"""

                with st.spinner("🤖 Analyzing competitors..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI Competitor Analysis")
                st.write(result)


    # ========================================================
    # 1️⃣4️⃣ CTA GENERATOR
    # ========================================================

    elif marketing_tool == "🔥 CTA Generator":

        st.subheader("🔥 Call-To-Action Generator")

        product = st.text_area(
            "Product / Service",
            placeholder="Example: Website design service",
            key="nexa_cta_product"
        )

        goal = st.selectbox(
            "CTA Goal",
            [
                "Buy Now",
                "Get Leads",
                "Book a Call",
                "Sign Up",
                "Download",
                "Contact Us",
                "Learn More"
            ],
            key="nexa_cta_goal"
        )

        if st.button(
            "🔥 Generate CTAs",
            use_container_width=True,
            key="generate_ctas"
        ):

            if not product.strip():

                st.warning("⚠️ Enter product/service.")

            else:

                prompt = f"""
Generate powerful Call-To-Actions.

Product/Service:
{product}

Goal:
{goal}

Create:

- 10 short CTAs
- 10 persuasive CTAs
- 10 emotional CTAs
- 5 urgency CTAs
- 5 premium/luxury CTAs

Make them suitable for digital marketing.
"""

                with st.spinner("🤖 Creating powerful CTAs..."):

                    result = nexa_marketing_ai(prompt)

                st.markdown("### 🤖 Nexa AI CTAs")
                st.write(result)



st.caption(
    "🚀 AI generation engine will be connected in the next step."
)
st.header("Turn your thoughts into action.")

# Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # ============================================================
# 🧠 NEXA WEB SEARCH DETECTOR
# ============================================================

def needs_web_search(user_input):

    text = user_input.lower()

    keywords = [
        "latest",
        "today",
        "current",
        "right now",
        "recent",
        "news",
        "price",
        "weather",
        "score",
        "update",
        "updates",
        "search",
        "online",
        "website",
        "internet",
        "2026",
        "what happened",
        "find"
    ]

    return any(word in text for word in keywords)
    # =========================
# 🧠 NEXA MEMORY SYSTEM
# =========================

MEMORY_FILE = Path(__file__).parent / "nexa_memory.json"

if not MEMORY_FILE.exists():
    MEMORY_FILE.write_text(
        "{}",
        encoding="utf-8"
    )


def load_nexa_memory():
    try:
        return json.loads(
            MEMORY_FILE.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return {}


def save_nexa_memory(memory):
    MEMORY_FILE.write_text(
        json.dumps(
            memory,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


if "nexa_memory" not in st.session_state:
    st.session_state.nexa_memory = load_nexa_memory()
    # Fix old memory format
if isinstance(st.session_state.nexa_memory, dict):
    st.session_state.nexa_memory = []
    # =========================
# 📋 NEXA SAVED MEMORIES
# =========================

if st.session_state.nexa_memory:

    st.markdown("### 🧠 Nexa Memories")

    for index, memory in enumerate(st.session_state.nexa_memory):

        st.write(f"🧠 {memory}")

from openai import OpenAI

st.title("⚡ Nexa your thoughts into action.")
# =========================
# MODERN NEXA UI
# =========================

st.markdown("""
<style>

.stApp {
    background: #0B0F19;
    color: #F8FAFC;
}

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1F2937;
}
/* 
""", unsafe_allow_html=True)
# =========================
# NEXA SIDEBAR
# =========================

with st.sidebar:
    st.markdown(
        '<div class="nexa-logo">🚀 NEXA AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="nexa-tagline">Think • Create • Build</div>',
        unsafe_allow_html=True
    )

if st.button("＋ New Chat"):
    if st.session_state.chat_history:

        first_message = st.session_state.chat_history[0]

        if isinstance(first_message, dict):
            title = first_message.get("idea", "Nexa Chat")
        else:
            title = str(first_message)

        st.session_state.recent_chats.append({
            "title": title[:30],
            "messages": st.session_state.chat_history.copy()
        })

        # Sirf last 10 chats
        st.session_state.recent_chats = \
            st.session_state.recent_chats[-10:]

    # New empty chat
    st.session_state.chat_history = []

    st.rerun()
           # =========================
    # 🎨 AI CREATION
    # =========================

    if "show_ai_creation" not in st.session_state:
        st.session_state.show_ai_creation = False

    if st.button(
        "🎨 AI Creation",
        use_container_width=True
    ):
        st.session_state.show_ai_creation = True
       # =========================
# 🎙️ VOICE MENU
# =========================

if "show_voices" not in st.session_state:
    st.session_state.show_voices = False

if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = "👨 Male — Calm"

if st.button("🎙️ Voices"):
    st.session_state.show_voices = not st.session_state.show_voices

if st.session_state.show_voices:

    st.markdown("#### 🎙️ Choose Voice")

    st.radio(
        "Nexa Voice",
        [
            "👨 Male — Calm",
            "👨 Male — Deep",
            "👩 Female — Natural",
            "👩 Female — Professional"
        ],
        key="selected_voice"
    )

    st.caption(
        f"Selected: {st.session_state.selected_voice}"
    )

selected_model = st.selectbox(
    "🤖 Select Model",
    [
        "nvidia/nemotron-3-ultra-550b-a55b:free"
    ]
)

st.caption(f"Current model: {selected_model}")
temperature = st.slider(
    "🌡️ Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="Lower = more focused, Higher = more creative"
)

st.caption(f"Temperature: {temperature}")
#============================================================
# 🎙️ NEXA SIMPLE VOICE CALL
# ============================================================

st.markdown("### 📞 Nexa Voice Call")

st.caption(
    "Talk naturally with Nexa using your microphone."
)

call_mode = st.toggle(
    "📞 Start Voice Call",
    key="nexa_call_mode"
)

if call_mode:

    st.success("🟢 Nexa Voice Call is ready")

    voice_audio = st.audio_input(
        "🎙️ Tap here and speak to Nexa",
        key="nexa_call_audio"
    )

    if voice_audio:

        recognizer = sr.Recognizer()

        try:

            # ====================================================
            # 🎙️ SPEECH → TEXT
            # ====================================================

            audio_bytes = voice_audio.getvalue()

            with sr.AudioFile(
                io.BytesIO(audio_bytes)
            ) as source:

                recorded_audio = recognizer.record(source)

            voice_text = recognizer.recognize_google(
                recorded_audio
            )

            st.markdown("### 🗣️ You")
            st.write(voice_text)

            # ====================================================
            # 🧠 NEXA AI RESPONSE
            # ====================================================

            with st.spinner("🧠 Nexa is thinking..."):

                voice_response = client.chat.completions.create(

                    model=selected_model,

                    messages=[
                        {
                            "role": "system",
                            "content": """
You are Nexa AI, a friendly and intelligent
voice assistant.

Speak naturally like a real human assistant.

Keep your responses:
- Clear
- Short
- Natural
- Conversational
- Easy to understand

Do not use unnecessary headings.

Do not give very long answers unless
the user asks for detailed information.
"""
                        },
                        {
                            "role": "user",
                            "content": voice_text
                        }
                    ],

                    temperature=temperature,
                    max_tokens=500
                )

            # ====================================================
            # 💬 SHOW NEXA RESPONSE
            # ====================================================

            if voice_response and voice_response.choices:

                voice_answer = (
                    voice_response
                    .choices[0]
                    .message
                    .content
                )

                st.markdown("### 🤖 Nexa AI")

                st.write(voice_answer)

                # ====================================================
                # 🔊 SPEAK RESPONSE
                # ====================================================

                speech_script = f"""
                <script>

                const text = {json.dumps(voice_answer)};

                const speech =
                    new SpeechSynthesisUtterance(text);

                speech.rate = 0.95;
                speech.pitch = 1.0;
                speech.volume = 1.0;

                window.speechSynthesis.cancel();

                window.speechSynthesis.speak(speech);

                </script>
                """

                st.components.v1.html(
                    speech_script,
                    height=20
                )

            else:

                st.error(
                    "❌ Nexa did not return a response."
                )

        except sr.UnknownValueError:

            st.error(
                "❌ Nexa could not understand your voice."
            )

        except sr.RequestError as e:

            st.error(
                f"❌ Speech recognition error: {e}"
            )

        except Exception as e:

            st.error(
                f"❌ Voice Call Error: {e}"
            )
            # ============================================================
# 💳 NEXA SUBSCRIPTION
# ============================================================

st.markdown("### 💳 Subscription")

if current_plan == "Free":
    st.info("🆓 Current Plan: Free")
elif current_plan == "Pro":
    st.success("⭐ Current Plan: Pro")
else:
    st.success("🏢 Current Plan: Business")

st.caption(
    f"Messages: {current_plan_data['daily_messages']}"
)

if st.button("💎 View Plans", use_container_width=True):

    st.session_state.show_subscription = True


# ============================================================
# 📦 PLAN SELECTION
# ============================================================

if "show_subscription" not in st.session_state:
    st.session_state.show_subscription = False


if st.session_state.show_subscription:

    st.markdown("---")
    st.markdown("## 💎 Nexa AI Plans")

    st.caption(
        "Choose a plan that fits your usage."
    )

    # ========================================================
    # 🆓 FREE
    # ========================================================

    st.markdown("### 🆓 Free")

    st.write("Rs. 0 — Forever")
    st.write("• 10 AI messages/day")
    st.write("• 2 image generations")
    st.write("• Basic Nexa features")

    if st.button(
        "Use Free",
        key="choose_free",
        use_container_width=True
    ):

        st.session_state.subscription_plan = "Free"

        st.success(
            "✅ Free plan selected!"
        )

        st.rerun()


    st.markdown("---")


    # ========================================================
    # ⭐ PRO
    # ========================================================

    st.markdown("### ⭐ Pro")

    st.write("**Rs. 1,499 / month**")
    st.write("• 100 AI messages/day")
    st.write("• 20 image generations")
    
    st.write("• 50 voice calls")
    st.write("• Higher limits")

    if st.button(
        "⭐ Upgrade to Pro",
        key="choose_pro",
        use_container_width=True
    ):

        st.info(
            "💳 Pro subscription payment ke baad "
            "activate hogi."
        )


    st.markdown("---")


    # ========================================================
    # 🏢 BUSINESS
    # ========================================================

    st.markdown("### 🏢 Business")

    st.write("**Rs. 4,999 / month**")
    st.write("• 500 AI messages/day")
    st.write("• 100 image generations")
    
    st.write("• 200 voice calls")
    st.write("• Business features")
    st.write("• Higher usage limits")

    if st.button(
        "🏢 Upgrade to Business",
        key="choose_business",
        use_container_width=True
    ):

        st.info(
            "💳 Business subscription payment ke baad "
            "activate hogi."
        )
            
theme = st.radio(
    "🌓 Theme",
    ["Dark", "Light"],
    horizontal=True
)

if theme == "Light":
    st.markdown("""
        <style>
        .stApp {
            background: #FFFFFF !important;
            color: #111827 !important;
        }

        section[data-testid="stSidebar"] {
            background: #F3F4F6 !important;
        }

        .stMarkdown, .stText, label {
            color: #111827 !important;
        }
        </style>
    """, unsafe_allow_html=True)


# ============================================================
# 👤 USER + LOGOUT
# ============================================================

st.markdown("---")

st.markdown(
    f"👤 **{st.session_state.logged_username}**"
)

if st.button(
    "🚪 Logout",
    use_container_width=True
):

    username = st.session_state.logged_username

    # Save latest user data
    if username in users:

        users[username]["plan"] = st.session_state.get(
            "subscription_plan",
            "Free"
        )

        users[username]["usage"] = st.session_state.get(
            "subscription_usage",
            {
                "messages": 0,
                "images": 0,
                "voice": 0
            }
        )

        save_users(users)

    # Logout
    st.session_state.account_logged_in = False
    st.session_state.logged_username = None

    st.rerun()
else:
    st.markdown("""
        <style>
        .stApp {
            background: #0B0F19 !important;
            color: #F8FAFC !important;
        }

        section[data-testid="stSidebar"] {
            background: #111827 !important;
        }
        </style>
    """, unsafe_allow_html=True)

st.markdown("### 🟢 API Status")

if st.button("🔄 Check API Status"):
    st.success("✅ BUTTON IS WORKING")

    try:
        test_response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "user",
                    "content": "Reply with only: OK"
                }
            ],
            max_tokens=5,
            temperature=0
        )

        if test_response and test_response.choices:
            st.success("🟢 API Connected")
        else:
            st.warning("🟡 API connected, but no response received.")
    except Exception as e:
        st.error("🔴 API Connection Failed")
        st.code(str(e))
st.markdown("### 🗑️ Chat History")

if st.button("🗑️ Clear All Chat History"):
    st.session_state.chat_history = []
    st.session_state.confirm_clear = False
    st.success("✅ Chat history cleared!")
    st.rerun()

# ============================================================
# 💾 NEXA AI — PERMANENT RECENT CHATS
# ============================================================

RECENT_CHATS_FILE = Path(__file__).parent / "recent_chats.json"


# ============================================================
# 📂 LOAD SAVED CHATS
# ============================================================

def load_recent_chats():
    try:
        if RECENT_CHATS_FILE.exists():

            with open(
                RECENT_CHATS_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            if isinstance(data, list):
                return data

    except Exception:
        pass

    return []


# ============================================================
# 💾 SAVE CHATS
# ============================================================

def save_recent_chats(chats):
    try:

        with open(
            RECENT_CHATS_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                chats,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception:
        pass


# ============================================================
# 🕘 RECENT CHATS
# ============================================================

st.markdown("### 🕘")
st.markdown("**RECENT CHATS**")


# Load chats when Nexa starts
if "recent_chats" not in st.session_state:

    st.session_state.recent_chats = (
        load_recent_chats()
    )


# ============================================================
# 💬 SAVE / UPDATE CURRENT CHAT
# ============================================================

if st.session_state.chat_history:

    first_message = st.session_state.chat_history[0]

    # Get title from first user message
    if isinstance(first_message, dict):

        chat_title = first_message.get(
            "idea",
            "Nexa Chat"
        )

    else:

        chat_title = str(first_message)


    chat_title = str(chat_title).strip()[:40]


    # ========================================================
    # CHECK IF CHAT ALREADY EXISTS
    # ========================================================

    existing_chat = None

    for chat in st.session_state.recent_chats:

        if chat.get("title") == chat_title:

            existing_chat = chat
            break


    # ========================================================
    # UPDATE EXISTING CHAT
    # ========================================================

    if existing_chat:

        existing_chat["messages"] = (
            st.session_state.chat_history.copy()
        )


    # ========================================================
    # ADD NEW CHAT
    # ========================================================

    else:

        st.session_state.recent_chats.insert(
            0,
            {
                "title": chat_title,
                "messages": (
                    st.session_state.chat_history.copy()
                )
            }
        )


    # ========================================================
    # KEEP ONLY LATEST 10
    # ========================================================

    st.session_state.recent_chats = (
        st.session_state.recent_chats[:10]
    )


    # ========================================================
    # 💾 PERMANENTLY SAVE TO JSON
    # ========================================================

    save_recent_chats(
        st.session_state.recent_chats
    )


# ============================================================
# 📋 DISPLAY RECENT CHATS
# ============================================================

if st.session_state.recent_chats:

    for i, chat in enumerate(
        st.session_state.recent_chats
    ):

        if st.button(
            f"💬 {chat.get('title', 'Nexa Chat')}",
            key=f"recent_chat_{i}"
        ):

            st.session_state.chat_history = (
                chat.get("messages", []).copy()
            )

            st.rerun()

else:

    st.caption("No chats yet.")


# ============================================================
# 🗑️ CLEAR CONVERSATION
# ============================================================

if st.button("🗑️ Clear Conversation"):

    st.session_state.confirm_clear = True


if st.session_state.get(
    "confirm_clear",
    False
):

    st.warning(
        "⚠️ Are you sure you want to clear your conversation?"
    )

    col1, col2 = st.columns(2)


    # ========================================================
    # ✅ YES, CLEAR
    # ========================================================

    with col1:

        if st.button("✅ Yes, Clear"):

            st.session_state.chat_history = []

            st.session_state.confirm_clear = False

            st.rerun()


    # ========================================================
    # ❌ CANCEL
    # ========================================================

    with col2:

        if st.button("❌ Cancel"):

            st.session_state.confirm_clear = False

            st.rerun()


# ============================================================
# 🗑️ CLEAR ALL SAVED RECENT CHATS
# ============================================================

st.markdown("### 🗑️ Chat History")

if st.button(
    "🗑️ Clear All Chat History",
    key="clear_all_chat_history_button"
):

    st.session_state.chat_history = []

    st.session_state.recent_chats = []

    # Permanently delete saved chats
    save_recent_chats([])

    st.success(
        "✅ All chat history cleared!"
    )

    st.rerun()

# =========================
# 🧩 NEXA PLUGINS
# =========================

st.markdown("### 🧩 Nexa Plugins")

plugin = st.selectbox(
    "Choose a Plugin",
    [
        "🤖 Normal AI",
        "💻 Code Expert",
        "📈 Business Advisor",
        "🎨 Content Creator",
        "📚 Study Assistant",
        "🌐 Translator",
        "📄 File Analyzer",
        "🖼️ Image Analyzer",
        "🔎 Web Search",
        "📊 Data Analyst",
        "✍️ Writing Assistant",
        "🧠 Deep Think",
        
    ],
    key="nexa_plugin_selector"
)


# ============================================================
# 🧩 NEXA AI PLUGIN SYSTEM
# ============================================================

NEXA_PLUGINS = {

    "🤖 Normal AI": """
You are Nexa AI, a helpful and intelligent general-purpose AI assistant.

Answer the user's questions clearly and naturally.
Be accurate, useful, friendly and concise.
If the user asks for code, provide working code with explanation.
If the user asks for advice, give practical step-by-step guidance.
""",

    "💻 Code Expert": """
You are Nexa AI Code Expert.

Your job is to help users with programming and software development.

You can:
- Write complete code
- Debug errors
- Explain code line by line
- Improve existing code
- Find bugs
- Build Python, Streamlit, HTML, CSS and JavaScript projects
- Explain errors in simple language

Always provide practical and working solutions.
When fixing code, clearly show exactly what should be replaced.
""",

    "📈 Business Advisor": """
You are Nexa AI Business Advisor.

Help users with:
- Business ideas
- Business planning
- Marketing strategy
- Digital marketing
- Customer acquisition
- Pricing
- Sales
- Branding
- Competitor analysis
- Small business growth

Give realistic, actionable and step-by-step advice.
Avoid unnecessary theory.
""",

    "🎨 Content Creator": """
You are Nexa AI Content Creator.

Help create high-quality:
- Social media posts
- Instagram captions
- Facebook posts
- YouTube titles
- YouTube descriptions
- Reels scripts
- TikTok scripts
- Ad copy
- Marketing content

Make content engaging, modern and audience-focused.
Use emojis when appropriate.
""",

    "📚 Study Assistant": """
You are Nexa AI Study Assistant.

Help students learn difficult topics in simple language.

You can:
- Explain concepts
- Summarize chapters
- Create notes
- Generate MCQs
- Create quizzes
- Make study plans
- Explain answers
- Help with homework

Teach step-by-step and use simple examples.
Do not just give answers when explanation would help learning.
""",

    "🌐 Translator": """
You are Nexa AI Translator.

Translate the user's text accurately while preserving:
- Meaning
- Tone
- Context
- Formatting

If the user specifies a target language, translate into that language.
If no target language is specified, ask which language they want.

Do not unnecessarily explain the translation unless requested.
""",

    "📄 File Analyzer": """
You are Nexa AI File Analyzer.

Analyze uploaded files carefully.

You can:
- Summarize documents
- Answer questions about files
- Extract important information
- Find key points
- Explain difficult content
- Extract tables or structured information
- Compare sections
- Create notes from documents

Base your answers on the uploaded file whenever file content is available.
If the required information is not present, clearly say so.
""",

    "🖼️ Image Analyzer": """
You are Nexa AI Image Analyzer.

Analyze uploaded images carefully.

You can:
- Describe images
- Read visible text
- Explain diagrams
- Identify objects
- Analyze screenshots
- Explain charts
- Extract useful information
- Help understand UI screenshots
- Analyze visual problems

Only claim information that can actually be observed from the image.
""",
"🔎 Web Search": """
You are Nexa AI Web Search Agent.

Your job is to find accurate, current, and useful information from the
internet by searching MULTIPLE different websites and sources.

When the user asks for current or online information, perform web searches
and gather information from several relevant sources instead of relying on
only one website.

Search across different types of reliable sources when appropriate, such as:
- Official websites
- Government websites
- Official company websites
- News websites
- Technology websites
- Research papers and academic sources
- Product websites
- Documentation websites
- Trusted industry websites
- Other reputable sources relevant to the user's question

IMPORTANT MULTI-SOURCE RULES:

1. Search multiple different websites whenever possible.
2. Do not depend on a single source for important information.
3. Compare information from different sources.
4. Prefer official and authoritative sources for facts, products,
   software, companies, policies, prices, and announcements.
5. For news and current events, compare reports from multiple reputable
   news sources.
6. For technology and AI updates, check official announcements,
   documentation, and reliable technology sources.
7. If different sources provide different information, clearly mention
   the difference instead of choosing a result without explanation.
8. Do not invent websites, search results, quotes, statistics, prices,
   or sources.
9. Clearly distinguish CURRENT information from general/background knowledge.
10. Give the user a concise answer first, followed by useful details.
11. When web sources are used, mention the important sources/websites
    used to form the answer.
12. Prefer recent information when the question is time-sensitive.

Use web search for:
- Latest news
- Current events
- Current prices
- Product availability
- Weather
- Sports scores
- Current technology updates
- AI model updates
- Software updates
- Current websites and online information
- Company announcements
- New product launches
- Current market information
- Current social media trends
- Recent research
- Current laws, policies, or official announcements

SOURCE QUALITY PRIORITY:

For important factual questions, prefer sources roughly in this order:

1. Official government / official organization sources
2. Official company or product websites
3. Official documentation
4. Academic / research sources
5. Major reputable news organizations
6. Established industry publications
7. Other reputable websites

If the information cannot be verified from multiple reliable sources,
say so clearly.

If web search is unavailable, do NOT pretend that you searched the web.
Honestly tell the user that live web search is currently unavailable.

Never fabricate search results or sources.
""",
    " 📊 Data Analyst": """
You are Nexa AI Data Analyst.

Help users analyze data.

You can:
- Analyze CSV and Excel files
- Find trends
- Calculate statistics
- Identify patterns
- Explain datasets
- Create summaries
- Compare values
- Find anomalies
- Suggest useful charts
- Help with Python/Pandas analysis

Show calculations or methodology when useful.
Explain results in simple language.
""",

    "✍️ Writing Assistant": """
You are Nexa AI Writing Assistant.

Improve the user's writing while preserving their intended meaning.

You can:
- Rewrite
- Proofread
- Fix grammar
- Improve clarity
- Make text professional
- Make text friendly
- Shorten text
- Expand text
- Write emails
- Write applications
- Write reports
- Improve captions

When rewriting, produce polished ready-to-use text.
""",

    "🧠 Deep Think": """
You are Nexa AI Deep Think.

Solve complex problems carefully and systematically.

Before answering:
- Understand the problem
- Break it into smaller parts
- Consider important possibilities
- Check assumptions
- Look for errors
- Give a clear final conclusion

Do not reveal private chain-of-thought.
Instead, provide a concise explanation of the reasoning and the final answer.
"""
}


# ============================================================
# 🧩 PLUGIN UI
# ============================================================

st.markdown("### 🧩 Nexa AI Plugins")

plugin = st.selectbox(
    "Choose a Plugin",
    list(NEXA_PLUGINS.keys()),
    key="nexa_plugin"
)


# ============================================================
# 🔥 SELECTED PLUGIN INFO
# ============================================================

PLUGIN_INFO = {

    "🤖 Normal AI": "General purpose AI assistant",
    "💻 Code Expert": "Programming, debugging & development",
    "📈 Business Advisor": "Business, sales & marketing strategy",
    "🎨 Content Creator": "Social media & marketing content",
    "📚 Study Assistant": "Learning, notes, quizzes & explanations",
    "🌐 Translator": "Translate text between languages",
    "📄 File Analyzer": "Analyze uploaded documents & files",
    "🖼️ Image Analyzer": "Analyze images & screenshots",
    "🔎 Web Search": "Search current information from the web",
    "📊 Data Analyst": "Analyze CSV, Excel & datasets",
    "✍️ Writing Assistant": "Rewrite, improve & proofread text",
    "🧠 Deep Think": "Complex problem solving"
}


st.caption(
    f"⚡ Active Plugin: **{plugin}** — {PLUGIN_INFO[plugin]}"
)


# ============================================================
# 🎯 EXTRA UI FOR SELECTED PLUGINS
# ============================================================

if plugin == "🌐 Translator":

    target_language = st.selectbox(
        "🌍 Translate To",
        [
            "English",
            "Urdu",
            "Roman Urdu",
            "Arabic",
            "Hindi",
            "French",
            "German",
            "Spanish",
            "Chinese",
            "Japanese"
        ],
        key="translator_language"
    )


elif plugin == "📄 File Analyzer":

    st.info("📄 Upload a file below and Nexa will analyze it.")

    uploaded_plugin_file = st.file_uploader(
        "Upload File",
        type=[
            "pdf",
            "txt",
            "docx",
            "csv",
            "xlsx"
        ],
        key="plugin_file_upload"
    )


elif plugin == "🖼️ Image Analyzer":

    st.info("🖼️ Upload an image for Nexa to analyze.")

    uploaded_plugin_image = st.file_uploader(
        "Upload Image",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        key="plugin_image_upload"
    )


elif plugin == "📊 Data Analyst":

    st.info("📊 Upload CSV or Excel data for analysis.")

    uploaded_data_file = st.file_uploader(
        "Upload Dataset",
        type=[
            "csv",
            "xlsx"
        ],
        key="plugin_data_upload"
    )


elif plugin == "🧠 Deep Think":

    st.info(
        "🧠 Deep Think mode is active. "
        "Nexa will focus on complex problem solving."
    )


# ============================================================
# 🧠 CREATE ACTIVE SYSTEM PROMPT
# ============================================================

active_plugin_prompt = NEXA_PLUGINS[plugin]

active_plugin_prompt += """

FORMATTING RULES:
- Use clear Markdown headings (## and ###) to organize your answer.
- Use relevant emojis naturally in headings and key points.
- Use bullet points or numbered lists where helpful.
"""


# ============================================================
# 🌐 TRANSLATOR ADDITION
# ============================================================

if plugin == "🌐 Translator":

    active_plugin_prompt += f"""

The selected target language is: {target_language}

Translate the user's requested text into this language.
"""


# =========================
# 🧠 TEST NEXA MEMORY
# =========================

memory_input = st.text_input(
    "🧠 Tell Nexa something to remember",
    placeholder="Example: My name is Ayyan"
)
if st.button("💾 Remember This"):

    if memory_input.strip():

        st.session_state.nexa_memory.append(
            memory_input.strip()
        )

        save_nexa_memory(
            st.session_state.nexa_memory
        )

        st.success("🧠 Nexa remembered this permanently!")

    else:

        st.warning("⚠️ Please enter something first.")


st.markdown("###  Tell Nexa what you have in mind")
idea = st.text_area(
    "Tell nexa your goal , idea , probelm or question...",
    placeholder="start typing here...",
    height=150
)
# 🎙️ Nexa Browser Voice

st.markdown("### 🎙️ Voice Input")

st.components.v1.html("""
<script>
function startNexaVoice() {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Voice recognition is not supported in this browser.");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.start();

    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        document.getElementById("nexaVoiceText").innerText =
            "🗣️ You said: " + text;
    };

    recognition.onerror = function(event) {
        document.getElementById("nexaVoiceText").innerText =
            "❌ Voice error: " + event.error;
    };
}
</script>

<button onclick="startNexaVoice()">
🎙️ Start Voice
</button>

<p id="nexaVoiceText">Press the button and speak.</p>
""", height=120)






        

# =========================
# 🚀 NEXA LAUNCH + 🛑 STOP
# =========================

if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False

if "current_response" not in st.session_state:
    st.session_state.current_response = ""

col1, col2 = st.columns(2)

with col1:
    launch = st.button(
        "⚡ Launch Nexa",
        use_container_width=True
    )

with col2:
    stop = st.button(
        "🛑 Stop Generation",
        use_container_width=True
    )


# =========================
# 🛑 STOP GENERATION
# =========================

if stop:
    st.session_state.stop_generation = True
    st.warning("⛔ Stop signal sent to Nexa.")



# =========================
# ⚡ LAUNCH NEXA
# =========================

if launch:

    st.session_state.stop_generation = False

    if not idea.strip():

        st.warning("⚠️ Please enter an idea first.")

    else:

        # =================================================
        # 💳 SUBSCRIPTION LIMIT CHECK
        # =================================================

        current_plan = st.session_state.subscription_plan

        plan_limit = PLANS[current_plan]["daily_messages"]

        current_usage = st.session_state.subscription_usage["messages"]

        if current_usage >= plan_limit:

            st.error(
                f"🔒 {current_plan} plan limit reached.\n\n"
                f"You have used {current_usage} / {plan_limit} messages."
            )

            st.info(
                "💎 Upgrade your plan to get higher limits."
            )

            st.stop()

        # Count this AI request
        st.session_state.subscription_usage["messages"] += 1

        try:

            st.info("🔵 Launch clicked")

            # =================================================
            # 🔎 AUTOMATIC WEB SEARCH
            # =================================================

            search_results = ""

            if needs_web_search(idea):

                with st.spinner("🔎 Nexa is searching the web..."):

                    search_results = web_search(idea)

            # =================================================
            # 🧠 FINAL SYSTEM PROMPT
            # =================================================

            final_system_prompt = active_plugin_prompt

            if search_results:

                final_system_prompt += f"""

LIVE WEB SEARCH RESULTS:

{search_results}

IMPORTANT WEB SEARCH RULES:

- Use the live web search results to answer the user's question.
- Prefer information from the search results.
- Do not invent facts, prices, dates, or sources.
- Clearly distinguish current information from general knowledge.
- If the search results are insufficient, say so honestly.
"""

            # =================================================
            # 🤖 NEXA AI RESPONSE
            # =================================================

            with st.spinner("🧠 Nexa is thinking..."):

                response = client.chat.completions.create(

                    model=selected_model,

                    messages=[
                        {
                            "role": "system",
                            "content": final_system_prompt
                        },
                        {
                            "role": "user",
                            "content": idea
                        }
                    ],

                    temperature=temperature,
                    max_tokens=1000
                )

            # =================================================
            # 🛑 CHECK IF STOPPED
            # =================================================

            if st.session_state.stop_generation:

                st.warning("⛔ Nexa generation stopped.")

            elif response is None:

                st.error("❌ Nexa returned no response.")

            elif not response.choices:

                st.error("❌ Nexa returned no choices.")

                st.code(str(response))

            else:

                result = response.choices[0].message.content

                if result and result.strip():

                    st.session_state.current_response = result

                    # =================================================
                    # 🤖 NEXA RESPONSE
                    # =================================================

                    st.markdown("### 🤖 Nexa Response")

                    st.write(result)

                    # =================================================
                    # 🔎 WEB SEARCH STATUS
                    # =================================================

                    if search_results:

                        st.success(
                            "🔎 Live Web Search was used for this answer."
                        )

                    # =================================================
                    # 🔊 NEXA VOICE
                    # =================================================

                    voice_text = result.replace("\n", " ")

                    selected_voice = st.session_state.get(
                        "selected_voice",
                        "👨 Male — Calm"
                    )

                    voice_script = f"""
                    <script>

                    function playNexaVoice() {{

                        const text = {json.dumps(voice_text)};
                        const selectedVoice = {json.dumps(selected_voice)};

                        const speak = () => {{

                            const voices =
                                window.speechSynthesis.getVoices();

                            let voice = null;

                            if (selectedVoice.includes("Female")) {{

                                voice = voices.find(v =>
                                    /zira|susan|hazel|samantha|aria|jenny|ava/i.test(v.name)
                                );

                            }} else {{

                                voice = voices.find(v =>
                                    /david|mark|guy|ryan|daniel/i.test(v.name)
                                );

                            }}

                            const utterance =
                                new SpeechSynthesisUtterance(text);

                            if (voice) {{
                                utterance.voice = voice;
                            }}

                            utterance.rate =
                                selectedVoice.includes("Deep")
                                ? 0.85
                                : 0.95;

                            utterance.pitch =
                                selectedVoice.includes("Female")
                                ? 1.1
                                : 0.9;

                            utterance.volume = 1.0;

                            window.speechSynthesis.cancel();

                            window.speechSynthesis.speak(utterance);

                        }};

                        if (
                            window.speechSynthesis.getVoices().length === 0
                        ) {{

                            window.speechSynthesis.onvoiceschanged = speak;

                        }} else {{

                            speak();

                        }}

                    }}

                    function stopNexaVoice() {{

                        window.speechSynthesis.cancel();

                    }}

                    </script>

                    <button onclick="playNexaVoice()">
                        🔊 Play Voice
                    </button>

                    <button onclick="stopNexaVoice()">
                        🛑 Stop Voice
                    </button>
                    """

                    st.components.v1.html(
                        voice_script,
                        height=60
                    )

                    # =================================================
                    # 📤 SHARE & DOWNLOAD
                    # =================================================

                    st.markdown("### 📤 Share & Download")

                    share_col1, share_col2, share_col3, share_col4 = st.columns(4)

                    # =================================================
                    # ⬇️ DOWNLOAD
                    # =================================================

                    with share_col1:

                        st.download_button(
                            "⬇️ Download",
                            data=result,
                            file_name="nexa_response.txt",
                            mime="text/plain",
                            use_container_width=True,
                            key="download_nexa_response"
                        )

                    # =================================================
                    # 🔗 SHARE
                    # =================================================

                    with share_col2:

                        share_script = f"""
                        <script>

                        function shareNexaResponse() {{

                            const text = {json.dumps(result)};

                            if (navigator.share) {{

                                navigator.share({{
                                    title: "Nexa AI Response",
                                    text: text
                                }});

                            }} else {{

                                navigator.clipboard.writeText(text);

                                alert("✅ Response copied!");

                            }}

                        }}

                        </script>

                        <button onclick="shareNexaResponse()">
                            🔗 Share
                        </button>
                        """

                        st.components.v1.html(
                            share_script,
                            height=60
                        )

                    # =================================================
                    # 🟢 WHATSAPP
                    # =================================================

                    with share_col3:

                        whatsapp_text = json.dumps(
                            "Nexa AI Response:\n\n" + result
                        )

                        whatsapp_script = f"""
                        <script>

                        function shareWhatsApp() {{

                            const text = {whatsapp_text};

                            const url =
                                "https://wa.me/?text=" +
                                encodeURIComponent(text);

                            window.open(url, "_blank");

                        }}

                        </script>

                        <button onclick="shareWhatsApp()">
                            🟢 WhatsApp
                        </button>
                        """

                        st.components.v1.html(
                            whatsapp_script,
                            height=60
                        )

                    # =================================================
                    # 📸 INSTAGRAM
                    # =================================================

                    with share_col4:

                        instagram_script = f"""
                        <script>

                        function shareInstagram() {{

                            const text = {json.dumps(result)};

                            navigator.clipboard.writeText(text);

                            window.open(
                                "https://www.instagram.com/",
                                "_blank"
                            );

                            alert(
                                "✅ Response copied! Paste it into Instagram."
                            );

                        }}

                        </script>

                        <button onclick="shareInstagram()">
                            📸 Instagram
                        </button>
                        """

                        st.components.v1.html(
                            instagram_script,
                            height=60
                        )

                    # =================================================
                    # 💾 SAVE CHAT HISTORY
                    # =================================================

                    st.session_state.chat_history.append(
                        {
                            "idea": idea,
                            "response": result,
                            "goal": goal
                        }
                    )

                    # =================================================
                    # ✅ SUCCESS
                    # =================================================

                    st.success(
                        "⚡ Nexa has analyzed your idea!"
                    )

                else:

                    st.error(
                        "❌ Nexa returned an empty response."
                    )

        except Exception as e:

            st.error(
                "❌ Nexa generation failed."
            )

            st.code(str(e))



col1, col2 = st.columns(2)


with col1:
    if st.button("💡 Idea Lab"):
        st.info("💡 Idea Lab activated — let's turn your idea into a clear plan.")
         
with col2:
    if st.button("📈 Business"):
        st.info("📈 Business mode activated — let's build a smarter growth strategy.")

col3, col4 = st.columns(2)

with col3:
    if st.button("🎨 Creative"):
        st.info("🎨 Creative mode activated — let's turn your ideas into something memorable.")

with col4:
    if st.button("🧠 Deep Think"):
        st.info("🧠 Deep Think activated — let's break your problem into smarter steps.")

        st.markdown("---")
        st.caption("⚡ Nexa is ready. Choose a mode and bring your idea to life.")

        st.markdown("### 💭 What are you working on?")
        idea = st.text_area(
    "Tell nexa your goal , idea , probelm or question...",
    placeholder="start typing here...",
    height=150
)
st.markdown("### 📎 Upload a File")

uploaded_file = st.file_uploader(
    "Upload your file",
    type=["txt", "pdf", "docx"]
)

if uploaded_file:
    st.success(f"✅ {uploaded_file.name} uploaded successfully!")

    if uploaded_file.type == "text/plain":
        file_text = uploaded_file.read().decode("utf-8")

    elif uploaded_file.type == "application/pdf":
        import PyPDF2

        pdf_reader = PyPDF2.PdfReader(uploaded_file)

        file_text = ""

        for page in pdf_reader.pages:
            file_text += page.extract_text() or ""

    else:
        file_text = ""

    if file_text:
        st.success("📄 File text successfully extracted!")

        file_question = st.text_input(
            "❓ Ask a question about your file"
        )

        if st.button("🔎 Ask Nexa"):
            if file_question:

                try:
                    response = client.chat.completions.create(
                        model="nvidia/nemotron-3-ultra-550b-a55b:free",
                        messages=[
                            {
                                "role": "system",
                                "content": "You answer questions using the uploaded file."
                            },
                            {
                                "role": "user",
                                "content": f"""
Here is the uploaded file:

{file_text}

User's question:
{file_question}

Answer the question using the uploaded file.
If the answer is not present in the file, clearly say that.
"""
                            }
                        ]
                    )

                    answer = response.choices[0].message.content

                    st.markdown("### 🤖 Nexa Answer")
                    st.write(answer)

                except Exception as e:
                    st.error("❌ Nexa couldn't read the file or answer the question.")
                    st.code(str(e))

            else:
                st.warning("⚠️ Please enter a question first.")

# ============================================================
# 🖼️ IMAGE UPLOAD
# ============================================================

st.markdown("### 🖼️ Image Upload")

media_file = st.file_uploader(
    "Upload an image",
    type=[
        "png",
        "jpg",
        "jpeg",
        "webp"
    ],
    key="media_uploader"
)

if media_file:

    # ========================================================
    # 🖼️ IMAGE ANALYSIS
    # ========================================================

    if media_file.type.startswith("image/"):

        st.success(
            f"✅ Image uploaded: {media_file.name}"
        )

        st.image(
            media_file,
            caption="Uploaded Image",
            use_container_width=True
        )

        image_prompt = st.text_area(
            "🤖 What should Nexa analyze?",
            placeholder=(
                "Example: Analyze this image in detail "
                "and tell me what you see."
            ),
            key="media_image_prompt"
        )

        if st.button(
            "🔍 Analyze Image",
            use_container_width=True,
            key="analyze_uploaded_image"
        ):

            with st.spinner(
                "🧠 Nexa is analyzing the image..."
            ):

                analysis_result = analyze_image(
                    media_file,
                    image_prompt.strip()
                    if image_prompt.strip()
                    else "Analyze this image in detail."
                )

            st.markdown(
                "### 🤖 Nexa Image Analysis"
            )

            st.write(analysis_result)



st.markdown("### 💻 Code Generator")

code_request = st.text_area(
    "Describe the code you want Nexa to create",
    placeholder="Example: Create a Python calculator.",
    height=120,
    key="code_request"
)

if st.button("💻 Generate Code"):

    if not code_request.strip():
        st.warning("⚠️ Please describe the code you want.")

    else:
        try:
            with st.spinner("🧠 Nexa is writing your code..."):

                response = client.chat.completions.create(
                    model="nvidia/nemotron-3-ultra-550b-a55b:free",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are Nexa AI Code Generator. Generate complete, clean and working code."
                        },
                        {
                            "role": "user",
                            "content": code_request
                        }
                    ]
                )

                if response is None:
                    st.error("❌ Nexa returned no response.")

                elif not response.choices:
                    st.error("❌ Nexa returned an empty response.")

                else:
                    generated_code = response.choices[0].message.content

                    if generated_code:
                        st.success("✅ Code generated successfully!")
                        st.markdown("### 💻 Generated Code")
                        st.code(generated_code)

                    else:
                        st.error("❌ Nexa returned empty code.")

        except Exception as e:
            st.error("❌ Code generation failed.")
            st.code(str(e))
st.markdown("### 🔍 Code Explanation")

code_to_explain = st.text_area(
    "Paste your code here",
    placeholder="Example:\nfor i in range(5):\n    print(i)",
    height=180,
    key="code_explanation"
)

if st.button("🔍 Explain Code"):

    if not code_to_explain.strip():
        st.warning("⚠️ Please paste some code first.")

    else:
        try:
            with st.spinner("🧠 Nexa is analyzing your code..."):

                response = client.chat.completions.create(
                    model="nvidia/nemotron-3-ultra-550b-a55b:free",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are Nexa AI Code Explainer.

Explain code in simple beginner-friendly language.

Include:
1. What the code does
2. How it works
3. Important lines
4. Any possible errors
5. How it could be improved
"""
                        },
                        {
                            "role": "user",
                            "content": code_to_explain
                        }
                    ]
                )

                if response is None or not response.choices:
                    st.error("❌ Nexa returned no explanation.")

                else:
                    explanation = response.choices[0].message.content

                    if explanation:
                        st.success("✅ Code explained successfully!")
                        st.markdown("### 🤖 Nexa Explanation")
                        st.write(explanation)

                    else:
                        st.error("❌ Nexa returned an empty explanation.")

        except Exception as e:
            st.error("❌ Code explanation failed.")
            st.code(str(e))
st.markdown("### 📝 Text Summarizer")

text_to_summarize = st.text_area(
    "Paste the text you want to summarize",
    placeholder="Paste an article, notes, paragraph, or any long text here...",
    height=180,
    key="summarize_text"
)

if st.button("📝 Summarize Text"):

    if not text_to_summarize.strip():
        st.warning("⚠️ Please enter some text first.")

    else:
        try:
            with st.spinner("🧠 Nexa is summarizing your text..."):

                response = client.chat.completions.create(
                    model="nvidia/nemotron-3-ultra-550b-a55b:free",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are Nexa AI Text Summarizer.

Summarize the user's text clearly and accurately.

Rules:
- Keep the important information.
- Remove unnecessary repetition.
- Use simple language.
- Use bullet points when helpful.
- Do not change the meaning.
"""
                        },
                        {
                            "role": "user",
                            "content": text_to_summarize
                        }
                    ]
                )

                if response is None or not response.choices:
                    st.error("❌ Nexa returned no summary.")

                else:
                    summary = response.choices[0].message.content

                    if summary:
                        st.success("✅ Summary generated successfully!")
                        st.markdown("### 📋 Summary")
                        st.write(summary)

                    else:
                        st.error("❌ Nexa returned an empty summary.")

        except Exception as e:
            st.error("❌ Text summarization failed.")
            st.code(str(e))
            st.markdown("### 🌐 Nexa Translator")

translation_text = st.text_area(
    "Enter text to translate",
    placeholder="Example: Hello, how are you?",
    height=150,
    key="translation_text"
)

target_language = st.selectbox(
    "Choose target language",
    [
        "English",
        "Urdu",
        "Hindi",
        "Arabic",
        "Spanish",
        "French",
        "German",
        "Chinese"
    ],
    key="target_language"
)

if st.button("🌐 Translate Text"):

    if not translation_text.strip():
        st.warning("⚠️ Please enter some text first.")

    else:
        try:
            with st.spinner("🧠 Nexa is translating..."):

                response = client.chat.completions.create(
                    model="nvidia/nemotron-3-ultra-550b-a55b:free",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are Nexa AI Translator.

Translate the user's text accurately into the requested language.

Rules:
- Preserve the original meaning.
- Keep the tone natural.
- Do not add unnecessary information.
- Return only the translated text.
"""
                        },
                        {
                            "role": "user",
                            "content": f"""
Translate this text into {target_language}:

{translation_text}
"""
                        }
                    ]
                )

                if response is None or not response.choices:
                    st.error("❌ Nexa returned no translation.")

                else:
                    translation = response.choices[0].message.content

                    if translation:
                        st.success("✅ Translation completed!")
                        st.markdown("### 🌐 Translation")
                        st.write(translation)

                    else:
                        st.error("❌ Nexa returned an empty translation.")

        except Exception as e:
            st.error("❌ Translation failed.")
            st.code(str(e))