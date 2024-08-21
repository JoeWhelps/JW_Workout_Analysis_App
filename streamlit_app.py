import random
import streamlit as st
from yt_extractor import get_info
import database_service as dbs
# from py_workout_table import dates
# from py_workout_table import data_boi
import pandas as pd
import matplotlib.pyplot as plt

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

def parse_reps(reps_str):
    """Parse the reps string into a list of integers."""
    # Removing brackets and splitting by comma
    reps_str = reps_str.replace('[', '').replace(']', '')
    reps_list = []
    for rep in reps_str.split(","):
        print(rep)
        try:
            reps_list.append(int(rep))
        except:
            continue
    print(reps_list)
    
    return reps_list

def parse_weights(weights_str):
    """Parse the weights string into a list of integers."""
    return [int(weight) for weight in weights_str.split(',') if weight]

def analyze_workout(workouts, exercise_name):
    """Extract and analyze workout data for the selected exercise."""
    weight, reps, dates, table_w = [], [], [], []
    
    for workout_day in workouts:
        for workout in workout_day:
            if exercise_name.lower() in workout["Exercise Name"].lower():
                table_w.append(workout)
                weights = parse_weights(workout["Weight"])
                reps_list = parse_reps(workout["Reps"])
                
                if len(weights) == len(reps_list):
                    weight.extend(weights)
                    reps.extend(reps_list)
                    dates.extend([workout["Date"]] * len(weights))

    return weight, reps, dates, table_w

def display_analysis(weight, reps, dates, table_w):
    """Display analysis results using Streamlit."""
    st.markdown("## Analysis")
    if not weight:
        st.text("No data found for the selected exercise.")
        return

    st.text("Table of all entries with that exercise:")
    st.table(table_w)
    
    # Data preparation for plotting
    df = pd.DataFrame({
        "Date": pd.to_datetime(dates, format='%m/%d/%y'),
        "Weight": weight,
        "Reps": reps
    }).sort_values('Date')

    # Plot weight over time
    st.title('Weight Over Time')
    plt.figure(figsize=(10, 5))
    plt.plot(df['Date'], df['Weight'], marker='o')
    plt.xlabel('Date')
    plt.ylabel('Weight')
    plt.title('Weight Tracking')
    plt.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(plt)

    # Bar chart for weights
    st.bar_chart(df['Weight'])
    
    # Summary statistics
    st.markdown("### Summary Statistics")
    st.text(f"Max Weight: {df['Weight'].max()}")
    st.text(f"Min Weight: {df['Weight'].min()}")
    st.text(f"Average Weight: {df['Weight'].mean():.2f}")
    
    # Additional plot: Reps vs Weight
    st.title('Reps vs Weight')
    plt.figure(figsize=(10, 5))
    plt.scatter(df['Reps'], df['Weight'], marker='o')
    plt.xlabel('Reps')
    plt.ylabel('Weight')
    plt.title('Reps vs Weight')
    plt.grid(True)
    st.pyplot(plt)

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
st.text("This app connects to a harperdb database that contains 3 years of my workouts logged on my notes app, and a library of workout/motivation videos. Explore around and feel free to add your own entries")

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
    sel_work = st.text_input("choose a workout to analyze")
    if sel_work:
        if st.button("Analyze"):
            weight, reps, dates, table_w = analyze_workout(data_t["workouts"], sel_work)
            display_analysis(weight, reps, dates, table_w)
    
elif selection == "Log a Workout":
    st.markdown("Log a Workout")
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
    st.text("this is an app")

else:
    [ st.table(reversed(pep)) for pep in data_t["workouts"] ]
    # st.table(data_t["workouts"][1])
    # select_d = st.selectbox("Choose a date",dates)

    # Reverse the table when button is clicked
    if st.button("whatttt?"):  # Display the reversed table
        st.text("bro you good?")


