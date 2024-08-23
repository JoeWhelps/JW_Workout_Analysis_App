import random
import streamlit as st
from yt_extractor import get_info
import database_service as dbs
from analysis import Analysis_class

@st.cache_data
def get_workouts():
    return dbs.get_all_workouts()

def get_duration_text(duration_s):
    seconds = duration_s % 60
    minutes = int((duration_s / 60) % 60)
    hours = int((duration_s / (60*60)) % 24)
    text = ''
    if hours > 0:
        text += f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    else:
        text += f'{minutes:02d}:{seconds:02d}'
    return text

# Custom CSS
st.markdown(
    """
    <style>
    /* Background color for the entire app */
    .reportview-container {
        background-color: #e0e0e0; /* Light grey */
        color: #333333; /* Dark grey text */
    }
    /* Sidebar background color */
    .sidebar .sidebar-content {
        background-color: #b0b0b0; /* Medium grey */
    }
    /* Title styles */
    h1, h2, h3 {
        color: #990000; /* Red */
        text-align: center;
    }
    /* Default text color */
    .stMarkdown p, .stTextInput>div>input, .stTextArea>div>textarea {
        color: #333333; /* Dark grey text */
    }
    /* Button styles */
    .stButton>button {
        background-color: #990000; /* Red */
        color: white; /* White text on buttons */
    }
    /* Sidebar text color */
    .css-1n76uvr, .css-1v3fvcr, .css-1fv8s86, .css-12oz5g7 {
        color: #333333; /* Dark grey text */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# title
st.title("Workout APP")
st.subheader("By Joseph Whelpley")
st.text("Welcome, this app has three main functions:")
st.text("Workout Database")
st.text("Workout Analyzer")
st.text("Workout Youtube Video Library")

# menu options and sidebar 
opts = ("Workouts Home", "Analysis", "Log a Workout","Today's workout video", "All workout videos", "Add workout video","About this app")
selection = st.sidebar.selectbox("Menu", opts)

data_t = dbs.fetch_workout_data() # get all the workout_table data

# menu options selection
if selection == "All workout videos":
    st.markdown(f"## All workout videos")
    
    workouts = get_workouts()
    for wo in workouts:
        url = "https://youtu.be/" + wo["video_id"]
        st.text(wo['title'])
        st.text(f"{wo['channel']} - {get_duration_text(wo['duration'])}")
        
        ok = st.button('Delete workout video', key=wo["video_id"])
        if ok:
            dbs.delete_workout(wo["video_id"])
            st.cache_data.clear()
            st.experimental_rerun()
            
        st.video(url)
    else:
        st.text("No workout videos in Database!")
elif selection == "Add workout video":
    st.markdown(f"## Add workout video")
    
    url = st.text_input('Please enter the video url')
    if url:
        workout_data = get_info(url)
        if workout_data is None:
            st.text("Could not find video")
        else:
            st.text(workout_data['title'])
            st.text(workout_data['channel'])
            st.video(url)
            if st.button("Add workout video"):
                dbs.insert_workout(workout_data)
                st.text("Added workout!")
                st.cache_data.clear()
elif selection == "Today's workout video":
    st.markdown(f"## Today's workout video")
    
    workouts = get_workouts()
    if not workouts:
        st.text("No workout videos in Database!")
    else:
        wo = dbs.get_workout_today() # workout of the day
        
        if not wo:
            # not yet defined
            workouts = get_workouts()
            n = len(workouts)
            idx = random.randint(0, n-1) # randomly select one
            wo = workouts[idx]
            dbs.update_workout_today(wo, insert=True) # make it the one of the day
        else:
            # first item in list
            wo = wo[0]
        
        if st.button("Choose another workout video"): 
            workouts = get_workouts()
            n = len(workouts)
            if n > 1:
                idx = random.randint(0, n-1)
                wo_new = workouts[idx]
                while wo_new['video_id'] == wo['video_id']:
                    idx = random.randint(0, n-1)
                    wo_new = workouts[idx]
                wo = wo_new
                dbs.update_workout_today(wo)
        
        url = "https://youtu.be/" + wo["video_id"]
        st.text(wo['title'])
        st.text(f"{wo['channel']} - {get_duration_text(wo['duration'])}")
        st.video(url)

elif selection == "Analysis":
    st.markdown(f"## Analysis")
    sel_work = st.text_input("Choose a workout to analyze (ex: 'bench')")
    if sel_work:
        if st.button("Analyze"):
            ays = Analysis_class(data_t["workouts"])

            weight, reps, dates, table_w = ays.analyze_workout(data_t["workouts"], sel_work)
            ays.display_analysis(weight, reps, dates, table_w)
    
elif selection == "Log a Workout":
    st.markdown("## Log a Workout")
    st.text("This feature is currently not available. Need to fix user permissions")
    log1 = st.text_input('New workout (cleaned)')
    if log1:
        if st.button("Add workout entry"):
            log = {
                "workout_d": "value1",
                "field2": "value2",
                "joe" : "yes"
            }
            dbs.insert_workout_entry(log)
            dbs.insert_workout_entry(log1)
            st.text("Added workout!")
            st.cache_data.clear()

elif selection == "About this app":
    st.markdown(f"## About this app")
    st.text("For the past three years I have been logging my workouts in my notes app")
    st.text("They were very disorganized and hard to interpret")
    st.text("Then I had the idea to clean the data and see overall trends from this valuable data")
    st.text("With the help of chatgbt, I made sure each workout was fully converted into a JSON")
    st.text("Next, I uploaded my large JSON data onto HarperDB")
    st.text("After connecting to the database, I built the streamlit app and deployed")
    st.text("However, I am far from finished. I desire to keep building new features and new functions to expand the applications of this data.")

else:
    st.markdown("### All Workout Data")
    [ st.table(reversed(pep)) for pep in data_t["workouts"] ]


