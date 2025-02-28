import streamlit as st
import pandas as pd
import pyodbc
import matplotlib.pyplot as plt
import seaborn as sns

# Function to connect to SQL Server using Windows Authentication
def connect_to_sql_server(server, database):
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"  # Use Windows Authentication
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to SQL Server: {e}")
        st.error("Please verify the server name, database name, and your permissions.")
        return None

# Function to fetch data from SQL Server
def fetch_data(conn, query):
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Login Page
def login_page():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Hardcoded credentials for demonstration
        if username == "admin" and password == "password":
            st.session_state.logged_in = True
            st.success("Login successful! Redirecting to the dashboard...")
        else:
            st.error("Invalid username or password. Please try again.")

# Main Dashboard
def main_dashboard():
    st.title("📊 Employee Data Visualization Dashboard")
    st.markdown("Welcome to the interactive employee data visualization dashboard! Use the sidebar filters to explore the data.")

    # Sidebar for SQL Server connection details
    st.sidebar.header("🔍 SQL Server Connection")
    server = st.sidebar.text_input("Server Name", "DESKTOP-CBADVFM\SQLEXPRESS")
    database = st.sidebar.text_input("Database Name", "DE_CAPSTONE_PROJECT")

    # Connect to SQL Server
    if st.sidebar.button("Connect to SQL Server"):
        with st.spinner("Connecting to SQL Server..."):
            conn = connect_to_sql_server(server, database)
            if conn:
                st.success("Connected to SQL Server successfully!")
                st.session_state.conn = conn  # Save connection in session state

    # Fetch data from SQL Server
    if "conn" in st.session_state:
        st.sidebar.header("🔍 Filters")
        st.sidebar.markdown("Use the filters below to customize the data displayed.")

        # Fetch data from SQL Server
        query = "SELECT * FROM final_table"  # Replace with your table name
        df = fetch_data(st.session_state.conn, query)

        if df is not None:
            # Convert date columns to datetime (if applicable)
            if "hire_date" in df.columns:
                df["hire_date"] = pd.to_datetime(df["hire_date"])
            if "last_date" in df.columns:
                df["last_date"] = pd.to_datetime(df["last_date"])

            # Calculate tenure (in years)
            if "hire_date" in df.columns and "last_date" in df.columns:
                df["tenure"] = (df["last_date"].fillna(pd.Timestamp.today()) - df["hire_date"]).dt.days / 365

            # Custom CSS to reduce font size of metrics
            st.markdown("""
                <style>
                .stMetric {
                    font-size: 6px !important;
                }
                </style>
                """, unsafe_allow_html=True)

            # Display key metrics
            st.header("📈 Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Employees", df.shape[0])
            with col2:
                st.metric("Employees Left", df[df["left"] == 1].shape[0])
            with col3:
                st.metric("Employees Stayed", df[df["left"] == 0].shape[0])
            with col4:
                st.metric("Maximum Salary", f"{df['salary'].max():,.2f}")

            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.metric("Minimum Salary", f"{df['salary'].min():,.2f}")
            with col6:
                st.metric("Average Salary", f"{df['salary'].mean():,.2f}")
            with col7:
                st.metric("Average Tenure", f"{df['tenure'].mean():.2f} yr")
            with col8:
                st.metric("Median Tenure", f"{df['tenure'].median():.2f} yr")

            # Visualization 1: Salary Distribution
            st.header("📊 Salary Distribution Among Employees")
            plt.figure(figsize=(6, 4))
            plt.hist(df["salary"], bins=5, color="skyblue", edgecolor="black")
            plt.title("Salary Distribution Among Employees")
            plt.xlabel("Salary")
            plt.ylabel("Number of Employees")
            plt.grid(False)
            st.pyplot(plt)

            # Visualization 2: Average Salary by Job Title
            st.header("📊 Average Salary Per Title")
            unique_employees = df.drop_duplicates(subset="emp_no")
            avg_salary_by_title = unique_employees.groupby("title")["salary"].mean().sort_values(ascending=False).reset_index()
            plt.figure(figsize=(8, 4))
            sns.barplot(x="title", y="salary", data=avg_salary_by_title, palette="viridis")
            plt.title("Average Salary Per Title")
            plt.xlabel("Job Title")
            plt.ylabel("Average Salary")
            plt.xticks(rotation=45)
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            st.pyplot(plt)

            # Visualization 3: Tenure Distribution
            st.header("📊 Tenure Distribution of Employees")
            plt.figure(figsize=(6, 4))
            plt.hist(df["tenure"], color="skyblue", edgecolor="black")
            plt.title("Tenure Distribution of Employees")
            plt.xlabel("Tenure (Years)")
            plt.ylabel("Number of Employees")
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            st.pyplot(plt)

            # Visualization 4: Employee Attrition Distribution
            st.header("📊 Employee Attrition Distribution")
            emp_left = df[df["left"] == 1].shape[0]
            emp_stayed = df[df["left"] == 0].shape[0]
            result_df = pd.DataFrame({
                "emp_status": ["Left", "Stayed"],
                "no_of_emp": [emp_left, emp_stayed]
            })
            result_df["percntg"] = (result_df["no_of_emp"] * 100.00) / result_df["no_of_emp"].sum()
            colors = sns.color_palette("pastel")
            plt.figure(figsize=(2,2))
            plt.pie(result_df["no_of_emp"], labels=result_df["emp_status"], autopct="%1.1f%%", colors=colors, startangle=140)
            plt.title("Employee Attrition Distribution")
            st.pyplot(plt)

            # Visualization 5: Employee Attrition by Gender
            st.header("📊 Employee Attrition by Gender")
            male_emp = df[(df["left"] == 1) & (df["sex"] == "M")].shape[0]
            female_emp = df[(df["left"] == 1) & (df["sex"] == "F")].shape[0]
            gen_df = pd.DataFrame({
                "emp_gender": ["Male", "Female"],
                "no_of_emp": [male_emp, female_emp]
            })
            plt.figure(figsize=(6, 4))
            sns.barplot(x="emp_gender", y="no_of_emp", data=gen_df, hue="emp_gender", legend=False, palette="coolwarm")
            plt.xlabel("Gender")
            plt.ylabel("Number of Employees Left")
            plt.title("Employee Attrition by Gender")
            st.pyplot(plt)

            # Visualization 6: Employee Attrition by Job Title
            st.header("📊 Employee Attrition by Job Title")
            df_filtered = df[df["left"] == 1]
            title_counts = df_filtered.groupby("title").size().reset_index(name="total_no")
            total_sum = title_counts["total_no"].sum()
            title_counts["pct"] = title_counts["total_no"] * 100.0 / total_sum
            title_counts_sorted = title_counts.sort_values(by="total_no", ascending=False)
            plt.figure(figsize=(12, 6))
            sns.barplot(x="total_no", y="title", hue="title", data=title_counts_sorted, palette="viridis")
            plt.xlabel("Total Count")
            plt.ylabel("Job Title")
            plt.title("Employee Attrition by Job Title")
            for index, row in title_counts_sorted.iterrows():
                plt.text(row["total_no"] + 100, index, f"{row['pct']:.2f}%", va="center", fontsize=9)
            st.pyplot(plt)

            # Visualization 7: Employee Attrition by Salary Range
            st.header("📊 Employee Attrition by Salary Range")
            def get_salary_range(salary):
                if 40000 <= salary <= 60000:
                    return "40k-60k"
                elif 60001 <= salary <= 80000:
                    return "60k-80k"
                elif 80001 <= salary <= 100000:
                    return "80k-100k"
                elif 100001 <= salary <= 129492:
                    return "100k-130k"
                else:
                    return "Unknown"
            df["salary_range"] = df["salary"].apply(get_salary_range)
            salary_counts = df.groupby("salary_range")["emp_no"].count().reset_index(name="NO_OF_EMP")
            total_employees = salary_counts["NO_OF_EMP"].sum()
            salary_counts["PCT"] = salary_counts["NO_OF_EMP"] * 100.0 / total_employees
            salary_counts_sorted = salary_counts.sort_values("salary_range")
            plt.figure(figsize=(12, 6))
            sns.barplot(data=salary_counts_sorted, x="salary_range", y="NO_OF_EMP", hue="salary_range", palette="viridis")
            plt.title("Employee Attrition by Salary Range")
            plt.xlabel("Salary Range")
            plt.ylabel("Number of Employees")
            ax2 = plt.gca().twinx()
            sns.lineplot(data=salary_counts_sorted, x="salary_range", y="PCT", ax=ax2, color="red", marker="o", label="Percentage", linewidth=2)
            ax2.set_ylabel("Percentage of Total (%)", fontsize=12, color="red")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(plt)

            # Visualization 8: Total Number of People and Percentage per Last Performance Rating
            st.header("📊 Total Number of People and Percentage per Last Performance Rating")
            filtered_df = df[df["left"] == 1]
            grouped_df = filtered_df.groupby("Last_performance_rating").size().reset_index(name="total_no")
            total_count = grouped_df["total_no"].sum()
            grouped_df["pct"] = (grouped_df["total_no"] * 100.0) / total_count
            grouped_df = grouped_df.sort_values(by="total_no", ascending=False)
            plt.figure(figsize=(12, 6))
            sns.barplot(x="Last_performance_rating", y="total_no", data=grouped_df, hue="Last_performance_rating", palette="viridis")
            plt.title("Total Number of People and Percentage per Last Performance Rating", fontsize=16)
            plt.xlabel("Last Performance Rating", fontsize=12)
            plt.ylabel("Total Number of People", fontsize=12)
            ax2 = plt.gca().twinx()
            sns.lineplot(x="Last_performance_rating", y="pct", data=grouped_df, ax=ax2, color="red", marker="o", label="Percentage", linewidth=2)
            ax2.set_ylabel("Percentage of Total (%)", fontsize=12, color="red")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

            # Visualization 9: Number of Employees by Tenure Group
            st.header("📊 Number of Employees by Tenure Group")
            filtered_df = df[df["left"] == 1]
            def tenure_group(tenure):
                if 1 <= tenure <= 4:
                    return "Low Tenure(>=1 to <=4)"
                elif 4 < tenure <= 8:
                    return "Medium Tenure(>4 to <=8)"
                else:
                    return "High Tenure(>8 to <=14)"
            filtered_df["tenure_group"] = filtered_df["tenure"].apply(tenure_group)
            grouped_df = filtered_df.groupby("tenure_group").size().reset_index(name="NO_OF_EMP")
            grouped_df["PCT"] = (grouped_df["NO_OF_EMP"] * 100.00) / grouped_df["NO_OF_EMP"].sum()
            plt.figure(figsize=(10, 6))
            sns.barplot(x="tenure_group", y="NO_OF_EMP", data=grouped_df, hue="tenure_group", palette="viridis")
            plt.title("Number of Employees by Tenure Group", fontsize=16)
            plt.xlabel("Tenure Group", fontsize=14)
            plt.ylabel("Number of Employees", fontsize=14)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            st.pyplot(plt)

            # Visualization 10: Percentage of Employees by Tenure Group (Pie Chart)
            st.header("📊 Percentage of Employees by Tenure Group")
            plt.figure(figsize=(8, 8))
            plt.pie(
                grouped_df["PCT"],
                labels=grouped_df["tenure_group"],
                autopct="%1.1f%%",
                startangle=140,
                colors=sns.color_palette("viridis", len(grouped_df)))
            plt.title("Percentage of Employees by Tenure Group", fontsize=16)
            st.pyplot(plt)

            # Visualization 11: Number and Percentage of Employees by Age Group
            st.header("📊 Number and Percentage of Employees who left by Age Group")
         
          
            df['hire_date'] = pd.to_datetime(df['birth_date'])
            df['last_date'] = pd.to_datetime(df['last_date'])

            df['birth_date'] = pd.to_datetime(df['birth_date'])

         
            df['age'] = ((df['last_date'].fillna(pd.Timestamp.today()) - df['birth_date']).dt.days )/ 365

         
            filtered_df = df[df["left"] == 1]

            def age_group(age):
                if 21 <= age <= 30:
                    return "21-30"
                elif 30 < age <= 40:
                    return "31-40"
                elif 40 < age <= 50:
                    return "41-50"
                elif 50 < age <= 60:
                    return "51-60"
                else:
                    return ">60"

            
            filtered_df["age_group"] = filtered_df["age"].apply(age_group)

          
            grouped_df = filtered_df.groupby("age_group").size().reset_index(name="NO_OF_EMP")
            grouped_df["PCT"] = (grouped_df["NO_OF_EMP"] * 100.00) / grouped_df["NO_OF_EMP"].sum()

            fig, ax1 = plt.subplots(figsize=(12, 6))
            sns.barplot(x="age_group", y="NO_OF_EMP", data=grouped_df, hue="age_group", palette="viridis", ax=ax1)
            ax1.set_title("Number and Percentage of Employees by Age Group", fontsize=16)
            ax1.set_xlabel("Age Group", fontsize=14)
            ax1.set_ylabel("Number of Employees", fontsize=14)
            ax1.tick_params(axis="x", labelsize=12)
            ax1.tick_params(axis="y", labelsize=12)

            ax2 = ax1.twinx()
            sns.lineplot(x="age_group", y="PCT", data=grouped_df, color="red", marker="o", ax=ax2)
            ax2.set_ylabel("Percentage (%)", fontsize=14)
            ax2.tick_params(axis="y", labelsize=12)

            st.pyplot(fig)
        

            # Visualization 12: Number of Employees by Job Title
            st.header("📊 Number of Employees by Job Title")
            result = df.groupby("title").size().reset_index(name="total_emp")
            result = result.sort_values(by="total_emp", ascending=False)
            plt.figure(figsize=(10, 6))
            sns.barplot(x="title", y="total_emp", data=result, hue="title", palette="viridis")
            plt.title("Number of Employees by Job Title", fontsize=16)
            plt.xlabel("Job Title", fontsize=14)
            plt.ylabel("Number of Employees", fontsize=14)
            plt.xticks(rotation=45, fontsize=12)
            plt.yticks(fontsize=12)
            for index, value in enumerate(result["total_emp"]):
                plt.text(index, value + 0.1, str(value), ha="center", va="bottom", fontsize=12)
            plt.tight_layout()
            st.pyplot(plt)

            # Visualization 13: Average Salary by Job Title
            st.header("📊 Average Salary by Job Title")
            result = df.groupby("title")["salary"].mean().reset_index(name="avg_sal")
            result = result.sort_values(by="avg_sal", ascending=False)
            plt.figure(figsize=(10, 6))
            sns.barplot(x="title", y="avg_sal", data=result, hue="title", palette="viridis")
            plt.title("Average Salary by Job Title", fontsize=16)
            plt.xlabel("Job Title", fontsize=14)
            plt.ylabel("Average Salary", fontsize=14)
            plt.xticks(rotation=45, fontsize=12)
            plt.yticks(fontsize=12)
            for index, value in enumerate(result["avg_sal"]):
                plt.text(index, value + 500, f"{value:.2f}", ha="center", va="bottom", fontsize=12)
            plt.tight_layout()
            st.pyplot(plt)

            # Visualization 14: Number of Employees Hired by Year
            st.header("📊 Number of Employees Hired by Year")
            df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce")
            df["hire_year"] = df["hire_date"].dt.year
            result = df.groupby("hire_year").size().reset_index(name="employee_count")
            result = result.sort_values(by="hire_year")
            plt.figure(figsize=(10, 6))
            sns.lineplot(x="hire_year", y="employee_count", data=result, marker="o", color="blue")
            plt.title("Number of Employees Hired by Year", fontsize=16)
            plt.xlabel("Year", fontsize=14)
            plt.ylabel("Number of Employees", fontsize=14)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            for index, row in result.iterrows():
                plt.text(row["hire_year"], row["employee_count"] + 0.1, str(row["employee_count"]), ha="center", va="bottom", fontsize=12)
            plt.grid(False)
            plt.tight_layout()
            st.pyplot(plt)

            # Visualization 15: Number of Exits per Year
            st.header("📊 Number of Exits per Year")
            df["last_date"] = pd.to_datetime(df["last_date"], errors="coerce")
            df_valid = df[df["last_date"].notna()]
            df_valid["exit_year"] = df_valid["last_date"].dt.year
            exit_counts = df_valid.groupby("exit_year").agg(total_exits=("emp_no", "count")).reset_index()
            exit_counts_sorted = exit_counts.sort_values(by="exit_year").reset_index(drop=True)
            plt.figure(figsize=(6, 4))
            sns.lineplot(data=exit_counts_sorted, x="exit_year", y="total_exits", marker="o", color="blue")
            plt.title("Number of Exits per Year", fontsize=16)
            plt.xlabel("Exit Year", fontsize=12)
            plt.ylabel("Total Exits", fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

            # Visualization 16: Average Salary by Hire Year
            st.header("📊 Average Salary by Hire Year")
            df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce")
            df["hire_year"] = df["hire_date"].dt.year
            result = df.groupby("hire_year")["salary"].mean().reset_index(name="avg_salary")
            result = result.sort_values(by="hire_year")
            plt.figure(figsize=(6, 4))
            sns.lineplot(data=result, x="hire_year", y="avg_salary", marker="o", color="green")
            plt.title("Average Salary by Hire Year", fontsize=16)
            plt.xlabel("Hire Year", fontsize=12)
            plt.ylabel("Average Salary", fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

            # Visualization 17: Gender Distribution in the Company
            st.header("📊 Gender Distribution in the Company")
            female_count = df[df["sex"] == "F"].shape[0]
            male_count = df[df["sex"] == "M"].shape[0]
            gender_counts = pd.DataFrame({
                "gender": ["Female", "Male"],
                "total_no": [female_count, male_count]
            })
            total_count = gender_counts["total_no"].sum()
            gender_counts["pct"] = (gender_counts["total_no"] * 100) / total_count
            plt.figure(figsize=(3, 3))
            plt.pie(gender_counts["total_no"], labels=gender_counts["gender"], autopct="%1.1f%%", startangle=90, colors=["#ff9999", "#66b3ff"])
            plt.title("Gender Distribution in the Company", fontsize=16)
            plt.axis("equal")
            plt.tight_layout()
            st.pyplot(plt)

    # Close connection
    if "conn" in st.session_state and st.sidebar.button("Disconnect"):
        st.session_state.conn.close()
        del st.session_state.conn
        st.success("Disconnected from SQL Server.")

# Run the app
if __name__ == "__main__":
    # Check if the user is logged in
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        main_dashboard()
