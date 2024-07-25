import streamlit as st
import pandas as pd
import mysql.connector

# Function to create a MySQL connection
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="***",
        database="db"
    )

# Function to execute a query and fetch data
def execute_query(query, conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return data

# Function to execute a query that modifies the database
def execute_update_query(query, conn):
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()

# Function to check student login credentials
def student_login(username, password, conn):
    query = f"SELECT * FROM student WHERE `Student_id` = '{username}' AND `Password` = '{password}'"
    result = execute_query(query, conn)
    return bool(result)

# Function to check mentor login credentials
def mentor_login(username, password, conn):
    query = f"SELECT * FROM mentors WHERE `Mentor ID` = '{username}' AND `Password` = '{password}'"
    result = execute_query(query, conn)
    return bool(result)

# Function to check if a student ID already exists
def student_exists(username, conn):
    query = f"SELECT * FROM student WHERE `Student_id` = '{username}'"
    result = execute_query(query, conn)
    return bool(result)

# Function to register a new student
def register_student(username, password, name,conn):
    query = f"INSERT INTO student (`Student_id`, `Password`, `Name`) VALUES ('{username}', '{password}','{name}' )"
    execute_update_query(query, conn)

def set_page(page_name):
    st.experimental_set_query_params(page=page_name)


# Streamlit app
st.title('College Credits Management System')



# Create a MySQL connection
conn = create_connection()

# Login or Register page
login_or_register = st.radio("Select Action:", ["Login", "Register"])

if login_or_register == "Login":
    # Login page
    login_option = st.radio("Select Login Type:", ["Student", "Mentor"])

    if login_option == "Student":
        st.subheader('Student Login:')
        username = st.text_input('Student_id:')
        password = st.text_input('Password:', type='password')

        if st.button('Login'):
            if student_login(username, password, conn):
                st.success('Login successful as student!')
                st.session_state.logged_in = True
                st.session_state.user_type = 'student'
                st.session_state.username = username
                set_page('student_dashboard')
            else:
                st.warning('Invalid credentials. Please try again.')

    elif login_option == "Mentor":
        st.subheader('Mentor Login:')
        username = st.text_input('Mentor ID:')
        password = st.text_input('Password:', type='password')

        if st.button('Login'):
            if mentor_login(username, password, conn):
                st.success('Login successful as mentor!')
                st.session_state.logged_in = True
                st.session_state.user_type = 'Mentor'
                st.session_state.username = username
                set_page('mentor_dashboard')
            else:
                st.warning('Invalid credentials. Please try again.')

elif login_or_register == "Register":
    # Registration page for students only
    st.subheader('Student Registration:')
    username = st.text_input('Student_id:')
    password = st.text_input('Password:', type='password')
    name = st.text_input('Name:')

    if st.button('Register'):
        if student_exists(username, conn):
            st.warning('Student_id already exists. Please choose another ID.')
        else:
            register_student(username, password,name, conn)
            st.success('Student registration successful! You can now login.')

if 'page' in st.experimental_get_query_params():
    page_name = st.experimental_get_query_params()['page'][0]
    if page_name == 'student_dashboard':
        # Display student dashboard
        st.subheader(f'Welcome, Student {st.session_state.username}!')

        # Add the code for student dashboard here
        # Assuming st.session_state.username is a string
        username = st.session_state.username
        query = f"SELECT * FROM student WHERE Student_id = '{username}'"
        df = pd.read_sql(query, conn)
        st.subheader('Current Data:')
        st.dataframe(df)

        # Courses selection for the logged-in student
        st.subheader('Choose Courses:')

        # Get the list of available courses from the Courses table
        courses_query = "SELECT Course_id, Title FROM Courses"
        courses_df = pd.read_sql(courses_query, conn)

        # Display a multiselect widget to allow the student to choose courses
        chosen_courses = st.multiselect("Semester Coursework:", courses_df['Title'])

        if st.button('Submit Choices'):
            # Check if the chosen courses are unique for the student
            existing_choices_query = f"SELECT Course_id FROM Sem_courses WHERE Student_id = '{username}'"
            existing_choices_df = pd.read_sql(existing_choices_query, conn)
            existing_course_ids = existing_choices_df['Course_id'].tolist()

            # Insert the chosen courses into the Sem_courses table if they are unique
            for course_title in chosen_courses:
                # Get the Course_id corresponding to the selected course title
                course_id = courses_df.loc[courses_df['Title'] == course_title, 'Course_id'].iloc[0]

                # Check if the course is not already chosen by the student
                if course_id not in existing_course_ids:
                    # Insert the choice into the Sem_courses table
                    insert_query = f"INSERT INTO Sem_courses (Student_id, Course_id) VALUES ('{username}', '{course_id}')"
                    execute_update_query(insert_query, conn)

            st.success('Courses chosen successfully!')


        # SQL query to get courses taken by the logged-in student
        query = f"""
            SELECT Sem_courses.Course_id, Courses.Title, Courses.Credits
            FROM Courses
            JOIN Sem_courses ON Courses.Course_id = Sem_courses.Course_id
            WHERE Sem_courses.Student_id = '{username}'
        """

        # Execute the query and display the result
        df_courses_taken = pd.read_sql(query, conn)
        st.subheader(f'Courses taken:')
        st.dataframe(df_courses_taken)

        if not df_courses_taken.empty:
            st.subheader('Delete Chosen Courses:')
            delete_chosen_courses = st.multiselect("Select Courses to Delete:", df_courses_taken['Title'])

            if st.button('Delete Courses'):
                for course_title in delete_chosen_courses:
                    # Get the Course_id corresponding to the selected course title
                    course_id_to_delete = df_courses_taken.loc[df_courses_taken['Title'] == course_title, 'Course_id'].iloc[0]

                    # Delete the chosen course from the Sem_courses table
                    delete_query = f"DELETE FROM Sem_courses WHERE Student_id = '{username}' AND Course_id = '{course_id_to_delete}'"
                    execute_update_query(delete_query, conn)

                st.success('Courses deleted successfully!')
        

        
    
        # Display form for entering project details
        st.subheader('Enter Your Capstone Project Details:')
        project_id = st.number_input('Project ID:', min_value=1, step=1)
        project_title = st.text_input('Project Title:')
        mentor_name = st.text_input('Mentor Name:')
        project_credits = st.number_input('Credits:', min_value=0, value=0)

        if st.button('Submit Project Details'):
            # Insert the project details into the Capstone_Project table
            insert_query = f"""
                INSERT INTO Capstone_Project (Title, Mentor, Credits, Project_id)
                VALUES ('{project_title}', '{mentor_name}', {project_credits}, {project_id})
            """
            execute_update_query(insert_query, conn)

            # Insert the student's involvement into the Workson table
            workson_query = f"INSERT INTO Workson (Student_id, Project_id) VALUES ('{username}', {project_id})"
            execute_update_query(workson_query, conn)

            st.success('Project details submitted successfully!')

        # Display the Capstone Project details for the logged-in student
        st.subheader('Your Capstone Project Details:')
        student_project_query = f"""
            SELECT Capstone_Project.Project_id, Capstone_Project.Title, Capstone_Project.Mentor, Capstone_Project.Credits
            FROM Capstone_Project
            JOIN Workson ON Capstone_Project.Project_id = Workson.Project_id
            WHERE Workson.Student_id = '{username}'
        """
        student_project_details = pd.read_sql(student_project_query, conn)

        if not student_project_details.empty:
            st.dataframe(student_project_details)

            # Allow students to update their Capstone Project details
            st.subheader('Update Capstone Project Details:')
            update_project_id = st.number_input('Project ID to Update:', min_value=1, step=1)
            update_title = st.text_input('New Project Title:')
            update_mentor = st.text_input('New Mentor Name:')
            update_credits = st.number_input('New Credits:', min_value=0, value=0)

            if st.button('Update Project Details'):
                # Update the Capstone_Project table with new details
                update_query = f"""
                    UPDATE Capstone_Project
                    SET Title = '{update_title}', Mentor = '{update_mentor}', Credits = {update_credits}
                    WHERE Project_id = {update_project_id} AND Project_id IN (
                        SELECT Project_id FROM Workson WHERE Student_id = '{username}'
                    )
                """
                execute_update_query(update_query, conn)

                st.success('Project details updated successfully!')
        else:
            st.warning('No Capstone Project details available for the logged-in student.')
        # Create

        # Display form for entering internship details
        st.subheader('Enter Your Internship Participation Details:')
        company_id = st.number_input('Company ID:', min_value=1, step=1)
        company_name = st.text_input('Company Name:')
        credits = st.number_input('Credits offered:', min_value=0, value=0)
        duration = st.number_input('Duration (weeks):', min_value=1, step=1)

        if st.button('Submit Internship Details'):
            # Insert the internship details into the Internship table
            insert_internship_query = f"""
                INSERT INTO Internship (Company_name, Credits, Duration, Company_id)
                VALUES ('{company_name}', {credits}, {duration}, {company_id})
            """
            execute_update_query(insert_internship_query, conn)

            # Insert the student's participation into the Participates table
            participates_query = f"INSERT INTO Participates (Student_id, Company_id) VALUES ('{username}', {company_id})"
            execute_update_query(participates_query, conn)

            st.success('Internship details submitted successfully!')

        # Display the Internship details for the logged-in student
        st.subheader('Your Internship Participation Details:')
        student_internship_query = f"""
            SELECT Internship.Company_id, Internship.Company_name, Internship.Credits, Internship.Duration
            FROM Internship
            JOIN Participates ON Internship.Company_id = Participates.Company_id
            WHERE Participates.Student_id = '{username}'
        """
        student_internship_details = pd.read_sql(student_internship_query, conn)

        if not student_internship_details.empty:
            st.dataframe(student_internship_details)

            # Allow the user to delete entries
            st.subheader('Delete Internship Entry:')
            delete_company_id = st.number_input('Enter Company ID to Delete:', min_value=1, step=1)

            if st.button('Delete Entry'):
                # Check if the entry exists before deleting
                check_entry_query = f"""
                    SELECT * FROM Participates
                    WHERE Student_id = '{username}' AND Company_id = {delete_company_id}
                """
                check_entry_df = pd.read_sql(check_entry_query, conn)

                if not check_entry_df.empty:
                    # Delete the entry from Participates
                    delete_participates_query = f"""
                        DELETE FROM Participates
                        WHERE Student_id = '{username}' AND Company_id = {delete_company_id}
                    """
                    execute_update_query(delete_participates_query, conn)

                    st.success('Entry deleted successfully!')
                else:
                    st.warning('Entry not found. Nothing to delete.')
        else:
            st.warning('No Internship details available for the logged-in student.')

        st.subheader('Choose Summer Courses:')

        # Get the list of available summer courses from the Summer_Course table
        courses_query = "SELECT Course_id, Title FROM Summer_Course"
        courses_df = pd.read_sql(courses_query, conn)

        # Display a multiselect widget to allow the student to choose summer courses
        chosen_courses = st.multiselect("Select Summer Courses:", courses_df['Title'])

        if st.button('Enroll'):
            # Check if the chosen courses are unique for the student
            existing_choices_query = f"SELECT Course_id FROM Chooses WHERE Student_id = '{username}'"
            existing_choices_df = pd.read_sql(existing_choices_query, conn)
            existing_course_ids = existing_choices_df['Course_id'].tolist()

            # Insert the chosen courses into the Chooses table if they are unique
            for course_title in chosen_courses:
                # Get the Course_id corresponding to the selected course title
                course_id = courses_df.loc[courses_df['Title'] == course_title, 'Course_id'].iloc[0]

                # Check if the course is not already chosen by the student
                if course_id not in existing_course_ids:
                    # Insert the choice into the Chooses table
                    insert_query = f"INSERT INTO Chooses (Student_id, Course_id) VALUES ('{username}', '{course_id}')"
                    execute_update_query(insert_query, conn)

            st.success('Summer courses chosen successfully!')

        # SQL query to get summer courses taken by the logged-in student
        query = f"""
            SELECT Chooses.Course_id, Summer_Course.Title, Summer_Course.Credits
            FROM Summer_Course
            JOIN Chooses ON Summer_Course.Course_id = Chooses.Course_id
            WHERE Chooses.Student_id = '{username}'
        """

        # Execute the query and display the result
        df_courses_taken = pd.read_sql(query, conn)
        st.subheader(f'Summer Courses taken:')
        st.dataframe(df_courses_taken)


    elif page_name == 'mentor_dashboard':
       
        st.subheader(f'Welcome, mentor {st.session_state.username}!')
        
        def_query = """
        SELECT s.Student_id, s.Name
        FROM Student s
        WHERE EXISTS (
            SELECT 1
            FROM Chooses ch
            JOIN Summer_Course sc ON ch.Course_id = sc.Course_id
            WHERE s.Student_id = ch.Student_id
            GROUP BY ch.Student_id
            HAVING SUM(sc.Credits) > 6
        )
        """
        defaulter_data = execute_query(def_query, conn)
        if defaulter_data:
            st.subheader('Defaulter Students:')
            df_defaulter = pd.DataFrame(defaulter_data)
            st.dataframe(df_defaulter)
        else:
            st.info('No defaulter students found.')

        # Read
        st.subheader('Search Student:')
        # search_id = st.text_input('Enter Student ID:', min_value=0, value=0)
        search_id = st.text_input('Enter Student ID:')

        if st.button('Search'):
            query = f"SELECT student.Student_id, student.Name, student.Total_credits FROM student WHERE `Student_id` = {search_id}"
            student_info = pd.read_sql(query, conn)
            if not student_info.empty:
                st.subheader('Student Information:')
                st.write(student_info)
            else:
                st.warning('Student not found.')

            course_query = f"""
                SELECT Sem_courses.Course_id, Courses.Title, Courses.Credits
                FROM Courses
                JOIN Sem_courses ON Courses.Course_id = Sem_courses.Course_id
                WHERE Sem_courses.Student_id = '{search_id}'
            """

            # Execute the query and display the result
            df_courses_taken = pd.read_sql(course_query, conn)
            st.subheader(f'Courses taken:')
            st.dataframe(df_courses_taken)

            int_query = f"""
                SELECT Participates.Company_id, Internship.Company_name, Internship.Duration, Internship.Credits
                FROM Internship
                JOIN Participates ON Internship.Company_id = Participates.Company_id
                WHERE Participates.Student_id = '{search_id}'
            """

            # Execute the query and display the result
            df_int = pd.read_sql(int_query, conn)
            st.subheader(f'Intership Details:')
            st.dataframe(df_int)

            cap_query = f"""
                SELECT Workson.Project_id, Capstone_Project.Title, Capstone_Project.Mentor, Capstone_Project.Credits
                FROM Capstone_Project
                JOIN Workson ON Capstone_Project.Project_id = Workson.Project_id
                WHERE Workson.Student_id = '{search_id}'
            """

            # Execute the query and display the result
            df_cap = pd.read_sql(cap_query, conn)
            st.subheader(f'Capstone Project Details:')
            st.dataframe(df_cap)

            summ_query = f"""
                SELECT Chooses.Student_id, Summer_Course.Title, Summer_Course.Credits
                FROM Chooses
                JOIN Summer_Course ON Chooses.Course_id = Summer_Course.Course_id
                WHERE Chooses.Student_id = '{search_id}'
            """

            # Execute the query and display the result
            df_sum = pd.read_sql(summ_query, conn)
            st.subheader(f'Summer Courses Enrolled:')
            st.dataframe(df_sum)


            unique_courses_query=f""""
                SELECT Name
                FROM Student
                WHERE Student_id IN (
                SELECT sc.Student_id
                FROM Sem_courses sc
                JOIN Courses c ON sc.Course_id = c.Course_id
                WHERE c.Credits > (
                    SELECT AVG(Credits)
                    FROM Courses)
                );
                """
        
conn.close()

