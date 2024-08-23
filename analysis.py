import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# file which holds the class for the analysis section

class Analysis_class:
    def __init__(self, workouts):
        self.workouts = workouts

    def parse_reps(self,reps_str):
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

    def parse_weights(self, weights_str):
        """Parse the weights string into a list of integers."""
        return [int(weight) for weight in weights_str.split(',') if weight]

    def analyze_workout(self, workouts, exercise_name):
        """Extract and analyze workout data for the selected exercise."""
        weight, reps, dates, table_w = [], [], [], []
        
        for workout_day in workouts:
            for workout in workout_day:
                if exercise_name.lower() in workout["Exercise Name"].lower():
                    table_w.append(workout)
                    weights = self.parse_weights(workout["Weight"])
                    reps_list = self.parse_reps(workout["Reps"])
                    
                    if len(weights) == len(reps_list):
                        weight.extend(weights)
                        reps.extend(reps_list)
                        dates.extend([workout["Date"]] * len(weights))

        return weight, reps, dates, table_w

    def display_analysis(self,weight, reps, dates, table_w):
        """Display analysis results using Streamlit."""
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

        # Summary statistics
        st.markdown("### Summary Statistics")
        st.text(f"Max Weight: {df['Weight'].max()}")
        st.text(f"Min Weight: {df['Weight'].min()}")
        st.text(f"Number of Workouts: {len(df['Weight'])}")
        st.text(f"Average Weight: {df['Weight'].mean():.2f}")

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
        st.title("Weight over time (bar chart)")
        st.bar_chart(df['Weight'])

        # Reps vs Weight
        st.title('Reps vs Weight')
        plt.figure(figsize=(10, 5))
        plt.scatter(df['Reps'], df['Weight'], marker='o')
        plt.xlabel('Reps')
        plt.ylabel('Weight')
        plt.title('Reps vs Weight')
        plt.grid(True)
        st.pyplot(plt)

        
        
        
        
        

