import streamlit as st
from datetime import datetime, date

#1. SETTINGS
st.set_page_config(page_title="Assignment Tracker", layout="wide", page_icon="📝")

st.markdown("""
<style>
    /* Card Container */
    .main-card {
        background-color: #1e2130;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border-top: 4px solid #4f46e5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }

    /* Date & Time Badge */
    .date-badge {
        background-color: #31364a;
        padding: 5px 12px;
        border-radius: 8px;
        color: #e2e8f0;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* Difficulty Pill */
    .pill {
        float: right;
        padding: 6px 18px; /* Increased padding */
        border-radius: 20px;
        font-size: 1.1rem; /* Much bigger font size */
        font-weight: 800;  /* Extra bold */
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: -5px;
    }
    .pill-hard { background-color: #ef4444; color: white; }
    .pill-easy { background-color: #10b981; color: white; }

    /* Progress bar color tweak */
    .stProgress > div > div > div > div { background-color: #4f46e5; }
</style>
""", unsafe_allow_html=True)

if 'assignments' not in st.session_state:
    st.session_state.assignments = []
if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None


#2. LOGIC
def get_difficulty(marks, due_date):
    days_left = (due_date - date.today()).days
    score = marks / max(days_left, 1)
    return "HARD" if score > 10 else "EASY"


#3. MAIN INTERFACE
st.title("🎯 Assignment Hub")

form_label = "✏️ Edit Mode" if st.session_state.editing_index is not None else "➕ Add New Task"
with st.expander(form_label, expanded=(st.session_state.editing_index is not None)):
    curr = st.session_state.assignments[
        st.session_state.editing_index] if st.session_state.editing_index is not None else {"title": "", "course": "",
                                                                                            "group": "",
                                                                                            "date": date.today(),
                                                                                            "marks": 10, "desc": ""}

    t_col, c_col = st.columns([2, 1])
    title = t_col.text_input("Assignment Title", value=curr['title'])
    course = c_col.text_input("Course/Module", value=curr['course'])

    group = st.text_input("Group Name", value=curr['group'], placeholder="Leave empty for Individual")

    d_col, m_col = st.columns(2)
    due_date = d_col.date_input("Due Date", value=curr.get('date', date.today()))
    marks = m_col.number_input("Total Marks", min_value=1, value=curr['marks'])

    desc = st.text_area("Task Description", value=curr['desc'])

    s_col, can_col = st.columns([1, 6])
    if s_col.button("Save", type="primary", use_container_width=True):
        if title:
            diff = get_difficulty(marks, due_date)
            entry = {"title": title, "course": course, "group": group, "date": due_date, "marks": marks, "desc": desc,
                     "diff": diff}
            if st.session_state.editing_index is not None:
                st.session_state.assignments[st.session_state.editing_index] = entry
                st.session_state.editing_index = None
            else:
                st.session_state.assignments.append(entry)
            st.rerun()
    if st.session_state.editing_index is not None and can_col.button("Cancel"):
        st.session_state.editing_index = None
        st.rerun()

st.divider()

#4. DISPLAY SECTION
if not st.session_state.assignments:
    st.info("No assignments found. Enjoy your free time🥳!")
else:
    # Sort and split
    sorted_items = sorted(enumerate(st.session_state.assignments), key=lambda x: x[1]['date'])
    due_urgent = [i for i in sorted_items if (i[1]['date'] - date.today()).days <= 1]
    due_later = [i for i in sorted_items if (i[1]['date'] - date.today()).days > 1]


    def render_list(items, section_title, emoji):
        st.subheader(f"{emoji} {section_title}")
        for idx, a in items:
            days_rem = (a['date'] - date.today()).days
            pill_class = "pill-hard" if a['diff'] == "HARD" else "pill-easy"
            st.markdown(f"""
                <div class="main-card">
                    <span class="pill {pill_class}">{a['diff']}</span>
                    <div class="date-badge">📅 {a['date'].strftime('%d %b, %Y')}</div>
                    <h2 style="margin: 5px 0;">{a['title']}</h2>
                    <p style="color: #94a3b8; font-size: 0.9rem;">
                        📚Course: {a['course']} {' | 👥Group: ' + a['group'] if a['group'] else ' | 👤 Individual'}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            ctrl_col, ed_col, del_col = st.columns([4, 0.5, 0.5])

            with ctrl_col:
                if days_rem == 0:
                    st.error("❗DUE TODAY")
                if days_rem < 0:
                    st.error("❗OVERDUE")
                else:
                    prog_val = max(0, min(100, (14 - days_rem) * 7))  # Fills up over 2 weeks
                    st.progress(prog_val / 100, text=f"⏳ {days_rem} days until deadline")

            with ed_col:
                if st.button("📝", key=f"edit_{idx}"):
                    st.session_state.editing_index = idx
                    st.rerun()
            with del_col:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.assignments.pop(idx)
                    st.rerun()

            with st.expander("Show Detailed Description"):
                st.write(a['desc'] if a['desc'] else "No additional notes.")
            st.write("---")


    if due_urgent: render_list(due_urgent, "Due Very Soon", "🚨")
    if due_later: render_list(due_later, "Upcoming Assignments", "📅")